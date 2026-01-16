"""
用户模型
用户表，支持用户名密码登录
"""
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class User(Base, TimestampMixin):
    """用户表"""
    
    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}
    
    # 主键
    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        default=generate_uuid,
        comment="用户ID"
    )
    
    # 用户名（唯一，用于登录）
    username = Column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
        comment="用户名"
    )
    
    # 密码哈希
    password_hash = Column(
        String(128),
        nullable=True,
        comment="密码哈希"
    )
    
    # 用户昵称（显示名称）
    nickname = Column(
        String(50),
        nullable=True,
        comment="用户昵称"
    )
    
    # 关系：一个用户有多个对话
    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # 关系：一个用户有多个收藏
    favorites = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, nickname={self.nickname})>"
