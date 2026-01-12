# 工具注册表
# 管理所有可用工具的注册和检索

from typing import Type
from app.agent.tools.base import BaseTool


class ToolRegistry:
    """工具注册表，单例模式"""
    
    _instance: "ToolRegistry | None" = None
    _tools: dict[str, BaseTool]
    
    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
        return cls._instance
    
    def register(self, tool: BaseTool) -> None:
        """
        注册工具
        
        Args:
            tool: 工具实例
        """
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> BaseTool | None:
        """
        按名称获取工具
        
        Args:
            name: 工具名称
            
        Returns:
            工具实例，不存在则返回 None
        """
        return self._tools.get(name)
    
    def get_all(self) -> list[BaseTool]:
        """
        获取所有已注册工具
        
        Returns:
            工具列表
        """
        return list(self._tools.values())
    
    def get_by_names(self, names: list[str]) -> list[BaseTool]:
        """
        按名称列表获取多个工具
        
        Args:
            names: 工具名称列表
            
        Returns:
            工具列表（跳过不存在的）
        """
        return [self._tools[name] for name in names if name in self._tools]
    
    def get_schemas(self, names: list[str] | None = None) -> list[dict]:
        """
        获取工具的 OpenAI schema 列表
        
        Args:
            names: 工具名称列表，None 表示所有工具
            
        Returns:
            OpenAI function schema 列表
        """
        if names is None:
            tools = self.get_all()
        else:
            tools = self.get_by_names(names)
        return [tool.to_openai_schema() for tool in tools]
    
    def exists(self, name: str) -> bool:
        """
        检查工具是否存在
        
        Args:
            name: 工具名称
            
        Returns:
            是否存在
        """
        return name in self._tools
    
    def clear(self) -> None:
        """清空所有注册的工具（主要用于测试）"""
        self._tools.clear()


# 全局注册表实例
tool_registry = ToolRegistry()


def register_tool(tool_class: Type[BaseTool]) -> Type[BaseTool]:
    """
    工具注册装饰器
    
    用法:
        @register_tool
        class MyTool(BaseTool):
            ...
    """
    tool_instance = tool_class()
    tool_registry.register(tool_instance)
    return tool_class
