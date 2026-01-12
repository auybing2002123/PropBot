# 工具模块

from app.utils.exceptions import (
    # 基类
    BaseAppException,
    # LLM 错误
    LLMException,
    LLMTimeoutError,
    LLMAuthError,
    LLMRateLimitError,
    LLMUnknownError,
    # 工具错误
    ToolException,
    ToolValidationError,
    ToolDataQueryError,
    ToolCalculationError,
    # 请求错误
    RequestException,
    MissingParameterError,
    InvalidParameterTypeError,
    ResourceNotFoundError,
    # 数据库错误
    DatabaseException,
    DatabaseConnectionError,
    DatabaseQueryError,
    # 会话错误
    SessionException,
    SessionNotFoundError,
    SessionExpiredError,
)

__all__ = [
    # 基类
    "BaseAppException",
    # LLM 错误
    "LLMException",
    "LLMTimeoutError",
    "LLMAuthError",
    "LLMRateLimitError",
    "LLMUnknownError",
    # 工具错误
    "ToolException",
    "ToolValidationError",
    "ToolDataQueryError",
    "ToolCalculationError",
    # 请求错误
    "RequestException",
    "MissingParameterError",
    "InvalidParameterTypeError",
    "ResourceNotFoundError",
    # 数据库错误
    "DatabaseException",
    "DatabaseConnectionError",
    "DatabaseQueryError",
    # 会话错误
    "SessionException",
    "SessionNotFoundError",
    "SessionExpiredError",
]
