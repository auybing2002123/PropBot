"""
健康检查接口
用于监控服务状态
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any

from app.db.database import Database, get_db

router = APIRouter(tags=["健康检查"])


class ServiceStatus(BaseModel):
    """服务状态模型"""
    postgres: str
    redis: str


class HealthData(BaseModel):
    """健康检查数据模型"""
    status: str
    services: ServiceStatus


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    code: int
    message: str
    data: HealthData


@router.get("/health", response_model=HealthResponse, summary="健康检查")
async def health_check() -> Dict[str, Any]:
    """
    检查服务健康状态
    
    返回 PostgreSQL 和 Redis 的连接状态
    """
    from app.db.database import db
    
    services = {}
    overall_healthy = True
    
    # 检查 PostgreSQL
    try:
        if db and await db.check_postgres():
            services["postgres"] = "healthy"
        else:
            services["postgres"] = "unhealthy: 未连接"
            overall_healthy = False
    except Exception as e:
        services["postgres"] = f"unhealthy: {str(e)}"
        overall_healthy = False
    
    # 检查 Redis
    try:
        if db and await db.check_redis():
            services["redis"] = "healthy"
        else:
            services["redis"] = "unhealthy: 未连接"
            overall_healthy = False
    except Exception as e:
        services["redis"] = f"unhealthy: {str(e)}"
        overall_healthy = False
    
    # 构建响应
    if overall_healthy:
        return {
            "code": 0,
            "message": "success",
            "data": {
                "status": "healthy",
                "services": services
            }
        }
    else:
        return {
            "code": 500,
            "message": "服务异常",
            "data": {
                "status": "unhealthy",
                "services": services
            }
        }
