"""
Unit tests for update_task MCP tool.

Tests:
- Valid task updates (title only, description only, both)
- user_id and task_id validation
- Ownership verification (wrong owner)
- No updates provided validation
- Title validation (empty/whitespace)
- Task not found handling
- Database error handling
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.mcp.tools.update_task import update_task


@pytest.mark.asyncio
async def test_update_task_title_only():
    """Test update_task updates only title."""
    # Mock existing task
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.user_id = 1
    mock_task.title = "Old title"
    mock_task.description = "Original description"
    mock_task.completed = False

    # Mock result object
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_task)

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.update_task.get_session", mock_get_session):
        result = await update_task(
            user_id=1,
            task_id=1,
            title="New title"
        )

    assert result["success"] is True
    assert result["task"]["id"] == 1
    assert mock_task.title == "New title"
    assert mock_task.description == "Original description"
    assert "updated successfully" in result["message"]


@pytest.mark.asyncio
async def test_update_task_description_only():
    """Test update_task updates only description."""
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.user_id = 1
    mock_task.title = "Original title"
    mock_task.description = "Old description"
    mock_task.completed = False

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_task)

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.update_task.get_session", mock_get_session):
        result = await update_task(
            user_id=1,
            task_id=1,
            description="New description"
        )

    assert result["success"] is True
    assert mock_task.title == "Original title"
    assert mock_task.description == "New description"


@pytest.mark.asyncio
async def test_update_task_both_fields():
    """Test update_task updates both title and description."""
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.user_id = 1
    mock_task.title = "Old title"
    mock_task.description = "Old description"
    mock_task.completed = False

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_task)

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.update_task.get_session", mock_get_session):
        result = await update_task(
            user_id=1,
            task_id=1,
            title="New title",
            description="New description"
        )

    assert result["success"] is True
    assert mock_task.title == "New title"
    assert mock_task.description == "New description"


@pytest.mark.asyncio
async def test_update_task_wrong_owner():
    """Test update_task validates ownership (task not found for wrong user)."""
    # Mock result with no task found
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.update_task.get_session", mock_get_session):
        with pytest.raises(ValueError, match="not found or does not belong to user"):
            await update_task(
                user_id=999,  # Wrong user
                task_id=1,
                title="New title"
            )


@pytest.mark.asyncio
async def test_update_task_task_not_found():
    """Test update_task handles non-existent task."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.update_task.get_session", mock_get_session):
        with pytest.raises(ValueError, match="not found"):
            await update_task(
                user_id=1,
                task_id=999,  # Non-existent task
                title="New title"
            )


@pytest.mark.asyncio
async def test_update_task_user_id_validation_zero():
    """Test update_task validates zero user_id."""
    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await update_task(user_id=0, task_id=1, title="Test")


@pytest.mark.asyncio
async def test_update_task_user_id_validation_negative():
    """Test update_task validates negative user_id."""
    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await update_task(user_id=-1, task_id=1, title="Test")


@pytest.mark.asyncio
async def test_update_task_user_id_validation_none():
    """Test update_task validates None user_id."""
    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await update_task(user_id=None, task_id=1, title="Test")


@pytest.mark.asyncio
async def test_update_task_task_id_validation_zero():
    """Test update_task validates zero task_id."""
    with pytest.raises(ValueError, match="task_id must be a positive integer"):
        await update_task(user_id=1, task_id=0, title="Test")


@pytest.mark.asyncio
async def test_update_task_task_id_validation_negative():
    """Test update_task validates negative task_id."""
    with pytest.raises(ValueError, match="task_id must be a positive integer"):
        await update_task(user_id=1, task_id=-1, title="Test")


@pytest.mark.asyncio
async def test_update_task_task_id_validation_none():
    """Test update_task validates None task_id."""
    with pytest.raises(ValueError, match="task_id must be a positive integer"):
        await update_task(user_id=1, task_id=None, title="Test")


@pytest.mark.asyncio
async def test_update_task_no_updates_provided():
    """Test update_task validates that at least one update is provided."""
    with pytest.raises(ValueError, match="At least one of title or description must be provided"):
        await update_task(user_id=1, task_id=1)


@pytest.mark.asyncio
async def test_update_task_title_validation_empty():
    """Test update_task validates empty title."""
    with pytest.raises(ValueError, match="title cannot be empty"):
        await update_task(user_id=1, task_id=1, title="")


@pytest.mark.asyncio
async def test_update_task_title_validation_whitespace():
    """Test update_task validates whitespace-only title."""
    with pytest.raises(ValueError, match="title cannot be empty"):
        await update_task(user_id=1, task_id=1, title="   ")


@pytest.mark.asyncio
async def test_update_task_trims_title():
    """Test update_task trims whitespace from title."""
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.user_id = 1
    mock_task.title = "Original"
    mock_task.description = None
    mock_task.completed = False

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_task)

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.update_task.get_session", mock_get_session):
        result = await update_task(
            user_id=1,
            task_id=1,
            title="  Trimmed title  "
        )

    assert mock_task.title == "Trimmed title"


@pytest.mark.asyncio
async def test_update_task_database_error():
    """Test update_task handles database errors."""
    mock_task = MagicMock()
    mock_task.id = 1

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_task)

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock(side_effect=Exception("Database connection failed"))

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.update_task.get_session", mock_get_session):
        with pytest.raises(Exception, match="Database error"):
            await update_task(user_id=1, task_id=1, title="Test")


@pytest.mark.asyncio
async def test_update_task_updates_timestamp():
    """Test update_task updates the updated_at timestamp."""
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.user_id = 1
    mock_task.title = "Old title"
    mock_task.description = None
    mock_task.completed = False
    mock_task.updated_at = None

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_task)

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.update_task.get_session", mock_get_session):
        await update_task(user_id=1, task_id=1, title="New title")

    # Verify updated_at was set
    assert mock_task.updated_at is not None
