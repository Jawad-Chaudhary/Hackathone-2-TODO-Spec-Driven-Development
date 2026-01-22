"""
Unit tests for delete_task MCP tool.

Tests:
- Valid task deletion
- Non-existent task_id
- Ownership validation (wrong owner)
- user_id validation (empty, negative, None)
- task_id validation
- Database error handling
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.mcp.tools.delete_task import delete_task


@pytest.mark.asyncio
async def test_delete_task_with_valid_inputs():
    """Test delete_task removes task with valid inputs."""
    # Mock existing task
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.title = "Buy groceries"
    mock_task.user_id = "1"

    # Mock query result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_task)

    # Mock database session
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.delete = AsyncMock()
    mock_db.commit = AsyncMock()

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.delete_task.get_session", mock_get_session):
        result = await delete_task(
            user_id=1,
            task_id=1
        )

    assert result["success"] is True
    assert result["task_id"] == 1
    assert "deleted successfully" in result["message"]
    assert "Buy groceries" in result["message"]
    mock_db.delete.assert_called_once_with(mock_task)
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_task_with_nonexistent_task():
    """Test delete_task handles non-existent task_id."""
    # Mock query result with no task found
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.delete_task.get_session", mock_get_session):
        with pytest.raises(Exception, match="not found or you don't have permission"):
            await delete_task(user_id=1, task_id=999)


@pytest.mark.asyncio
async def test_delete_task_ownership_validation_wrong_owner():
    """Test delete_task validates ownership (wrong owner)."""
    # Mock query result with no task found (ownership check fails)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.delete_task.get_session", mock_get_session):
        with pytest.raises(Exception, match="not found or you don't have permission"):
            await delete_task(user_id=2, task_id=1)  # Task belongs to user 1, not user 2


@pytest.mark.asyncio
async def test_delete_task_user_id_validation_empty():
    """Test delete_task validates empty user_id (0)."""
    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await delete_task(user_id=0, task_id=1)


@pytest.mark.asyncio
async def test_delete_task_user_id_validation_negative():
    """Test delete_task validates negative user_id."""
    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await delete_task(user_id=-1, task_id=1)


@pytest.mark.asyncio
async def test_delete_task_user_id_validation_none():
    """Test delete_task validates None user_id."""
    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await delete_task(user_id=None, task_id=1)


@pytest.mark.asyncio
async def test_delete_task_task_id_validation_empty():
    """Test delete_task validates empty task_id (0)."""
    with pytest.raises(ValueError, match="task_id must be a positive integer"):
        await delete_task(user_id=1, task_id=0)


@pytest.mark.asyncio
async def test_delete_task_task_id_validation_negative():
    """Test delete_task validates negative task_id."""
    with pytest.raises(ValueError, match="task_id must be a positive integer"):
        await delete_task(user_id=1, task_id=-1)


@pytest.mark.asyncio
async def test_delete_task_task_id_validation_none():
    """Test delete_task validates None task_id."""
    with pytest.raises(ValueError, match="task_id must be a positive integer"):
        await delete_task(user_id=1, task_id=None)


@pytest.mark.asyncio
async def test_delete_task_database_error():
    """Test delete_task handles database errors."""
    # Mock task found
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.title = "Test task"
    mock_task.user_id = "1"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_task)

    # Mock database error on delete
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.delete = AsyncMock()
    mock_db.commit = AsyncMock(side_effect=Exception("Database connection failed"))

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.delete_task.get_session", mock_get_session):
        with pytest.raises(Exception, match="Database error"):
            await delete_task(user_id=1, task_id=1)
