# [Task]: T-013
# [From]: specs/001-ai-todo-chatbot/tasks.md

"""
Add Task MCP Tool

Creates a new task for a user with title and optional description.
Enforces user isolation and validates input constraints.

Input Schema:
    - user_id: str (required) - User ID who owns the task
    - title: str (required, 1-200 chars) - Task title
    - description: str (optional, max 1000 chars) - Task description

Output:
    JSON response with status and task data or error message
"""

import json
from datetime import datetime
from typing import Any

from mcp.types import TextContent

from ..database.session import async_session
from ..models.task import Task


async def add_task(arguments: dict[str, Any]) -> list[TextContent]:
    """
    Create a new task for a user.

    Args:
        arguments: Dict containing:
            - user_id (str): User ID who owns the task
            - title (str): Task title (1-200 characters)
            - description (str, optional): Task description (max 1000 characters)

    Returns:
        list[TextContent]: JSON response with created task data or error

    Validation:
        - user_id: required, non-empty string
        - title: required, 1-200 characters
        - description: optional, max 1000 characters

    Example Success Response:
        {
            "status": "success",
            "task": {
                "id": 1,
                "user_id": "user123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": false,
                "created_at": "2025-01-14T12:00:00",
                "updated_at": "2025-01-14T12:00:00"
            }
        }

    Example Error Response:
        {
            "error": "title is required",
            "status": "error"
        }
    """
    # Validate required fields
    user_id = arguments.get("user_id")
    title = arguments.get("title")

    if not user_id:
        return [TextContent(type="text", text=json.dumps({
            "error": "user_id is required",
            "status": "error"
        }))]

    if not title:
        return [TextContent(type="text", text=json.dumps({
            "error": "title is required",
            "status": "error"
        }))]

    # Validate title length
    if len(title) < 1 or len(title) > 200:
        return [TextContent(type="text", text=json.dumps({
            "error": "title must be between 1 and 200 characters",
            "status": "error"
        }))]

    # Validate description if provided
    description = arguments.get("description")
    if description and len(description) > 1000:
        return [TextContent(type="text", text=json.dumps({
            "error": "description must not exceed 1000 characters",
            "status": "error"
        }))]

    # Create database session and insert task
    try:
        async with async_session() as session:
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)

            result = {
                "status": "success",
                "task": {
                    "id": task.id,
                    "user_id": task.user_id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
            }
            return [TextContent(type="text", text=json.dumps(result))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({
            "error": f"Database error: {str(e)}",
            "status": "error"
        }))]
