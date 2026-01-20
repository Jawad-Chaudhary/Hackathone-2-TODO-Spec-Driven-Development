"""
add_task MCP tool for creating new tasks.

This tool creates a new task for a user with validation
and returns the created task details.
"""

import logging
from typing import Optional, Dict, Any
from sqlmodel import Session, select

from app.database import get_session
from app.models.task import Task

logger = logging.getLogger(__name__)


async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a new task for a user.

    Args:
        user_id: ID of the user creating the task (required)
        title: Task title (required)
        description: Optional task description

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
        ValueError: If user_id is invalid or title is empty
        Exception: For database errors
    """
    # Validate user_id
    if not user_id or not isinstance(user_id, str) or len(user_id) == 0:
        logger.error(f"Invalid user_id: {user_id}")
        raise ValueError("user_id must be a non-empty string")

    # Validate title
    if not title or not title.strip():
        logger.error("Empty title provided")
        raise ValueError("title cannot be empty")

    title = title.strip()

    # Trim description if provided
    if description:
        description = description.strip() if description.strip() else None

    try:
        # Create task in database
        async for db in get_session():
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                completed=False
            )

            db.add(task)
            await db.commit()
            await db.refresh(task)

            logger.info(f"Task created: id={task.id}, user_id={user_id}, title={title}")

            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "user_id": task.user_id
                },
                "message": f"Task '{title}' created successfully"
            }

    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise Exception(f"Database error: {str(e)}")
