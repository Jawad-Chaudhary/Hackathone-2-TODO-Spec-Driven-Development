# [Task T020] Event publisher service for task events

from datetime import datetime
from typing import Optional
import uuid
import logging

from app.dapr_config import dapr_client
from app.events.schemas import (
    TaskCreatedEvent,
    TaskUpdatedEvent,
    TaskCompletedEvent,
    TaskDeletedEvent,
    ReminderScheduledEvent,
    TaskEventData
)
from app.models.task import Task

logger = logging.getLogger(__name__)


class EventPublisher:
    """Service for publishing task-related events to Dapr Pub/Sub."""

    def __init__(self):
        self.task_events_topic = "task-events"
        self.task_updates_topic = "task-updates"
        self.reminders_topic = "reminders"

    def _task_to_event_data(self, task: Task) -> TaskEventData:
        """Convert Task model to TaskEventData."""
        return TaskEventData(
            task_id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            priority=task.priority,
            tags=task.tags or [],
            due_date=task.due_date,
            recurrence=task.recurrence,
            recurrence_interval=task.recurrence_interval,
            parent_task_id=task.parent_task_id,
            created_at=task.created_at,
            updated_at=task.updated_at
        )

    async def publish_task_created(self, task: Task) -> None:
        """
        Publish task.created.v1 event.

        Args:
            task: The created task
        """
        event = TaskCreatedEvent(
            task_id=task.id,
            user_id=task.user_id,
            task_data=self._task_to_event_data(task)
        )

        await dapr_client.publish_event(
            topic=self.task_events_topic,
            data=event.model_dump(),
            metadata={
                "cloudevent.id": str(uuid.uuid4()),
                "cloudevent.source": "todo-backend",
                "cloudevent.type": "task.created.v1",
                "cloudevent.specversion": "1.0"
            }
        )
        logger.info(f"Published task.created.v1 event for task {task.id}")

    async def publish_task_updated(self, task: Task, changes: dict) -> None:
        """
        Publish task.updated.v1 event.

        Args:
            task: The updated task
            changes: Dictionary of changed fields
        """
        event = TaskUpdatedEvent(
            task_id=task.id,
            user_id=task.user_id,
            task_data=self._task_to_event_data(task),
            changes=changes
        )

        await dapr_client.publish_event(
            topic=self.task_events_topic,
            data=event.model_dump(),
            metadata={
                "cloudevent.id": str(uuid.uuid4()),
                "cloudevent.source": "todo-backend",
                "cloudevent.type": "task.updated.v1",
                "cloudevent.specversion": "1.0"
            }
        )
        logger.info(f"Published task.updated.v1 event for task {task.id}")

    async def publish_task_completed(self, task: Task) -> None:
        """
        Publish task.completed.v1 event.

        Args:
            task: The completed task
        """
        event = TaskCompletedEvent(
            task_id=task.id,
            user_id=task.user_id,
            task_data=self._task_to_event_data(task),
            completed_at=datetime.utcnow()
        )

        await dapr_client.publish_event(
            topic=self.task_events_topic,
            data=event.model_dump(),
            metadata={
                "cloudevent.id": str(uuid.uuid4()),
                "cloudevent.source": "todo-backend",
                "cloudevent.type": "task.completed.v1",
                "cloudevent.specversion": "1.0"
            }
        )
        logger.info(f"Published task.completed.v1 event for task {task.id}")

    async def publish_task_deleted(self, task_id: int, user_id: str) -> None:
        """
        Publish task.deleted.v1 event.

        Args:
            task_id: ID of the deleted task
            user_id: User who owns the task
        """
        event = TaskDeletedEvent(
            task_id=task_id,
            user_id=user_id
        )

        await dapr_client.publish_event(
            topic=self.task_events_topic,
            data=event.model_dump(),
            metadata={
                "cloudevent.id": str(uuid.uuid4()),
                "cloudevent.source": "todo-backend",
                "cloudevent.type": "task.deleted.v1",
                "cloudevent.specversion": "1.0"
            }
        )
        logger.info(f"Published task.deleted.v1 event for task {task_id}")

    async def publish_reminder(
        self,
        task_id: int,
        user_id: str,
        title: str,
        due_at: datetime,
        remind_at: Optional[datetime] = None
    ) -> None:
        """
        Publish reminder.scheduled.v1 event.

        Args:
            task_id: ID of the task
            user_id: User to remind
            title: Task title
            due_at: When the task is due
            remind_at: When the reminder was scheduled (defaults to now)
        """
        event = ReminderScheduledEvent(
            task_id=task_id,
            user_id=user_id,
            title=title,
            due_at=due_at,
            remind_at=remind_at or datetime.utcnow()
        )

        await dapr_client.publish_event(
            topic=self.reminders_topic,
            data=event.model_dump(),
            metadata={
                "cloudevent.id": str(uuid.uuid4()),
                "cloudevent.source": "todo-backend",
                "cloudevent.type": "reminder.scheduled.v1",
                "cloudevent.specversion": "1.0"
            }
        )
        logger.info(f"Published reminder.scheduled.v1 event for task {task_id}")


# Global event publisher instance
event_publisher = EventPublisher()
