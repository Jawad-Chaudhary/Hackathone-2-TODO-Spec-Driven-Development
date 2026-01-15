# [Task]: T-014
# [From]: specs/001-ai-todo-chatbot/tasks.md

"""
List Tasks MCP Tool

Retrieves all tasks for a user with optional status filtering.
Enforces user isolation by filtering on user_id.

Input Schema:
    - user_id: str (required) - User ID whose tasks to list
    - status: str (optional) - Filter by status: "all", "pending", or "completed"

Output:
    JSON response with array of tasks matching the filter
"""

import json
from typing import Any

from mcp.types import TextContent
from sqlmodel import select

from ..database.session import async_session
from ..models.task import Task


async def list_tasks(arguments: dict[str, Any]) -> list[TextContent]:
    """
    List all tasks for a user with optional status filter.

    Args:
        arguments: Dict containing:
            - user_id (str): User ID whose tasks to list
            - status (str, optional): Filter by "all", "pending", or "completed" (default: "all")

    Returns:
        list[TextContent]: JSON response with task array or error

    Validation:
        - user_id: required, non-empty string
        - status: optional, must be "all", "pending", or "completed"

    Example Success Response:
        {
            "status": "success",
            "tasks": [
                {
                    "id": 1,
                    "user_id": "user123",
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                    "completed": false,
                    "created_at": "2025-01-14T12:00:00",
                    "updated_at": "2025-01-14T12:00:00"
                },
                {
                    "id": 2,
                    "user_id": "user123",
                    "title": "Complete project",
                    "description": null,
                    "completed": true,
                    "created_at": "2025-01-13T10:00:00",
                    "updated_at": "2025-01-14T09:00:00"
                }
            ],
            "count": 2
        }

    Example Error Response:
        {
            "error": "status must be 'all', 'pending', or 'completed'",
            "status": "error"
        }
    """
    # Validate required fields
    user_id = arguments.get("user_id")

    if not user_id:
        return [TextContent(type="text", text=json.dumps({
            "error": "user_id is required",
            "status": "error"
        }))]

    status = arguments.get("status", "all")

    # Validate status filter
    if status not in ["all", "pending", "completed"]:
        return [TextContent(type="text", text=json.dumps({
            "error": "status must be 'all', 'pending', or 'completed'",
            "status": "error"
        }))]

    # Query database with user isolation
    try:
        async with async_session() as session:
            # Base query with user isolation
            stmt = select(Task).where(Task.user_id == user_id)

            # Apply status filter
            if status == "pending":
                stmt = stmt.where(Task.completed == False)
            elif status == "completed":
                stmt = stmt.where(Task.completed == True)

            # Order by created_at descending (newest first)
            stmt = stmt.order_by(Task.created_at.desc())

            result = await session.execute(stmt)
            tasks = result.scalars().all()

            task_list = [
                {
                    "id": task.id,
                    "user_id": task.user_id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in tasks
            ]

            response = {
                "status": "success",
                "tasks": task_list,
                "count": len(task_list)
            }
            return [TextContent(type="text", text=json.dumps(response))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({
            "error": f"Database error: {str(e)}",
            "status": "error"
        }))]
