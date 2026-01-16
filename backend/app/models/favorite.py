"""
收藏模型
存储用户收藏的问答对
"""
from sqlalchemy import Column, String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class Favorite(Base, TimestampMixin):
    """收藏表"""
    
    __tablename__ = "favorites"
    __table_args__ = (
        # 复合索引：按用户ID和创建时间查询
        Index("idx_favorites_user_created", "user_id", "created_at"),
        {"comment": "收藏表"}
    )
    
    # 主键
    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        default=generate_uuid,
        comment="收藏ID"
    )
    
    # 外键：关联用户
    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID"
    )
    
    # 关联的消息ID（可选，用于跳转）
    message_id = Column(
        UUID(as_uuid=False),
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
        comment="关联消息ID"
    )
    
    # 关联的对话ID（用于跳转）
    conversation_id = Column(
        UUID(as_uuid=False),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        comment="关联对话ID"
    )
    
    # 问题内容（用户消息摘要）
    question = Column(
        String(500),
        nullable=False,
        comment="问题摘要"
    )
    
    # 回答内容（完整的 AI 回复）
    answer = Column(
        Text,
        nullable=False,
        comment="完整回答"
    )
    
    # 元数据：存储额外信息
    extra_data = Column(
        "metadata",
        JSONB,
        nullable=True,
        default=dict,
        comment="元数据"
    )
    
    # 关系
    user = relationship("User", back_populates="favorites")
    message = relationship("Message")
    conversation = relationship("Conversation")
    
    def __repr__(self):
        question_preview = self.question[:30] + "..." if len(self.question) > 30 else self.question
        return f"<Favorite(id={self.id}, question={question_preview})>"
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "question": self.question,
            "answer": self.answer,
            "metadata": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
