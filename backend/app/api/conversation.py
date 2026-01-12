"""
对话历史 API
提供对话的增删改查接口
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.conversation import ConversationService
from app.utils.logger import get_logger

logger = get_logger("house_advisor.api.conversation")

router = APIRouter(prefix="/conversations", tags=["对话历史"])


# ==================== 请求/响应模型 ====================

class CreateConversationRequest(BaseModel):
    """创建对话请求"""
    user_id: Optional[str] = Field(None, description="用户ID（可选）")
    title: Optional[str] = Field(None, description="对话标题（可选）")


class UpdateConversationRequest(BaseModel):
    """更新对话请求"""
    title: str = Field(..., description="对话标题")


class MessageResponse(BaseModel):
    """消息响应"""
    id: str
    role: str
    content: str
    metadata: Optional[dict] = None
    created_at: str


class ConversationResponse(BaseModel):
    """对话响应"""
    id: str
    user_id: Optional[str] = None
    title: Optional[str] = None
    created_at: str
    updated_at: str


class ConversationDetailResponse(BaseModel):
    """对话详情响应（含消息）"""
    id: str
    user_id: Optional[str] = None
    title: Optional[str] = None
    created_at: str
    updated_at: str
    messages: list[MessageResponse] = []


class ApiResponse(BaseModel):
    """统一响应格式"""
    code: int = 0
    message: str = "success"
    data: Optional[dict] = None


# ==================== 依赖注入 ====================

async def get_session():
    """获取数据库会话"""
    db = get_db()
    async with db.async_session() as session:
        yield session


async def get_conversation_service(
    session: AsyncSession = Depends(get_session)
) -> ConversationService:
    """获取对话服务"""
    return ConversationService(session)


# ==================== API 端点 ====================

@router.get("", response_model=ApiResponse)
async def list_conversations(
    user_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    service: ConversationService = Depends(get_conversation_service)
):
    """
    获取对话列表
    
    - user_id: 用户ID（可选，为空获取匿名对话）
    - limit: 返回数量（默认20）
    - offset: 偏移量（默认0）
    """
    conversations = await service.list_conversations(
        user_id=user_id,
        limit=limit,
        offset=offset
    )
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "conversations": [
                {
                    "id": c.id,
                    "user_id": c.user_id,
                    "title": c.title,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None
                }
                for c in conversations
            ],
            "total": len(conversations)
        }
    }


@router.post("", response_model=ApiResponse)
async def create_conversation(
    request: CreateConversationRequest,
    service: ConversationService = Depends(get_conversation_service)
):
    """
    创建新对话
    
    - user_id: 用户ID（可选）
    - title: 对话标题（可选）
    """
    conversation = await service.create_conversation(
        user_id=request.user_id,
        title=request.title
    )
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None
        }
    }


@router.get("/{conversation_id}", response_model=ApiResponse)
async def get_conversation(
    conversation_id: str,
    include_messages: bool = True,
    service: ConversationService = Depends(get_conversation_service)
):
    """
    获取对话详情
    
    - conversation_id: 对话ID
    - include_messages: 是否包含消息列表（默认true）
    """
    conversation = await service.get_conversation(
        conversation_id=conversation_id,
        include_messages=include_messages
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    data = {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
        "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None
    }
    
    if include_messages:
        data["messages"] = [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "metadata": m.extra_data,
                "created_at": m.created_at.isoformat() if m.created_at else None
            }
            for m in conversation.messages
        ]
    
    return {
        "code": 0,
        "message": "success",
        "data": data
    }


@router.put("/{conversation_id}", response_model=ApiResponse)
async def update_conversation(
    conversation_id: str,
    request: UpdateConversationRequest,
    service: ConversationService = Depends(get_conversation_service)
):
    """
    更新对话标题
    
    - conversation_id: 对话ID
    - title: 新标题
    """
    conversation = await service.update_conversation_title(
        conversation_id=conversation_id,
        title=request.title
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "id": conversation.id,
            "title": conversation.title,
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None
        }
    }


@router.delete("/{conversation_id}", response_model=ApiResponse)
async def delete_conversation(
    conversation_id: str,
    service: ConversationService = Depends(get_conversation_service)
):
    """
    删除对话（级联删除消息）
    
    - conversation_id: 对话ID
    """
    deleted = await service.delete_conversation(conversation_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    return {
        "code": 0,
        "message": "success",
        "data": {"deleted": True}
    }


@router.get("/{conversation_id}/messages", response_model=ApiResponse)
async def get_messages(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0,
    service: ConversationService = Depends(get_conversation_service)
):
    """
    获取对话的消息列表
    
    - conversation_id: 对话ID
    - limit: 返回数量（默认50）
    - offset: 偏移量（默认0）
    """
    # 先检查对话是否存在
    conversation = await service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    messages = await service.get_messages(
        conversation_id=conversation_id,
        limit=limit,
        offset=offset
    )
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "metadata": m.extra_data,
                    "created_at": m.created_at.isoformat() if m.created_at else None
                }
                for m in messages
            ],
            "total": len(messages)
        }
    }
