"""
Unit tests for add_task MCP tool.

Tests:
- Valid task creation
- user_id validation
- title validation
- description handling
- Database error handling
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.mcp.tools.add_task import add_task


@pytest.mark.asyncio
async def test_add_task_with_valid_inputs():
    """Test add_task creates task with valid inputs."""
    # Mock database session and task
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.title = "Buy groceries"
    mock_task.description = "Get milk and eggs"
    mock_task.completed = False
    mock_task.user_id = 1

    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.add_task.get_session", mock_get_session):
        with patch("app.mcp.tools.add_task.Task", return_value=mock_task):
            result = await add_task(
                user_id=1,
                title="Buy groceries",
                description="Get milk and eggs"
            )

    assert result["success"] is True
    assert result["task"]["id"] == 1
    assert result["task"]["title"] == "Buy groceries"
    assert result["task"]["description"] == "Get milk and eggs"
    assert result["task"]["completed"] is False
    assert result["task"]["user_id"] == 1
    assert "created successfully" in result["message"]


@pytest.mark.asyncio
async def test_add_task_without_description():
    """Test add_task creates task without description."""
    mock_task = MagicMock()
    mock_task.id = 2
    mock_task.title = "Call dentist"
    mock_task.description = None
    mock_task.completed = False
    mock_task.user_id = 1

    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.add_task.get_session", mock_get_session):
        with patch("app.mcp.tools.add_task.Task", return_value=mock_task):
            result = await add_task(
                user_id=1,
                title="Call dentist"
            )

    assert result["success"] is True
    assert result["task"]["description"] is None


@pytest.mark.asyncio
async def test_add_task_user_id_validation_empty():
    """Test add_task validates empty user_id."""
    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await add_task(user_id=0, title="Test task")


@pytest.mark.asyncio
async def test_add_task_user_id_validation_negative():
    """Test add_task validates negative user_id."""
    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await add_task(user_id=-1, title="Test task")


@pytest.mark.asyncio
async def test_add_task_user_id_validation_none():
    """Test add_task validates None user_id."""
    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await add_task(user_id=None, title="Test task")


@pytest.mark.asyncio
async def test_add_task_title_validation_empty():
    """Test add_task validates empty title."""
    with pytest.raises(ValueError, match="title cannot be empty"):
        await add_task(user_id=1, title="")


@pytest.mark.asyncio
async def test_add_task_title_validation_whitespace():
    """Test add_task validates whitespace-only title."""
    with pytest.raises(ValueError, match="title cannot be empty"):
        await add_task(user_id=1, title="   ")


@pytest.mark.asyncio
async def test_add_task_title_validation_none():
    """Test add_task validates None title."""
    with pytest.raises(ValueError, match="title cannot be empty"):
        await add_task(user_id=1, title=None)


@pytest.mark.asyncio
async def test_add_task_trims_title():
    """Test add_task trims whitespace from title."""
    mock_task = MagicMock()
    mock_task.id = 3
    mock_task.title = "Trimmed title"
    mock_task.description = None
    mock_task.completed = False
    mock_task.user_id = 1

    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.add_task.get_session", mock_get_session):
        with patch("app.mcp.tools.add_task.Task", return_value=mock_task):
            result = await add_task(
                user_id=1,
                title="  Trimmed title  "
            )

    assert result["task"]["title"] == "Trimmed title"


@pytest.mark.asyncio
async def test_add_task_database_error():
    """Test add_task handles database errors."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock(side_effect=Exception("Database connection failed"))

    async def mock_get_session():
        yield mock_db

    with patch("app.mcp.tools.add_task.get_session", mock_get_session):
        with patch("app.mcp.tools.add_task.Task", return_value=MagicMock()):
            with pytest.raises(Exception, match="Database error"):
                await add_task(user_id=1, title="Test task")
