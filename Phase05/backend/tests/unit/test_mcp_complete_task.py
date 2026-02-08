"""
Unit tests for complete_task MCP tool.

Tests:
- Valid task completion
- Task not found handling
- Ownership validation (wrong user)
- user_id validation
- task_id validation
- Database error handling
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.mcp.tools.complete_task import complete_task


@pytest.mark.asyncio
async def test_complete_task_with_valid_task_id():
    """Test complete_task marks task as completed with valid task_id."""
    # Mock existing task
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.title = "Buy groceries"
    mock_task.description = "Get milk and eggs"
    mock_task.completed = True
    mock_task.user_id = 1

    # Mock database session
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    # Mock query result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_task)
    mock_db.execute.return_value = mock_result

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.complete_task.get_session", mock_get_session):
        result = await complete_task(
            user_id=1,
            task_id=1
        )

    assert result["success"] is True
    assert result["task"]["id"] == 1
    assert result["task"]["title"] == "Buy groceries"
    assert result["task"]["completed"] is True
    assert "marked as completed" in result["message"]


@pytest.mark.asyncio
async def test_complete_task_with_nonexistent_task_id():
    """Test complete_task raises error for non-existent task_id."""
    # Mock database session with no task found
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()

    # Mock query result returning None
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_db.execute.return_value = mock_result

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.complete_task.get_session", mock_get_session):
        with pytest.raises(Exception, match="not found"):
            await complete_task(user_id=1, task_id=999)


@pytest.mark.asyncio
async def test_complete_task_ownership_validation():
    """Test complete_task validates task ownership (wrong user)."""
    # Mock database session with no task found (wrong owner)
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()

    # Mock query result returning None (task exists but different owner)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_db.execute.return_value = mock_result

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.complete_task.get_session", mock_get_session):
        with pytest.raises(Exception, match="not found or you don't have permission"):
            await complete_task(user_id=2, task_id=1)


@pytest.mark.asyncio
async def test_complete_task_user_id_validation_empty():
    """Test complete_task validates empty user_id."""
    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await complete_task(user_id=0, task_id=1)


@pytest.mark.asyncio
async def test_complete_task_user_id_validation_negative():
    """Test complete_task validates negative user_id."""
    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await complete_task(user_id=-1, task_id=1)


@pytest.mark.asyncio
async def test_complete_task_user_id_validation_none():
    """Test complete_task validates None user_id."""
    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await complete_task(user_id=None, task_id=1)


@pytest.mark.asyncio
async def test_complete_task_task_id_validation_empty():
    """Test complete_task validates empty task_id."""
    with pytest.raises(ValueError, match="task_id must be a positive integer"):
        await complete_task(user_id=1, task_id=0)


@pytest.mark.asyncio
async def test_complete_task_task_id_validation_negative():
    """Test complete_task validates negative task_id."""
    with pytest.raises(ValueError, match="task_id must be a positive integer"):
        await complete_task(user_id=1, task_id=-1)


@pytest.mark.asyncio
async def test_complete_task_task_id_validation_none():
    """Test complete_task validates None task_id."""
    with pytest.raises(ValueError, match="task_id must be a positive integer"):
        await complete_task(user_id=1, task_id=None)


@pytest.mark.asyncio
async def test_complete_task_database_error():
    """Test complete_task handles database errors."""
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(side_effect=Exception("Database connection failed"))

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.complete_task.get_session", mock_get_session):
        with pytest.raises(Exception, match="Database error"):
            await complete_task(user_id=1, task_id=1)
