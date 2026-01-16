"""测试导入"""
from app.agent.intent import IntentRecognizer, ExecutionPlan, ExecutionNode
from app.agent.engine import AgentEngine

print("导入成功")

# 测试 ExecutionPlan
plan = ExecutionPlan(
    nodes=[
        ExecutionNode(role_id="policy_expert", depends_on=[]),
        ExecutionNode(role_id="financial_advisor", depends_on=[]),
        ExecutionNode(role_id="purchase_consultant", depends_on=["policy_expert", "financial_advisor"])
    ],
    reason="测试"
)

print(f"角色: {plan.role_ids}")

# 测试 get_ready_nodes
completed = set()
ready = plan.get_ready_nodes(completed)
print(f"第1轮可执行: {[n.role_id for n in ready]}")

completed = {"policy_expert", "financial_advisor"}
ready = plan.get_ready_nodes(completed)
print(f"第2轮可执行: {[n.role_id for n in ready]}")

print("测试通过!")
