# [Task]: T-015
# [From]: specs/001-ai-todo-chatbot/tasks.md

"""
Complete Task MCP Tool

Marks a task as completed for a user.
Enforces user isolation - only the task owner can complete their tasks.

Input Schema:
    - user_id: str (required) - User ID who owns the task
    - task_id: int (required) - ID of the task to complete

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


async def complete_task(arguments: dict[str, Any]) -> list[TextContent]:
    """
    Mark a task as completed.

    Args:
        arguments: Dict containing:
            - user_id (str): User ID who owns the task
            - task_id (int): ID of the task to complete

    Returns:
        list[TextContent]: JSON response with updated task data or error

    Validation:
        - user_id: required, non-empty string
        - task_id: required, must exist and belong to user_id
        - Ownership: Only the task owner can complete the task (403 if mismatch)

    Example Success Response:
        {
            "status": "success",
            "task": {
                "id": 1,
                "user_id": "user123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": true,
                "created_at": "2025-01-14T12:00:00",
                "updated_at": "2025-01-14T13:30:00"
            }
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

            # Update task completion status
            task.completed = True
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
