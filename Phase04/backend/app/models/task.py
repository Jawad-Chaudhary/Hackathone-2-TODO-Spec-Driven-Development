# [Task T011] Task SQLModel with indexes

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Index


class Task(SQLModel, table=True):
    """
    Task model representing a user's todo item.
    Indexed on user_id, completed, and created_at for efficient queries.
    """

    __tablename__ = "tasks"
    __table_args__ = (
        Index("idx_tasks_user_id", "user_id"),
        Index("idx_tasks_user_completed", "user_id", "completed"),
        Index("idx_tasks_created_at", "created_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(nullable=False, index=True, max_length=255)
    title: str = Field(nullable=False, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
