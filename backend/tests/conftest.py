# pytest 配置文件
# 确保工具在所有测试之前被注册

import pytest

# 导入工具模块以触发注册（在所有测试之前）
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
    SearchFAQTool
)


@pytest.fixture(scope="session", autouse=True)
def ensure_tools_registered():
    """确保所有工具在测试会话开始时已注册"""
    # 验证工具已注册
    expected_tools = [
        "calc_loan", "calc_tax", "calc_total_cost", "assess_pressure",
        "query_market", "query_price_trend", "compare_districts", "judge_timing",
        "search_policy", "search_faq"
    ]
    
    registered = [t.name for t in tool_registry.get_all()]
    for tool_name in expected_tools:
        if tool_name not in registered:
            raise RuntimeError(f"工具 {tool_name} 未注册")
    
    yield
