"""
意图识别模块
根据用户输入识别需要调用的角色，并生成 DAG 执行计划
"""
import json
import re
from dataclasses import dataclass, field

from app.agent.roles import (
    Role,
    PURCHASE_CONSULTANT,
    get_specialist_roles,
    get_role
)
from app.llm.client import DeepSeekClient, LLMError
from app.utils.logger import get_logger

logger = get_logger("house_advisor.agent.intent")


@dataclass
class ExecutionNode:
    """
    执行节点
    
    Attributes:
        role_id: 角色 ID
        depends_on: 依赖的角色 ID 列表（空表示无依赖，可立即执行）
    """
    role_id: str
    depends_on: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "role_id": self.role_id,
            "depends_on": self.depends_on
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ExecutionNode":
        return cls(
            role_id=data.get("role_id", ""),
            depends_on=data.get("depends_on", [])
        )


@dataclass
class ExecutionPlan:
    """
    执行计划（DAG）
    
    Attributes:
        nodes: 执行节点列表
        reason: LLM 给出的规划理由
    """
    nodes: list[ExecutionNode] = field(default_factory=list)
    reason: str = ""
    
    @property
    def roles(self) -> list[Role]:
        """获取所有角色对象"""
        roles = []
        for node in self.nodes:
            role = get_role(node.role_id)
            if role:
                roles.append(role)
        return roles
    
    @property
    def role_ids(self) -> list[str]:
        """获取所有角色 ID"""
        return [node.role_id for node in self.nodes]
    
    def get_node(self, role_id: str) -> ExecutionNode | None:
        """根据角色 ID 获取节点"""
        for node in self.nodes:
            if node.role_id == role_id:
                return node
        return None
    
    def get_ready_nodes(self, completed: set[str]) -> list[ExecutionNode]:
        """
        获取当前可执行的节点（依赖都已完成）
        
        Args:
            completed: 已完成的角色 ID 集合
            
        Returns:
            可执行的节点列表
        """
        ready = []
        for node in self.nodes:
            if node.role_id in completed:
                continue  # 已完成，跳过
            # 检查依赖是否都已完成
            if all(dep in completed for dep in node.depends_on):
                ready.append(node)
        return ready
    
    def to_dict(self) -> dict:
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "reason": self.reason
        }


class IntentRecognizer:
    """
    意图识别器
    
    使用 LLM 分析用户意图，生成 DAG 执行计划
    """
    
    # 系统提示词模板
    SYSTEM_PROMPT = """你是一个智能任务规划器，负责分析用户的购房咨询问题，决定需要哪些专家角色来回答，以及它们之间的执行依赖关系。

## 可用的专家角色

1. **financial_advisor（财务顾问）**
   - 职责：贷款计算、月供计算、税费估算、购房成本分析、还款压力评估
   - 适用问题：贷款怎么算、月供多少、要交多少税、买房要花多少钱

2. **policy_expert（政策专家）**
   - 职责：限购限贷政策、公积金政策、购房资格、税收优惠政策
   - 适用问题：限购吗、能买几套、公积金能贷多少、需要什么条件

3. **market_analyst（市场分析师）**
   - 职责：房价走势、区域对比、市场行情、购房时机判断
   - 适用问题：房价多少、哪个区好、现在能买吗、会涨还是跌

4. **purchase_consultant（购房顾问）**
   - 职责：综合建议、整合多方信息、购房流程指导
   - 适用问题：综合分析、给我建议、怎么买房
   - **特殊规则**：当需要整合多个专家的结果时，purchase_consultant 应该依赖这些专家

## 依赖关系判断规则

1. **无依赖（可并行）**：两个角色的分析相互独立，不需要对方的结果
   - 例：政策专家查限购 + 市场分析师查房价 → 互不依赖，可并行

2. **有依赖（需串行）**：一个角色需要另一个角色的结果才能工作
   - 例：财务顾问计算贷款需要政策专家提供的利率信息 → 财务依赖政策
   - 例：购房顾问整合建议需要其他专家的分析结果 → 顾问依赖其他专家

3. **整合场景**：当有多个专家参与时，通常需要 purchase_consultant 来整合
   - purchase_consultant 应该依赖所有其他参与的专家

## 输出格式

请返回 JSON 格式：
```json
{
  "nodes": [
    {"role_id": "角色ID", "depends_on": ["依赖的角色ID列表，无依赖则为空数组"]}
  ],
  "reason": "简要说明规划理由"
}
```

## 示例

用户问题："南宁限购吗"
```json
{
  "nodes": [
    {"role_id": "policy_expert", "depends_on": []}
  ],
  "reason": "单一政策问题，只需政策专家"
}
```

用户问题："外地人在南宁买房要准备多少钱"
```json
{
  "nodes": [
    {"role_id": "policy_expert", "depends_on": []},
    {"role_id": "financial_advisor", "depends_on": []}
  ],
  "reason": "政策专家查购房资格，财务顾问算费用，两者独立可并行"
}
```

用户问题："根据南宁公积金政策帮我算下能贷多少"
```json
{
  "nodes": [
    {"role_id": "policy_expert", "depends_on": []},
    {"role_id": "financial_advisor", "depends_on": ["policy_expert"]}
  ],
  "reason": "财务计算需要政策专家提供的公积金额度信息，需串行"
}
```

用户问题："我想在南宁买150万的房子，月入1.5万，现在是好时机吗"
```json
{
  "nodes": [
    {"role_id": "policy_expert", "depends_on": []},
    {"role_id": "financial_advisor", "depends_on": []},
    {"role_id": "market_analyst", "depends_on": []},
    {"role_id": "purchase_consultant", "depends_on": ["policy_expert", "financial_advisor", "market_analyst"]}
  ],
  "reason": "综合问题：政策、财务、市场三者独立可并行，购房顾问最后整合"
}
```

## 注意事项

1. 尽量精简角色，不要过度调用
2. 能并行就并行，减少等待时间
3. 只有真正需要整合时才加入 purchase_consultant
4. 简单问题通常只需要 1 个角色"""
    
    def __init__(self, llm_client: DeepSeekClient | None = None):
        """
        初始化意图识别器
        
        Args:
            llm_client: LLM 客户端
        """
        self._llm_client = llm_client
    
    @property
    def llm_client(self) -> DeepSeekClient:
        """懒加载 LLM 客户端"""
        if self._llm_client is None:
            self._llm_client = DeepSeekClient()
        return self._llm_client
    
    async def plan_execution(self, user_input: str) -> ExecutionPlan:
        """
        分析用户输入，生成 DAG 执行计划
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            ExecutionPlan 执行计划
        """
        user_input = user_input.strip()
        if not user_input:
            return ExecutionPlan(
                nodes=[ExecutionNode(role_id="purchase_consultant", depends_on=[])],
                reason="空输入，使用默认角色"
            )
        
        try:
            return await self._plan_with_llm(user_input)
        except LLMError as e:
            logger.error(f"LLM 规划失败: {e.message}")
            # 降级：返回默认的购房顾问
            return ExecutionPlan(
                nodes=[ExecutionNode(role_id="purchase_consultant", depends_on=[])],
                reason=f"LLM 调用失败，使用默认角色: {e.message}"
            )
        except Exception as e:
            logger.exception(f"规划执行计划时发生错误: {e}")
            return ExecutionPlan(
                nodes=[ExecutionNode(role_id="purchase_consultant", depends_on=[])],
                reason=f"规划失败，使用默认角色: {str(e)}"
            )
    
    async def _plan_with_llm(self, user_input: str) -> ExecutionPlan:
        """
        使用 LLM 生成执行计划
        
        Args:
            user_input: 用户输入
            
        Returns:
            ExecutionPlan 执行计划
        """
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"用户问题：{user_input}"}
        ]
        
        response = await self.llm_client.chat(
            messages=messages,
            temperature=0.1  # 低温度以获得更确定的结果
        )
        
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        logger.debug(f"LLM 规划响应: {content}")
        
        return self._parse_plan_response(content)
    
    def _parse_plan_response(self, content: str) -> ExecutionPlan:
        """
        解析 LLM 返回的执行计划
        
        Args:
            content: LLM 返回的内容
            
        Returns:
            ExecutionPlan 执行计划
        """
        try:
            # 尝试提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', content)
            if not json_match:
                raise ValueError("No JSON found in response")
            
            data = json.loads(json_match.group())
            
            # 解析节点
            nodes = []
            nodes_data = data.get("nodes", [])
            
            for node_data in nodes_data:
                role_id = node_data.get("role_id", "")
                # 验证角色 ID 是否有效
                if get_role(role_id):
                    depends_on = node_data.get("depends_on", [])
                    # 过滤无效的依赖
                    valid_depends = [d for d in depends_on if get_role(d)]
                    nodes.append(ExecutionNode(role_id=role_id, depends_on=valid_depends))
            
            # 如果没有有效节点，返回默认
            if not nodes:
                return ExecutionPlan(
                    nodes=[ExecutionNode(role_id="purchase_consultant", depends_on=[])],
                    reason="解析结果为空，使用默认角色"
                )
            
            # 验证 DAG 有效性（检查循环依赖）
            if not self._validate_dag(nodes):
                logger.warning("检测到循环依赖，清除所有依赖")
                for node in nodes:
                    node.depends_on = []
            
            return ExecutionPlan(
                nodes=nodes,
                reason=data.get("reason", "")
            )
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"解析执行计划失败: {e}, content: {content}")
            return ExecutionPlan(
                nodes=[ExecutionNode(role_id="purchase_consultant", depends_on=[])],
                reason=f"解析失败，使用默认角色: {str(e)}"
            )
    
    def _validate_dag(self, nodes: list[ExecutionNode]) -> bool:
        """
        验证 DAG 是否有效（无循环依赖）
        
        使用拓扑排序检测循环
        
        Args:
            nodes: 节点列表
            
        Returns:
            True 如果 DAG 有效，False 如果存在循环
        """
        # 构建邻接表和入度表
        role_ids = {node.role_id for node in nodes}
        in_degree = {node.role_id: 0 for node in nodes}
        graph = {node.role_id: [] for node in nodes}
        
        for node in nodes:
            for dep in node.depends_on:
                if dep in role_ids:
                    graph[dep].append(node.role_id)
                    in_degree[node.role_id] += 1
        
        # 拓扑排序
        queue = [rid for rid, deg in in_degree.items() if deg == 0]
        visited = 0
        
        while queue:
            current = queue.pop(0)
            visited += 1
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # 如果访问的节点数等于总节点数，则无循环
        return visited == len(nodes)


# 全局意图识别器实例
_intent_recognizer: IntentRecognizer | None = None


def get_intent_recognizer() -> IntentRecognizer:
    """
    获取全局意图识别器实例
    
    Returns:
        IntentRecognizer 实例
    """
    global _intent_recognizer
    if _intent_recognizer is None:
        _intent_recognizer = IntentRecognizer()
    return _intent_recognizer
