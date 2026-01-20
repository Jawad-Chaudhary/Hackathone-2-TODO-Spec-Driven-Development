"""
update_task MCP tool for updating existing tasks.

This tool updates a task's title and/or description with validation,
ownership verification, and returns the updated task details.
"""

import logging
from typing import Optional, Dict, Any
from sqlmodel import select
from datetime import datetime

from app.database import get_session
from app.models.task import Task

logger = logging.getLogger(__name__)


async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing task for a user.

    Args:
        user_id: ID of the user owning the task (required)
        task_id: ID of the task to update (required)
        title: New task title (optional)
        description: New task description (optional)

    Returns:
        Dictionary with updated task details:
        {
            "success": True,
            "task": {
                "id": int,
                "title": str,
                "description": str | None,
                "completed": bool,
                "user_id": int
            },
            "message": str
        }

    Raises:
        ValueError: If user_id/task_id is invalid, no updates provided, or task not found
        Exception: For database errors
    """
    # Validate user_id
    if not user_id or len(user_id) == 0:
        logger.error(f"Invalid user_id: {user_id}")
        raise ValueError("user_id must be a non-empty string")

    # Validate task_id
    if not task_id or task_id <= 0:
        logger.error(f"Invalid task_id: {task_id}")
        raise ValueError("task_id must be a positive integer")

    # At least one update must be provided
    if title is None and description is None:
        logger.error("No updates provided")
        raise ValueError("At least one of title or description must be provided")

    # Validate and trim title if provided
    if title is not None:
        if not title.strip():
            logger.error("Empty title provided")
            raise ValueError("title cannot be empty")
        title = title.strip()

    # Trim description if provided
    if description is not None:
        description = description.strip() if description.strip() else None

    try:
        # Query and update task in database
        async for db in get_session():
            # Find task by id and user_id (ownership check)
            stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            result = await db.execute(stmt)
            task = result.scalar_one_or_none()

            if not task:
                logger.error(f"Task not found: id={task_id}, user_id={user_id}")
                raise ValueError(f"Task with id {task_id} not found or does not belong to user {user_id}")

            # Update provided fields
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description

            # Update timestamp
            task.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(task)

            logger.info(f"Task updated: id={task.id}, user_id={user_id}")

            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "user_id": task.user_id
                },
                "message": f"Task updated successfully"
            }

    except ValueError:
        # Re-raise validation errors
        raise
    except Exception as e:
        logger.error(f"Failed to update task: {e}")
        raise Exception(f"Database error: {str(e)}")
