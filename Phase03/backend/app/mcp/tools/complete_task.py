"""
complete_task MCP tool for marking tasks as completed.

This tool updates a task's completed status with ownership validation
and returns the updated task details.
"""

import logging
from typing import Dict, Any
from sqlmodel import select

from app.database import get_session
from app.models.task import Task

logger = logging.getLogger(__name__)


async def complete_task(
    user_id: str,
    task_id: int
) -> Dict[str, Any]:
    """
    Mark a task as completed for a user.

    Args:
        user_id: ID of the user who owns the task (required)
        task_id: ID of the task to complete (required)

    Returns:
        Dictionary with task details:
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
        ValueError: If user_id or task_id is invalid
        Exception: For database errors or task not found
    """
    # Validate user_id
    if not user_id or len(user_id) == 0:
        logger.error(f"Invalid user_id: {user_id}")
        raise ValueError("user_id must be a non-empty string")

    # Validate task_id
    if not task_id or task_id <= 0:
        logger.error(f"Invalid task_id: {task_id}")
        raise ValueError("task_id must be a positive integer")

    try:
        # Query database for task with ownership check
        async for db in get_session():
            stmt = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            result = await db.execute(stmt)
            task = result.scalar_one_or_none()

            # Check if task exists and belongs to user
            if not task:
                logger.warning(f"Task not found or access denied: task_id={task_id}, user_id={user_id}")
                raise Exception(f"Task with id {task_id} not found or you don't have permission to access it")

            # Update task completion status
            task.completed = True
            from datetime import datetime
            task.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(task)

            logger.info(f"Task completed: id={task.id}, user_id={user_id}, title={task.title}")

            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "user_id": task.user_id
                },
                "message": f"Task '{task.title}' marked as completed"
            }

    except ValueError:
        # Re-raise validation errors
        raise
    except Exception as e:
        if "not found" in str(e):
            # Re-raise not found errors
            raise
        logger.error(f"Failed to complete task: {e}")
        raise Exception(f"Database error: {str(e)}")
