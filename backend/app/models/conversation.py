"""
对话会话模型
存储用户与 AI 的对话会话
"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class Conversation(Base, TimestampMixin):
    """对话会话表"""
    
    __tablename__ = "conversations"
    __table_args__ = {"comment": "对话会话表"}
    
    # 主键
    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        default=generate_uuid,
        comment="对话ID"
    )
    
    # 外键：关联用户（可选，支持匿名对话）
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="用户ID"
    )
    
    # 对话标题（取首条消息摘要）
    title = Column(
        String(200),
        nullable=True,
        comment="对话标题"
    )
    
    # 关系
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title})>"
