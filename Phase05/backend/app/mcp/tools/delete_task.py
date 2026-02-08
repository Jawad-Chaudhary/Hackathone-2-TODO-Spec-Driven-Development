"""
delete_task MCP tool for removing existing tasks.

This tool deletes a task for a user with validation,
ownership verification, and returns deletion confirmation.
"""

import logging
from typing import Dict, Any
from sqlmodel import select

from app.database import get_session
from app.models.task import Task

logger = logging.getLogger(__name__)


async def delete_task(
    user_id: str,
    task_id: int
) -> Dict[str, Any]:
    """
    Delete an existing task for a user.

    Args:
        user_id: ID of the user deleting the task (required)
        task_id: ID of the task to delete (required)

    Returns:
        Dictionary with deletion details:
        {
            "success": True,
            "task_id": int,
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
        # Delete task from database with ownership verification
        async for db in get_session():
            # Query for task with user ownership check
            stmt = select(Task).where(
                Task.id == task_id,
                Task.user_id == str(user_id)  # Convert to match model's string type
            )
            result = await db.execute(stmt)
            task = result.scalar_one_or_none()

            # Check if task exists
            if not task:
                logger.warning(f"Task not found or access denied: task_id={task_id}, user_id={user_id}")
                raise Exception(f"Task with id {task_id} not found or you don't have permission to delete it")

            # Store task title for message
            task_title = task.title

            # Delete the task
            await db.delete(task)
            await db.commit()

            logger.info(f"Task deleted: id={task_id}, user_id={user_id}, title={task_title}")

            return {
                "success": True,
                "task_id": task_id,
                "message": f"Task '{task_title}' deleted successfully"
            }

    except Exception as e:
        logger.error(f"Failed to delete task: {e}")
        # Re-raise the exception if it's our custom message
        if "not found or you don't have permission" in str(e):
            raise
        # Otherwise wrap as database error
        raise Exception(f"Database error: {str(e)}")
