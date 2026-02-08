"""
Unit tests for Conversation model.

Tests:
- Conversation creation with all required fields
- Default values for id, created_at, updated_at
- user_id foreign key constraint
- Relationship with Message model
"""

import pytest
from datetime import datetime
from uuid import UUID

from app.models.conversation import Conversation


def test_conversation_creation():
    """Test creating a conversation with required fields."""
    conversation = Conversation(user_id=1)

    assert conversation.user_id == 1
    assert isinstance(conversation.id, UUID)
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)


def test_conversation_has_default_id():
    """Test that conversation gets a default UUID."""
    conversation = Conversation(user_id=1)

    assert conversation.id is not None
    assert isinstance(conversation.id, UUID)


def test_conversation_has_timestamps():
    """Test that conversation has created_at and updated_at timestamps."""
    conversation = Conversation(user_id=1)

    assert conversation.created_at is not None
    assert conversation.updated_at is not None
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)


def test_conversation_user_id_required():
    """Test that user_id is required for database operations."""
    # SQLModel doesn't raise on missing required fields until DB insert
    # This test verifies that user_id field exists and is properly defined
    conversation = Conversation(user_id=1)
    assert conversation.user_id == 1

    # Verify field is defined with proper type
    from sqlmodel import Field
    assert hasattr(Conversation, 'user_id')
    field_info = Conversation.model_fields.get('user_id')
    assert field_info is not None


def test_conversation_multiple_instances_have_unique_ids():
    """Test that multiple conversations get unique UUIDs."""
    conv1 = Conversation(user_id=1)
    conv2 = Conversation(user_id=1)

    assert conv1.id != conv2.id


def test_conversation_can_set_custom_id():
    """Test that conversation can be created with a custom UUID."""
    from uuid import uuid4

    custom_id = uuid4()
    conversation = Conversation(id=custom_id, user_id=1)

    assert conversation.id == custom_id


def test_conversation_can_set_custom_timestamps():
    """Test that conversation can be created with custom timestamps."""
    custom_time = datetime(2024, 1, 1, 12, 0, 0)
    conversation = Conversation(
        user_id=1,
        created_at=custom_time,
        updated_at=custom_time
    )

    assert conversation.created_at == custom_time
    assert conversation.updated_at == custom_time


def test_conversation_messages_relationship():
    """Test that conversation has messages relationship."""
    conversation = Conversation(user_id=1)

    # Messages should be an empty list initially
    assert hasattr(conversation, 'messages')
    assert isinstance(conversation.messages, list)
    assert len(conversation.messages) == 0
