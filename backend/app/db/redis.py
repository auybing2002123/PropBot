# Redis 客户端模块
# 提供 Redis 连接和缓存操作

import json
from typing import Any
import redis.asyncio as redis

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 全局 Redis 客户端
_redis_client: redis.Redis | None = None


async def get_redis_client() -> redis.Redis | None:
    """
    获取 Redis 客户端（懒加载）
    
    Returns:
        Redis 客户端实例，连接失败返回 None
    """
    global _redis_client
    
    if _redis_client is not None:
        return _redis_client
    
    try:
        settings = get_settings()
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        # 测试连接
        await _redis_client.ping()
        logger.info("Redis 连接成功")
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis 连接失败: {e}，缓存功能将被禁用")
        _redis_client = None
        return None


async def close_redis():
    """关闭 Redis 连接"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis 连接已关闭")


class KnowledgeCache:
    """
    知识库缓存服务
    缓存知识库查询结果，减少重复检索
    """
    
    # 缓存 key 前缀
    PREFIX = "kb:"
    
    # 默认过期时间（1小时）
    DEFAULT_TTL = 3600
    
    @staticmethod
    def _make_key(tool_name: str, query: str, city: str | None = None, **kwargs) -> str:
        """
        生成缓存 key
        
        Args:
            tool_name: 工具名称
            query: 查询内容
            city: 城市
            **kwargs: 其他参数
            
        Returns:
            缓存 key
        """
        # 构建 key：kb:{tool}:{city}:{query_hash}
        parts = [KnowledgeCache.PREFIX, tool_name]
        if city:
            parts.append(city)
        
        # 对查询内容做简单 hash（取前50字符 + 长度）
        query_key = f"{query[:50]}_{len(query)}"
        parts.append(query_key)
        
        # 添加其他参数
        for k, v in sorted(kwargs.items()):
            if v is not None:
                parts.append(f"{k}={v}")
        
        return ":".join(parts)
    
    @staticmethod
    async def get(
        tool_name: str, 
        query: str, 
        city: str | None = None,
        **kwargs
    ) -> dict | None:
        """
        获取缓存的查询结果
        
        Args:
            tool_name: 工具名称
            query: 查询内容
            city: 城市
            
        Returns:
            缓存的结果，未命中返回 None
        """
        client = await get_redis_client()
        if not client:
            return None
        
        try:
            key = KnowledgeCache._make_key(tool_name, query, city, **kwargs)
            data = await client.get(key)
            
            if data:
                logger.debug(f"缓存命中: {tool_name}, query={query[:20]}...")
                return json.loads(data)
            
            return None
        except Exception as e:
            logger.warning(f"读取缓存失败: {e}")
            return None
    
    @staticmethod
    async def set(
        tool_name: str,
        query: str,
        result: dict,
        city: str | None = None,
        ttl: int = DEFAULT_TTL,
        **kwargs
    ) -> bool:
        """
        缓存查询结果
        
        Args:
            tool_name: 工具名称
            query: 查询内容
            result: 查询结果
            city: 城市
            ttl: 过期时间（秒）
            
        Returns:
            是否成功
        """
        client = await get_redis_client()
        if not client:
            return False
        
        try:
            key = KnowledgeCache._make_key(tool_name, query, city, **kwargs)
            await client.setex(key, ttl, json.dumps(result, ensure_ascii=False))
            logger.debug(f"缓存写入: {tool_name}, query={query[:20]}..., ttl={ttl}s")
            return True
        except Exception as e:
            logger.warning(f"写入缓存失败: {e}")
            return False
    
    @staticmethod
    async def invalidate(tool_name: str | None = None) -> int:
        """
        清除缓存
        
        Args:
            tool_name: 工具名称，为 None 时清除所有知识库缓存
            
        Returns:
            清除的 key 数量
        """
        client = await get_redis_client()
        if not client:
            return 0
        
        try:
            pattern = f"{KnowledgeCache.PREFIX}{tool_name or ''}*"
            keys = []
            async for key in client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await client.delete(*keys)
                logger.info(f"清除缓存: {len(keys)} 个 key")
            
            return len(keys)
        except Exception as e:
            logger.warning(f"清除缓存失败: {e}")
            return 0
