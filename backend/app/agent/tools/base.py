# 工具基类和参数模型
# 定义所有 Agent 工具的基础结构

from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """工具参数定义"""
    name: str = Field(..., description="参数名称")
    type: str = Field(..., description="参数类型: string, number, integer, boolean")
    description: str = Field(..., description="参数描述")
    required: bool = Field(default=True, description="是否必需")
    enum: list[str] | None = Field(default=None, description="枚举值列表")

    def to_json_schema(self) -> dict:
        """转换为 JSON Schema 格式"""
        schema = {
            "type": self.type,
            "description": self.description
        }
        if self.enum:
            schema["enum"] = self.enum
        return schema


class BaseTool(ABC):
    """工具基类，所有工具必须继承此类"""
    
    name: str  # 工具名称
    description: str  # 工具描述
    parameters: list[ToolParameter]  # 参数列表
    
    def __init__(self):
        """初始化工具，子类可覆盖"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> dict:
        """
        执行工具
        
        Args:
            **kwargs: 工具参数
            
        Returns:
            执行结果字典
        """
        pass
    
    def validate_params(self, **kwargs) -> None:
        """
        验证输入参数
        
        Args:
            **kwargs: 待验证的参数
            
        Raises:
            ValueError: 参数验证失败时抛出
        """
        # 检查必需参数
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                raise ValueError(f"缺少必需参数: {param.name}")
            
            # 检查参数类型
            if param.name in kwargs:
                value = kwargs[param.name]
                if not self._check_type(value, param.type):
                    raise ValueError(
                        f"参数 {param.name} 类型错误: 期望 {param.type}, "
                        f"实际 {type(value).__name__}"
                    )
                
                # 检查枚举值
                if param.enum and value not in param.enum:
                    raise ValueError(
                        f"参数 {param.name} 值无效: {value}, "
                        f"允许值: {param.enum}"
                    )
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """检查值是否符合期望类型"""
        type_mapping = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool
        }
        expected = type_mapping.get(expected_type)
        if expected is None:
            return True  # 未知类型，跳过检查
        return isinstance(value, expected)
    
    def to_openai_schema(self) -> dict:
        """
        转换为 OpenAI 函数调用格式
        
        Returns:
            符合 OpenAI function calling 格式的字典
        """
        # 构建 parameters schema
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = param.to_json_schema()
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
