# [Tasks T032-T037] Task CRUD API Endpoints with user isolation
# [Tasks T048-T051] Task Update API Endpoint
# [Tasks T056-T057] Add priority and tags filtering
# [Task T084] Dashboard stats endpoint

from typing import List, Literal, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.task import Task, PriorityEnum
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.dependencies.auth import get_current_user
from app.database import get_session
from app.services.stats_service import get_user_stats
import httpx
import logging

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api",
    tags=["tasks"],
)


# Helper function to send notifications to WebSocket clients
async def send_notification(user_id: str, notification_data: dict):
    """Send notification to WebSocket clients via internal endpoint."""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"http://localhost:8000/notify/{user_id}",
                json=notification_data,
                timeout=2.0
            )
    except Exception as e:
        # Log but don't fail the request if notification fails
        logger.warning(f"Failed to send notification: {e}")


# [Task T032, T033, T034] GET /api/{user_id}/tasks - List tasks with status filtering
# [Task T056] Add priority filtering
# [Task T057] Add tags filtering
# [Task T065] Add search query parameter
# [Task T067] Add due_start and due_end date range filtering
# [User Story 5] Add sorting support
@router.get(
    "/{user_id}/tasks",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all tasks for a user",
    description="Returns all tasks for the authenticated user, with optional filtering, search, and sorting",
)
async def get_tasks(
    user_id: str,
    authenticated_user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    status_filter: Literal["all", "pending", "completed"] = Query(
        "all",
        alias="status",
        description="Filter tasks by completion status: 'all' (default), 'pending', or 'completed'",
    ),
    priority: Optional[Literal["high", "medium", "low"]] = Query(
        None,
        description="Filter tasks by priority level"
    ),
    tags: Optional[List[str]] = Query(
        None,
        description="Filter tasks by tags (AND logic - task must have all specified tags)"
    ),
    search: Optional[str] = Query(
        None,
        description="Search tasks by title or description (case-insensitive partial match)"
    ),
    due_start: Optional[str] = Query(
        None,
        description="Filter tasks with due_date >= this date (ISO format)"
    ),
    due_end: Optional[str] = Query(
        None,
        description="Filter tasks with due_date <= this date (ISO format)"
    ),
    sort_by: Literal["created", "due_date", "priority", "title"] = Query(
        "created",
        description="Sort tasks by: created (default), due_date, priority, or title"
    ),
    sort_order: Literal["asc", "desc"] = Query(
        "desc",
        description="Sort order: asc (ascending) or desc (descending, default)"
    ),
) -> List[TaskResponse]:
    """
    Get all tasks for the authenticated user with filtering, search, and sorting.

    Args:
        user_id: User ID from path parameter
        authenticated_user_id: User ID extracted from JWT token
        session: Database session
        status_filter: Optional filter for task status (all/pending/completed)
        priority: Optional filter for priority level (high/medium/low)
        tags: Optional list of tags (AND logic - task must have all)
        search: Optional search query for title/description
        due_start: Optional start date for due_date range filter
        due_end: Optional end date for due_date range filter
        sort_by: Sort field (created, due_date, priority, title)
        sort_order: Sort direction (asc, desc)

    Returns:
        List of tasks sorted according to sort_by and sort_order parameters

    Raises:
        HTTPException 404: If user_id doesn't match authenticated user (prevents info leakage)
    """
    # [Task T033] Verify user_id matches authenticated user
    # Use 404 instead of 403 to prevent information leakage
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    # [Task T034] Build query with status filtering
    query = select(Task).where(Task.user_id == user_id)

    if status_filter == "pending":
        query = query.where(Task.completed == False)
    elif status_filter == "completed":
        query = query.where(Task.completed == True)
    # For "all", no additional filter needed

    # [Task T056] Add priority filtering
    if priority:
        # Cast priority string to enum value for comparison
        # Use the string value directly to avoid PostgreSQL type casting issues
        query = query.where(Task.priority == priority)

    # [Task T057] Add tags filtering (AND logic - task must have all specified tags)
    if tags and len(tags) > 0:
        # PostgreSQL JSONB contains operator (@>) checks if all elements are present
        # For SQLAlchemy, we need to check if all tags are in the task.tags array
        for tag in tags:
            # Use JSONB contains check: task.tags must contain the tag
            query = query.where(Task.tags.contains([tag]))

    # [Task T065] Add search filtering (case-insensitive partial match on title or description)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Task.title.ilike(search_pattern)) |
            (Task.description.ilike(search_pattern))
        )

    # [Task T067] Add due date range filtering
    if due_start:
        try:
            due_start_dt = datetime.fromisoformat(due_start.replace('Z', '+00:00'))
            query = query.where(Task.due_date >= due_start_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid due_start date format: {due_start}"
            )

    if due_end:
        try:
            due_end_dt = datetime.fromisoformat(due_end.replace('Z', '+00:00'))
            query = query.where(Task.due_date <= due_end_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid due_end date format: {due_end}"
            )

    # [User Story 5] [Task T078] Dynamic sorting based on sort_by and sort_order parameters
    if sort_by == "created":
        order_field = Task.created_at
    elif sort_by == "due_date":
        # NULL values last for both ASC and DESC
        order_field = Task.due_date.nullslast() if sort_order == "asc" else Task.due_date.nullsfirst()
    elif sort_by == "priority":
        # Priority enum: high > medium > low (alphabetically reversed for proper ordering)
        order_field = Task.priority
    elif sort_by == "title":
        order_field = Task.title
    else:
        # Default fallback to created_at
        order_field = Task.created_at

    # Apply sort order only for non-nullable fields (due_date handled above)
    if sort_by != "due_date":
        if sort_order == "asc":
            query = query.order_by(order_field.asc())
        else:
            query = query.order_by(order_field.desc())
    else:
        # For due_date, nullslast/nullsfirst already applied
        if sort_order == "asc":
            query = query.order_by(order_field.asc())
        else:
            query = query.order_by(order_field.desc())

    # Execute query
    result = await session.execute(query)
    tasks = result.scalars().all()

    return tasks


# [Task T035, T036, T037] POST /api/{user_id}/tasks - Create new task
@router.post(
    "/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Creates a new task for the authenticated user",
)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    authenticated_user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """
    Create a new task for the authenticated user.

    Args:
        user_id: User ID from path parameter
        task_data: Task creation data (title, description)
        authenticated_user_id: User ID extracted from JWT token
        session: Database session

    Returns:
        Created task with all fields including generated ID and timestamps

    Raises:
        HTTPException 404: If user_id doesn't match authenticated user
        HTTPException 422: If validation fails (handled by FastAPI/Pydantic)
    """
    # [Task T033] Verify user_id matches authenticated user
    # Use 404 instead of 403 to prevent information leakage
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    # [Task T037] Automatic user_id injection from JWT
    # NEVER trust user_id from request body - always use authenticated user ID

    # Debug logging
    logger.info(f"Received task data: priority={task_data.priority} (type={type(task_data.priority)}), tags={task_data.tags}, recurrence={task_data.recurrence}")

    new_task = Task(
        user_id=authenticated_user_id,
        title=task_data.title,
        description=task_data.description,
        completed=False,  # New tasks are always incomplete
        # Phase 5 fields - convert enum to string value for database storage
        priority=task_data.priority.value if task_data.priority else None,
        tags=task_data.tags,
        due_date=task_data.due_date,  # Pydantic already parsed it as datetime
        recurrence=task_data.recurrence.value if task_data.recurrence else None,
        recurrence_interval=task_data.recurrence_interval,
    )

    # [Task T035] Save to database
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    # Send notification to WebSocket service
    await send_notification(authenticated_user_id, {
        "type": "task_update",
        "event_type": "task.created.v1",
        "task_id": new_task.id,
        "task_data": {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "completed": new_task.completed,
            "priority": new_task.priority,
            "tags": new_task.tags,
            "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
            "created_at": new_task.created_at.isoformat() if new_task.created_at else None,
        },
        "timestamp": datetime.utcnow().isoformat()
    })

    return new_task


# [Task T048, T049, T050, T051] PUT /api/{user_id}/tasks/{id} - Update existing task
@router.put(
    "/{user_id}/tasks/{id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing task",
    description="Updates an existing task for the authenticated user. All fields are optional (partial update).",
)
async def update_task(
    user_id: str,
    id: int,
    task_data: TaskUpdate,
    authenticated_user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """
    Update an existing task for the authenticated user.

    Args:
        user_id: User ID from path parameter
        id: Task ID to update
        task_data: Task update data (all fields optional)
        authenticated_user_id: User ID extracted from JWT token
        session: Database session

    Returns:
        Updated task with all fields including updated timestamp

    Raises:
        HTTPException 401: If JWT is invalid or missing
        HTTPException 404: If user_id doesn't match authenticated user OR task not found
        HTTPException 422: If validation fails (invalid title/description)
    """
    # [Task T050] Verify user_id matches authenticated user
    # Use 404 instead of 403 to prevent information leakage
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    # [Task T048] Query database for task by id
    task = await session.get(Task, id)

    # [Task T050] Verify task exists and belongs to authenticated user
    # Return 404 if task not found OR if task belongs to different user (prevents info leakage)
    if task is None or task.user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    # [Task T049] Update only fields that are provided (partial update)
    # TaskUpdate schema validates: title (1-200 chars), description (max 1000 chars), completed (bool)
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed

    # Phase 5 field updates - convert enum to string value for database storage
    if task_data.priority is not None:
        task.priority = task_data.priority.value if task_data.priority else None
    if task_data.tags is not None:
        task.tags = task_data.tags
    if task_data.due_date is not None:
        task.due_date = task_data.due_date  # Pydantic already parsed it as datetime
    if task_data.recurrence is not None:
        task.recurrence = task_data.recurrence.value if task_data.recurrence else None
    if task_data.recurrence_interval is not None:
        task.recurrence_interval = task_data.recurrence_interval

    # [Task T051] Update updated_at timestamp automatically on every PUT
    task.updated_at = datetime.utcnow()

    # Save changes to database
    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Send notification for task update
    event_type = "task.completed.v1" if task.completed else "task.updated.v1"
    await send_notification(authenticated_user_id, {
        "type": "task_update",
        "event_type": event_type,
        "task_id": task.id,
        "task_data": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "tags": task.tags,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        },
        "timestamp": datetime.utcnow().isoformat()
    })

    return task


# [Task T065, T066, T067] DELETE /api/{user_id}/tasks/{id} - Delete task
@router.delete(
    "/{user_id}/tasks/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Permanently deletes a task for the authenticated user",
)
async def delete_task(
    user_id: str,
    id: int,
    authenticated_user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """
    Delete a task for the authenticated user.

    Args:
        user_id: User ID from path parameter
        id: Task ID to delete
        authenticated_user_id: User ID extracted from JWT token
        session: Database session

    Returns:
        204 No Content on success (no response body)

    Raises:
        HTTPException 401: If JWT is invalid or missing
        HTTPException 404: If user_id doesn't match authenticated user OR task not found
    """
    # [Task T066] Verify user_id matches authenticated user
    # Use 404 instead of 403 to prevent information leakage
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    # [Task T065] Query database for task by id
    task = await session.get(Task, id)

    # [Task T066] Verify task exists and belongs to authenticated user
    # Return 404 if task not found OR if task belongs to different user (prevents info leakage)
    if task is None or task.user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    # Store task info before deletion for notification
    task_id = task.id
    task_title = task.title

    # [Task T067] Hard delete task from database
    # Permanently remove the record (no soft delete)
    await session.delete(task)
    await session.commit()

    # Send notification for task deletion
    await send_notification(authenticated_user_id, {
        "type": "task_update",
        "event_type": "task.deleted.v1",
        "task_id": task_id,
        "task_data": {
            "id": task_id,
            "title": task_title,
        },
        "timestamp": datetime.utcnow().isoformat()
    })

    # Return 204 No Content (no response body)


# GET /api/{user_id}/tasks/{id} - Get single task details
@router.get(
    "/{user_id}/tasks/{id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single task by ID",
    description="Returns details of a specific task for the authenticated user",
)
async def get_task_by_id(
    user_id: str,
    id: int,
    authenticated_user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """
    Get a single task by ID for the authenticated user.

    Args:
        user_id: User ID from path parameter
        id: Task ID to retrieve
        authenticated_user_id: User ID extracted from JWT token
        session: Database session

    Returns:
        Task details with all fields

    Raises:
        HTTPException 401: If JWT is invalid or missing
        HTTPException 404: If user_id doesn't match authenticated user OR task not found
    """
    # Verify user_id matches authenticated user
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    # Query database for task by id
    task = await session.get(Task, id)

    # Verify task exists and belongs to authenticated user
    if task is None or task.user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    return task


# PATCH /api/{user_id}/tasks/{id}/complete - Toggle task completion
@router.patch(
    "/{user_id}/tasks/{id}/complete",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle task completion status",
    description="Toggles the completion status of a task (completed ↔ pending)",
)
async def toggle_task_completion(
    user_id: str,
    id: int,
    authenticated_user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """
    Toggle the completion status of a task.

    This endpoint flips the task's completed status:
    - If task is completed (True), it becomes pending (False)
    - If task is pending (False), it becomes completed (True)

    Args:
        user_id: User ID from path parameter
        id: Task ID to toggle
        authenticated_user_id: User ID extracted from JWT token
        session: Database session

    Returns:
        Updated task with toggled completion status

    Raises:
        HTTPException 401: If JWT is invalid or missing
        HTTPException 404: If user_id doesn't match authenticated user OR task not found
    """
    # Verify user_id matches authenticated user
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    # Query database for task by id
    task = await session.get(Task, id)

    # Verify task exists and belongs to authenticated user
    if task is None or task.user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    # Toggle completion status
    task.completed = not task.completed

    # Update timestamp
    task.updated_at = datetime.utcnow()

    # Save changes to database
    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


# [Task T084] GET /api/{user_id}/dashboard/stats - Get dashboard statistics
@router.get(
    "/{user_id}/dashboard/stats",
    status_code=status.HTTP_200_OK,
    summary="Get dashboard statistics",
    description="Returns task statistics for the authenticated user: total, completed, pending, overdue counts",
)
async def get_dashboard_stats(
    user_id: str,
    authenticated_user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Get dashboard statistics for the authenticated user.

    Args:
        user_id: User ID from path parameter
        authenticated_user_id: User ID extracted from JWT token
        session: Database session

    Returns:
        Dictionary with counts: {total, completed, pending, overdue}

    Raises:
        HTTPException 404: If user_id doesn't match authenticated user
    """
    # Verify user_id matches authenticated user
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    # Get statistics
    stats = await get_user_stats(user_id, session)

    return stats
