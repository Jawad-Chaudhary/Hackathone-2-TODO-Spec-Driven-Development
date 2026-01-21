"""
Message model for storing individual messages within conversations.

This model represents a single message (user or assistant) within a conversation.
Messages are ordered by created_at and include support for tool calls.
"""

from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import Text, JSON

if TYPE_CHECKING:
    from .conversation import Conversation


class Message(SQLModel, table=True):
    """
    Message model for persisting chat messages.

    Attributes:
        id: Unique message identifier (UUID)
        conversation_id: Foreign key to conversations table
        role: Message role ('user' or 'assistant')
        content: Message text content
        tool_calls: Optional JSON data for tool calls made by assistant
        created_at: Timestamp when message was created
        conversation: Relationship to Conversation model (many-to-one)
    """

    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique message identifier"
    )

    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        description="Conversation this message belongs to"
    )

    role: str = Field(
        nullable=False,
        description="Message role: 'user' or 'assistant'",
        max_length=20
    )

    content: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Message text content"
    )

    tool_calls: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
        description="Tool calls made by assistant (JSON format)"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Timestamp when message was created"
    )

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")

    def __init__(self, **data):
        """
        Initialize message with validation.

        Validates that:
        - role is either 'user' or 'assistant'
        - content is not empty (unless tool_calls are present for assistant)
        """
        super().__init__(**data)

        # Validate role
        if self.role not in ['user', 'assistant']:
            raise ValueError(f"Invalid role: {self.role}. Must be 'user' or 'assistant'")

        # Validate content
        # Allow empty content for assistant messages with tool_calls
        if not self.content or len(self.content.strip()) == 0:
            if not (self.role == 'assistant' and self.tool_calls):
                raise ValueError("Message content cannot be empty")
