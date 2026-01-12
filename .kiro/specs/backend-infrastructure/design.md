# Design Document

## Overview

本设计文档描述 backend-infrastructure Spec 的技术实现方案，包括 FastAPI 项目结构、Docker 数据库服务、配置管理、健康检查接口、数据库连接和日志配置。

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (WSL)                         │
│                    Port: 8080                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    app/main.py                           │   │
│  │  • FastAPI 应用实例                                       │   │
│  │  • CORS 配置                                              │   │
│  │  • 生命周期管理 (startup/shutdown)                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│         ┌────────────────────┼────────────────────┐            │
│         ▼                    ▼                    ▼            │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐      │
│  │ app/config/ │     │  app/api/   │     │  app/db/    │      │
│  │ settings.py │     │ health.py   │     │ database.py │      │
│  │ • Pydantic  │     │ • /health   │     │ • SQLAlchemy│      │
│  │ • .env 加载  │     │ • 状态检查   │     │ • Redis     │      │
│  └─────────────┘     └─────────────┘     └─────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│ PostgreSQL  │       │    Redis    │       │   Chroma    │
│ Port: 5433  │       │ Port: 6380  │       │ Port: 8001  │
│ (Docker)    │       │ (Docker)    │       │ (Docker)    │
└─────────────┘       └─────────────┘       └─────────────┘
```

## Components

### 1. 项目目录结构

```
~/projects/house-advisor/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py      # Pydantic Settings 配置
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── health.py        # 健康检查路由
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   └── database.py      # 数据库连接管理
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── logger.py        # 日志配置
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_health.py       # 健康检查测试
│   ├── requirements.txt         # Python 依赖
│   ├── .env.example             # 环境变量模板
│   └── .env                     # 环境变量（不提交 Git）
├── docker-compose.yml           # Docker 数据库服务
└── .gitignore
```

### 2. 配置管理 (app/config/settings.py)

使用 Pydantic Settings 从环境变量加载配置：

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str
    REDIS_URL: str
    CHROMA_URL: str
    
    # API 配置
    DEEPSEEK_API_KEY: str
    
    # 应用配置
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### 3. 数据库连接 (app/db/database.py)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis

class Database:
    def __init__(self, settings):
        # PostgreSQL 异步引擎
        self.engine = create_async_engine(
            settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
            echo=settings.DEBUG
        )
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Redis 异步客户端
        self.redis = redis.from_url(settings.REDIS_URL)
    
    async def connect(self):
        # 测试连接
        async with self.engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        await self.redis.ping()
    
    async def disconnect(self):
        await self.engine.dispose()
        await self.redis.close()
```

### 4. 健康检查 (app/api/health.py)

```python
from fastapi import APIRouter, Depends
from app.db.database import Database

router = APIRouter()

@router.get("/health")
async def health_check(db: Database = Depends(get_db)):
    services = {}
    overall_healthy = True
    
    # 检查 PostgreSQL
    try:
        await db.check_postgres()
        services["postgres"] = "healthy"
    except Exception as e:
        services["postgres"] = f"unhealthy: {str(e)}"
        overall_healthy = False
    
    # 检查 Redis
    try:
        await db.check_redis()
        services["redis"] = "healthy"
    except Exception as e:
        services["redis"] = f"unhealthy: {str(e)}"
        overall_healthy = False
    
    if overall_healthy:
        return {"code": 0, "message": "success", "data": {"status": "healthy", "services": services}}
    else:
        return {"code": 500, "message": "服务异常", "data": {"status": "unhealthy", "services": services}}
```

### 5. 日志配置 (app/utils/logger.py)

```python
import logging
import sys

def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
    
    return logging.getLogger("house_advisor")
```

### 6. FastAPI 主入口 (app/main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.settings import get_settings
from app.db.database import Database
from app.api import health
from app.utils.logger import setup_logging

settings = get_settings()
db = Database(settings)
logger = setup_logging(settings.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    logger.info("正在连接数据库...")
    await db.connect()
    logger.info("数据库连接成功")
    yield
    # 关闭时
    logger.info("正在关闭数据库连接...")
    await db.disconnect()
    logger.info("数据库连接已关闭")

app = FastAPI(
    title="购房决策智能助手 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, prefix=settings.API_PREFIX)
```

### 7. Docker Compose (docker-compose.yml)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: house_advisor_postgres
    ports:
      - "5433:5432"
    environment:
      POSTGRES_USER: house_advisor
      POSTGRES_PASSWORD: house_advisor_pwd
      POSTGRES_DB: house_advisor
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U house_advisor"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    container_name: house_advisor_redis
    ports:
      - "6380:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  chroma:
    image: chromadb/chroma
    container_name: house_advisor_chroma
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma

volumes:
  postgres_data:
  redis_data:
  chroma_data:
```

## Data Models

### 统一响应格式

```python
from pydantic import BaseModel
from typing import Any, Optional

class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None
```

### 健康检查响应

```python
class ServiceStatus(BaseModel):
    postgres: str
    redis: str

class HealthData(BaseModel):
    status: str  # "healthy" | "unhealthy"
    services: ServiceStatus
```

## Correctness Properties

### Property 1: 配置完整性
- 应用启动时必须验证所有必需配置项存在
- 缺失配置项时抛出明确错误，阻止启动

### Property 2: 数据库连接可靠性
- 启动时必须成功连接 PostgreSQL 和 Redis
- 连接失败时记录错误日志并抛出异常

### Property 3: 健康检查准确性
- 健康检查必须真实反映各服务状态
- 任一服务不可用时返回 unhealthy 状态

### Property 4: 资源清理
- 应用关闭时必须正确关闭所有数据库连接
- 防止连接泄漏

## Error Handling

| 错误场景 | 处理方式 | 返回格式 |
|---------|---------|---------|
| 配置缺失 | 启动时抛出 ValidationError | 控制台错误信息 |
| 数据库连接失败 | 记录日志，抛出异常 | 启动失败 |
| 健康检查失败 | 返回 unhealthy 状态 | `{"code": 500, "message": "服务异常", ...}` |

## Testing Strategy

### 单元测试
- 配置加载测试：验证 Pydantic Settings 正确解析环境变量
- 日志配置测试：验证日志格式和级别

### 集成测试
- 健康检查接口测试：使用 HTTP MCP 调用 `/api/v1/health`
- 数据库连接测试：验证 PostgreSQL 和 Redis 连接

### 测试命令
```bash
# 在 WSL 中运行
conda activate house-advisor
pytest tests/ -v
```

## Dependencies

### requirements.txt
```
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
sqlalchemy==2.0.25
asyncpg==0.29.0
redis==5.0.1
```

## Environment Variables

### .env.example
```bash
# 数据库配置
DATABASE_URL=postgresql://house_advisor:house_advisor_pwd@localhost:5433/house_advisor
REDIS_URL=redis://localhost:6380/0
CHROMA_URL=http://localhost:8001

# API 配置
DEEPSEEK_API_KEY=your_api_key_here

# 应用配置
DEBUG=true
```
