"""
配置管理模块
使用 Pydantic Settings 从环境变量加载配置
"""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 数据库配置
    DATABASE_URL: str
    REDIS_URL: str
    CHROMA_URL: str
    
    # API 配置
    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    
    # Embedding 模型配置（使用本地 BGE 模型）
    EMBEDDING_MODEL_PATH: str = "~/models/bge-base-zh-v1.5"
    
    # 应用配置
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    APP_NAME: str = "购房决策智能助手"
    APP_VERSION: str = "1.0.0"
    
    # CORS 配置（支持本地开发和 cpolar 穿透）
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "https://3e6579fa.r16.cpolar.top",  # cpolar 前端穿透地址
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例
    使用 lru_cache 缓存配置实例，避免重复加载
    """
    return Settings()
