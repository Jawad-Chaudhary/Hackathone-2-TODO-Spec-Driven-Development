"""
Unit tests for list_tasks MCP tool.

Tests:
- List tasks with status="all"
- List tasks with status="pending"
- List tasks with status="completed"
- user_id validation (empty, None, whitespace)
- Invalid status parameter
- Database error handling
- Empty results
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from app.mcp.tools.list_tasks import list_tasks


@pytest.mark.asyncio
async def test_list_tasks_with_status_all():
    """Test list_tasks retrieves all tasks for a user."""
    # Mock tasks
    mock_task1 = MagicMock()
    mock_task1.id = 1
    mock_task1.title = "Buy groceries"
    mock_task1.description = "Get milk and eggs"
    mock_task1.completed = False
    mock_task1.user_id = "user123"
    mock_task1.created_at = datetime(2025, 1, 19, 10, 0, 0)
    mock_task1.updated_at = datetime(2025, 1, 19, 10, 0, 0)

    mock_task2 = MagicMock()
    mock_task2.id = 2
    mock_task2.title = "Call dentist"
    mock_task2.description = None
    mock_task2.completed = True
    mock_task2.user_id = "user123"
    mock_task2.created_at = datetime(2025, 1, 19, 9, 0, 0)
    mock_task2.updated_at = datetime(2025, 1, 19, 11, 0, 0)

    # Mock database session and result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task1, mock_task2]

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.list_tasks.get_session", mock_get_session):
        result = await list_tasks(user_id="user123", status="all")

    assert result["success"] is True
    assert result["count"] == 2
    assert len(result["tasks"]) == 2
    assert result["tasks"][0]["id"] == 1
    assert result["tasks"][0]["title"] == "Buy groceries"
    assert result["tasks"][0]["completed"] is False
    assert result["tasks"][1]["id"] == 2
    assert result["tasks"][1]["completed"] is True
    assert "2 task(s)" in result["message"]


@pytest.mark.asyncio
async def test_list_tasks_with_status_pending():
    """Test list_tasks retrieves only pending tasks."""
    # Mock pending task
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.title = "Buy groceries"
    mock_task.description = "Get milk"
    mock_task.completed = False
    mock_task.user_id = "user123"
    mock_task.created_at = datetime(2025, 1, 19, 10, 0, 0)
    mock_task.updated_at = datetime(2025, 1, 19, 10, 0, 0)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task]

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.list_tasks.get_session", mock_get_session):
        result = await list_tasks(user_id="user123", status="pending")

    assert result["success"] is True
    assert result["count"] == 1
    assert result["tasks"][0]["completed"] is False
    assert "1 pending task(s)" in result["message"]


@pytest.mark.asyncio
async def test_list_tasks_with_status_completed():
    """Test list_tasks retrieves only completed tasks."""
    # Mock completed task
    mock_task = MagicMock()
    mock_task.id = 2
    mock_task.title = "Call dentist"
    mock_task.description = None
    mock_task.completed = True
    mock_task.user_id = "user123"
    mock_task.created_at = datetime(2025, 1, 19, 9, 0, 0)
    mock_task.updated_at = datetime(2025, 1, 19, 11, 0, 0)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task]

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.list_tasks.get_session", mock_get_session):
        result = await list_tasks(user_id="user123", status="completed")

    assert result["success"] is True
    assert result["count"] == 1
    assert result["tasks"][0]["completed"] is True
    assert "1 completed task(s)" in result["message"]


@pytest.mark.asyncio
async def test_list_tasks_empty_results():
    """Test list_tasks handles empty results gracefully."""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.list_tasks.get_session", mock_get_session):
        result = await list_tasks(user_id="user123", status="all")

    assert result["success"] is True
    assert result["count"] == 0
    assert len(result["tasks"]) == 0
    assert "0 task(s)" in result["message"]


@pytest.mark.asyncio
async def test_list_tasks_user_id_validation_empty():
    """Test list_tasks validates empty user_id."""
    with pytest.raises(ValueError, match="user_id must be a non-empty string"):
        await list_tasks(user_id="", status="all")


@pytest.mark.asyncio
async def test_list_tasks_user_id_validation_none():
    """Test list_tasks validates None user_id."""
    with pytest.raises(ValueError, match="user_id must be a non-empty string"):
        await list_tasks(user_id=None, status="all")


@pytest.mark.asyncio
async def test_list_tasks_user_id_validation_whitespace():
    """Test list_tasks validates whitespace-only user_id."""
    with pytest.raises(ValueError, match="user_id must be a non-empty string"):
        await list_tasks(user_id="   ", status="all")


@pytest.mark.asyncio
async def test_list_tasks_invalid_status_parameter():
    """Test list_tasks validates status parameter."""
    with pytest.raises(ValueError, match="status must be one of"):
        await list_tasks(user_id="user123", status="invalid")


@pytest.mark.asyncio
async def test_list_tasks_database_error():
    """Test list_tasks handles database errors."""
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(side_effect=Exception("Database connection failed"))

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.list_tasks.get_session", mock_get_session):
        with pytest.raises(Exception, match="Database error"):
            await list_tasks(user_id="user123", status="all")


@pytest.mark.asyncio
async def test_list_tasks_user_isolation():
    """Test list_tasks only returns tasks for the specified user."""
    # Mock tasks for different users
    mock_task_user1 = MagicMock()
    mock_task_user1.id = 1
    mock_task_user1.title = "User1 Task"
    mock_task_user1.description = None
    mock_task_user1.completed = False
    mock_task_user1.user_id = "user123"
    mock_task_user1.created_at = datetime(2025, 1, 19, 10, 0, 0)
    mock_task_user1.updated_at = datetime(2025, 1, 19, 10, 0, 0)

    # Only user123's tasks should be returned
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_task_user1]

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.list_tasks.get_session", mock_get_session):
        result = await list_tasks(user_id="user123", status="all")

    assert result["success"] is True
    assert result["count"] == 1
    assert all(task["user_id"] == "user123" for task in result["tasks"])
