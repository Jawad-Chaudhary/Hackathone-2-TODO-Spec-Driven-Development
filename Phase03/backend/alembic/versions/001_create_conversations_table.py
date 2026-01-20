"""create conversations table

Revision ID: 001
Revises:
Create Date: 2026-01-19 09:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = '000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create conversations table with indexes and trigger."""
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_conversations_user_id'),
        sa.PrimaryKeyConstraint('id', name='pk_conversations')
    )

    # Create index on user_id for fast user conversation lookups
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])

    # Create index on updated_at for sorting recent conversations
    op.create_index('ix_conversations_updated_at', 'conversations', ['updated_at'])

    # Create trigger to auto-update updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_conversations_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trigger_update_conversations_updated_at
        BEFORE UPDATE ON conversations
        FOR EACH ROW
        EXECUTE FUNCTION update_conversations_updated_at();
    """)


def downgrade() -> None:
    """Drop conversations table, indexes, and trigger."""
    # Drop trigger and function
    op.execute("DROP TRIGGER IF EXISTS trigger_update_conversations_updated_at ON conversations")
    op.execute("DROP FUNCTION IF EXISTS update_conversations_updated_at()")

    # Drop indexes
    op.drop_index('ix_conversations_updated_at', table_name='conversations')
    op.drop_index('ix_conversations_user_id', table_name='conversations')

    # Drop table
    op.drop_table('conversations')
