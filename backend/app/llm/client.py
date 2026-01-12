"""
DeepSeek API 客户端
封装 DeepSeek API 调用，支持工具调用和流式输出
"""
import json
import httpx
from typing import Any, AsyncGenerator
from dataclasses import dataclass, field

from app.config.settings import get_settings


class LLMError(Exception):
    """LLM 调用异常基类"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class LLMTimeoutError(LLMError):
    """API 超时错误"""
    def __init__(self, message: str = "服务响应超时，请稍后重试"):
        super().__init__(code=1001, message=message)


class LLMAuthError(LLMError):
    """API 认证错误"""
    def __init__(self, message: str = "服务配置错误，请联系管理员"):
        super().__init__(code=1002, message=message)


class LLMRateLimitError(LLMError):
    """请求频率限制错误"""
    def __init__(self, message: str = "请求过于频繁，请稍后重试"):
        super().__init__(code=1003, message=message)


class LLMUnknownError(LLMError):
    """未知错误"""
    def __init__(self, message: str = "服务暂时不可用，请稍后重试"):
        super().__init__(code=1099, message=message)


@dataclass
class StreamChunk:
    """流式响应块"""
    content: str = ""  # 文本内容增量
    tool_calls: list[dict] | None = None  # 工具调用（完整或增量）
    finish_reason: str | None = None  # 结束原因


@dataclass
class StreamResult:
    """流式响应完整结果（用于工具调用场景）"""
    content: str = ""
    tool_calls: list[dict] = field(default_factory=list)
    finish_reason: str = ""


class DeepSeekClient:
    """
    DeepSeek API 客户端
    
    使用 httpx 异步调用 DeepSeek API，支持对话、工具调用和流式输出
    """
    
    def __init__(self):
        """初始化客户端，从配置读取 API 密钥和 base_url"""
        settings = get_settings()
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL.rstrip("/")
        self.timeout = 60.0  # 默认超时时间（秒）
    
    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        model: str = "deepseek-chat"
    ) -> dict[str, Any]:
        """
        调用 DeepSeek 对话接口（非流式）
        
        Args:
            messages: 对话消息列表，格式为 [{"role": "user", "content": "..."}]
            tools: 可用工具列表（OpenAI 函数调用格式）
            temperature: 温度参数，控制输出随机性，范围 0-2
            model: 模型名称，默认 deepseek-chat
            
        Returns:
            API 响应字典，包含 choices、usage 等字段
            
        Raises:
            LLMTimeoutError: API 调用超时
            LLMAuthError: API 密钥无效
            LLMRateLimitError: 请求频率超限
            LLMUnknownError: 其他未知错误
        """
        payload = self._build_payload(messages, tools, temperature, model, stream=False)
        headers = self._build_headers()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                self._check_response_status(response)
                return response.json()
                
            except httpx.TimeoutException:
                raise LLMTimeoutError()
            except httpx.ConnectError:
                raise LLMUnknownError("无法连接到 DeepSeek 服务，请检查网络")
            except LLMError:
                raise
            except Exception as e:
                raise LLMUnknownError(f"调用 DeepSeek API 时发生错误: {str(e)}")

    async def chat_stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        model: str = "deepseek-chat"
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        调用 DeepSeek 对话接口（流式）
        
        Args:
            messages: 对话消息列表
            tools: 可用工具列表
            temperature: 温度参数
            model: 模型名称
            
        Yields:
            StreamChunk: 流式响应块，包含内容增量或工具调用
        """
        payload = self._build_payload(messages, tools, temperature, model, stream=True)
        headers = self._build_headers()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                ) as response:
                    # 检查状态码
                    if response.status_code == 401:
                        raise LLMAuthError()
                    elif response.status_code == 429:
                        raise LLMRateLimitError()
                    elif response.status_code >= 500:
                        raise LLMUnknownError("DeepSeek 服务暂时不可用")
                    elif response.status_code != 200:
                        raise LLMUnknownError(f"API 调用失败: HTTP {response.status_code}")
                    
                    # 流式读取 SSE 数据
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        
                        data_str = line[6:]  # 去掉 "data: " 前缀
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            chunk = self._parse_stream_chunk(data)
                            if chunk:
                                yield chunk
                        except json.JSONDecodeError:
                            continue
                            
            except httpx.TimeoutException:
                raise LLMTimeoutError()
            except httpx.ConnectError:
                raise LLMUnknownError("无法连接到 DeepSeek 服务，请检查网络")
            except LLMError:
                raise
            except Exception as e:
                raise LLMUnknownError(f"流式调用 DeepSeek API 时发生错误: {str(e)}")

    async def chat_stream_complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        model: str = "deepseek-chat"
    ) -> tuple[AsyncGenerator[str, None], "StreamResultCollector"]:
        """
        流式调用并收集完整结果（用于需要工具调用的场景）
        
        Returns:
            (内容生成器, 结果收集器)
            - 内容生成器：yield 文本增量
            - 结果收集器：调用 get_result() 获取完整结果（包括工具调用）
        """
        collector = StreamResultCollector()
        
        async def content_generator() -> AsyncGenerator[str, None]:
            async for chunk in self.chat_stream(messages, tools, temperature, model):
                collector.add_chunk(chunk)
                if chunk.content:
                    yield chunk.content
        
        return content_generator(), collector

    def _build_payload(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
        temperature: float,
        model: str,
        stream: bool
    ) -> dict[str, Any]:
        """构建请求体"""
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        return payload
    
    def _build_headers(self) -> dict[str, str]:
        """构建请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def _check_response_status(self, response: httpx.Response) -> None:
        """检查响应状态码"""
        if response.status_code == 401:
            raise LLMAuthError()
        elif response.status_code == 429:
            raise LLMRateLimitError()
        elif response.status_code >= 500:
            raise LLMUnknownError("DeepSeek 服务暂时不可用，请稍后重试")
        elif response.status_code != 200:
            try:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "未知错误")
            except Exception:
                error_msg = f"HTTP {response.status_code}"
            raise LLMUnknownError(f"API 调用失败: {error_msg}")
    
    def _parse_stream_chunk(self, data: dict) -> StreamChunk | None:
        """解析流式响应块"""
        choices = data.get("choices", [])
        if not choices:
            return None
        
        choice = choices[0]
        delta = choice.get("delta", {})
        finish_reason = choice.get("finish_reason")
        
        content = delta.get("content", "")
        tool_calls = delta.get("tool_calls")
        
        if content or tool_calls or finish_reason:
            return StreamChunk(
                content=content or "",
                tool_calls=tool_calls,
                finish_reason=finish_reason
            )
        return None


class StreamResultCollector:
    """流式结果收集器，用于收集完整的工具调用"""
    
    def __init__(self):
        self.content = ""
        self.tool_calls: dict[int, dict] = {}  # index -> tool_call
        self.finish_reason = ""
    
    def add_chunk(self, chunk: StreamChunk) -> None:
        """添加流式块"""
        if chunk.content:
            self.content += chunk.content
        
        if chunk.tool_calls:
            for tc in chunk.tool_calls:
                index = tc.get("index", 0)
                if index not in self.tool_calls:
                    # 新的工具调用
                    self.tool_calls[index] = {
                        "id": tc.get("id", ""),
                        "type": tc.get("type", "function"),
                        "function": {
                            "name": tc.get("function", {}).get("name", ""),
                            "arguments": tc.get("function", {}).get("arguments", "")
                        }
                    }
                else:
                    # 增量更新（主要是 arguments）
                    if "function" in tc and "arguments" in tc["function"]:
                        self.tool_calls[index]["function"]["arguments"] += tc["function"]["arguments"]
        
        if chunk.finish_reason:
            self.finish_reason = chunk.finish_reason
    
    def get_result(self) -> StreamResult:
        """获取完整结果"""
        return StreamResult(
            content=self.content,
            tool_calls=list(self.tool_calls.values()),
            finish_reason=self.finish_reason
        )
