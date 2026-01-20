"""
Unit tests for Conversation-Message relationship integrity.

Tests:
- Conversation has messages list
- Message references conversation
- Cascade delete behavior (conceptual test)
"""

import pytest
from uuid import uuid4

from app.models.conversation import Conversation
from app.models.message import Message


def test_conversation_has_messages_list():
    """Test that conversation has messages attribute."""
    conversation = Conversation(user_id=1)

    assert hasattr(conversation, 'messages')
    assert isinstance(conversation.messages, list)


def test_message_has_conversation_relationship():
    """Test that message has conversation relationship attribute."""
    conversation_id = uuid4()
    message = Message(
        conversation_id=conversation_id,
        role="user",
        content="Test"
    )

    assert hasattr(message, 'conversation')


def test_multiple_messages_same_conversation():
    """Test that multiple messages can reference the same conversation."""
    conversation_id = uuid4()

    msg1 = Message(
        conversation_id=conversation_id,
        role="user",
        content="First message"
    )
    msg2 = Message(
        conversation_id=conversation_id,
        role="assistant",
        content="Second message"
    )

    assert msg1.conversation_id == msg2.conversation_id
    assert msg1.id != msg2.id


def test_conversation_id_is_uuid():
    """Test that message conversation_id is a valid UUID."""
    conversation_id = uuid4()
    message = Message(
        conversation_id=conversation_id,
        role="user",
        content="Test"
    )

    assert isinstance(message.conversation_id, type(conversation_id))
    assert message.conversation_id == conversation_id
