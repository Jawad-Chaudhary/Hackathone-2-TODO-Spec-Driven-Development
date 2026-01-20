"""
User model for storing user information.

This model represents a user in the system. It's referenced by the
Conversation model for user isolation.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .conversation import Conversation


class User(SQLModel, table=True):
    """
    User model for persisting user information.

    Attributes:
        id: Unique user identifier (auto-increment integer)
        email: User's email address (unique)
        created_at: Timestamp when user was created
        conversations: Relationship to Conversation model (one-to-many)
    """

    __tablename__ = "users"

    id: str = Field(
        primary_key=True,
        nullable=False,
        max_length=255,
        description="Unique user identifier"
    )

    email: str = Field(
        unique=True,
        nullable=False,
        index=True,
        max_length=255,
        description="User's email address"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when user was created"
    )

    # Relationships
    conversations: List["Conversation"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
