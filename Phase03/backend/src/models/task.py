# [Task]: T-006
# [From]: specs/001-ai-todo-chatbot/plan.md

from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional


class Task(SQLModel, table=True):
    """
    Task model representing a user's todo item.

    Fields:
        id: Primary key, auto-incremented
        user_id: Indexed string for user isolation (max 255 chars)
        title: Task title (1-200 chars, required)
        description: Optional task description (max 1000 chars)
        completed: Boolean flag indicating completion status (default: False)
        created_at: Timestamp of task creation
        updated_at: Timestamp of last update
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
