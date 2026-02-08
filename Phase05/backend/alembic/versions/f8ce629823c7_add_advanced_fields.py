"""add_advanced_fields

Revision ID: f8ce629823c7
Revises: 6d4862870882
Create Date: 2026-01-22 19:54:08.466658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8ce629823c7'
down_revision: Union[str, Sequence[str], None] = '6d4862870882'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns for Phase 5 advanced features
    op.add_column('tasks', sa.Column('priority', sa.String(length=10), nullable=True))
    op.add_column('tasks', sa.Column('tags', sa.dialects.postgresql.JSONB(), nullable=True))
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('recurrence', sa.String(length=10), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_interval', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('parent_task_id', sa.Integer(), nullable=True))

    # Create indexes for performance
    op.create_index('idx_task_due_date', 'tasks', ['due_date'])
    op.create_index('idx_task_priority', 'tasks', ['priority'])
    # GIN index for tags (PostgreSQL-specific for JSON array search) with jsonb_path_ops
    op.execute('CREATE INDEX IF NOT EXISTS idx_task_tags_gin ON tasks USING gin (tags jsonb_path_ops)')
    op.create_index('idx_task_user_status', 'tasks', ['user_id', 'completed'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_task_user_status', table_name='tasks')
    op.execute('DROP INDEX IF EXISTS idx_task_tags_gin')
    op.drop_index('idx_task_priority', table_name='tasks')
    op.drop_index('idx_task_due_date', table_name='tasks')

    # Drop columns
    op.drop_column('tasks', 'parent_task_id')
    op.drop_column('tasks', 'recurrence_interval')
    op.drop_column('tasks', 'recurrence')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'priority')
