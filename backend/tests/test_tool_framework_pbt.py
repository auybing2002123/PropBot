# 工具框架属性测试
# Property 1: 工具 Schema 转换一致性
# Property 2: 工具注册和检索一致性
# 验证: 需求 2.3, 2.4

import pytest
from hypothesis import given, strategies as st, settings

from app.agent.tools.base import BaseTool, ToolParameter
from app.agent.tools.registry import ToolRegistry


# ============================================================
# 测试数据生成策略
# ============================================================

# 有效的参数类型
VALID_PARAM_TYPES = ["string", "number", "integer", "boolean"]

# 生成有效的工具名称（非空字符串，只包含字母数字和下划线）
tool_name_strategy = st.from_regex(r"[a-z][a-z0-9_]{0,29}", fullmatch=True)

# 生成有效的参数名称
param_name_strategy = st.from_regex(r"[a-z][a-z0-9_]{0,19}", fullmatch=True)

# 生成有效的描述（非空字符串）
description_strategy = st.text(min_size=1, max_size=100).filter(lambda x: x.strip())

# 生成有效的参数类型
param_type_strategy = st.sampled_from(VALID_PARAM_TYPES)

# 生成可选的枚举值列表
enum_strategy = st.one_of(
    st.none(),
    st.lists(st.text(min_size=1, max_size=20).filter(lambda x: x.strip()), min_size=1, max_size=5)
)


@st.composite
def tool_parameter_strategy(draw):
    """生成有效的 ToolParameter"""
    return ToolParameter(
        name=draw(param_name_strategy),
        type=draw(param_type_strategy),
        description=draw(description_strategy),
        required=draw(st.booleans()),
        enum=draw(enum_strategy) if draw(st.booleans()) else None
    )


@st.composite
def tool_parameters_list_strategy(draw):
    """生成有效的参数列表（确保名称唯一）"""
    params = draw(st.lists(tool_parameter_strategy(), min_size=0, max_size=5))
    # 确保参数名称唯一
    seen_names = set()
    unique_params = []
    for param in params:
        if param.name not in seen_names:
            seen_names.add(param.name)
            unique_params.append(param)
    return unique_params


# ============================================================
# 动态创建测试工具类
# ============================================================

def create_test_tool(name: str, description: str, parameters: list[ToolParameter]):
    """动态创建测试用的工具类"""
    
    class TestTool(BaseTool):
        async def execute(self, **kwargs):
            return {"status": "ok"}
    
    TestTool.name = name
    TestTool.description = description
    TestTool.parameters = parameters
    
    return TestTool()


# ============================================================
# Property 1: 工具 Schema 转换一致性
# 对于任意工具定义，to_openai_schema() 应返回符合 OpenAI 函数调用格式的字典
# 验证: 需求 2.3
# ============================================================

class TestToolSchemaConversion:
    """Property 1: 工具 Schema 转换一致性"""
    
    @given(
        name=tool_name_strategy,
        description=description_strategy,
        parameters=tool_parameters_list_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_schema_has_required_fields(self, name: str, description: str, parameters: list[ToolParameter]):
        """
        **Feature: agent-core, Property 1: 工具 Schema 转换一致性**
        **Validates: Requirements 2.3**
        
        对于任意工具定义，to_openai_schema() 应返回包含以下字段的字典：
        - type: "function"
        - function.name: 工具名称
        - function.description: 工具描述
        - function.parameters: 参数 schema
        """
        # 创建测试工具
        tool = create_test_tool(name, description, parameters)
        
        # 转换为 OpenAI schema
        schema = tool.to_openai_schema()
        
        # 验证顶层结构
        assert isinstance(schema, dict), "Schema 应该是字典"
        assert "type" in schema, "Schema 应包含 type 字段"
        assert schema["type"] == "function", "type 应为 'function'"
        assert "function" in schema, "Schema 应包含 function 字段"
        
        # 验证 function 结构
        func = schema["function"]
        assert isinstance(func, dict), "function 应该是字典"
        assert "name" in func, "function 应包含 name 字段"
        assert "description" in func, "function 应包含 description 字段"
        assert "parameters" in func, "function 应包含 parameters 字段"
        
        # 验证字段值
        assert func["name"] == name, "name 应与工具名称一致"
        assert func["description"] == description, "description 应与工具描述一致"
        
        # 验证 parameters 结构
        params = func["parameters"]
        assert isinstance(params, dict), "parameters 应该是字典"
        assert params.get("type") == "object", "parameters.type 应为 'object'"
        assert "properties" in params, "parameters 应包含 properties"
        assert "required" in params, "parameters 应包含 required"
    
    @given(
        name=tool_name_strategy,
        description=description_strategy,
        parameters=tool_parameters_list_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_schema_parameters_match(self, name: str, description: str, parameters: list[ToolParameter]):
        """
        **Feature: agent-core, Property 1: 工具 Schema 转换一致性**
        **Validates: Requirements 2.3**
        
        对于任意工具参数，转换后的 schema 应正确反映参数定义
        """
        tool = create_test_tool(name, description, parameters)
        schema = tool.to_openai_schema()
        
        props = schema["function"]["parameters"]["properties"]
        required = schema["function"]["parameters"]["required"]
        
        # 验证参数数量
        assert len(props) == len(parameters), "properties 数量应与参数数量一致"
        
        # 验证每个参数
        for param in parameters:
            assert param.name in props, f"参数 {param.name} 应在 properties 中"
            prop = props[param.name]
            
            # 验证类型
            assert prop["type"] == param.type, f"参数 {param.name} 类型应一致"
            
            # 验证描述
            assert prop["description"] == param.description, f"参数 {param.name} 描述应一致"
            
            # 验证枚举值
            if param.enum:
                assert "enum" in prop, f"参数 {param.name} 应包含 enum"
                assert prop["enum"] == param.enum, f"参数 {param.name} enum 值应一致"
            
            # 验证必需参数
            if param.required:
                assert param.name in required, f"必需参数 {param.name} 应在 required 列表中"
            else:
                assert param.name not in required, f"可选参数 {param.name} 不应在 required 列表中"


# ============================================================
# Property 2: 工具注册和检索一致性
# 对于任意工具，注册后通过相同名称检索应返回相同的工具实例
# 验证: 需求 2.4
# ============================================================

class TestToolRegistryConsistency:
    """Property 2: 工具注册和检索一致性"""
    
    @pytest.fixture(autouse=True)
    def setup_registry(self):
        """每个测试前创建新的注册表"""
        # 创建独立的注册表实例用于测试
        self.registry = ToolRegistry.__new__(ToolRegistry)
        self.registry._tools = {}
        yield
        # 清理
        self.registry._tools.clear()
    
    @given(
        name=tool_name_strategy,
        description=description_strategy,
        parameters=tool_parameters_list_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_register_then_get_returns_same_instance(
        self, name: str, description: str, parameters: list[ToolParameter]
    ):
        """
        **Feature: agent-core, Property 2: 工具注册和检索一致性**
        **Validates: Requirements 2.4**
        
        对于任意工具，注册到 Tool_Registry 后，通过相同名称检索应返回相同的工具实例
        """
        # 清空注册表确保测试隔离
        self.registry._tools.clear()
        
        # 创建工具
        tool = create_test_tool(name, description, parameters)
        
        # 注册工具
        self.registry.register(tool)
        
        # 检索工具
        retrieved = self.registry.get(name)
        
        # 验证返回相同实例
        assert retrieved is tool, "检索到的工具应与注册的工具是同一实例"
    
    @given(
        tools_data=st.lists(
            st.tuples(tool_name_strategy, description_strategy, tool_parameters_list_strategy()),
            min_size=1,
            max_size=10,
            unique_by=lambda x: x[0]  # 确保名称唯一
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_multiple_tools_register_and_retrieve(self, tools_data):
        """
        **Feature: agent-core, Property 2: 工具注册和检索一致性**
        **Validates: Requirements 2.4**
        
        对于任意多个工具，注册后都能通过名称正确检索
        """
        # 清空注册表确保测试隔离
        self.registry._tools.clear()
        
        tools = []
        
        # 注册所有工具
        for name, description, parameters in tools_data:
            tool = create_test_tool(name, description, parameters)
            self.registry.register(tool)
            tools.append((name, tool))
        
        # 验证所有工具都能正确检索
        for name, original_tool in tools:
            retrieved = self.registry.get(name)
            assert retrieved is original_tool, f"工具 {name} 检索结果应与注册实例一致"
    
    @given(name=tool_name_strategy)
    @settings(max_examples=100, deadline=None)
    def test_get_nonexistent_returns_none(self, name: str):
        """
        **Feature: agent-core, Property 2: 工具注册和检索一致性**
        **Validates: Requirements 2.4**
        
        对于未注册的工具名称，get 应返回 None
        """
        # 确保注册表为空
        self.registry._tools.clear()
        
        # 检索不存在的工具
        result = self.registry.get(name)
        
        assert result is None, "未注册的工具应返回 None"
    
    @given(
        name=tool_name_strategy,
        description=description_strategy,
        parameters=tool_parameters_list_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_exists_after_register(self, name: str, description: str, parameters: list[ToolParameter]):
        """
        **Feature: agent-core, Property 2: 工具注册和检索一致性**
        **Validates: Requirements 2.4**
        
        对于任意工具，注册后 exists() 应返回 True
        """
        # 清空注册表确保测试隔离
        self.registry._tools.clear()
        
        tool = create_test_tool(name, description, parameters)
        
        # 注册前不存在
        assert not self.registry.exists(name), "注册前工具不应存在"
        
        # 注册工具
        self.registry.register(tool)
        
        # 注册后存在
        assert self.registry.exists(name), "注册后工具应存在"
