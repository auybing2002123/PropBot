"""初始化数据库表结构

Revision ID: 001
Revises: 
Create Date: 2026-01-11

创建用户表、对话表、消息表
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建用户表
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='用户ID'),
        sa.Column('nickname', sa.String(50), nullable=True, comment='用户昵称'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='用户表'
    )
    
    # 创建对话表
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='对话ID'),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=True, comment='用户ID'),
        sa.Column('title', sa.String(200), nullable=True, comment='对话标题'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='对话会话表'
    )
    # 对话表索引
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_updated_at', 'conversations', ['updated_at'])
    
    # 创建消息表
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='消息ID'),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=False), nullable=False, comment='对话ID'),
        sa.Column('role', sa.String(20), nullable=False, comment='消息角色'),
        sa.Column('content', sa.Text(), nullable=False, comment='消息内容'),
        sa.Column('metadata', postgresql.JSONB(), nullable=True, comment='元数据（工具调用、角色信息等）'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='消息表'
    )
    # 消息表索引
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])


def downgrade() -> None:
    # 删除消息表
    op.drop_index('idx_messages_conversation_created', table_name='messages')
    op.drop_index('idx_messages_conversation_id', table_name='messages')
    op.drop_table('messages')
    
    # 删除对话表
    op.drop_index('idx_conversations_updated_at', table_name='conversations')
    op.drop_index('idx_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
    
    # 删除用户表
    op.drop_table('users')
