"""
add_task MCP tool for creating new tasks.

This tool creates a new task for a user with validation
and returns the created task details.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import Session, select

from app.database import get_session
from app.models.task import Task, PriorityEnum, RecurrenceEnum

logger = logging.getLogger(__name__)


async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[list[str]] = None,
    due_date: Optional[str] = None,
    recurrence: Optional[str] = None,
    recurrence_interval: Optional[int] = None
) -> Dict[str, Any]:
    """
    Add a new task for a user with Phase 5 advanced features.

    Args:
        user_id: ID of the user creating the task (required)
        title: Task title (required)
        description: Optional task description
        priority: Task priority (high, medium, low)
        tags: List of tags for categorization
        due_date: Due date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        recurrence: Recurrence pattern (daily, weekly, monthly, custom)
        recurrence_interval: Interval for custom recurrence (days)

    Returns:
        Dictionary with task details:
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
        ValueError: If user_id is invalid, title is empty, or parameters are invalid
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

    # Validate and convert priority
    priority_enum = None
    if priority:
        try:
            priority_enum = PriorityEnum(priority.lower())
        except ValueError:
            raise ValueError(f"Invalid priority: {priority}. Must be one of: high, medium, low")

    # Validate and convert recurrence
    recurrence_enum = None
    if recurrence:
        try:
            recurrence_enum = RecurrenceEnum(recurrence.lower())
        except ValueError:
            raise ValueError(f"Invalid recurrence: {recurrence}. Must be one of: daily, weekly, monthly, custom")

        # Validate recurrence_interval for custom recurrence
        if recurrence_enum == RecurrenceEnum.CUSTOM and not recurrence_interval:
            raise ValueError("recurrence_interval is required when recurrence is 'custom'")
        if recurrence_interval and recurrence_interval < 1:
            raise ValueError("recurrence_interval must be a positive integer")

    # Parse due_date if provided
    due_date_dt = None
    if due_date:
        try:
            # Try parsing ISO format
            due_date_dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f"Invalid due_date format: {due_date}. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")

    try:
        # Create task in database
        async for db in get_session():
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                completed=False,
                priority=priority_enum.value if priority_enum else None,
                tags=tags,
                due_date=due_date_dt,
                recurrence=recurrence_enum.value if recurrence_enum else None,
                recurrence_interval=recurrence_interval
            )

            db.add(task)
            await db.commit()
            await db.refresh(task)

            logger.info(f"Task created: id={task.id}, user_id={user_id}, title={title}, recurrence={recurrence_enum}")

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
                "message": f"Task '{title}' created successfully"
            }

    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise Exception(f"Database error: {str(e)}")
