# [Task T018] Event schemas for CloudEvents format

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field
from app.models.task import PriorityEnum, RecurrenceEnum


class CloudEventMetadata(BaseModel):
    """CloudEvents metadata wrapper."""
    id: str = Field(..., description="Unique event ID")
    source: str = Field(..., description="Event source (e.g., 'todo-backend')")
    specversion: str = Field(default="1.0", description="CloudEvents spec version")
    type: str = Field(..., description="Event type (e.g., 'task.created.v1')")
    datacontenttype: str = Field(default="application/json", description="Content type")
    time: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")


class TaskEventData(BaseModel):
    """Task data included in task events."""
    task_id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: Optional[PriorityEnum]
    tags: Optional[list[str]]
    due_date: Optional[datetime]
    recurrence: Optional[RecurrenceEnum]
    recurrence_interval: Optional[int]
    parent_task_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class TaskCreatedEvent(BaseModel):
    """Event published when a task is created."""
    type: Literal["task.created.v1"] = "task.created.v1"
    task_id: int
    user_id: str
    task_data: TaskEventData


class TaskUpdatedEvent(BaseModel):
    """Event published when a task is updated."""
    type: Literal["task.updated.v1"] = "task.updated.v1"
    task_id: int
    user_id: str
    task_data: TaskEventData
    changes: dict  # Fields that were changed


class TaskCompletedEvent(BaseModel):
    """Event published when a task is marked complete."""
    type: Literal["task.completed.v1"] = "task.completed.v1"
    task_id: int
    user_id: str
    task_data: TaskEventData
    completed_at: datetime


class TaskDeletedEvent(BaseModel):
    """Event published when a task is deleted."""
    type: Literal["task.deleted.v1"] = "task.deleted.v1"
    task_id: int
    user_id: str


class ReminderScheduledEvent(BaseModel):
    """Event published when a reminder should be sent."""
    type: Literal["reminder.scheduled.v1"] = "reminder.scheduled.v1"
    task_id: int
    user_id: str
    title: str
    due_at: datetime
    remind_at: datetime  # When the reminder was/will be sent


class TaskUpdateMessage(BaseModel):
    """Real-time task update message for WebSocket."""
    type: Literal["task.updated.v1"] = "task.updated.v1"
    task_id: int
    changes: dict  # Changed fields
