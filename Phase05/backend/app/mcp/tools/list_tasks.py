"""
list_tasks MCP tool for retrieving tasks.

This tool retrieves tasks for a user with optional status filtering
and returns the list of tasks with count.
"""

import logging
from typing import Dict, Any
from sqlmodel import select

from app.database import get_session
from app.models.task import Task

logger = logging.getLogger(__name__)


async def list_tasks(
    user_id: str,
    status: str = "all"
) -> Dict[str, Any]:
    """
    List all tasks for a user with optional status filtering.

    Args:
        user_id: ID of the user (required, non-empty string)
        status: Filter by status - "all", "pending", or "completed" (default: "all")

    Returns:
        Dictionary with task list and metadata:
        {
            "success": True,
            "tasks": [
                {
                    "id": int,
                    "title": str,
                    "description": str | None,
                    "completed": bool,
                    "user_id": str,
                    "created_at": str,
                    "updated_at": str,
                    "priority": str | None,
                    "tags": list[str] | None,
                    "due_date": str | None,
                    "recurrence": str | None,
                    "recurrence_interval": int | None,
                    "parent_task_id": int | None
                },
                ...
            ],
            "count": int,
            "message": str
        }

    Raises:
        ValueError: If user_id is invalid or status is not valid
        Exception: For database errors
    """
    # Validate user_id
    if not user_id or not isinstance(user_id, str) or not user_id.strip():
        logger.error(f"Invalid user_id: {user_id}")
        raise ValueError("user_id must be a non-empty string")

    # Validate status parameter
    valid_statuses = ["all", "pending", "completed"]
    if status not in valid_statuses:
        logger.error(f"Invalid status: {status}")
        raise ValueError(f"status must be one of: {', '.join(valid_statuses)}")

    user_id = user_id.strip()

    try:
        # Query database for tasks
        async for db in get_session():
            # Base query with user isolation
            stmt = select(Task).where(Task.user_id == user_id)

            # Apply status filter
            if status == "pending":
                stmt = stmt.where(Task.completed == False)
            elif status == "completed":
                stmt = stmt.where(Task.completed == True)

            # Order by created_at descending (newest first)
            stmt = stmt.order_by(Task.created_at.desc())

            result = await db.execute(stmt)
            tasks = result.scalars().all()

            # Convert tasks to dict format with Phase 5 fields
            task_list = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "user_id": task.user_id,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    # Phase 5 fields
                    "priority": task.priority if task.priority else None,
                    "tags": task.tags if task.tags else None,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "recurrence": task.recurrence if task.recurrence else None,
                    "recurrence_interval": task.recurrence_interval if task.recurrence_interval else None,
                    "parent_task_id": task.parent_task_id if task.parent_task_id else None
                }
                for task in tasks
            ]

            count = len(task_list)

            # Create appropriate message
            if status == "all":
                message = f"Retrieved {count} task(s)"
            else:
                message = f"Retrieved {count} {status} task(s)"

            logger.info(f"Tasks retrieved: user_id={user_id}, status={status}, count={count}")

            return {
                "success": True,
                "tasks": task_list,
                "count": count,
                "message": message
            }

    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise Exception(f"Database error: {str(e)}")
