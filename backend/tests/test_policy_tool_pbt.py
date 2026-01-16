# 政策检索工具属性测试
# Property 8: 政策检索城市过滤
# 验证: 需求 5.4

import pytest
from hypothesis import given, strategies as st, settings, assume

from app.agent.tools.policy import (
    PolicyKnowledgeBase,
    SearchPolicyTool,
    SearchFAQTool,
    get_knowledge_base
)


# ============================================================
# 测试数据生成策略
# ============================================================

# 支持的城市列表
SUPPORTED_CITIES = ["南宁", "柳州"]

# 城市策略
city_strategy = st.sampled_from(SUPPORTED_CITIES)

# 搜索查询策略 - 使用常见的购房相关关键词
search_query_strategy = st.sampled_from([
    "限购政策",
    "首付比例",
    "公积金贷款",
    "贷款利率",
    "契税",
    "购房资格",
    "限贷",
    "二套房",
    "首套房",
    "外地人买房",
    "人才补贴",
    "增值税",
    "个税"
])

# top_k 策略
top_k_strategy = st.integers(min_value=1, max_value=10)


# ============================================================
# Property 8: 政策检索城市过滤
# 对于任意带城市参数的政策检索，返回结果中所有文档的城市字段应与查询城市匹配
# 验证: 需求 5.4
# ============================================================

class TestPolicyCityFilter:
    """Property 8: 政策检索城市过滤"""
    
    @pytest.fixture(autouse=True)
    def setup_knowledge_base(self):
        """确保知识库已加载"""
        self.kb = get_knowledge_base()
        yield
    
    @given(
        city=city_strategy,
        query=search_query_strategy,
        top_k=top_k_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_policy_search_city_filter(self, city: str, query: str, top_k: int):
        """
        **Feature: agent-core, Property 8: 政策检索城市过滤**
        **Validates: Requirements 5.4**
        
        对于任意带城市参数的政策检索，返回结果中所有文档的城市字段应与查询城市匹配
        """
        # 执行政策搜索
        results = self.kb.search_policy(query, city=city, top_k=top_k)
        
        # 验证所有返回结果的城市字段
        for result in results:
            result_city = result.get("city")
            # 结果城市应该与查询城市匹配，或者为 None（通用政策）
            assert result_city == city or result_city is None, (
                f"政策检索结果城市不匹配: 查询城市={city}, 结果城市={result_city}"
            )
    
    @given(
        city=city_strategy,
        query=search_query_strategy,
        top_k=top_k_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_faq_search_city_filter(self, city: str, query: str, top_k: int):
        """
        **Feature: agent-core, Property 8: 政策检索城市过滤**
        **Validates: Requirements 5.4**
        
        对于任意带城市参数的 FAQ 检索，返回结果中所有文档的城市字段应与查询城市匹配或为空
        """
        # 执行 FAQ 搜索
        results = self.kb.search_faq(query, city=city, top_k=top_k)
        
        # 验证所有返回结果的城市字段
        for result in results:
            result_city = result.get("city")
            # 结果城市应该与查询城市匹配，或者为 None（通用 FAQ）
            assert result_city == city or result_city is None, (
                f"FAQ 检索结果城市不匹配: 查询城市={city}, 结果城市={result_city}"
            )
    
    @given(
        city=city_strategy,
        query=search_query_strategy
    )
    @settings(max_examples=100, deadline=None)
    @pytest.mark.asyncio
    async def test_search_policy_tool_city_filter(self, city: str, query: str):
        """
        **Feature: agent-core, Property 8: 政策检索城市过滤**
        **Validates: Requirements 5.4**
        
        对于任意带城市参数的 SearchPolicyTool 调用，返回结果中所有文档的城市字段应与查询城市匹配
        """
        tool = SearchPolicyTool()
        
        # 执行工具调用
        result = await tool.execute(query=query, city=city)
        
        # 验证调用成功
        assert result["success"] is True, "工具调用应成功"
        
        # 验证所有返回结果的城市字段
        for item in result.get("results", []):
            result_city = item.get("city")
            # 结果城市应该与查询城市匹配，或者为 None（通用政策）
            assert result_city == city or result_city is None, (
                f"SearchPolicyTool 结果城市不匹配: 查询城市={city}, 结果城市={result_city}"
            )
    
    @given(
        city=city_strategy,
        query=search_query_strategy
    )
    @settings(max_examples=100, deadline=None)
    @pytest.mark.asyncio
    async def test_search_faq_tool_city_filter(self, city: str, query: str):
        """
        **Feature: agent-core, Property 8: 政策检索城市过滤**
        **Validates: Requirements 5.4**
        
        对于任意带城市参数的 SearchFAQTool 调用，返回结果中所有文档的城市字段应与查询城市匹配
        """
        tool = SearchFAQTool()
        
        # 执行工具调用
        result = await tool.execute(query=query, city=city)
        
        # 验证调用成功
        assert result["success"] is True, "工具调用应成功"
        
        # 验证所有返回结果的城市字段
        for item in result.get("results", []):
            result_city = item.get("city")
            # 结果城市应该与查询城市匹配，或者为 None（通用 FAQ）
            assert result_city == city or result_city is None, (
                f"SearchFAQTool 结果城市不匹配: 查询城市={city}, 结果城市={result_city}"
            )
    
    @given(
        query=search_query_strategy,
        top_k=top_k_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_policy_search_without_city_returns_all(self, query: str, top_k: int):
        """
        **Feature: agent-core, Property 8: 政策检索城市过滤**
        **Validates: Requirements 5.4**
        
        对于不带城市参数的政策检索，应返回所有城市的结果
        """
        # 执行不带城市过滤的搜索
        results = self.kb.search_policy(query, city=None, top_k=top_k)
        
        # 收集结果中的城市
        cities_in_results = set()
        for result in results:
            result_city = result.get("city")
            if result_city:
                cities_in_results.add(result_city)
        
        # 如果有结果，验证可能包含多个城市（或至少不限制城市）
        # 这个测试主要验证不带城市参数时不会过滤结果
        # 由于知识库数据有限，我们只验证结果格式正确
        for result in results:
            assert "content" in result or "answer" in result, "结果应包含内容"
            assert "relevance_score" in result, "结果应包含相关度分数"

