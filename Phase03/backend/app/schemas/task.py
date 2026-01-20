# [Task T012] Pydantic schemas for Task validation and serialization

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title (required)")
    description: Optional[str] = Field(None, max_length=1000, description="Task description (optional)")


class TaskUpdate(BaseModel):
    """Schema for updating an existing task. All fields are optional."""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated task title")
    description: Optional[str] = Field(None, max_length=1000, description="Updated task description")
    completed: Optional[bool] = Field(None, description="Task completion status")


class TaskResponse(BaseModel):
    """Schema for task response returned to client."""

    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
