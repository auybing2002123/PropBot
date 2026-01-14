"""添加收藏表

Revision ID: 004_favorites
Revises: 769d9b38ea93
Create Date: 2026-01-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_favorites'
down_revision: Union[str, None] = '769d9b38ea93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建收藏表
    op.create_table(
        'favorites',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, comment='收藏ID'),
        sa.Column('user_id', postgresql.UUID(as_uuid=False), nullable=False, comment='用户ID'),
        sa.Column('message_id', postgresql.UUID(as_uuid=False), nullable=True, comment='关联消息ID'),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=False), nullable=True, comment='关联对话ID'),
        sa.Column('question', sa.String(500), nullable=False, comment='问题摘要'),
        sa.Column('answer', sa.Text(), nullable=False, comment='完整回答'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='元数据'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='收藏表'
    )
    
    # 创建索引
    op.create_index('idx_favorites_user_id', 'favorites', ['user_id'])
    op.create_index('idx_favorites_user_created', 'favorites', ['user_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('idx_favorites_user_created', table_name='favorites')
    op.drop_index('idx_favorites_user_id', table_name='favorites')
    op.drop_table('favorites')
