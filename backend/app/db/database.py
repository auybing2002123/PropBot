"""
数据库连接管理模块
管理 PostgreSQL 和 Redis 的异步连接
"""
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import redis.asyncio as redis

from app.utils.logger import get_logger

logger = get_logger("house_advisor.db")


class Database:
    """数据库连接管理类"""
    
    def __init__(self, database_url: str, redis_url: str, debug: bool = False):
        """
        初始化数据库连接
        
        Args:
            database_url: PostgreSQL 连接字符串
            redis_url: Redis 连接字符串
            debug: 是否开启 SQL 日志
        """
        # 转换为异步连接字符串
        async_database_url = database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        
        # PostgreSQL 异步引擎
        self.engine: AsyncEngine = create_async_engine(
            async_database_url,
            echo=debug,  # 开发环境打印 SQL
            pool_size=5,
            max_overflow=10
        )
        
        # 异步会话工厂
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Redis 异步客户端
        self.redis: Optional[redis.Redis] = None
        self._redis_url = redis_url
    
    async def connect(self) -> None:
        """建立数据库连接"""
        logger.info("正在连接数据库...")
        
        # 测试 PostgreSQL 连接
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("PostgreSQL 连接成功")
        except Exception as e:
            logger.error(f"PostgreSQL 连接失败: {e}")
            raise
        
        # 连接 Redis
        try:
            self.redis = redis.from_url(self._redis_url, decode_responses=True)
            await self.redis.ping()
            logger.info("Redis 连接成功")
        except Exception as e:
            logger.error(f"Redis 连接失败: {e}")
            raise
    
    async def disconnect(self) -> None:
        """关闭数据库连接"""
        logger.info("正在关闭数据库连接...")
        
        # 关闭 PostgreSQL
        await self.engine.dispose()
        logger.info("PostgreSQL 连接已关闭")
        
        # 关闭 Redis
        if self.redis:
            await self.redis.close()
            logger.info("Redis 连接已关闭")
    
    async def check_postgres(self) -> bool:
        """检查 PostgreSQL 连接状态"""
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    async def check_redis(self) -> bool:
        """检查 Redis 连接状态"""
        try:
            if self.redis:
                await self.redis.ping()
                return True
            return False
        except Exception:
            return False
    
    async def get_session(self) -> AsyncSession:
        """获取数据库会话"""
        async with self.async_session() as session:
            yield session


# 全局数据库实例
db: Optional[Database] = None


def get_db() -> Database:
    """获取数据库实例"""
    if db is None:
        raise RuntimeError("数据库未初始化")
    return db


async def get_async_session() -> AsyncSession:
    """
    获取异步数据库会话（用于 FastAPI 依赖注入）
    
    Yields:
        AsyncSession: 数据库会话
    """
    if db is None:
        raise RuntimeError("数据库未初始化")
    
    async with db.async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
