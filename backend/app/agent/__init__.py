# Agent 模块
# 包含伪多 Agent 引擎、角色系统、意图识别和工具调用

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

from app.agent.intent import (
    IntentRecognizer,
    ExecutionPlan,
    get_intent_recognizer
)

from app.agent.engine import (
    AgentEngine,
    ConversationContext,
    get_agent_engine
)

__all__ = [
    # 角色相关
    "Role",
    "FINANCIAL_ADVISOR",
    "POLICY_EXPERT",
    "MARKET_ANALYST",
    "PURCHASE_CONSULTANT",
    "ALL_ROLES",
    "ROLE_MAP",
    "get_role",
    "get_all_roles",
    "get_role_by_name",
    "get_specialist_roles",
    # 意图识别
    "IntentRecognizer",
    "ExecutionPlan",
    "get_intent_recognizer",
    # Agent 引擎
    "AgentEngine",
    "ConversationContext",
    "get_agent_engine",
]
