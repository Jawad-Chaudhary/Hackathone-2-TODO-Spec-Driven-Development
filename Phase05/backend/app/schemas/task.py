# [Task T016] Pydantic schemas for Task validation with Phase 5 fields

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.models.task import PriorityEnum, RecurrenceEnum


class TaskCreate(BaseModel):
    """Schema for creating a new task with Phase 5 advanced features."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title (required)")
    description: Optional[str] = Field(None, max_length=1000, description="Task description (optional)")
    priority: Optional[PriorityEnum] = Field(None, description="Task priority: high, medium, or low")
    tags: Optional[list[str]] = Field(None, description="List of tags for categorization")
    due_date: Optional[datetime] = Field(None, description="Task due date and time")
    recurrence: Optional[RecurrenceEnum] = Field(None, description="Recurrence pattern: daily, weekly, monthly, custom")
    recurrence_interval: Optional[int] = Field(None, description="Recurrence interval (for custom recurrence)")


class TaskUpdate(BaseModel):
    """Schema for updating an existing task. All fields are optional."""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated task title")
    description: Optional[str] = Field(None, max_length=1000, description="Updated task description")
    completed: Optional[bool] = Field(None, description="Task completion status")
    priority: Optional[PriorityEnum] = Field(None, description="Updated priority")
    tags: Optional[list[str]] = Field(None, description="Updated tags")
    due_date: Optional[datetime] = Field(None, description="Updated due date")
    recurrence: Optional[RecurrenceEnum] = Field(None, description="Updated recurrence pattern")
    recurrence_interval: Optional[int] = Field(None, description="Updated recurrence interval")


class TaskResponse(BaseModel):
    """Schema for task response returned to client with Phase 5 fields."""

    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
    # Phase 5 fields
    priority: Optional[PriorityEnum]
    tags: Optional[list[str]]
    due_date: Optional[datetime]
    recurrence: Optional[RecurrenceEnum]
    recurrence_interval: Optional[int]
    parent_task_id: Optional[int]

    model_config = {"from_attributes": True}

    @field_validator('priority', mode='before')
    @classmethod
    def convert_priority_str_to_enum(cls, v):
        """Convert string from database to PriorityEnum for API response."""
        if v is None or isinstance(v, PriorityEnum):
            return v
        return PriorityEnum(v)

    @field_validator('recurrence', mode='before')
    @classmethod
    def convert_recurrence_str_to_enum(cls, v):
        """Convert string from database to RecurrenceEnum for API response."""
        if v is None or isinstance(v, RecurrenceEnum):
            return v
        return RecurrenceEnum(v)
