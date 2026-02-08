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
from app.models.task import Task, PriorityEnum, RecurrenceEnum

logger = logging.getLogger(__name__)


async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[list[str]] = None,
    due_date: Optional[str] = None,
    recurrence: Optional[str] = None,
    recurrence_interval: Optional[int] = None
) -> Dict[str, Any]:
    """
    Update an existing task for a user with Phase 5 fields.

    Args:
        user_id: ID of the user owning the task (required)
        task_id: ID of the task to update (required)
        title: New task title (optional)
        description: New task description (optional)
        priority: Task priority (high, medium, low) (optional)
        tags: List of tags (optional)
        due_date: Due date in ISO format (optional)
        recurrence: Recurrence pattern (daily, weekly, monthly, custom) (optional)
        recurrence_interval: Interval for custom recurrence (optional)

    Returns:
        Dictionary with updated task details:
        {
            "success": True,
            "task": {
                "id": int,
                "title": str,
                "description": str | None,
                "completed": bool,
                "user_id": int,
                "priority": str | None,
                "tags": list[str] | None,
                "due_date": str | None,
                "recurrence": str | None,
                "recurrence_interval": int | None
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
    if all(v is None for v in [title, description, priority, tags, due_date, recurrence, recurrence_interval]):
        logger.error("No updates provided")
        raise ValueError("At least one field must be provided for update")

    # Validate and trim title if provided
    if title is not None:
        if not title.strip():
            logger.error("Empty title provided")
            raise ValueError("title cannot be empty")
        title = title.strip()

    # Trim description if provided
    if description is not None:
        description = description.strip() if description.strip() else None

    # Validate and convert priority
    priority_enum = None
    if priority is not None:
        try:
            priority_enum = PriorityEnum(priority.lower())
        except ValueError:
            raise ValueError(f"Invalid priority: {priority}. Must be one of: high, medium, low")

    # Validate and convert recurrence
    recurrence_enum = None
    if recurrence is not None:
        try:
            recurrence_enum = RecurrenceEnum(recurrence.lower())
        except ValueError:
            raise ValueError(f"Invalid recurrence: {recurrence}. Must be one of: daily, weekly, monthly, custom")

        # Validate recurrence_interval for custom recurrence
        if recurrence_enum == RecurrenceEnum.CUSTOM and not recurrence_interval:
            raise ValueError("recurrence_interval is required when recurrence is 'custom'")

    # Parse due_date if provided
    due_date_dt = None
    if due_date is not None:
        try:
            due_date_dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f"Invalid due_date format: {due_date}. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")

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
            if priority is not None:
                task.priority = priority_enum.value if priority_enum else None
            if tags is not None:
                task.tags = tags
            if due_date is not None:
                task.due_date = due_date_dt
            if recurrence is not None:
                task.recurrence = recurrence_enum.value if recurrence_enum else None
            if recurrence_interval is not None:
                task.recurrence_interval = recurrence_interval

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
                    "user_id": task.user_id,
                    "priority": task.priority,  # Already a string from database
                    "tags": task.tags,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "recurrence": task.recurrence,  # Already a string from database
                    "recurrence_interval": task.recurrence_interval
                },
                "message": f"Task updated successfully"
            }

    except ValueError:
        # Re-raise validation errors
        raise
    except Exception as e:
        logger.error(f"Failed to update task: {e}")
        raise Exception(f"Database error: {str(e)}")
