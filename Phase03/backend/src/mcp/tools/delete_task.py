# [Task]: T-016
# [From]: specs/001-ai-todo-chatbot/tasks.md

"""
Delete Task MCP Tool

Deletes a task for a user.
Enforces user isolation - only the task owner can delete their tasks.

Input Schema:
    - user_id: str (required) - User ID who owns the task
    - task_id: int (required) - ID of the task to delete

Output:
    JSON response with success status or error message
"""

import json
from typing import Any

from mcp.types import TextContent
from sqlmodel import select

from ..database.session import async_session
from ..models.task import Task


async def delete_task(arguments: dict[str, Any]) -> list[TextContent]:
    """
    Delete a task.

    Args:
        arguments: Dict containing:
            - user_id (str): User ID who owns the task
            - task_id (int): ID of the task to delete

    Returns:
        list[TextContent]: JSON response with status or error

    Validation:
        - user_id: required, non-empty string
        - task_id: required, must exist and belong to user_id
        - Ownership: Only the task owner can delete the task (403 if mismatch)

    Example Success Response:
        {
            "status": "success",
            "message": "Task 1 deleted successfully"
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

    # Query and delete with user isolation
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

            # Delete task
            await session.delete(task)
            await session.commit()

            response = {
                "status": "success",
                "message": f"Task {task_id} deleted successfully"
            }
            return [TextContent(type="text", text=json.dumps(response))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({
            "error": f"Database error: {str(e)}",
            "status": "error"
        }))]
