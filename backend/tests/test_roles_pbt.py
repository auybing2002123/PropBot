# 角色系统属性测试
# Property 9: 角色工具列表完整性
# 验证: 需求 6.5

import pytest
from hypothesis import given, strategies as st, settings

from app.agent.roles import (
    Role,
    ALL_ROLES,
    get_role,
    get_all_roles,
    FINANCIAL_ADVISOR,
    POLICY_EXPERT,
    MARKET_ANALYST,
    PURCHASE_CONSULTANT
)
# 从 __init__.py 导入以触发工具注册
from app.agent.tools import (
    tool_registry,
    CalcLoanTool,
    CalcTaxTool,
    QueryMarketTool,
    SearchPolicyTool
)


# ============================================================
# 测试数据生成策略
# ============================================================

# 生成有效的角色 ID（从已定义的角色中选择）
role_id_strategy = st.sampled_from([role.id for role in ALL_ROLES])

# 生成角色对象（从已定义的角色中选择）
role_strategy = st.sampled_from(ALL_ROLES)


# ============================================================
# Property 9: 角色工具列表完整性
# 对于任意已定义角色，加载后的 tools 列表应非空且所有工具名称都在 Tool_Registry 中注册
# 验证: 需求 6.5
# ============================================================

class TestRoleToolsIntegrityPBT:
    """Property 9: 角色工具列表完整性 - 属性测试"""
    
    @given(role=role_strategy)
    @settings(max_examples=100, deadline=None)
    def test_role_tools_list_non_empty(self, role: Role):
        """
        **Feature: agent-core, Property 9: 角色工具列表完整性**
        **Validates: Requirements 6.5**
        
        对于任意已定义角色，tools 列表应非空
        """
        assert isinstance(role.tools, list), f"角色 {role.name} 的 tools 应为列表"
        assert len(role.tools) > 0, f"角色 {role.name} 的 tools 列表不应为空"
    
    @given(role=role_strategy)
    @settings(max_examples=100, deadline=None)
    def test_role_tools_all_registered(self, role: Role):
        """
        **Feature: agent-core, Property 9: 角色工具列表完整性**
        **Validates: Requirements 6.5**
        
        对于任意已定义角色，所有工具名称都应在 Tool_Registry 中注册
        """
        for tool_name in role.tools:
            assert tool_registry.exists(tool_name), \
                f"角色 {role.name} 的工具 '{tool_name}' 未在 Tool_Registry 中注册"
    
    @given(role=role_strategy)
    @settings(max_examples=100, deadline=None)
    def test_role_tools_retrievable(self, role: Role):
        """
        **Feature: agent-core, Property 9: 角色工具列表完整性**
        **Validates: Requirements 6.5**
        
        对于任意已定义角色，所有工具都应能从 Tool_Registry 中检索到
        """
        for tool_name in role.tools:
            tool = tool_registry.get(tool_name)
            assert tool is not None, \
                f"角色 {role.name} 的工具 '{tool_name}' 无法从 Tool_Registry 检索"
            assert tool.name == tool_name, \
                f"检索到的工具名称 '{tool.name}' 与请求的名称 '{tool_name}' 不一致"
    
    @given(role_id=role_id_strategy)
    @settings(max_examples=100, deadline=None)
    def test_role_by_id_tools_integrity(self, role_id: str):
        """
        **Feature: agent-core, Property 9: 角色工具列表完整性**
        **Validates: Requirements 6.5**
        
        对于任意角色 ID，通过 get_role 获取的角色应满足工具完整性
        """
        role = get_role(role_id)
        assert role is not None, f"角色 ID '{role_id}' 应存在"
        
        # 验证工具列表非空
        assert len(role.tools) > 0, f"角色 {role.name} 的 tools 列表不应为空"
        
        # 验证所有工具已注册
        for tool_name in role.tools:
            assert tool_registry.exists(tool_name), \
                f"角色 {role.name} 的工具 '{tool_name}' 未在 Tool_Registry 中注册"
    
    @given(role=role_strategy)
    @settings(max_examples=100, deadline=None)
    def test_role_tools_can_generate_schema(self, role: Role):
        """
        **Feature: agent-core, Property 9: 角色工具列表完整性**
        **Validates: Requirements 6.5**
        
        对于任意已定义角色，所有工具都应能生成有效的 OpenAI schema
        """
        schemas = tool_registry.get_schemas(role.tools)
        
        # 验证 schema 数量与工具数量一致
        assert len(schemas) == len(role.tools), \
            f"角色 {role.name} 的 schema 数量应与工具数量一致"
        
        # 验证每个 schema 结构正确
        for schema in schemas:
            assert isinstance(schema, dict), "Schema 应为字典"
            assert "type" in schema, "Schema 应包含 type 字段"
            assert schema["type"] == "function", "Schema type 应为 'function'"
            assert "function" in schema, "Schema 应包含 function 字段"
            assert "name" in schema["function"], "Schema function 应包含 name"

