# [Task]: Authentication Implementation
# [From]: Phase II - Better Auth + JWT Integration

"""
User Model for Authentication

Stores user credentials and profile information for JWT-based authentication.
Password is hashed using bcrypt before storage.
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class User(SQLModel, table=True):
    """
    User model for authentication and profile management.

    Attributes:
        id: Auto-incrementing primary key
        email: Unique email address for login
        password_hash: Bcrypt-hashed password (never store plaintext)
        full_name: Optional user's full name
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """SQLModel configuration"""
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe"
            }
        }
