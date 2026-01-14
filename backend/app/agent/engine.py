"""
Agent 引擎核心
伪多 Agent 引擎，负责意图识别、DAG 调度、工具调用和结果整合
支持真正的流式输出
"""
import asyncio
import json
from typing import AsyncGenerator
from dataclasses import dataclass, field

from app.agent.intent import IntentRecognizer, ExecutionPlan, ExecutionNode, get_intent_recognizer
from app.agent.roles import Role, PURCHASE_CONSULTANT, get_role
from app.agent.tools import tool_registry
from app.llm.client import DeepSeekClient, LLMError, StreamResultCollector
from app.db.database import get_db
from app.utils.logger import get_logger

logger = get_logger("house_advisor.agent")


@dataclass
class ConversationContext:
    """
    对话上下文
    
    Attributes:
        session_id: 会话 ID
        history: 历史消息列表
        user_info: 用户信息（预算、收入等）
        role_results: 各角色的执行结果
    """
    session_id: str
    history: list[dict] = field(default_factory=list)
    user_info: dict = field(default_factory=dict)
    role_results: dict[str, str] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str) -> None:
        """添加消息到历史"""
        self.history.append({"role": role, "content": content})
    
    def get_recent_history(self, max_turns: int = 10) -> list[dict]:
        """获取最近的对话历史"""
        max_messages = max_turns * 2
        return self.history[-max_messages:] if len(self.history) > max_messages else self.history
    
    def to_dict(self) -> dict:
        """转换为字典（用于 Redis 存储）"""
        return {
            "session_id": self.session_id,
            "history": self.history,
            "user_info": self.user_info,
            "role_results": self.role_results
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ConversationContext":
        """从字典创建（用于 Redis 读取）"""
        return cls(
            session_id=data.get("session_id", ""),
            history=data.get("history", []),
            user_info=data.get("user_info", {}),
            role_results=data.get("role_results", {})
        )


@dataclass
class RoleResult:
    """角色执行结果"""
    role_id: str
    role_name: str
    role_icon: str
    content: str
    success: bool = True
    error: str = ""


class AgentEngine:
    """
    伪多 Agent 引擎
    
    采用"一个大脑，多个人格"的架构，对外表现为多智能体协作，
    内部实现为单 Agent + 多角色 + 多工具 + DAG 调度
    """
    
    CONTEXT_KEY_PREFIX = "chat:context:"
    CONTEXT_TTL = 3600 * 24  # 24 小时
    
    def __init__(self, llm_client: DeepSeekClient | None = None):
        self._llm_client = llm_client
        self._intent_recognizer: IntentRecognizer | None = None
    
    @property
    def llm_client(self) -> DeepSeekClient:
        if self._llm_client is None:
            self._llm_client = DeepSeekClient()
        return self._llm_client
    
    @property
    def intent_recognizer(self) -> IntentRecognizer:
        if self._intent_recognizer is None:
            self._intent_recognizer = IntentRecognizer(self.llm_client)
        return self._intent_recognizer

    async def process(
        self,
        user_input: str,
        session_id: str,
        mode: str = "standard"
    ) -> AsyncGenerator[dict, None]:
        """
        处理用户输入，流式返回结果
        
        Args:
            user_input: 用户输入
            session_id: 会话 ID
            mode: 执行模式（standard/discussion）
        
        Yields:
            事件字典
        """
        logger.info(f"处理用户输入: session={session_id}, mode={mode}, input={user_input[:50]}...")
        
        context = await self._load_context(session_id)
        context.add_message("user", user_input)
        
        try:
            # 发送思考开始事件
            yield {"type": "thinking_start"}
            
            # 1. 意图识别，生成 DAG 执行计划
            yield {
                "type": "thinking_step",
                "step_type": "planning",
                "content": "正在分析您的问题..."
            }
            
            plan = await self.intent_recognizer.plan_execution(user_input)
            logger.info(f"执行计划: roles={plan.role_ids}, reason={plan.reason}")
            
            # 发送规划结果
            role_names = [get_role(rid).name for rid in plan.role_ids if get_role(rid)]
            yield {
                "type": "thinking_step",
                "step_type": "planning",
                "content": f"已确定由 {', '.join(role_names)} 为您解答"
            }
            
            # 2. 根据模式执行
            if mode == "discussion" and len(plan.nodes) > 1:
                async for event in self._process_discussion_mode(user_input, plan, context):
                    yield event
            else:
                # 标准模式：DAG 调度执行
                async for event in self._process_dag_mode(user_input, plan, context):
                    yield event
            
            # 3. 保存上下文
            await self._save_context(context)
            
            # 4. 完成
            yield {"type": "done"}
            
        except LLMError as e:
            logger.error(f"LLM 调用失败: {e.message}")
            yield {"type": "error", "code": e.code, "message": e.message}
        except Exception as e:
            logger.exception(f"处理用户输入时发生错误: {e}")
            yield {"type": "error", "code": 1099, "message": "服务暂时不可用，请稍后重试"}

    async def _process_dag_mode(
        self,
        user_input: str,
        plan: ExecutionPlan,
        context: ConversationContext
    ) -> AsyncGenerator[dict, None]:
        """
        DAG 调度模式：根据依赖关系并行/串行执行角色
        
        Args:
            user_input: 用户输入
            plan: DAG 执行计划
            context: 对话上下文
            
        Yields:
            角色执行事件
        """
        context.role_results.clear()
        completed: set[str] = set()  # 已完成的角色 ID
        total_nodes = len(plan.nodes)  # 总节点数
        is_multi_expert = total_nodes > 1  # 是否多专家场景
        
        while True:
            # 获取当前可执行的节点
            ready_nodes = plan.get_ready_nodes(completed)
            
            if not ready_nodes:
                # 没有可执行的节点了
                if len(completed) < len(plan.nodes):
                    logger.warning(f"DAG 执行未完成，可能存在问题: completed={completed}, total={len(plan.nodes)}")
                break
            
            # 判断当前节点是否是最后一批节点
            is_last_batch = (len(completed) + len(ready_nodes)) == total_nodes
            
            # 判断是并行还是串行
            if len(ready_nodes) == 1:
                # 单节点执行
                node = ready_nodes[0]
                
                if is_multi_expert and not is_last_batch:
                    # 多专家场景的中间节点：不流式输出，只保存结果
                    async for event in self._execute_node_silent(node, user_input, context):
                        yield event
                else:
                    # 单专家场景 或 多专家场景的最后一个节点：流式输出
                    async for event in self._execute_node(node, user_input, context):
                        yield event
                completed.add(node.role_id)
            else:
                # 多节点，并行执行
                logger.info(f"并行执行 {len(ready_nodes)} 个角色: {[n.role_id for n in ready_nodes]}")
                
                # 先发送所有 role_start 事件和思考步骤
                for node in ready_nodes:
                    role = get_role(node.role_id)
                    if role:
                        yield {
                            "type": "role_start",
                            "role": role.id,
                            "name": role.name,
                            "icon": role.icon
                        }
                        yield {
                            "type": "thinking_step",
                            "step_type": "role_dispatch",
                            "content": f"{role.name}正在分析...",
                            "role": role.id
                        }
                
                # 并行执行所有角色
                tasks = [
                    self._execute_role_async(node, user_input, context)
                    for node in ready_nodes
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 按顺序发送结果
                for node, result in zip(ready_nodes, results):
                    if isinstance(result, Exception):
                        logger.error(f"角色 {node.role_id} 执行失败: {result}")
                        yield {
                            "type": "role_result",
                            "role": node.role_id,
                            "content": f"执行出错: {str(result)}"
                        }
                    else:
                        role_result, events = result
                        context.role_results[node.role_id] = role_result.content
                        
                        # 发送工具调用事件
                        for event in events:
                            yield event
                        
                        yield {
                            "type": "role_result",
                            "role": role_result.role_id,
                            "content": role_result.content
                        }
                    completed.add(node.role_id)
        
        # 多角色时自动整合（方案3：折叠展示）
        # 如果有多个角色结果且没有购房顾问，自动调用购房顾问整合
        if len(context.role_results) > 1 and "purchase_consultant" not in context.role_results:
            logger.info("多角色结果，自动调用购房顾问整合")
            
            # 发送整合思考步骤
            yield {
                "type": "thinking_step",
                "step_type": "synthesizing",
                "content": "正在整合各专家意见，生成综合建议..."
            }
            
            # 发送整合开始事件
            consultant = get_role("purchase_consultant")
            yield {
                "type": "role_start",
                "role": consultant.id,
                "name": consultant.name,
                "icon": consultant.icon,
                "is_summary": True  # 标记这是整合结果
            }
            
            # 流式生成整合结果
            summary = ""
            async for event in self._synthesize_results(user_input, context):
                if event["type"] == "content_delta":
                    yield event
                elif event["type"] == "content_complete":
                    summary = event["content"]
            
            context.role_results["purchase_consultant"] = summary
            
            yield {
                "type": "role_result",
                "role": consultant.id,
                "content": summary,
                "is_summary": True  # 标记这是整合结果
            }
        
        # 保存最终结果到历史
        if context.role_results:
            # 使用购房顾问的整合结果，或者最后一个角色的结果
            if "purchase_consultant" in context.role_results:
                final_result = context.role_results["purchase_consultant"]
            else:
                final_result = list(context.role_results.values())[-1]
            context.add_message("assistant", final_result)
    
    async def _synthesize_results(
        self,
        user_input: str,
        context: ConversationContext
    ) -> AsyncGenerator[dict, None]:
        """
        流式整合多角色结果
        
        Args:
            user_input: 用户原始问题
            context: 包含各角色结果的上下文
            
        Yields:
            流式事件（content_delta 和 content_complete）
        """
        # 构建整合提示词
        results_text = []
        for role_id, content in context.role_results.items():
            role = get_role(role_id)
            if role:
                results_text.append(f"【{role.name}的分析】\n{content}")
        
        synthesis_prompt = f"""基于以下各专家的分析，为用户提供简洁的综合建议。

用户问题：{user_input}

各专家分析：
{chr(10).join(results_text)}

请综合以上信息，给出：
1. 核心结论（一句话总结）
2. 关键要点（3-5条）
3. 建议下一步行动

注意：不要重复专家已经说过的详细内容，只做提炼和整合。

最后，在回复结束后输出 2-3 个相关的后续问题供用户选择，格式如下：

【推荐问题】
- 问题1
- 问题2
- 问题3"""
        
        consultant = get_role("purchase_consultant")
        messages = [
            {"role": "system", "content": consultant.system_prompt},
            {"role": "user", "content": synthesis_prompt}
        ]
        
        # 流式输出整合结果
        full_content = ""
        async for chunk in self.llm_client.chat_stream(messages=messages, temperature=0.7):
            if chunk.content:
                full_content += chunk.content
                yield {
                    "type": "content_delta",
                    "role": consultant.id,
                    "delta": chunk.content
                }
        
        yield {
            "type": "content_complete",
            "role": consultant.id,
            "content": full_content
        }

    async def _execute_node(
        self,
        node: ExecutionNode,
        user_input: str,
        context: ConversationContext
    ) -> AsyncGenerator[dict, None]:
        """
        执行单个节点（串行模式，流式输出）
        
        Args:
            node: 执行节点
            user_input: 用户输入
            context: 对话上下文
            
        Yields:
            角色执行事件（包括流式内容）
        """
        role = get_role(node.role_id)
        if not role:
            logger.warning(f"角色不存在: {node.role_id}")
            return
        
        # 发送开始事件
        yield {
            "type": "role_start",
            "role": role.id,
            "name": role.name,
            "icon": role.icon
        }
        
        # 发送角色调度事件
        yield {
            "type": "thinking_step",
            "step_type": "role_dispatch",
            "content": f"{role.name}正在分析...",
            "role": role.id
        }
        
        # 流式执行角色
        try:
            full_content = ""
            async for event in self._execute_role_stream(role, user_input, context):
                if event["type"] == "content_delta":
                    # 转发内容增量
                    yield event
                elif event["type"] == "content_complete":
                    # 保存完整内容
                    full_content = event["content"]
                    context.role_results[role.id] = full_content
                elif event["type"] in ("tool_call", "tool_result"):
                    # 转发工具事件
                    yield event
            
            # 发送角色结果完成事件
            yield {
                "type": "role_result",
                "role": role.id,
                "content": full_content
            }
        except Exception as e:
            logger.error(f"角色 {role.id} 执行失败: {e}")
            yield {
                "type": "role_result",
                "role": role.id,
                "content": f"执行出错: {str(e)}"
            }

    async def _execute_node_silent(
        self,
        node: ExecutionNode,
        user_input: str,
        context: ConversationContext
    ) -> AsyncGenerator[dict, None]:
        """
        静默执行单个节点（多专家场景的中间节点）
        不流式输出内容，只发送思考步骤和工具调用事件
        
        Args:
            node: 执行节点
            user_input: 用户输入
            context: 对话上下文
            
        Yields:
            思考步骤和工具调用事件（不包括 content_delta）
        """
        role = get_role(node.role_id)
        if not role:
            logger.warning(f"角色不存在: {node.role_id}")
            return
        
        # 发送角色调度事件（在思考过程中展示）
        yield {
            "type": "thinking_step",
            "step_type": "role_dispatch",
            "content": f"{role.name}正在分析...",
            "role": role.id
        }
        
        # 执行角色，但不流式输出内容
        try:
            full_content = ""
            async for event in self._execute_role_stream(role, user_input, context):
                if event["type"] == "content_delta":
                    # 不转发内容增量，只累积
                    pass
                elif event["type"] == "content_complete":
                    # 保存完整内容
                    full_content = event["content"]
                    context.role_results[role.id] = full_content
                elif event["type"] in ("tool_call", "tool_result"):
                    # 转发工具事件（在思考过程中展示）
                    yield event
            
            # 发送专家分析完成的简洁状态（不展示内容摘要）
            yield {
                "type": "thinking_step",
                "step_type": "role_complete",
                "content": f"{role.name}分析完成",
                "role": role.id
            }
            
            logger.info(f"中间专家 {role.name} 分析完成，结果已保存到上下文")
            
        except Exception as e:
            logger.error(f"角色 {role.id} 执行失败: {e}")
            yield {
                "type": "thinking_step",
                "step_type": "error",
                "content": f"{role.name}分析出错: {str(e)}",
                "role": role.id
            }

    async def _execute_role_async(
        self,
        node: ExecutionNode,
        user_input: str,
        context: ConversationContext
    ) -> tuple[RoleResult, list[dict]]:
        """
        异步执行角色（用于并行执行）
        
        Args:
            node: 执行节点
            user_input: 用户输入
            context: 对话上下文
            
        Returns:
            (RoleResult 执行结果, 事件列表)
        """
        role = get_role(node.role_id)
        if not role:
            return RoleResult(
                role_id=node.role_id,
                role_name="未知角色",
                role_icon="❓",
                content="角色不存在",
                success=False,
                error="角色不存在"
            ), []
        
        try:
            content, events = await self._execute_role(role, user_input, context, emit_events=True)
            return RoleResult(
                role_id=role.id,
                role_name=role.name,
                role_icon=role.icon,
                content=content,
                success=True
            ), events
        except Exception as e:
            return RoleResult(
                role_id=role.id,
                role_name=role.name,
                role_icon=role.icon,
                content=f"执行出错: {str(e)}",
                success=False,
                error=str(e)
            ), []

    async def _execute_role(
        self,
        role: Role,
        user_input: str,
        context: ConversationContext,
        emit_events: bool = False
    ) -> tuple[str, list[dict]]:
        """
        执行单个角色（非流式，用于并行执行）
        
        Args:
            role: 角色定义
            user_input: 用户输入
            context: 对话上下文
            emit_events: 是否返回事件
            
        Returns:
            (角色回复内容, 事件列表)
        """
        logger.info(f"执行角色: {role.id}")
        
        messages = self._build_role_messages(role, user_input, context)
        tools = tool_registry.get_schemas(role.tools)
        
        response = await self.llm_client.chat(
            messages=messages,
            tools=tools if tools else None,
            temperature=0.7
        )
        
        return await self._process_llm_response_with_events(
            response, role, messages, emit_events
        )

    async def _execute_role_stream(
        self,
        role: Role,
        user_input: str,
        context: ConversationContext
    ) -> AsyncGenerator[dict, None]:
        """
        流式执行单个角色
        
        Args:
            role: 角色定义
            user_input: 用户输入
            context: 对话上下文
            
        Yields:
            事件字典，包括 content_delta（内容增量）和工具调用事件
        """
        logger.info(f"流式执行角色: {role.id}")
        
        messages = self._build_role_messages(role, user_input, context)
        tools = tool_registry.get_schemas(role.tools)
        
        # 使用流式 API
        content_gen, collector = await self.llm_client.chat_stream_complete(
            messages=messages,
            tools=tools if tools else None,
            temperature=0.7
        )
        
        # 边接收边发送，实现真正的流式输出
        full_content = ""
        sent_content = ""  # 已发送的内容
        chunk_count = 0  # 调试用：统计发送的块数
        
        async for delta in content_gen:
            if delta:
                full_content += delta
                chunk_count += 1
                # 实时发送内容增量
                logger.debug(f"发送 content_delta #{chunk_count}: {delta[:20]}...")
                yield {
                    "type": "content_delta",
                    "role": role.id,
                    "delta": delta
                }
                sent_content += delta
        
        logger.info(f"流式输出完成: 共发送 {chunk_count} 个 content_delta 事件")
        
        # 检查是否有工具调用
        result = collector.get_result()
        has_tool_calls = bool(result.tool_calls)
        
        if has_tool_calls:
            # 有工具调用，之前发送的内容是思考过程
            # 发送一个标记，告诉前端之前的内容是思考过程
            if sent_content.strip():
                yield {
                    "type": "thinking_step",
                    "step_type": "planning",
                    "content": sent_content.strip()[:100] + "..." if len(sent_content) > 100 else sent_content.strip(),
                    "role": role.id
                }
            
            # 流式处理工具调用，这里会真正流式输出最终回复
            tool_content = ""
            async for event in self._handle_tool_calls_stream(
                result.tool_calls, role, messages, result.content
            ):
                if event["type"] == "tool_content_complete":
                    tool_content = event["content"]
                else:
                    yield event
            
            full_content = tool_content
        
        # 返回完整内容（用于保存到上下文）
        yield {
            "type": "content_complete",
            "role": role.id,
            "content": full_content
        }

    async def _handle_tool_calls_stream(
        self,
        tool_calls: list[dict],
        role: Role,
        messages: list[dict],
        assistant_content: str
    ) -> AsyncGenerator[dict, None]:
        """
        处理工具调用（流式版本）
        
        Yields:
            事件字典
        """
        # 构建 assistant 消息
        assistant_message = {
            "role": "assistant",
            "content": assistant_content or None,
            "tool_calls": tool_calls
        }
        messages.append(assistant_message)
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("function", {}).get("name", "")
            tool_args_str = tool_call.get("function", {}).get("arguments", "{}")
            tool_call_id = tool_call.get("id", "")
            
            logger.info(f"执行工具: {tool_name}, 参数: {tool_args_str}")
            
            # 发送工具调用事件
            yield {
                "type": "tool_call",
                "tool_name": tool_name,
                "tool_args": tool_args_str,
                "role": role.id
            }
            
            try:
                tool_args = json.loads(tool_args_str)
            except json.JSONDecodeError:
                tool_args = {}
            
            tool = tool_registry.get(tool_name)
            if tool:
                try:
                    result = await tool.execute(**tool_args)
                    tool_result = json.dumps(result, ensure_ascii=False)
                    
                    yield {
                        "type": "tool_result",
                        "tool_name": tool_name,
                        "content": f"工具 {tool_name} 执行完成",
                        "role": role.id
                    }
                except Exception as e:
                    logger.error(f"工具执行失败: {tool_name}, 错误: {e}")
                    tool_result = json.dumps({"error": str(e)}, ensure_ascii=False)
            else:
                logger.warning(f"工具不存在: {tool_name}")
                tool_result = json.dumps({"error": f"工具 {tool_name} 不存在"}, ensure_ascii=False)
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": tool_result
            })
        
        # 工具调用后，流式调用 LLM 获取最终回复
        tools = tool_registry.get_schemas(role.tools)
        
        # 使用 chat_stream_complete 来处理可能的后续工具调用
        content_gen, collector = await self.llm_client.chat_stream_complete(
            messages=messages,
            tools=tools if tools else None,
            temperature=0.7
        )
        
        # 真正的流式输出：边接收边发送
        full_content = ""
        tool_chunk_count = 0  # 调试用
        async for delta in content_gen:
            if delta:
                full_content += delta
                tool_chunk_count += 1
                logger.debug(f"工具调用后 content_delta #{tool_chunk_count}: {delta[:20]}...")
                # 实时发送内容增量
                yield {
                    "type": "content_delta",
                    "role": role.id,
                    "delta": delta,
                    "after_tool": True
                }
        
        logger.info(f"工具调用后流式输出完成: 共发送 {tool_chunk_count} 个 content_delta 事件")
        
        # 检查是否有后续工具调用
        result = collector.get_result()
        if result.tool_calls:
            # 有新的工具调用，递归处理
            if full_content.strip():
                yield {
                    "type": "thinking_step",
                    "step_type": "planning",
                    "content": full_content.strip()[:100] + "..." if len(full_content) > 100 else full_content.strip(),
                    "role": role.id
                }
            
            async for event in self._handle_tool_calls_stream(
                result.tool_calls, role, messages, result.content
            ):
                yield event
        else:
            # 返回完整内容标记
            yield {
                "type": "tool_content_complete",
                "role": role.id,
                "content": full_content
            }
    
    def _build_role_messages(
        self,
        role: Role,
        user_input: str,
        context: ConversationContext
    ) -> list[dict]:
        """构建角色专属的消息列表"""
        messages = []
        
        # 系统提示词
        system_content = role.system_prompt
        
        # 如果有其他角色的结果，添加到系统提示词
        if context.role_results:
            other_results = []
            for role_id, result in context.role_results.items():
                other_role = get_role(role_id)
                if other_role:
                    other_results.append(f"【{other_role.name}的分析】\n{result}")
            
            if other_results:
                system_content += "\n\n以下是其他专家的分析结果，请参考：\n" + "\n\n".join(other_results)
        
        # 添加推荐问题的指令（方案2+3：动态推荐 + 意图引导）
        system_content += """

## 回复格式要求

1. 信息收集：如果用户问题缺少关键信息（如城市、预算、房屋类型、首付比例等），先礼貌地追问，不要直接给出模糊的回答。

2. 推荐问题：在回复结束后，输出 2-3 个相关的后续问题供用户选择，帮助用户深入了解。格式如下：

【推荐问题】
- 问题1
- 问题2
- 问题3

注意：推荐问题要与当前话题相关，具体且有价值，避免过于宽泛。"""
        
        messages.append({"role": "system", "content": system_content})
        
        # 历史对话
        recent_history = context.get_recent_history(max_turns=5)
        messages.extend(recent_history)
        
        # 当前用户输入
        if not recent_history or recent_history[-1].get("content") != user_input:
            messages.append({"role": "user", "content": user_input})
        
        return messages
    
    async def _process_llm_response(
        self,
        response: dict,
        role: Role,
        messages: list[dict]
    ) -> str:
        """处理 LLM 响应，包括工具调用"""
        content, _ = await self._process_llm_response_with_events(
            response, role, messages, emit_events=False
        )
        return content
    
    async def _handle_tool_calls(
        self,
        tool_calls: list[dict],
        role: Role,
        messages: list[dict],
        assistant_message: dict,
        emit_events: bool = False
    ) -> tuple[str, list[dict]]:
        """
        处理工具调用
        
        Args:
            tool_calls: 工具调用列表
            role: 当前角色
            messages: 消息列表
            assistant_message: 助手消息
            emit_events: 是否返回事件（用于流式输出）
            
        Returns:
            (结果内容, 事件列表)
        """
        events = []
        
        # 如果 assistant_message 中有思考内容，发送为 thinking_step
        thinking_content = assistant_message.get("content", "")
        if thinking_content and thinking_content.strip() and emit_events:
            events.append({
                "type": "thinking_step",
                "step_type": "planning",
                "content": thinking_content.strip()[:100] + "..." if len(thinking_content) > 100 else thinking_content.strip(),
                "role": role.id
            })
        
        messages.append(assistant_message)
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("function", {}).get("name", "")
            tool_args_str = tool_call.get("function", {}).get("arguments", "{}")
            tool_call_id = tool_call.get("id", "")
            
            logger.info(f"执行工具: {tool_name}, 参数: {tool_args_str}")
            
            # 发送工具调用事件
            if emit_events:
                events.append({
                    "type": "tool_call",
                    "tool_name": tool_name,
                    "tool_args": tool_args_str,
                    "role": role.id
                })
            
            try:
                tool_args = json.loads(tool_args_str)
            except json.JSONDecodeError:
                tool_args = {}
            
            tool = tool_registry.get(tool_name)
            if tool:
                try:
                    result = await tool.execute(**tool_args)
                    tool_result = json.dumps(result, ensure_ascii=False)
                    
                    # 发送工具结果事件
                    if emit_events:
                        events.append({
                            "type": "tool_result",
                            "tool_name": tool_name,
                            "content": f"工具 {tool_name} 执行完成",
                            "role": role.id
                        })
                except Exception as e:
                    logger.error(f"工具执行失败: {tool_name}, 错误: {e}")
                    tool_result = json.dumps({"error": str(e)}, ensure_ascii=False)
            else:
                logger.warning(f"工具不存在: {tool_name}")
                tool_result = json.dumps({"error": f"工具 {tool_name} 不存在"}, ensure_ascii=False)
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": tool_result
            })
        
        tools = tool_registry.get_schemas(role.tools)
        response = await self.llm_client.chat(
            messages=messages,
            tools=tools if tools else None,
            temperature=0.7
        )
        
        content, more_events = await self._process_llm_response_with_events(
            response, role, messages, emit_events
        )
        events.extend(more_events)
        
        return content, events
    
    async def _process_llm_response_with_events(
        self,
        response: dict,
        role: Role,
        messages: list[dict],
        emit_events: bool = False
    ) -> tuple[str, list[dict]]:
        """处理 LLM 响应，包括工具调用，返回事件"""
        choice = response.get("choices", [{}])[0]
        message = choice.get("message", {})
        tool_calls = message.get("tool_calls")
        
        if tool_calls:
            return await self._handle_tool_calls(
                tool_calls, role, messages, message, emit_events
            )
        else:
            return message.get("content", ""), []

    async def _process_discussion_mode(
        self,
        user_input: str,
        plan: ExecutionPlan,
        context: ConversationContext
    ) -> AsyncGenerator[dict, None]:
        """高级模式：多角色对话协商"""
        MAX_ROUNDS = 5
        discussion_history: list[dict] = []
        
        # 第一轮：每个角色给出初步分析
        for role in plan.roles:
            yield {
                "type": "role_start",
                "role": role.id,
                "name": role.name,
                "icon": role.icon
            }
            
            # _execute_role 返回 (content, events) 元组
            result_content, _ = await self._execute_role(role, user_input, context)
            context.role_results[role.id] = result_content
            
            discussion_history.append({
                "role": role.id,
                "name": role.name,
                "content": result_content
            })
            
            yield {
                "type": "role_result",
                "role": role.id,
                "content": result_content
            }
        
        # 后续轮次：角色间讨论
        for round_num in range(1, MAX_ROUNDS):
            consensus = await self._check_consensus(user_input, discussion_history)
            if consensus:
                logger.info(f"第 {round_num} 轮达成共识")
                break
            
            for role in plan.roles:
                discussion_content = await self._generate_discussion(
                    role, user_input, discussion_history
                )
                
                if discussion_content:
                    discussion_history.append({
                        "role": role.id,
                        "name": role.name,
                        "content": discussion_content
                    })
                    
                    yield {
                        "type": "discussion",
                        "from": role.id,
                        "name": role.name,
                        "content": discussion_content,
                        "round": round_num + 1
                    }
        
        # 最终由购房顾问总结
        yield {
            "type": "role_start",
            "role": PURCHASE_CONSULTANT.id,
            "name": PURCHASE_CONSULTANT.name,
            "icon": PURCHASE_CONSULTANT.icon
        }
        
        summary = await self._summarize_discussion(user_input, discussion_history)
        
        yield {
            "type": "role_result",
            "role": PURCHASE_CONSULTANT.id,
            "content": summary
        }
        
        context.add_message("assistant", summary)
    
    async def _check_consensus(
        self,
        user_input: str,
        discussion_history: list[dict]
    ) -> bool:
        """检查是否达成共识"""
        if len(discussion_history) < 2:
            return False
        
        history_text = "\n".join([
            f"【{item['name']}】{item['content']}"
            for item in discussion_history[-4:]
        ])
        
        prompt = f'用户问题：{user_input}\n\n最近的讨论内容：\n{history_text}\n\n请判断专家们是否已经达成共识？只回答"是"或"否"。'
        
        messages = [
            {"role": "system", "content": "你是一个讨论协调者，负责判断专家们是否已经达成共识。"},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm_client.chat(messages=messages, temperature=0.1)
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        return "是" in content
    
    async def _generate_discussion(
        self,
        role: Role,
        user_input: str,
        discussion_history: list[dict]
    ) -> str:
        """生成角色的讨论内容"""
        history_text = "\n".join([
            f"【{item['name']}】{item['content']}"
            for item in discussion_history
        ])
        
        system_content = (
            f"{role.system_prompt}\n\n"
            "你正在参与一个多专家讨论。请根据其他专家的意见，补充你的观点或提出不同看法。"
            '如果你认为已经充分表达了观点，无需补充，请回复"无补充"。'
        )
        user_content = (
            f"用户问题：{user_input}\n\n"
            f"讨论历史：\n{history_text}\n\n"
            '请补充你的观点（如无需补充请回复"无补充"）：'
        )
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]
        
        response = await self.llm_client.chat(messages=messages, temperature=0.7)
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if "无补充" in content:
            return ""
        return content
    
    async def _summarize_discussion(
        self,
        user_input: str,
        discussion_history: list[dict]
    ) -> str:
        """总结讨论结果"""
        history_text = "\n".join([
            f"【{item['name']}】{item['content']}"
            for item in discussion_history
        ])
        
        messages = [
            {"role": "system", "content": f"{PURCHASE_CONSULTANT.system_prompt}\n\n你需要总结以下专家讨论的结果，为用户提供最终的综合建议。"},
            {"role": "user", "content": f"用户问题：{user_input}\n\n专家讨论记录：\n{history_text}\n\n请总结讨论结果，给出最终建议："}
        ]
        
        response = await self.llm_client.chat(messages=messages, temperature=0.7)
        return response.get("choices", [{}])[0].get("message", {}).get("content", "")

    async def _load_context(self, session_id: str) -> ConversationContext:
        """从 Redis 加载对话上下文"""
        try:
            db = get_db()
            if db.redis:
                key = f"{self.CONTEXT_KEY_PREFIX}{session_id}"
                data = await db.redis.get(key)
                if data:
                    context_dict = json.loads(data)
                    logger.debug(f"从 Redis 加载上下文: {session_id}")
                    return ConversationContext.from_dict(context_dict)
        except Exception as e:
            logger.warning(f"加载上下文失败: {e}")
        
        logger.debug(f"创建新上下文: {session_id}")
        return ConversationContext(session_id=session_id)
    
    async def _save_context(self, context: ConversationContext) -> None:
        """保存对话上下文到 Redis"""
        try:
            db = get_db()
            if db.redis:
                key = f"{self.CONTEXT_KEY_PREFIX}{context.session_id}"
                data = json.dumps(context.to_dict(), ensure_ascii=False)
                await db.redis.setex(key, self.CONTEXT_TTL, data)
                logger.debug(f"保存上下文到 Redis: {context.session_id}")
        except Exception as e:
            logger.warning(f"保存上下文失败: {e}")
    
    async def clear_context(self, session_id: str) -> bool:
        """清除会话上下文"""
        try:
            db = get_db()
            if db.redis:
                key = f"{self.CONTEXT_KEY_PREFIX}{session_id}"
                await db.redis.delete(key)
                logger.info(f"清除上下文: {session_id}")
                return True
        except Exception as e:
            logger.warning(f"清除上下文失败: {e}")
        return False


# 全局 Agent 引擎实例
_agent_engine: AgentEngine | None = None


def get_agent_engine() -> AgentEngine:
    """获取全局 Agent 引擎实例"""
    global _agent_engine
    if _agent_engine is None:
        _agent_engine = AgentEngine()
    return _agent_engine
