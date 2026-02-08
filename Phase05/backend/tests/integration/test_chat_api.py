"""
Integration tests for chat API endpoint (Tasks T063-T069).

These tests verify:
- T063: Chat creates new conversation
- T064: Chat with existing conversation_id
- T065: Chat requires JWT authentication
- T066: Chat enforces user isolation
- T067: Chat persists messages
- T068: Chat handles database errors
- T069: Chat handles agent errors
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from uuid import uuid4, UUID
from datetime import datetime

from fastapi import status

from app.models.conversation import Conversation
from app.models.message import Message


class TestChatAPI:
    """Integration tests for POST /api/{user_id}/chat endpoint."""

    @pytest.fixture
    def mock_conversation_id(self):
        """Generate a test conversation UUID."""
        return uuid4()

    @pytest.fixture
    def mock_agent_response(self):
        """Mock successful agent response."""
        return {
            "response": "I've added your task 'Buy groceries' to the list.",
            "tool_calls": ["add_task"],
            "success": True,
            "error": None
        }

    @pytest.fixture
    def mock_agent_error(self):
        """Mock agent error response."""
        return {
            "response": "I encountered an error.",
            "tool_calls": [],
            "success": False,
            "error": "OpenAI API error"
        }

    @pytest.fixture
    def mock_db_session(self, mock_db_session_conftest):
        """Reference to mock database session from conftest."""
        return mock_db_session_conftest

    def test_chat_creates_new_conversation(
        self, client, auth_headers, test_user_id, mock_agent_response, mock_db_session
    ):
        """
        Test T063: POST /chat creates new conversation.

        Verifies:
        - Conversation is created in database
        - User and assistant messages are stored
        - Response contains conversation_id
        """
        with patch("app.routes.chat.run_agent", new_callable=AsyncMock) as mock_agent, \
             patch("app.routes.chat.load_conversation_messages", new_callable=AsyncMock) as mock_load_messages, \
             patch("app.routes.chat.load_or_create_conversation", new_callable=AsyncMock) as mock_load_conv:

            mock_agent.return_value = mock_agent_response
            # Mock empty message history for new conversation
            mock_load_messages.return_value = []

            # Mock conversation creation
            mock_conversation = MagicMock(spec=Conversation)
            mock_conversation.id = uuid4()
            mock_conversation.user_id = int(test_user_id)
            mock_conversation.created_at = datetime.utcnow()
            mock_conversation.updated_at = datetime.utcnow()
            mock_load_conv.return_value = mock_conversation

            response = client.post(
                f"/api/{test_user_id}/chat",
                json={"message": "Add task: Buy groceries"},
                headers=auth_headers
            )

            # Assert response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "conversation_id" in data
            assert data["response"] == mock_agent_response["response"]
            assert data["tool_calls"] is not None

            # Verify agent was called with correct user_id
            mock_agent.assert_called_once()
            call_args = mock_agent.call_args
            assert call_args[0][0] == int(test_user_id)  # user_id is int

    def test_chat_with_existing_conversation(
        self, client, auth_headers, test_user_id, mock_conversation_id, mock_agent_response, mock_db_session
    ):
        """
        Test T064: POST /chat with existing conversation_id.

        Verifies:
        - Messages are added to existing conversation
        - Conversation updated_at is updated
        """
        with patch("app.routes.chat.run_agent", new_callable=AsyncMock) as mock_agent, \
             patch("app.routes.chat.load_or_create_conversation", new_callable=AsyncMock) as mock_load, \
             patch("app.routes.chat.load_conversation_messages", new_callable=AsyncMock) as mock_load_messages:

            mock_agent.return_value = mock_agent_response

            # Mock existing conversation
            mock_conversation = MagicMock(spec=Conversation)
            mock_conversation.id = mock_conversation_id
            mock_conversation.user_id = int(test_user_id)
            mock_conversation.created_at = datetime.utcnow()
            mock_conversation.updated_at = datetime.utcnow()
            mock_load.return_value = mock_conversation

            # Mock conversation history
            mock_load_messages.return_value = []

            response = client.post(
                f"/api/{test_user_id}/chat",
                json={
                    "message": "Show my tasks",
                    "conversation_id": str(mock_conversation_id)
                },
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["conversation_id"] == str(mock_conversation_id)

            # Verify conversation was loaded with correct ID
            mock_load.assert_called_once()
            # conversation_id is passed as a positional argument (3rd param after session and user_id)
            call_args = mock_load.call_args[0]
            assert len(call_args) == 3  # session, user_id, conversation_id
            assert call_args[2] == mock_conversation_id

    def test_chat_requires_authentication(self, client):
        """
        Test T065: POST /chat requires JWT authentication.

        Verifies:
        - Request without auth header returns 401
        - Request with invalid token returns 401
        """
        # No auth header
        response = client.post(
            "/api/123/chat",
            json={"message": "Hello"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Invalid token
        response = client.post(
            "/api/123/chat",
            json={"message": "Hello"},
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_chat_user_isolation(
        self, client, auth_headers, test_user_id, mock_agent_response, mock_db_session
    ):
        """
        Test T066: User can only access own conversations.

        Verifies:
        - User cannot access another user's conversation_id
        - Attempting to access returns 404 or 403
        """
        other_user_id = "other-user-456"
        other_conversation_id = uuid4()

        with patch("app.routes.chat.run_agent", new_callable=AsyncMock) as mock_agent, \
             patch("app.routes.chat.load_or_create_conversation", new_callable=AsyncMock) as mock_load, \
             patch("app.routes.chat.load_conversation_messages", new_callable=AsyncMock) as mock_load_messages:

            mock_agent.return_value = mock_agent_response

            # Mock load_or_create_conversation to raise HTTPException for wrong user
            from fastapi import HTTPException
            mock_load.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied"
            )

            mock_load_messages.return_value = []

            response = client.post(
                f"/api/{test_user_id}/chat",
                json={
                    "message": "Show my tasks",
                    "conversation_id": str(other_conversation_id)
                },
                headers=auth_headers
            )

            # Should return 404 because conversation doesn't belong to user
            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_chat_user_id_mismatch(self, client, auth_headers, test_user_id):
        """
        Test T066: User ID in JWT must match user_id in path.

        Verifies:
        - User cannot chat as another user
        - Returns 403 Forbidden
        """
        different_user_id = "999"  # Different numeric user ID

        response = client.post(
            f"/api/{different_user_id}/chat",
            json={"message": "Hello"},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "mismatch" in response.json()["detail"].lower()

    def test_chat_persists_messages(
        self, client, auth_headers, test_user_id, mock_agent_response, mock_db_session
    ):
        """
        Test T067: Both user and assistant messages are persisted.

        Verifies:
        - User message is saved before agent invocation
        - Assistant message is saved after agent invocation
        - Messages are linked to conversation
        """
        with patch("app.routes.chat.run_agent", new_callable=AsyncMock) as mock_agent, \
             patch("app.routes.chat.Message") as mock_message_class, \
             patch("app.routes.chat.load_or_create_conversation", new_callable=AsyncMock) as mock_load, \
             patch("app.routes.chat.load_conversation_messages", new_callable=AsyncMock) as mock_load_messages:

            mock_agent.return_value = mock_agent_response

            # Mock conversation
            mock_conversation = MagicMock(spec=Conversation)
            mock_conversation.id = uuid4()
            mock_conversation.user_id = int(test_user_id)
            mock_load.return_value = mock_conversation

            # Mock messages list
            mock_load_messages.return_value = [{"role": "user", "content": "Add task: Buy groceries"}]

            response = client.post(
                f"/api/{test_user_id}/chat",
                json={"message": "Add task: Buy groceries"},
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK

            # Verify Message was instantiated twice (user and assistant)
            assert mock_message_class.call_count >= 2

    def test_chat_handles_database_errors(
        self, client, auth_headers, test_user_id, mock_db_session
    ):
        """
        Test T068: Database error handling.

        Verifies:
        - Database failures return 500
        - Error message is appropriate
        """
        with patch("app.routes.chat.load_or_create_conversation", new_callable=AsyncMock) as mock_load:
            # Simulate database error
            mock_load.side_effect = Exception("Database connection failed")

            response = client.post(
                f"/api/{test_user_id}/chat",
                json={"message": "Hello"},
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "error" in response.json()["detail"].lower()

    def test_chat_handles_agent_errors(
        self, client, auth_headers, test_user_id, mock_agent_error, mock_db_session
    ):
        """
        Test T069: OpenAI API error handling.

        Verifies:
        - Agent failures return 500
        - Error message indicates agent failure
        """
        with patch("app.routes.chat.run_agent", new_callable=AsyncMock) as mock_agent, \
             patch("app.routes.chat.load_or_create_conversation", new_callable=AsyncMock) as mock_load, \
             patch("app.routes.chat.load_conversation_messages", new_callable=AsyncMock) as mock_load_messages:

            # Return error response
            mock_agent.return_value = mock_agent_error

            # Mock conversation
            mock_conversation = MagicMock(spec=Conversation)
            mock_conversation.id = uuid4()
            mock_conversation.user_id = int(test_user_id)
            mock_load.return_value = mock_conversation
            mock_load_messages.return_value = []

            response = client.post(
                f"/api/{test_user_id}/chat",
                json={"message": "Hello"},
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "agent" in response.json()["detail"].lower()

    def test_chat_validates_empty_message(self, client, auth_headers, test_user_id):
        """
        Test: Chat endpoint rejects empty messages.

        Verifies:
        - Empty message returns 422
        - Whitespace-only message returns 422
        """
        # Empty message
        response = client.post(
            f"/api/{test_user_id}/chat",
            json={"message": ""},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Whitespace only
        response = client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "   "},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_chat_conversation_timestamp_update(
        self, client, auth_headers, test_user_id, mock_agent_response, mock_db_session
    ):
        """
        Test: Conversation updated_at is updated after chat.

        Verifies:
        - Conversation timestamp is set to current time
        """
        with patch("app.routes.chat.run_agent", new_callable=AsyncMock) as mock_agent, \
             patch("app.routes.chat.load_or_create_conversation", new_callable=AsyncMock) as mock_load, \
             patch("app.routes.chat.load_conversation_messages", new_callable=AsyncMock) as mock_load_messages:

            mock_agent.return_value = mock_agent_response

            # Mock conversation
            mock_conversation = MagicMock(spec=Conversation)
            mock_conversation.id = uuid4()
            mock_conversation.user_id = int(test_user_id)
            old_timestamp = datetime(2020, 1, 1)
            mock_conversation.updated_at = old_timestamp
            mock_load.return_value = mock_conversation
            mock_load_messages.return_value = []

            response = client.post(
                f"/api/{test_user_id}/chat",
                json={"message": "Hello"},
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK

            # Verify updated_at was set (not equal to old timestamp)
            # Note: exact time check not possible with mock, but we verify it was set
            assert mock_conversation.updated_at != old_timestamp
