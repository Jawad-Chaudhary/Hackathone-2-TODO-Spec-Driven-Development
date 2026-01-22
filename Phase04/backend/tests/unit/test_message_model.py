"""
Unit tests for Message model.

Tests:
- Message creation with all required fields
- Default values for id, created_at
- Role validation ('user' or 'assistant' only)
- Content validation (non-empty)
- Tool calls JSON field
- Relationship with Conversation model
"""

import pytest
from datetime import datetime
from uuid import UUID, uuid4

from app.models.message import Message


def test_message_creation_with_user_role():
    """Test creating a message with user role."""
    conversation_id = uuid4()
    message = Message(
        conversation_id=conversation_id,
        role="user",
        content="Hello, world!"
    )

    assert message.conversation_id == conversation_id
    assert message.role == "user"
    assert message.content == "Hello, world!"
    assert isinstance(message.id, UUID)
    assert isinstance(message.created_at, datetime)
    assert message.tool_calls is None


def test_message_creation_with_assistant_role():
    """Test creating a message with assistant role."""
    conversation_id = uuid4()
    message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content="Hello! How can I help you?"
    )

    assert message.role == "assistant"
    assert message.content == "Hello! How can I help you?"


def test_message_has_default_id():
    """Test that message gets a default UUID."""
    conversation_id = uuid4()
    message = Message(
        conversation_id=conversation_id,
        role="user",
        content="Test"
    )

    assert message.id is not None
    assert isinstance(message.id, UUID)


def test_message_has_timestamp():
    """Test that message has created_at timestamp."""
    conversation_id = uuid4()
    message = Message(
        conversation_id=conversation_id,
        role="user",
        content="Test"
    )

    assert message.created_at is not None
    assert isinstance(message.created_at, datetime)


def test_message_role_validation_invalid():
    """Test that invalid role raises ValueError."""
    conversation_id = uuid4()

    with pytest.raises(ValueError, match="Invalid role"):
        Message(
            conversation_id=conversation_id,
            role="invalid",
            content="Test"
        )


def test_message_role_validation_empty():
    """Test that empty role raises ValueError."""
    conversation_id = uuid4()

    with pytest.raises(ValueError, match="Invalid role"):
        Message(
            conversation_id=conversation_id,
            role="",
            content="Test"
        )


def test_message_content_validation_empty():
    """Test that empty content raises ValueError."""
    conversation_id = uuid4()

    with pytest.raises(ValueError, match="content cannot be empty"):
        Message(
            conversation_id=conversation_id,
            role="user",
            content=""
        )


def test_message_content_validation_whitespace():
    """Test that whitespace-only content raises ValueError."""
    conversation_id = uuid4()

    with pytest.raises(ValueError, match="content cannot be empty"):
        Message(
            conversation_id=conversation_id,
            role="user",
            content="   "
        )


def test_message_required_fields():
    """Test that conversation_id, role, and content are required and validated."""
    # Creating a message without required fields will fail validation
    # The __init__ method validates role and content
    with pytest.raises(ValueError, match="Invalid role"):
        Message()  # No fields provided, role will be None


def test_message_with_tool_calls():
    """Test creating a message with tool_calls JSON data."""
    conversation_id = uuid4()
    tool_calls = {
        "tool": "add_task",
        "parameters": {"title": "Buy milk", "description": "Get 2 gallons"}
    }

    message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content="I'll add that task for you.",
        tool_calls=tool_calls
    )

    assert message.tool_calls == tool_calls
    assert message.tool_calls["tool"] == "add_task"
    assert message.tool_calls["parameters"]["title"] == "Buy milk"


def test_message_multiple_instances_have_unique_ids():
    """Test that multiple messages get unique UUIDs."""
    conversation_id = uuid4()

    msg1 = Message(
        conversation_id=conversation_id,
        role="user",
        content="Message 1"
    )
    msg2 = Message(
        conversation_id=conversation_id,
        role="user",
        content="Message 2"
    )

    assert msg1.id != msg2.id


def test_message_can_set_custom_id():
    """Test that message can be created with a custom UUID."""
    conversation_id = uuid4()
    custom_id = uuid4()

    message = Message(
        id=custom_id,
        conversation_id=conversation_id,
        role="user",
        content="Test"
    )

    assert message.id == custom_id


def test_message_can_set_custom_timestamp():
    """Test that message can be created with custom timestamp."""
    conversation_id = uuid4()
    custom_time = datetime(2024, 1, 1, 12, 0, 0)

    message = Message(
        conversation_id=conversation_id,
        role="user",
        content="Test",
        created_at=custom_time
    )

    assert message.created_at == custom_time
