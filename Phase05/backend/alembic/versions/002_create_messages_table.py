"""create messages table

Revision ID: 002
Revises: 001
Create Date: 2026-01-19 09:26:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create messages table with indexes and constraints."""
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(
            ['conversation_id'],
            ['conversations.id'],
            name='fk_messages_conversation_id',
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name='pk_messages'),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_message_role'),
        sa.CheckConstraint("length(content) > 0", name='check_message_content_not_empty')
    )

    # Create index on conversation_id for fast message lookups by conversation
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])

    # Create index on created_at for chronological message ordering
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])

    # Create composite index for efficient conversation message retrieval
    op.create_index(
        'ix_messages_conversation_created',
        'messages',
        ['conversation_id', 'created_at']
    )


def downgrade() -> None:
    """Drop messages table and indexes."""
    # Drop indexes
    op.drop_index('ix_messages_conversation_created', table_name='messages')
    op.drop_index('ix_messages_created_at', table_name='messages')
    op.drop_index('ix_messages_conversation_id', table_name='messages')

    # Drop table
    op.drop_table('messages')
