# [Task]: T-017
# [From]: specs/001-ai-todo-chatbot/tasks.md

"""
Update Task MCP Tool

Updates a task's title and/or description for a user.
Enforces user isolation - only the task owner can update their tasks.

Input Schema:
    - user_id: str (required) - User ID who owns the task
    - task_id: int (required) - ID of the task to update
    - title: str (optional, 1-200 chars) - New task title
    - description: str (optional, max 1000 chars) - New task description

Output:
    JSON response with updated task data or error message
"""

import json
from datetime import datetime
from typing import Any

from mcp.types import TextContent
from sqlmodel import select

from ..database.session import async_session
from ..models.task import Task


async def update_task(arguments: dict[str, Any]) -> list[TextContent]:
    """
    Update a task's title and/or description.

    Args:
        arguments: Dict containing:
            - user_id (str): User ID who owns the task
            - task_id (int): ID of the task to update
            - title (str, optional): New task title (1-200 characters)
            - description (str, optional): New task description (max 1000 characters)

    Returns:
        list[TextContent]: JSON response with updated task data or error

    Validation:
        - user_id: required, non-empty string
        - task_id: required, must exist and belong to user_id
        - At least one field (title or description) must be provided
        - title: if provided, 1-200 characters
        - description: if provided, max 1000 characters
        - Ownership: Only the task owner can update the task (403 if mismatch)

    Example Success Response:
        {
            "status": "success",
            "task": {
                "id": 1,
                "user_id": "user123",
                "title": "Buy groceries and supplies",
                "description": "Milk, eggs, bread, cleaning supplies",
                "completed": false,
                "created_at": "2025-01-14T12:00:00",
                "updated_at": "2025-01-14T14:30:00"
            }
        }

    Example Error Response (No Fields):
        {
            "error": "At least one field (title or description) must be provided",
            "status": "error"
        }

    Example Error Response (Not Found):
        {
            "error": "Task not found or access denied",
            "status": "error"
        }
    """
    # Validate required fields
    user_id = arguments.get("user_id")
    task_id = arguments.get("task_id")

    if not user_id:
        return [TextContent(type="text", text=json.dumps({
            "error": "user_id is required",
            "status": "error"
        }))]

    if not task_id:
        return [TextContent(type="text", text=json.dumps({
            "error": "task_id is required",
            "status": "error"
        }))]

    # Get update fields
    title = arguments.get("title")
    description = arguments.get("description")

    # Validate at least one field to update
    if title is None and description is None:
        return [TextContent(type="text", text=json.dumps({
            "error": "At least one field (title or description) must be provided",
            "status": "error"
        }))]

    # Validate title if provided
    if title is not None and (len(title) < 1 or len(title) > 200):
        return [TextContent(type="text", text=json.dumps({
            "error": "title must be between 1 and 200 characters",
            "status": "error"
        }))]

    # Validate description if provided
    if description is not None and len(description) > 1000:
        return [TextContent(type="text", text=json.dumps({
            "error": "description must not exceed 1000 characters",
            "status": "error"
        }))]

    # Query and update with user isolation
    try:
        async with async_session() as session:
            # Enforce user isolation in WHERE clause
            stmt = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            result = await session.execute(stmt)
            task = result.scalar_one_or_none()

            if not task:
                return [TextContent(type="text", text=json.dumps({
                    "error": "Task not found or access denied",
                    "status": "error"
                }))]

            # Update fields
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description

            task.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(task)

            response = {
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
            return [TextContent(type="text", text=json.dumps(response))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({
            "error": f"Database error: {str(e)}",
            "status": "error"
        }))]
