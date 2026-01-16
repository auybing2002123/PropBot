"""
FastAPI 应用主入口
购房决策智能助手后端服务
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config.settings import get_settings
from app.db.database import Database
from app.api import health, chat, calculator, conversation, auth, favorite
from app.utils.logger import setup_logging, get_logger
from app.utils.exceptions import BaseAppException, LLMException, ToolException

# 加载配置
settings = get_settings()

# 初始化日志
setup_logging(debug=settings.DEBUG)
logger = get_logger("house_advisor")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时连接数据库，关闭时断开连接
    """
    # 启动时
    logger.info(f"正在启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # 初始化数据库连接
    from app.db import database
    database.db = Database(
        database_url=settings.DATABASE_URL,
        redis_url=settings.REDIS_URL,
        debug=settings.DEBUG
    )
    await database.db.connect()
    
    # 初始化 Chroma 向量数据库
    from app.db import chroma
    try:
        chroma.chroma_client = chroma.ChromaClient(
            host="localhost",
            port=8001,
            embedding_model_path=settings.EMBEDDING_MODEL_PATH
        )
        await chroma.chroma_client.connect()
        logger.info("Chroma 向量数据库连接成功")
    except Exception as e:
        logger.warning(f"Chroma 连接失败，将使用关键词匹配: {e}")
        chroma.chroma_client = None
    
    logger.info("服务启动完成")
    
    yield
    
    # 关闭时
    logger.info("正在关闭服务...")
    if chroma.chroma_client:
        await chroma.chroma_client.disconnect()
    if database.db:
        await database.db.disconnect()
    logger.info("服务已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于多智能体协作的购房决策智能助手",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(chat.router, prefix=settings.API_PREFIX)
app.include_router(calculator.router, prefix=settings.API_PREFIX)
app.include_router(conversation.router, prefix=settings.API_PREFIX)
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(favorite.router, prefix=settings.API_PREFIX)


# 注册异常处理器
@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    """
    处理应用自定义异常
    返回统一格式：{code, message, data}
    不暴露堆栈信息
    """
    # 根据异常类型记录不同级别的日志
    if isinstance(exc, LLMException):
        logger.error(f"LLM 异常: code={exc.code}, message={exc.message}")
    elif isinstance(exc, ToolException):
        logger.warning(f"工具执行异常: code={exc.code}, message={exc.message}")
    else:
        logger.warning(f"业务异常: code={exc.code}, message={exc.message}")
    
    return JSONResponse(
        status_code=exc.http_status,
        content=exc.to_dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求参数验证错误
    返回统一格式：{code, message, data}
    """
    # 提取错误字段信息
    errors = exc.errors()
    if errors:
        # 获取第一个错误的字段名
        first_error = errors[0]
        field_path = " -> ".join(str(loc) for loc in first_error.get("loc", []))
        error_msg = first_error.get("msg", "参数验证失败")
        message = f"参数验证错误：{field_path} - {error_msg}"
    else:
        message = "参数验证错误"
    
    logger.warning(f"请求验证失败: {message}")
    
    return JSONResponse(
        status_code=422,
        content={
            "code": 3001,
            "message": message,
            "data": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    处理通用异常
    不暴露堆栈信息给前端
    """
    logger.exception(f"未处理的异常: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "code": 1099,
            "message": "服务暂时不可用，请稍后重试",
            "data": None
        }
    )


@app.get("/", tags=["根路径"])
async def root():
    """根路径，返回服务信息"""
    return {
        "code": 0,
        "message": "success",
        "data": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs"
        }
    }
