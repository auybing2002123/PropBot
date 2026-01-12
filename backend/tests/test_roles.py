# 角色系统测试
# 验证角色定义和工具列表完整性

import pytest
from app.agent.roles import (
    Role,
    FINANCIAL_ADVISOR,
    POLICY_EXPERT,
    MARKET_ANALYST,
    PURCHASE_CONSULTANT,
    ALL_ROLES,
    ROLE_MAP,
    get_role,
    get_all_roles,
    get_role_by_name,
    get_specialist_roles
)
# 从 __init__.py 导入以触发工具注册
from app.agent.tools import (
    tool_registry,
    CalcLoanTool,
    CalcTaxTool,
    QueryMarketTool,
    SearchPolicyTool
)


class TestRoleDataStructure:
    """测试角色数据结构"""
    
    def test_role_is_dataclass(self):
        """验证 Role 是 dataclass"""
        assert hasattr(Role, "__dataclass_fields__")
    
    def test_role_has_required_fields(self):
        """验证 Role 包含所有必需字段"""
        required_fields = ["id", "name", "icon", "system_prompt", "tools", "trigger_keywords"]
        for field in required_fields:
            assert hasattr(FINANCIAL_ADVISOR, field), f"缺少字段: {field}"
    
    def test_financial_advisor_structure(self):
        """验证财务顾问角色结构"""
        role = FINANCIAL_ADVISOR
        assert role.id == "financial_advisor"
        assert role.name == "财务顾问"
        assert role.icon == "💰"
        assert isinstance(role.system_prompt, str)
        assert len(role.system_prompt) > 0
        assert isinstance(role.tools, list)
        assert len(role.tools) > 0
        assert isinstance(role.trigger_keywords, list)
        assert len(role.trigger_keywords) > 0


class TestFourRoles:
    """测试四个角色定义"""
    
    def test_all_roles_count(self):
        """验证角色总数为 4"""
        assert len(ALL_ROLES) == 4
    
    def test_financial_advisor_exists(self):
        """验证财务顾问角色存在"""
        role = get_role("financial_advisor")
        assert role is not None
        assert role.name == "财务顾问"
        assert "calc_loan" in role.tools
        assert "calc_tax" in role.tools
        assert "assess_pressure" in role.tools
    
    def test_policy_expert_exists(self):
        """验证政策专家角色存在"""
        role = get_role("policy_expert")
        assert role is not None
        assert role.name == "政策专家"
        assert "search_policy" in role.tools
        assert "search_faq" in role.tools
    
    def test_market_analyst_exists(self):
        """验证市场分析师角色存在"""
        role = get_role("market_analyst")
        assert role is not None
        assert role.name == "市场分析师"
        assert "query_market" in role.tools
        assert "query_price_trend" in role.tools
        assert "compare_districts" in role.tools
        assert "judge_timing" in role.tools
    
    def test_purchase_consultant_exists(self):
        """验证购房顾问角色存在"""
        role = get_role("purchase_consultant")
        assert role is not None
        assert role.name == "购房顾问"
        # 购房顾问应该有所有工具
        assert len(role.tools) >= 4


class TestRoleToolsIntegrity:
    """测试角色工具列表完整性（Property 9）"""
    
    def test_all_role_tools_registered(self):
        """
        验证所有角色的工具都已在 Tool_Registry 中注册
        Property 9: 角色工具列表完整性
        """
        for role in ALL_ROLES:
            assert len(role.tools) > 0, f"角色 {role.name} 的工具列表为空"
            
            for tool_name in role.tools:
                assert tool_registry.exists(tool_name), \
                    f"角色 {role.name} 的工具 {tool_name} 未在 Tool_Registry 中注册"
    
    def test_financial_advisor_tools_complete(self):
        """验证财务顾问工具完整"""
        role = FINANCIAL_ADVISOR
        expected_tools = ["calc_loan", "calc_tax", "calc_total_cost", "assess_pressure"]
        for tool in expected_tools:
            assert tool in role.tools, f"财务顾问缺少工具: {tool}"
    
    def test_policy_expert_tools_complete(self):
        """验证政策专家工具完整"""
        role = POLICY_EXPERT
        expected_tools = ["search_policy", "search_faq"]
        for tool in expected_tools:
            assert tool in role.tools, f"政策专家缺少工具: {tool}"
    
    def test_market_analyst_tools_complete(self):
        """验证市场分析师工具完整"""
        role = MARKET_ANALYST
        expected_tools = ["query_market", "query_price_trend", "compare_districts", "judge_timing"]
        for tool in expected_tools:
            assert tool in role.tools, f"市场分析师缺少工具: {tool}"


class TestRoleTriggerKeywords:
    """测试角色触发关键词"""
    
    def test_all_roles_have_keywords(self):
        """验证所有角色都有触发关键词"""
        for role in ALL_ROLES:
            assert len(role.trigger_keywords) > 0, f"角色 {role.name} 没有触发关键词"
    
    def test_financial_keywords(self):
        """验证财务顾问关键词包含财务相关词汇"""
        role = FINANCIAL_ADVISOR
        financial_keywords = ["贷款", "月供", "首付", "税费"]
        for kw in financial_keywords:
            assert kw in role.trigger_keywords, f"财务顾问缺少关键词: {kw}"
    
    def test_policy_keywords(self):
        """验证政策专家关键词包含政策相关词汇"""
        role = POLICY_EXPERT
        policy_keywords = ["政策", "限购", "公积金"]
        for kw in policy_keywords:
            assert kw in role.trigger_keywords, f"政策专家缺少关键词: {kw}"
    
    def test_market_keywords(self):
        """验证市场分析师关键词包含市场相关词汇"""
        role = MARKET_ANALYST
        market_keywords = ["市场", "房价", "走势"]
        for kw in market_keywords:
            assert kw in role.trigger_keywords, f"市场分析师缺少关键词: {kw}"


class TestRoleHelperFunctions:
    """测试角色辅助函数"""
    
    def test_get_role_valid(self):
        """测试获取有效角色"""
        role = get_role("financial_advisor")
        assert role is not None
        assert role.id == "financial_advisor"
    
    def test_get_role_invalid(self):
        """测试获取无效角色"""
        role = get_role("invalid_role")
        assert role is None
    
    def test_get_all_roles(self):
        """测试获取所有角色"""
        roles = get_all_roles()
        assert len(roles) == 4
        # 验证返回的是副本
        roles.append(None)
        assert len(get_all_roles()) == 4
    
    def test_get_role_by_name(self):
        """测试按名称获取角色"""
        role = get_role_by_name("财务顾问")
        assert role is not None
        assert role.id == "financial_advisor"
    
    def test_get_role_by_name_invalid(self):
        """测试按无效名称获取角色"""
        role = get_role_by_name("不存在的角色")
        assert role is None
    
    def test_get_specialist_roles(self):
        """测试获取专家角色（不含购房顾问）"""
        specialists = get_specialist_roles()
        assert len(specialists) == 3
        specialist_ids = [r.id for r in specialists]
        assert "purchase_consultant" not in specialist_ids
        assert "financial_advisor" in specialist_ids
        assert "policy_expert" in specialist_ids
        assert "market_analyst" in specialist_ids


class TestRoleMap:
    """测试角色映射表"""
    
    def test_role_map_complete(self):
        """验证角色映射表包含所有角色"""
        assert len(ROLE_MAP) == 4
        assert "financial_advisor" in ROLE_MAP
        assert "policy_expert" in ROLE_MAP
        assert "market_analyst" in ROLE_MAP
        assert "purchase_consultant" in ROLE_MAP
    
    def test_role_map_values(self):
        """验证角色映射表的值正确"""
        assert ROLE_MAP["financial_advisor"] == FINANCIAL_ADVISOR
        assert ROLE_MAP["policy_expert"] == POLICY_EXPERT
        assert ROLE_MAP["market_analyst"] == MARKET_ANALYST
        assert ROLE_MAP["purchase_consultant"] == PURCHASE_CONSULTANT
