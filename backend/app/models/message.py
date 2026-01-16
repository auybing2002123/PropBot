"""
消息模型
存储对话中的每条消息
"""
from sqlalchemy import Column, String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class Message(Base, TimestampMixin):
    """消息表"""
    
    __tablename__ = "messages"
    __table_args__ = (
        # 复合索引：按对话ID和创建时间查询
        Index("idx_messages_conversation_created", "conversation_id", "created_at"),
        {"comment": "消息表"}
    )
    
    # 主键
    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        default=generate_uuid,
        comment="消息ID"
    )
    
    # 外键：关联对话
    conversation_id = Column(
        UUID(as_uuid=False),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="对话ID"
    )
    
    # 消息角色：user / assistant / system
    role = Column(
        String(20),
        nullable=False,
        comment="消息角色"
    )
    
    # 消息内容
    content = Column(
        Text,
        nullable=False,
        comment="消息内容"
    )
    
    # 元数据：存储工具调用结果、角色信息等（使用 extra_data 避免与 SQLAlchemy 保留字冲突）
    extra_data = Column(
        "metadata",  # 数据库列名仍为 metadata
        JSONB,
        nullable=True,
        default=dict,
        comment="元数据（工具调用、角色信息等）"
    )
    
    # 关系
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        content_preview = self.content[:30] + "..." if len(self.content) > 30 else self.content
        return f"<Message(id={self.id}, role={self.role}, content={content_preview})>"
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "metadata": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
