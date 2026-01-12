# 检查点测试 - 核心模块测试
# 验证所有工具可以独立执行，Agent 引擎可以处理简单问题

import asyncio
import pytest
from typing import Any

# 导入工具（从 __init__.py 导入以触发注册）
from app.agent.tools import (
    tool_registry,
    CalcLoanTool,
    CalcTaxTool,
    CalcTotalCostTool,
    AssessPressureTool,
    QueryMarketTool,
    QueryPriceTrendTool,
    CompareDistrictsTool,
    JudgeTimingTool,
    SearchPolicyTool,
    SearchFAQTool,
    get_knowledge_base
)

# 导入角色和意图识别
from app.agent.roles import (
    FINANCIAL_ADVISOR,
    POLICY_EXPERT,
    MARKET_ANALYST,
    PURCHASE_CONSULTANT,
    get_role,
    get_all_roles
)
from app.agent.intent import IntentRecognizer, ExecutionPlan


class TestToolRegistration:
    """测试工具注册完整性"""
    
    def test_all_tools_registered(self):
        """验证所有工具都已注册"""
        expected_tools = [
            "calc_loan",
            "calc_tax",
            "calc_total_cost",
            "assess_pressure",
            "query_market",
            "query_price_trend",
            "compare_districts",
            "judge_timing",
            "search_policy",
            "search_faq"
        ]
        
        for tool_name in expected_tools:
            assert tool_registry.exists(tool_name), f"工具 {tool_name} 未注册"
    
    def test_tool_count(self):
        """验证工具总数"""
        tools = tool_registry.get_all()
        assert len(tools) >= 10, f"工具数量不足，当前: {len(tools)}"


class TestFinancialToolsExecution:
    """测试财务计算工具独立执行"""
    
    @pytest.mark.asyncio
    async def test_calc_loan_equal_payment(self):
        """测试等额本息贷款计算"""
        tool = CalcLoanTool()
        result = await tool.execute(
            price=1000000,  # 100万
            down_payment_ratio=0.3,  # 30%首付
            years=30,
            rate=4.2,  # 4.2%年利率
            method="equal_payment"
        )
        
        assert "down_payment" in result
        assert "loan_amount" in result
        assert "monthly_payment" in result
        assert "total_interest" in result
        
        # 验证计算结果合理性
        assert result["down_payment"] == 300000  # 30万首付
        assert result["loan_amount"] == 700000  # 70万贷款
        assert result["monthly_payment"] > 0
        assert result["total_interest"] > 0
        assert result["method"] == "equal_payment"
    
    @pytest.mark.asyncio
    async def test_calc_loan_equal_principal(self):
        """测试等额本金贷款计算"""
        tool = CalcLoanTool()
        result = await tool.execute(
            price=1000000,
            down_payment_ratio=0.3,
            years=30,
            rate=4.2,
            method="equal_principal"
        )
        
        assert result["method"] == "equal_principal"
        assert result["first_month_payment"] > result["last_month_payment"]
    
    @pytest.mark.asyncio
    async def test_calc_tax_first_home_small(self):
        """测试首套小面积房税费计算"""
        tool = CalcTaxTool()
        result = await tool.execute(
            price=1000000,
            area=85,  # 小于90平
            is_first_home=True,
            house_age_years=3
        )
        
        assert "deed_tax" in result
        assert "vat" in result
        assert "income_tax" in result
        assert "agent_fee" in result
        assert "total" in result
        
        # 首套小面积契税1%
        assert result["deed_tax_rate"] == 0.01
        # 满2年免增值税
        assert result["vat"] == 0
    
    @pytest.mark.asyncio
    async def test_calc_tax_second_home_large(self):
        """测试二套大面积房税费计算"""
        tool = CalcTaxTool()
        result = await tool.execute(
            price=2000000,
            area=120,  # 大于90平
            is_first_home=False,
            house_age_years=1  # 不满2年
        )
        
        # 二套大面积契税2%
        assert result["deed_tax_rate"] == 0.02
        # 不满2年有增值税
        assert result["vat"] > 0
    
    @pytest.mark.asyncio
    async def test_calc_total_cost(self):
        """测试总成本计算"""
        tool = CalcTotalCostTool()
        result = await tool.execute(
            price=1000000,
            down_payment=300000,
            total_interest=500000,
            taxes=50000,
            decoration=100000,
            furniture=50000
        )
        
        assert "initial_cost" in result
        assert "total_cost" in result
        assert "breakdown" in result
        
        # 验证总成本计算
        expected_total = 1000000 + 500000 + 50000 + 100000 + 50000
        assert result["total_cost"] == expected_total
    
    @pytest.mark.asyncio
    async def test_assess_pressure_low(self):
        """测试低压力评估"""
        tool = AssessPressureTool()
        result = await tool.execute(
            monthly_payment=3000,
            monthly_income=15000  # 月供占比20%
        )
        
        assert result["level"] == "low"
        assert result["payment_ratio"] == 20.0
    
    @pytest.mark.asyncio
    async def test_assess_pressure_medium(self):
        """测试中压力评估"""
        tool = AssessPressureTool()
        result = await tool.execute(
            monthly_payment=6000,
            monthly_income=15000  # 月供占比40%
        )
        
        assert result["level"] == "medium"
    
    @pytest.mark.asyncio
    async def test_assess_pressure_high(self):
        """测试高压力评估"""
        tool = AssessPressureTool()
        result = await tool.execute(
            monthly_payment=9000,
            monthly_income=15000  # 月供占比60%
        )
        
        assert result["level"] == "high"


class TestMarketToolsExecution:
    """测试市场查询工具独立执行"""
    
    @pytest.mark.asyncio
    async def test_query_market_city(self):
        """测试城市市场数据查询"""
        tool = QueryMarketTool()
        result = await tool.execute(city="南宁")
        
        assert result["success"] is True
        assert "overview" in result
        assert "districts" in result
        assert len(result["districts"]) > 0
    
    @pytest.mark.asyncio
    async def test_query_market_district(self):
        """测试区域市场数据查询"""
        tool = QueryMarketTool()
        result = await tool.execute(city="南宁", district="青秀区")
        
        assert result["success"] is True
        assert "avg_price" in result
        assert "monthly_sales" in result
        assert result["district"] == "青秀区"
    
    @pytest.mark.asyncio
    async def test_query_market_invalid_city(self):
        """测试无效城市查询 - 参数验证会拒绝不在枚举中的城市"""
        tool = QueryMarketTool()
        # 由于 city 参数有 enum 限制，无效城市会在参数验证阶段被拒绝
        with pytest.raises(ValueError) as exc_info:
            await tool.execute(city="北京")
        assert "值无效" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_query_market_invalid_district(self):
        """测试无效区域查询 - 返回错误响应"""
        tool = QueryMarketTool()
        result = await tool.execute(city="南宁", district="不存在的区")
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_query_price_trend(self):
        """测试房价走势查询"""
        tool = QueryPriceTrendTool()
        result = await tool.execute(city="南宁", district="青秀区")
        
        assert result["success"] is True
        assert "trend" in result
        assert "statistics" in result
        assert len(result["trend"]) > 0
    
    @pytest.mark.asyncio
    async def test_compare_districts(self):
        """测试区域对比"""
        tool = CompareDistrictsTool()
        result = await tool.execute(
            city="南宁",
            districts="青秀区,江南区,良庆区"
        )
        
        assert result["success"] is True
        assert "comparison" in result
        assert "analysis" in result
        assert len(result["comparison"]) == 3
    
    @pytest.mark.asyncio
    async def test_judge_timing(self):
        """测试购房时机判断"""
        tool = JudgeTimingTool()
        result = await tool.execute(city="南宁", purpose="自住")
        
        assert result["success"] is True
        assert "score" in result
        assert "timing" in result
        assert "suggestions" in result
        assert result["score"]["total"] >= 0
        assert result["score"]["total"] <= 100


class TestPolicyToolsExecution:
    """测试政策检索工具独立执行"""
    
    def test_knowledge_base_loaded(self):
        """验证知识库已加载"""
        kb = get_knowledge_base()
        assert len(kb._policies) > 0, "政策文档未加载"
        assert len(kb._faqs) > 0, "FAQ 未加载"
    
    @pytest.mark.asyncio
    async def test_search_policy(self):
        """测试政策搜索"""
        tool = SearchPolicyTool()
        result = await tool.execute(query="限购政策")
        
        assert result["success"] is True
        assert "results" in result
        assert "count" in result
    
    @pytest.mark.asyncio
    async def test_search_policy_with_city(self):
        """测试带城市过滤的政策搜索"""
        tool = SearchPolicyTool()
        result = await tool.execute(query="首付比例", city="南宁")
        
        assert result["success"] is True
        # 如果有结果，验证城市过滤
        if result["count"] > 0:
            for r in result["results"]:
                if r.get("city"):
                    assert r["city"] == "南宁"
    
    @pytest.mark.asyncio
    async def test_search_faq(self):
        """测试 FAQ 搜索"""
        tool = SearchFAQTool()
        result = await tool.execute(query="公积金贷款")
        
        assert result["success"] is True
        assert "results" in result
    
    @pytest.mark.asyncio
    async def test_search_faq_with_category(self):
        """测试带分类的 FAQ 搜索"""
        tool = SearchFAQTool()
        result = await tool.execute(query="还款", category="贷款")
        
        assert result["success"] is True


class TestToolSchemaGeneration:
    """测试工具 Schema 生成"""
    
    def test_tool_schema_format(self):
        """验证工具 Schema 格式正确"""
        tool = CalcLoanTool()
        schema = tool.to_openai_schema()
        
        assert schema["type"] == "function"
        assert "function" in schema
        assert "name" in schema["function"]
        assert "description" in schema["function"]
        assert "parameters" in schema["function"]
        assert schema["function"]["name"] == "calc_loan"
    
    def test_all_tools_have_valid_schema(self):
        """验证所有工具都有有效的 Schema"""
        for tool in tool_registry.get_all():
            schema = tool.to_openai_schema()
            assert schema["type"] == "function"
            assert schema["function"]["name"] == tool.name
            assert len(schema["function"]["description"]) > 0


class TestRoleToolsIntegration:
    """测试角色与工具的集成"""
    
    def test_financial_advisor_tools_executable(self):
        """验证财务顾问的所有工具可执行"""
        role = FINANCIAL_ADVISOR
        for tool_name in role.tools:
            tool = tool_registry.get(tool_name)
            assert tool is not None, f"工具 {tool_name} 不存在"
            assert hasattr(tool, "execute"), f"工具 {tool_name} 没有 execute 方法"
    
    def test_policy_expert_tools_executable(self):
        """验证政策专家的所有工具可执行"""
        role = POLICY_EXPERT
        for tool_name in role.tools:
            tool = tool_registry.get(tool_name)
            assert tool is not None, f"工具 {tool_name} 不存在"
    
    def test_market_analyst_tools_executable(self):
        """验证市场分析师的所有工具可执行"""
        role = MARKET_ANALYST
        for tool_name in role.tools:
            tool = tool_registry.get(tool_name)
            assert tool is not None, f"工具 {tool_name} 不存在"
    
    def test_purchase_consultant_tools_executable(self):
        """验证购房顾问的所有工具可执行"""
        role = PURCHASE_CONSULTANT
        for tool_name in role.tools:
            tool = tool_registry.get(tool_name)
            assert tool is not None, f"工具 {tool_name} 不存在"


class TestIntentRecognitionBasic:
    """测试意图识别基础功能"""
    
    def setup_method(self):
        self.recognizer = IntentRecognizer()
    
    def test_financial_intent(self):
        """测试财务意图识别"""
        roles = self.recognizer.match_keywords("帮我计算一下贷款月供")
        assert FINANCIAL_ADVISOR in roles
    
    def test_policy_intent(self):
        """测试政策意图识别"""
        roles = self.recognizer.match_keywords("南宁限购政策是什么")
        assert POLICY_EXPERT in roles
    
    def test_market_intent(self):
        """测试市场意图识别"""
        roles = self.recognizer.match_keywords("青秀区房价多少")
        assert MARKET_ANALYST in roles
    
    def test_multi_intent(self):
        """测试多意图识别"""
        roles = self.recognizer.match_keywords("公积金贷款月供怎么算")
        assert len(roles) >= 2
        assert FINANCIAL_ADVISOR in roles
        assert POLICY_EXPERT in roles
    
    @pytest.mark.asyncio
    async def test_execution_plan_single_role(self):
        """测试单角色执行计划"""
        plan = await self.recognizer.plan_execution("计算贷款月供")
        assert len(plan.roles) >= 1
        assert isinstance(plan, ExecutionPlan)
    
    @pytest.mark.asyncio
    async def test_execution_plan_multi_role(self):
        """测试多角色执行计划"""
        plan = await self.recognizer.plan_execution(
            "公积金贷款月供怎么算",
            candidate_roles=[POLICY_EXPERT, FINANCIAL_ADVISOR]
        )
        assert len(plan.roles) == 2


class TestToolParameterValidation:
    """测试工具参数验证"""
    
    @pytest.mark.asyncio
    async def test_missing_required_param(self):
        """测试缺少必需参数"""
        tool = CalcLoanTool()
        with pytest.raises(ValueError) as exc_info:
            await tool.execute(price=1000000)  # 缺少其他必需参数
        assert "缺少必需参数" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_invalid_param_type(self):
        """测试参数类型错误"""
        tool = CalcLoanTool()
        with pytest.raises(ValueError) as exc_info:
            await tool.execute(
                price="not a number",  # 应该是数字
                down_payment_ratio=0.3,
                years=30,
                rate=4.2
            )
        assert "类型错误" in str(exc_info.value)


# 运行测试的入口
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
