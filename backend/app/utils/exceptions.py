"""
统一异常处理模块
定义业务异常类，用于规范化错误处理
"""
from typing import Any


class BaseAppException(Exception):
    """
    应用基础异常类
    所有业务异常都应继承此类
    """
    code: int = 1099
    message: str = "服务暂时不可用，请稍后重试"
    http_status: int = 500
    
    def __init__(
        self,
        message: str | None = None,
        code: int | None = None,
        data: Any = None
    ):
        self.message = message or self.__class__.message
        self.code = code or self.__class__.code
        self.data = data
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """转换为响应字典格式"""
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }


# ==================== LLM API 错误 (1xxx) ====================

class LLMException(BaseAppException):
    """LLM 相关异常基类"""
    http_status: int = 503


class LLMTimeoutError(LLMException):
    """API 超时"""
    code: int = 1001
    message: str = "服务响应超时，请稍后重试"


class LLMAuthError(LLMException):
    """API 密钥无效"""
    code: int = 1002
    message: str = "服务配置错误，请联系管理员"
    http_status: int = 500


class LLMRateLimitError(LLMException):
    """请求频率限制"""
    code: int = 1003
    message: str = "请求过于频繁，请稍后重试"
    http_status: int = 429


class LLMUnknownError(LLMException):
    """未知 LLM 错误"""
    code: int = 1099
    message: str = "服务暂时不可用，请稍后重试"


# ==================== 工具执行错误 (2xxx) ====================

class ToolException(BaseAppException):
    """工具执行异常基类"""
    http_status: int = 400


class ToolValidationError(ToolException):
    """参数验证失败"""
    code: int = 2001
    message: str = "输入参数有误"
    
    def __init__(self, field_name: str | None = None, detail: str | None = None):
        if field_name:
            message = f"输入参数有误：{field_name}"
            if detail:
                message = f"{message} - {detail}"
        else:
            message = detail or self.__class__.message
        super().__init__(message=message)


class ToolDataQueryError(ToolException):
    """数据查询失败"""
    code: int = 2002
    message: str = "数据查询失败，请稍后重试"
    http_status: int = 503


class ToolCalculationError(ToolException):
    """计算错误"""
    code: int = 2003
    message: str = "计算过程出错，请检查输入"


# ==================== 通用错误 (3xxx) ====================

class RequestException(BaseAppException):
    """请求相关异常基类"""
    http_status: int = 400


class MissingParameterError(RequestException):
    """请求参数缺失"""
    code: int = 3001
    message: str = "缺少必需参数"
    
    def __init__(self, field_name: str | None = None):
        if field_name:
            message = f"缺少必需参数：{field_name}"
        else:
            message = self.__class__.message
        super().__init__(message=message)


class InvalidParameterTypeError(RequestException):
    """请求参数类型错误"""
    code: int = 3002
    message: str = "参数类型错误"
    
    def __init__(self, field_name: str | None = None, expected_type: str | None = None):
        if field_name:
            message = f"参数类型错误：{field_name}"
            if expected_type:
                message = f"{message}，应为 {expected_type}"
        else:
            message = self.__class__.message
        super().__init__(message=message)


class ResourceNotFoundError(RequestException):
    """资源不存在"""
    code: int = 3003
    message: str = "请求的资源不存在"
    http_status: int = 404


# ==================== 数据库错误 (4xxx) ====================

class DatabaseException(BaseAppException):
    """数据库异常基类"""
    http_status: int = 503


class DatabaseConnectionError(DatabaseException):
    """数据库连接失败"""
    code: int = 4001
    message: str = "数据库连接失败，请稍后重试"


class DatabaseQueryError(DatabaseException):
    """数据库查询失败"""
    code: int = 4002
    message: str = "数据查询失败，请稍后重试"


# ==================== 会话错误 (5xxx) ====================

class SessionException(BaseAppException):
    """会话相关异常基类"""
    http_status: int = 400


class SessionNotFoundError(SessionException):
    """会话不存在"""
    code: int = 5001
    message: str = "会话不存在或已过期"


class SessionExpiredError(SessionException):
    """会话已过期"""
    code: int = 5002
    message: str = "会话已过期，请重新开始对话"
