"""
对话历史服务
提供对话和消息的 CRUD 操作
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger("house_advisor.services.conversation")


class ConversationService:
    """对话历史服务类"""
    
    def __init__(self, session: AsyncSession):
        """
        初始化服务
        
        Args:
            session: 异步数据库会话
        """
        self.session = session
    
    # ==================== 对话操作 ====================
    
    async def create_conversation(
        self,
        user_id: Optional[str] = None,
        title: Optional[str] = None
    ) -> Conversation:
        """
        创建新对话
        
        Args:
            user_id: 用户ID（可选，支持匿名对话）
            title: 对话标题（可选）
        
        Returns:
            创建的对话对象
        """
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        
        logger.info(f"创建对话: id={conversation.id}, user_id={user_id}")
        return conversation
    
    async def get_conversation(
        self,
        conversation_id: str,
        include_messages: bool = False
    ) -> Optional[Conversation]:
        """
        获取对话详情
        
        Args:
            conversation_id: 对话ID
            include_messages: 是否包含消息列表
        
        Returns:
            对话对象，不存在返回 None
        """
        query = select(Conversation).where(Conversation.id == conversation_id)
        
        if include_messages:
            query = query.options(selectinload(Conversation.messages))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def list_conversations(
        self,
        user_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[Conversation]:
        """
        获取对话列表
        
        Args:
            user_id: 用户ID（可选，为空则获取所有匿名对话）
            limit: 返回数量限制
            offset: 偏移量
        
        Returns:
            对话列表
        """
        query = select(Conversation).order_by(Conversation.updated_at.desc())
        
        if user_id:
            query = query.where(Conversation.user_id == user_id)
        else:
            # 匿名对话
            query = query.where(Conversation.user_id.is_(None))
        
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_conversation_title(
        self,
        conversation_id: str,
        title: str
    ) -> Optional[Conversation]:
        """
        更新对话标题
        
        Args:
            conversation_id: 对话ID
            title: 新标题
        
        Returns:
            更新后的对话对象
        """
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(conversation)
            logger.info(f"更新对话标题: id={conversation_id}, title={title}")
        return conversation
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        删除对话（级联删除消息）
        
        Args:
            conversation_id: 对话ID
        
        Returns:
            是否删除成功
        """
        result = await self.session.execute(
            delete(Conversation).where(Conversation.id == conversation_id)
        )
        await self.session.commit()
        
        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"删除对话: id={conversation_id}")
        return deleted
    
    # ==================== 消息操作 ====================
    
    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> Message:
        """
        添加消息到对话
        
        Args:
            conversation_id: 对话ID
            role: 消息角色（user/assistant/system）
            content: 消息内容
            metadata: 元数据（工具调用结果等）
        
        Returns:
            创建的消息对象
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            extra_data=metadata or {}
        )
        self.session.add(message)
        
        # 更新对话的 updated_at
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            
            # 如果是第一条用户消息且没有标题，自动设置标题
            if role == "user" and not conversation.title:
                # 取前30个字符作为标题
                conversation.title = content[:30] + ("..." if len(content) > 30 else "")
        
        await self.session.commit()
        await self.session.refresh(message)
        
        logger.debug(f"添加消息: conversation_id={conversation_id}, role={role}")
        return message
    
    async def get_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> list[Message]:
        """
        获取对话的消息列表
        
        Args:
            conversation_id: 对话ID
            limit: 返回数量限制
            offset: 偏移量
        
        Returns:
            消息列表（按时间正序）
        """
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_recent_messages(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> list[Message]:
        """
        获取最近的消息（用于构建上下文）
        
        Args:
            conversation_id: 对话ID
            limit: 返回数量
        
        Returns:
            消息列表（按时间正序）
        """
        # 先获取最近的消息（倒序）
        subquery = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .subquery()
        )
        
        # 再按正序返回
        query = select(Message).from_statement(
            select(subquery).order_by(subquery.c.created_at.asc())
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_messages(self, conversation_id: str) -> int:
        """
        统计对话的消息数量
        
        Args:
            conversation_id: 对话ID
        
        Returns:
            消息数量
        """
        query = (
            select(func.count(Message.id))
            .where(Message.conversation_id == conversation_id)
        )
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    # ==================== 用户操作 ====================
    
    async def get_or_create_user(
        self,
        user_id: Optional[str] = None,
        nickname: Optional[str] = None
    ) -> User:
        """
        获取或创建用户
        
        Args:
            user_id: 用户ID（可选，为空则创建新用户）
            nickname: 用户昵称
        
        Returns:
            用户对象
        """
        if user_id:
            query = select(User).where(User.id == user_id)
            result = await self.session.execute(query)
            user = result.scalar_one_or_none()
            if user:
                return user
        
        # 创建新用户
        user = User(nickname=nickname)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
        logger.info(f"创建用户: id={user.id}, nickname={nickname}")
        return user
