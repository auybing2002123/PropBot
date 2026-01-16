"""
SQLAlchemy ORM 基类
定义所有数据库模型的公共基类
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

# 声明式基类
Base = declarative_base()


class TimestampMixin:
    """时间戳混入类，提供 created_at 和 updated_at 字段"""
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="更新时间"
    )


def generate_uuid():
    """生成 UUID"""
    return str(uuid.uuid4())
