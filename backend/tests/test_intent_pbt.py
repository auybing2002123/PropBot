# 意图识别属性测试
# Property 10: 意图识别关键词匹配
# 验证: 需求 7.1, 7.2, 7.3

import pytest
from hypothesis import given, strategies as st, settings, assume

from app.agent.intent import IntentRecognizer
from app.agent.roles import (
    Role,
    ALL_ROLES,
    FINANCIAL_ADVISOR,
    POLICY_EXPERT,
    MARKET_ANALYST,
    PURCHASE_CONSULTANT,
    get_specialist_roles
)


# ============================================================
# 测试数据生成策略
# ============================================================

# 生成专家角色（不包括购房顾问）
specialist_role_strategy = st.sampled_from(get_specialist_roles())

# 生成所有角色
all_role_strategy = st.sampled_from(ALL_ROLES)

# 生成随机前缀文本（不包含任何关键词）
random_prefix_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
    min_size=0,
    max_size=20
).filter(lambda s: not any(
    kw in s.lower() for role in ALL_ROLES for kw in role.trigger_keywords
))

# 生成随机后缀文本（不包含任何关键词）
random_suffix_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
    min_size=0,
    max_size=20
).filter(lambda s: not any(
    kw in s.lower() for role in ALL_ROLES for kw in role.trigger_keywords
))


# ============================================================
# Property 10: 意图识别关键词匹配
# 对于任意包含角色触发关键词的用户输入，Intent_Recognizer 应返回包含该角色的列表
# 验证: 需求 7.1, 7.2, 7.3
# ============================================================

class TestIntentKeywordMatchingPBT:
    """Property 10: 意图识别关键词匹配 - 属性测试"""
    
    def setup_method(self):
        """每个测试方法前创建新的识别器实例"""
        self.recognizer = IntentRecognizer()
    
    @given(role=specialist_role_strategy)
    @settings(max_examples=100, deadline=None)
    def test_keyword_triggers_role_match(self, role: Role):
        """
        **Feature: agent-core, Property 10: 意图识别关键词匹配**
        **Validates: Requirements 7.1, 7.2, 7.3**
        
        对于任意专家角色的任意触发关键词，包含该关键词的输入应匹配到该角色
        """
        # 确保角色有触发关键词
        assume(len(role.trigger_keywords) > 0)
        
        # 对每个关键词进行测试
        for keyword in role.trigger_keywords:
            user_input = f"请问{keyword}相关的问题"
            matched_roles = self.recognizer.match_keywords(user_input)
            
            assert role in matched_roles, \
                f"输入包含关键词 '{keyword}' 应匹配到角色 '{role.name}'，但实际匹配到: {[r.name for r in matched_roles]}"
    
    @given(
        role=specialist_role_strategy,
        keyword_index=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=100, deadline=None)
    def test_random_keyword_from_role_triggers_match(self, role: Role, keyword_index: int):
        """
        **Feature: agent-core, Property 10: 意图识别关键词匹配**
        **Validates: Requirements 7.1, 7.2, 7.3**
        
        对于任意专家角色，随机选择一个触发关键词，包含该关键词的输入应匹配到该角色
        """
        assume(len(role.trigger_keywords) > 0)
        
        # 随机选择一个关键词
        keyword = role.trigger_keywords[keyword_index % len(role.trigger_keywords)]
        user_input = f"我想了解{keyword}"
        
        matched_roles = self.recognizer.match_keywords(user_input)
        
        assert role in matched_roles, \
            f"输入 '{user_input}' 应匹配到角色 '{role.name}'"
    
    @given(role=specialist_role_strategy)
    @settings(max_examples=100, deadline=None)
    def test_keyword_at_different_positions(self, role: Role):
        """
        **Feature: agent-core, Property 10: 意图识别关键词匹配**
        **Validates: Requirements 7.1, 7.2, 7.3**
        
        对于任意专家角色的关键词，无论关键词在输入中的位置如何，都应匹配到该角色
        """
        assume(len(role.trigger_keywords) > 0)
        keyword = role.trigger_keywords[0]
        
        # 关键词在开头
        input_start = f"{keyword}是什么意思"
        assert role in self.recognizer.match_keywords(input_start), \
            f"关键词在开头时应匹配: '{input_start}'"
        
        # 关键词在中间
        input_middle = f"请问{keyword}怎么办"
        assert role in self.recognizer.match_keywords(input_middle), \
            f"关键词在中间时应匹配: '{input_middle}'"
        
        # 关键词在结尾
        input_end = f"我想了解{keyword}"
        assert role in self.recognizer.match_keywords(input_end), \
            f"关键词在结尾时应匹配: '{input_end}'"
    
    @given(role=all_role_strategy)
    @settings(max_examples=100, deadline=None)
    def test_role_has_trigger_keywords(self, role: Role):
        """
        **Feature: agent-core, Property 10: 意图识别关键词匹配**
        **Validates: Requirements 7.1, 7.2, 7.3**
        
        对于任意角色，trigger_keywords 列表应非空
        """
        assert isinstance(role.trigger_keywords, list), \
            f"角色 {role.name} 的 trigger_keywords 应为列表"
        assert len(role.trigger_keywords) > 0, \
            f"角色 {role.name} 的 trigger_keywords 不应为空"
    
    @given(role=all_role_strategy)
    @settings(max_examples=100, deadline=None)
    def test_trigger_keywords_are_strings(self, role: Role):
        """
        **Feature: agent-core, Property 10: 意图识别关键词匹配**
        **Validates: Requirements 7.1, 7.2, 7.3**
        
        对于任意角色，所有触发关键词应为非空字符串
        """
        for keyword in role.trigger_keywords:
            assert isinstance(keyword, str), \
                f"角色 {role.name} 的关键词应为字符串，但得到 {type(keyword)}"
            assert len(keyword.strip()) > 0, \
                f"角色 {role.name} 的关键词不应为空字符串"


class TestFinancialAdvisorKeywordsPBT:
    """
    需求 7.1: 当用户输入包含财务关键词时，应返回 Financial_Advisor 角色
    """
    
    def setup_method(self):
        self.recognizer = IntentRecognizer()
    
    @given(keyword_index=st.integers(min_value=0, max_value=100))
    @settings(max_examples=100, deadline=None)
    def test_financial_keyword_matches_financial_advisor(self, keyword_index: int):
        """
        **Feature: agent-core, Property 10: 意图识别关键词匹配**
        **Validates: Requirements 7.1**
        
        对于任意财务顾问的触发关键词，包含该关键词的输入应匹配到财务顾问
        """
        keywords = FINANCIAL_ADVISOR.trigger_keywords
        keyword = keywords[keyword_index % len(keywords)]
        
        user_input = f"请帮我查询{keyword}的信息"
        matched_roles = self.recognizer.match_keywords(user_input)
        
        assert FINANCIAL_ADVISOR in matched_roles, \
            f"输入包含财务关键词 '{keyword}' 应匹配到财务顾问"


class TestPolicyExpertKeywordsPBT:
    """
    需求 7.2: 当用户输入包含政策关键词时，应返回 Policy_Expert 角色
    """
    
    def setup_method(self):
        self.recognizer = IntentRecognizer()
    
    @given(keyword_index=st.integers(min_value=0, max_value=100))
    @settings(max_examples=100, deadline=None)
    def test_policy_keyword_matches_policy_expert(self, keyword_index: int):
        """
        **Feature: agent-core, Property 10: 意图识别关键词匹配**
        **Validates: Requirements 7.2**
        
        对于任意政策专家的触发关键词，包含该关键词的输入应匹配到政策专家
        """
        keywords = POLICY_EXPERT.trigger_keywords
        keyword = keywords[keyword_index % len(keywords)]
        
        user_input = f"我想了解{keyword}的情况"
        matched_roles = self.recognizer.match_keywords(user_input)
        
        assert POLICY_EXPERT in matched_roles, \
            f"输入包含政策关键词 '{keyword}' 应匹配到政策专家"


class TestMarketAnalystKeywordsPBT:
    """
    需求 7.3: 当用户输入包含市场关键词时，应返回 Market_Analyst 角色
    """
    
    def setup_method(self):
        self.recognizer = IntentRecognizer()
    
    @given(keyword_index=st.integers(min_value=0, max_value=100))
    @settings(max_examples=100, deadline=None)
    def test_market_keyword_matches_market_analyst(self, keyword_index: int):
        """
        **Feature: agent-core, Property 10: 意图识别关键词匹配**
        **Validates: Requirements 7.3**
        
        对于任意市场分析师的触发关键词，包含该关键词的输入应匹配到市场分析师
        """
        keywords = MARKET_ANALYST.trigger_keywords
        keyword = keywords[keyword_index % len(keywords)]
        
        user_input = f"请分析{keyword}的数据"
        matched_roles = self.recognizer.match_keywords(user_input)
        
        assert MARKET_ANALYST in matched_roles, \
            f"输入包含市场关键词 '{keyword}' 应匹配到市场分析师"


class TestMultipleRoleMatchingPBT:
    """
    测试多角色匹配场景
    """
    
    def setup_method(self):
        self.recognizer = IntentRecognizer()
    
    @given(
        role1=specialist_role_strategy,
        role2=specialist_role_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_multiple_keywords_match_multiple_roles(self, role1: Role, role2: Role):
        """
        **Feature: agent-core, Property 10: 意图识别关键词匹配**
        **Validates: Requirements 7.1, 7.2, 7.3**
        
        对于包含多个角色关键词的输入，应匹配到所有相关角色
        """
        assume(len(role1.trigger_keywords) > 0)
        assume(len(role2.trigger_keywords) > 0)
        
        keyword1 = role1.trigger_keywords[0]
        keyword2 = role2.trigger_keywords[0]
        
        user_input = f"请问{keyword1}和{keyword2}的关系"
        matched_roles = self.recognizer.match_keywords(user_input)
        
        assert role1 in matched_roles, \
            f"输入包含关键词 '{keyword1}' 应匹配到角色 '{role1.name}'"
        assert role2 in matched_roles, \
            f"输入包含关键词 '{keyword2}' 应匹配到角色 '{role2.name}'"
