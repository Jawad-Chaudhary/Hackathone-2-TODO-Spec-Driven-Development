# [Task]: T-008
# [From]: specs/001-ai-todo-chatbot/plan.md

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Enum as SAEnum
from datetime import datetime
from typing import Optional
from enum import Enum


class MessageRole(str, Enum):
    """Enum for message roles in conversation."""
    user = "user"
    assistant = "assistant"


class Message(SQLModel, table=True):
    """
    Message model representing a single message in a conversation.

    Fields:
        id: Primary key, auto-incremented
        user_id: Indexed string for user isolation (max 255 chars)
        conversation_id: Foreign key to conversations table
        role: Message role enum ("user" | "assistant")
        content: Message content text
        created_at: Timestamp of message creation
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    conversation_id: int = Field(foreign_key="conversations.id")
    role: MessageRole = Field(sa_column=Column(SAEnum(MessageRole), nullable=False))
    content: str = Field()
    created_at: datetime = Field(default_factory=datetime.utcnow)
