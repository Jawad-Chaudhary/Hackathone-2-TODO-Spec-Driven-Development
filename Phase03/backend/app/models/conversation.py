"""
Conversation model for storing chat conversation metadata.

This model represents a chat conversation between a user and the AI agent.
Each conversation belongs to a single user and contains multiple messages.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .message import Message
    from .user import User


class Conversation(SQLModel, table=True):
    """
    Conversation model for persisting chat conversations.

    Attributes:
        id: Unique conversation identifier (UUID)
        user_id: Foreign key to users table
        created_at: Timestamp when conversation was created
        updated_at: Timestamp when conversation was last updated
        messages: Relationship to Message model (one-to-many)
    """

    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique conversation identifier"
    )

    user_id: str = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User who owns this conversation"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when conversation was created"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when conversation was last updated"
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    user: "User" = Relationship(back_populates="conversations")
