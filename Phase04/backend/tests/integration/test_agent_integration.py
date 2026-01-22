"""
Integration tests for OpenAI Agent.

These tests mock the OpenAI API to avoid real API calls and test
the agent's ability to integrate with MCP tools for task management.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from openai.types.chat import ChatCompletion, ChatCompletionMessage, ChatCompletionMessageToolCall
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message_tool_call import Function

from app.agent.runner import run_agent


def create_mock_response(
    content: str,
    tool_calls: list[dict] | None = None
) -> ChatCompletion:
    """
    Create a mock OpenAI ChatCompletion response.

    Args:
        content: The text response from the assistant
        tool_calls: Optional list of tool calls with format:
                   [{"name": "tool_name", "arguments": '{"arg": "value"}'}]

    Returns:
        ChatCompletion object
    """
    # Create tool calls if provided
    mock_tool_calls = None
    if tool_calls:
        mock_tool_calls = []
        for idx, tc in enumerate(tool_calls):
            mock_tool_calls.append(
                ChatCompletionMessageToolCall(
                    id=f"call_{idx}",
                    type="function",
                    function=Function(
                        name=tc["name"],
                        arguments=tc["arguments"]
                    )
                )
            )

    # Create message
    message = ChatCompletionMessage(
        role="assistant",
        content=content,
        tool_calls=mock_tool_calls
    )

    # Create choice
    choice = Choice(
        index=0,
        message=message,
        finish_reason="stop"
    )

    # Create completion
    return ChatCompletion(
        id="chatcmpl-test",
        model="gpt-4o",
        object="chat.completion",
        created=1234567890,
        choices=[choice]
    )


@pytest.mark.asyncio
async def test_agent_can_add_task():
    """Test T050: Agent can add task via natural language."""
    # Mock OpenAI response with tool call
    mock_response = create_mock_response(
        content="I've added that task for you.",
        tool_calls=[{
            "name": "add_task",
            "arguments": '{"user_id": 1, "title": "Buy milk"}'
        }]
    )

    with patch("app.agent.runner.get_openai_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=[
            mock_response,
            create_mock_response("Task added successfully!")
        ])
        mock_get_client.return_value = mock_client

        with patch("app.agent.runner.TOOL_FUNCTIONS") as mock_tools:
            mock_tools.__getitem__ = lambda self, key: AsyncMock(
                return_value={"success": True, "task": {"id": 1, "title": "Buy milk"}}
            )

            result = await run_agent(
                user_id=1,
                messages=[{"role": "user", "content": "Add task: Buy milk"}],
                client=mock_client
            )

            assert result["success"] is True
            assert "add_task" in result["tool_calls"]
            assert result["response"] is not None


@pytest.mark.asyncio
async def test_agent_can_list_tasks():
    """Test T051: Agent can list tasks with status filtering."""
    # Mock OpenAI response with list_tasks call
    mock_response = create_mock_response(
        content="Here are your pending tasks:",
        tool_calls=[{
            "name": "list_tasks",
            "arguments": '{"user_id": "1", "status": "pending"}'
        }]
    )

    with patch("app.agent.runner.get_openai_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=[
            mock_response,
            create_mock_response("You have 2 pending tasks.")
        ])
        mock_get_client.return_value = mock_client

        with patch("app.agent.runner.TOOL_FUNCTIONS") as mock_tools:
            mock_tools.__getitem__ = lambda self, key: AsyncMock(
                return_value={
                    "success": True,
                    "tasks": [
                        {"id": 1, "title": "Task 1", "completed": False},
                        {"id": 2, "title": "Task 2", "completed": False}
                    ]
                }
            )

            result = await run_agent(
                user_id=1,
                messages=[{"role": "user", "content": "Show my pending tasks"}],
                client=mock_client
            )

            assert result["success"] is True
            assert "list_tasks" in result["tool_calls"]


@pytest.mark.asyncio
async def test_agent_can_complete_task():
    """Test T052: Agent can mark task as completed."""
    # Mock OpenAI response with complete_task call
    mock_response = create_mock_response(
        content="Great! I've marked that task as completed.",
        tool_calls=[{
            "name": "complete_task",
            "arguments": '{"user_id": 1, "task_id": 1}'
        }]
    )

    with patch("app.agent.runner.get_openai_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=[
            mock_response,
            create_mock_response("Task completed!")
        ])
        mock_get_client.return_value = mock_client

        with patch("app.agent.runner.TOOL_FUNCTIONS") as mock_tools:
            mock_tools.__getitem__ = lambda self, key: AsyncMock(
                return_value={
                    "success": True,
                    "task": {"id": 1, "title": "Buy milk", "completed": True}
                }
            )

            result = await run_agent(
                user_id=1,
                messages=[{"role": "user", "content": "Mark task 1 as done"}],
                client=mock_client
            )

            assert result["success"] is True
            assert "complete_task" in result["tool_calls"]


@pytest.mark.asyncio
async def test_agent_handles_ambiguous_commands():
    """Test T053: Agent asks for clarification when command is ambiguous."""
    # Mock OpenAI response asking for clarification (no tool calls)
    mock_response = create_mock_response(
        content="Which task would you like to complete? Please provide the task number or title."
    )

    with patch("app.agent.runner.get_openai_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await run_agent(
            user_id=1,
            messages=[{"role": "user", "content": "complete task"}],
            client=mock_client
        )

        assert result["success"] is True
        assert result["tool_calls"] == []  # No tools called
        assert "which task" in result["response"].lower() or "task number" in result["response"].lower()


@pytest.mark.asyncio
async def test_agent_handles_tool_execution_errors():
    """Test T054: Agent handles tool execution errors gracefully."""
    # Mock OpenAI response with tool call
    mock_response = create_mock_response(
        content="Let me delete that task.",
        tool_calls=[{
            "name": "delete_task",
            "arguments": '{"user_id": 1, "task_id": 999}'
        }]
    )

    with patch("app.agent.runner.get_openai_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=[
            mock_response,
            create_mock_response("I couldn't find that task. Please check the task ID.")
        ])
        mock_get_client.return_value = mock_client

        with patch("app.agent.runner.TOOL_FUNCTIONS") as mock_tools:
            mock_tools.__getitem__ = lambda self, key: AsyncMock(
                return_value={"success": False, "error": "Task not found"}
            )

            result = await run_agent(
                user_id=1,
                messages=[{"role": "user", "content": "Delete task 999"}],
                client=mock_client
            )

            # Agent should still succeed but handle the tool error
            assert result["success"] is True
            assert "delete_task" in result["tool_calls"]
            assert result["response"] is not None


@pytest.mark.asyncio
async def test_agent_conversation_with_history():
    """Test agent maintains conversation context with message history."""
    # Simulate a multi-turn conversation
    conversation_history = [
        {"role": "user", "content": "Add task: Buy milk"},
        {"role": "assistant", "content": "I've added 'Buy milk' to your tasks."},
        {"role": "user", "content": "Add another one: Buy bread"}
    ]

    mock_response = create_mock_response(
        content="Added to your list!",
        tool_calls=[{
            "name": "add_task",
            "arguments": '{"user_id": 1, "title": "Buy bread"}'
        }]
    )

    with patch("app.agent.runner.get_openai_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=[
            mock_response,
            create_mock_response("Task added!")
        ])
        mock_get_client.return_value = mock_client

        with patch("app.agent.runner.TOOL_FUNCTIONS") as mock_tools:
            mock_tools.__getitem__ = lambda self, key: AsyncMock(
                return_value={"success": True, "task": {"id": 2, "title": "Buy bread"}}
            )

            result = await run_agent(
                user_id=1,
                messages=conversation_history,
                client=mock_client
            )

            assert result["success"] is True
            assert "add_task" in result["tool_calls"]


@pytest.mark.asyncio
async def test_agent_validates_user_id():
    """Test agent runner validates user_id parameter."""
    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await run_agent(
            user_id=0,
            messages=[{"role": "user", "content": "Add task"}]
        )

    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await run_agent(
            user_id=-1,
            messages=[{"role": "user", "content": "Add task"}]
        )


@pytest.mark.asyncio
async def test_agent_validates_messages():
    """Test agent runner validates messages parameter."""
    with pytest.raises(ValueError, match="messages must be a non-empty list"):
        await run_agent(user_id=1, messages=[])

    with pytest.raises(ValueError, match="messages must be a non-empty list"):
        await run_agent(user_id=1, messages=None)


@pytest.mark.asyncio
async def test_agent_handles_max_iterations():
    """Test agent stops after max iterations to prevent infinite loops."""
    # Mock OpenAI to always request tool calls
    mock_response = create_mock_response(
        content="Processing...",
        tool_calls=[{
            "name": "list_tasks",
            "arguments": '{"user_id": "1"}'
        }]
    )

    with patch("app.agent.runner.get_openai_client") as mock_get_client:
        mock_client = AsyncMock()
        # Always return a response with tool calls
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        with patch("app.agent.runner.TOOL_FUNCTIONS") as mock_tools:
            mock_tools.__getitem__ = lambda self, key: AsyncMock(
                return_value={"success": True, "tasks": []}
            )

            result = await run_agent(
                user_id=1,
                messages=[{"role": "user", "content": "List tasks"}],
                client=mock_client,
                max_iterations=3  # Set low limit for testing
            )

            assert result["success"] is False
            assert result["error"] == "Maximum iterations reached"
            assert "try rephrasing" in result["response"].lower()
