"""
对话 API
处理用户消息并返回 Agent 响应
"""
import json
from typing import AsyncGenerator, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.engine import get_agent_engine
from app.db.database import get_async_session
from app.services.conversation import ConversationService
from app.utils.logger import get_logger

logger = get_logger("house_advisor.api.chat")

router = APIRouter(prefix="/chat", tags=["对话"])


class ChatRequest(BaseModel):
    """对话请求模型"""
    session_id: str = Field(..., description="会话 ID", min_length=1)
    message: str = Field(..., description="用户消息", min_length=1)
    mode: str = Field(default="standard", description="执行模式: standard 或 discussion")
    conversation_id: Optional[str] = Field(default=None, description="对话ID（用于持久化）")
    user_id: Optional[str] = Field(default=None, description="用户ID（可选）")


class ChatResponse(BaseModel):
    """对话响应模型（非流式）"""
    code: int = 0
    message: str = "success"
    data: dict | None = None


async def event_generator(
    session_id: str,
    user_message: str,
    mode: str,
    conversation_id: Optional[str] = None,
    user_id: Optional[str] = None,
    db_session: Optional[AsyncSession] = None
) -> AsyncGenerator[str, None]:
    """
    生成 Server-Sent Events 流
    
    Args:
        session_id: 会话 ID
        user_message: 用户消息
        mode: 执行模式
        conversation_id: 对话ID（用于持久化）
        user_id: 用户ID
        db_session: 数据库会话
        
    Yields:
        SSE 格式的事件字符串
    """
    engine = get_agent_engine()
    conv_service = None
    actual_conversation_id = conversation_id
    
    # 初始化对话持久化服务
    if db_session:
        try:
            conv_service = ConversationService(db_session)
            
            # 如果没有 conversation_id，创建新对话
            if not actual_conversation_id:
                # 用用户消息前30个字符作为标题
                title = user_message[:30] + ("..." if len(user_message) > 30 else "")
                conversation = await conv_service.create_conversation(
                    user_id=user_id,
                    title=title
                )
                actual_conversation_id = str(conversation.id)
                
                # 发送对话创建事件（包含标题）
                yield f"data: {json.dumps({'type': 'conversation_created', 'conversation_id': actual_conversation_id, 'title': title}, ensure_ascii=False)}\n\n"
            
            # 保存用户消息
            await conv_service.add_message(
                conversation_id=actual_conversation_id,
                role="user",
                content=user_message
            )
        except Exception as e:
            logger.warning(f"对话持久化初始化失败: {e}")
            conv_service = None
    
    # 收集完整的 AI 回复
    full_response = ""
    role_results = {}
    
    try:
        async for event in engine.process(user_message, session_id, mode):
            # 收集角色结果用于持久化
            if event.get("type") == "role_result":
                role_id = event.get("role", "")
                content = event.get("content", "")
                role_results[role_id] = content
                full_response = content  # 最后一个角色的结果作为完整回复
            
            # 将事件转换为 SSE 格式
            event_data = json.dumps(event, ensure_ascii=False)
            yield f"data: {event_data}\n\n"
        
        # 保存 AI 回复到数据库
        if conv_service and actual_conversation_id and full_response:
            try:
                await conv_service.add_message(
                    conversation_id=actual_conversation_id,
                    role="assistant",
                    content=full_response,
                    metadata={"role_results": role_results, "mode": mode}
                )
            except Exception as e:
                logger.warning(f"保存 AI 回复失败: {e}")
            
    except Exception as e:
        logger.exception(f"处理对话时发生错误: {e}")
        error_event = {
            "type": "error",
            "code": 1099,
            "message": "服务暂时不可用，请稍后重试"
        }
        yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"


@router.post("", summary="发送对话消息")
async def chat(
    request: ChatRequest,
    db_session: AsyncSession = Depends(get_async_session)
):
    """
    发送对话消息，返回流式响应
    
    使用 Server-Sent Events 返回以下事件类型：
    - conversation_created: 新对话创建，包含 conversation_id
    - role_start: 角色开始处理，包含 role、name、icon
    - role_result: 角色处理结果，包含 role、content
    - discussion: 讨论事件（高级模式），包含 from、name、content、round
    - error: 错误事件，包含 code、message
    - done: 处理完成
    """
    logger.info(f"收到对话请求: session={request.session_id}, mode={request.mode}, conversation_id={request.conversation_id}")
    
    # 验证 mode 参数
    if request.mode not in ("standard", "discussion"):
        raise HTTPException(
            status_code=400,
            detail={
                "code": 3002,
                "message": "参数类型错误：mode 必须是 standard 或 discussion"
            }
        )
    
    return StreamingResponse(
        event_generator(
            request.session_id, 
            request.message, 
            request.mode,
            request.conversation_id,
            request.user_id,
            db_session
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用 nginx 缓冲
        }
    )


@router.delete("/{session_id}", summary="清除会话")
async def clear_session(session_id: str):
    """
    清除指定会话的上下文
    
    Args:
        session_id: 会话 ID
        
    Returns:
        操作结果
    """
    logger.info(f"清除会话: {session_id}")
    
    engine = get_agent_engine()
    success = await engine.clear_context(session_id)
    
    if success:
        return {
            "code": 0,
            "message": "success",
            "data": {"session_id": session_id}
        }
    else:
        return {
            "code": 0,
            "message": "会话不存在或已过期",
            "data": {"session_id": session_id}
        }
