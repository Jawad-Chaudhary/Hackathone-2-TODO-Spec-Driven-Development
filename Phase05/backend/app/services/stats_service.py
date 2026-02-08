# [Task T083] Stats service for dashboard statistics

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from app.models.task import Task


async def get_user_stats(user_id: str, session: AsyncSession) -> dict:
    """
    Get dashboard statistics for a user.

    Args:
        user_id: The user's ID
        session: Database session

    Returns:
        Dictionary with counts: {total, completed, pending, overdue}
    """
    # Get total count
    total_query = select(func.count(Task.id)).where(Task.user_id == user_id)
    total_result = await session.execute(total_query)
    total = total_result.scalar() or 0

    # Get completed count
    completed_query = select(func.count(Task.id)).where(
        Task.user_id == user_id,
        Task.completed == True
    )
    completed_result = await session.execute(completed_query)
    completed = completed_result.scalar() or 0

    # Get pending count
    pending_query = select(func.count(Task.id)).where(
        Task.user_id == user_id,
        Task.completed == False
    )
    pending_result = await session.execute(pending_query)
    pending = pending_result.scalar() or 0

    # Get overdue count (pending tasks with due_date < now)
    now = datetime.utcnow()
    overdue_query = select(func.count(Task.id)).where(
        Task.user_id == user_id,
        Task.completed == False,
        Task.due_date < now
    )
    overdue_result = await session.execute(overdue_query)
    overdue = overdue_result.scalar() or 0

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "overdue": overdue
    }
