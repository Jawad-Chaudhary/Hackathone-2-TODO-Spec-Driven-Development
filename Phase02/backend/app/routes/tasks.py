# [Tasks T032-T037] Task CRUD API Endpoints with user isolation
# [Tasks T048-T051] Task Update API Endpoint

from typing import List, Literal, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.dependencies.auth import get_current_user
from app.database import get_session


router = APIRouter(
    prefix="/api",
    tags=["tasks"],
)


# [Task T032, T033, T034] GET /api/{user_id}/tasks - List tasks with status filtering
@router.get(
    "/{user_id}/tasks",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all tasks for a user",
    description="Returns all tasks for the authenticated user, with optional status filtering",
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
) -> List[TaskResponse]:
    """
    Get all tasks for the authenticated user.

    Args:
        user_id: User ID from path parameter
        authenticated_user_id: User ID extracted from JWT token
        session: Database session
        status_filter: Optional filter for task status (all/pending/completed)

    Returns:
        List of tasks sorted by created_at DESC (newest first)

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

    # [Task T032] Sort by created_at DESC (newest first)
    query = query.order_by(Task.created_at.desc())

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
    new_task = Task(
        user_id=authenticated_user_id,
        title=task_data.title,
        description=task_data.description,
        completed=False,  # New tasks are always incomplete
    )

    # [Task T035] Save to database
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

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

    # [Task T051] Update updated_at timestamp automatically on every PUT
    task.updated_at = datetime.utcnow()

    # Save changes to database
    session.add(task)
    await session.commit()
    await session.refresh(task)

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

    # [Task T067] Hard delete task from database
    # Permanently remove the record (no soft delete)
    await session.delete(task)
    await session.commit()

    # Return 204 No Content (no response body)
