# [Task]: T-007
# [From]: specs/001-ai-todo-chatbot/plan.md

from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a chat session between user and AI.

    Fields:
        id: Primary key, auto-incremented
        user_id: Indexed string for user isolation (max 255 chars)
        created_at: Timestamp of conversation creation
        updated_at: Timestamp of last message in conversation
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
