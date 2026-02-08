# [Task T014] Task SQLModel with Phase 5 advanced fields

from datetime import datetime
from typing import Optional
from enum import Enum
from sqlmodel import Field, SQLModel, Index, Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String


class PriorityEnum(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecurrenceEnum(str, Enum):
    """Task recurrence patterns."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class Task(SQLModel, table=True):
    """
    Task model representing a user's todo item with Phase 5 advanced features.
    Indexed on user_id, completed, created_at, due_date, priority, and tags for efficient queries.
    """

    __tablename__ = "tasks"
    __table_args__ = (
        Index("idx_tasks_user_id", "user_id"),
        Index("idx_tasks_user_completed", "user_id", "completed"),
        Index("idx_tasks_created_at", "created_at"),
        Index("idx_task_due_date", "due_date"),
        Index("idx_task_priority", "priority"),
        Index("idx_task_user_status", "user_id", "completed"),
    )

    # Basic fields
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(nullable=False, index=True, max_length=255)
    title: str = Field(nullable=False, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Phase 5 advanced fields
    # Store enums as VARCHAR to match database schema and avoid type casting issues
    priority: Optional[str] = Field(default=None, sa_column=Column(String(10)))
    tags: Optional[list] = Field(default=None, sa_column=Column(JSONB))
    due_date: Optional[datetime] = Field(default=None)
    recurrence: Optional[str] = Field(default=None, sa_column=Column(String(10)))
    recurrence_interval: Optional[int] = Field(default=None)
    parent_task_id: Optional[int] = Field(default=None)
