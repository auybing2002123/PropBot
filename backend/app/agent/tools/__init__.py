# Agent 工具模块
# 包含工具基类、注册表和各类工具实现

from app.agent.tools.base import BaseTool, ToolParameter
from app.agent.tools.registry import (
    ToolRegistry,
    tool_registry,
    register_tool
)

# 导入财务计算工具（触发注册）
from app.agent.tools.financial import (
    CalcLoanTool,
    CalcTaxTool,
    CalcTotalCostTool,
    AssessPressureTool,
    GenerateRepaymentPlanTool
)

# 导入市场查询工具（触发注册）
from app.agent.tools.market import (
    QueryMarketTool,
    QueryPriceTrendTool,
    CompareDistrictsTool,
    JudgeTimingTool
)

# 导入政策检索工具（触发注册）
from app.agent.tools.policy import (
    SearchPolicyTool,
    SearchFAQTool,
    SearchGuideTool,
    get_knowledge_base
)

# 导入新闻搜索工具（触发注册）
from app.agent.tools.news import SearchNewsTool

# 导入报告生成工具（触发注册）
from app.agent.tools.report import GenerateReportTool

__all__ = [
    "BaseTool",
    "ToolParameter",
    "ToolRegistry",
    "tool_registry",
    "register_tool",
    # 财务计算工具
    "CalcLoanTool",
    "CalcTaxTool",
    "CalcTotalCostTool",
    "AssessPressureTool",
    "GenerateRepaymentPlanTool",
    # 市场查询工具
    "QueryMarketTool",
    "QueryPriceTrendTool",
    "CompareDistrictsTool",
    "JudgeTimingTool",
    # 政策检索工具
    "SearchPolicyTool",
    "SearchFAQTool",
    "SearchGuideTool",
    "get_knowledge_base",
    # 新闻搜索工具
    "SearchNewsTool",
    # 报告生成工具
    "GenerateReportTool"
]
