# [Task T033] Recurring Service microservice for handling recurring tasks
#
# This service subscribes to task-events topic and creates next recurring task
# instances when a recurring task is completed.

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, Response
from dapr.clients import DaprClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Recurring Service",
    description="Microservice for handling recurring task creation",
    version="1.0.0"
)

# Dapr configuration
DAPR_PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "pubsub")
DAPR_STATE_STORE = os.getenv("DAPR_STATE_STORE", "statestore")
TASK_EVENTS_TOPIC = "task-events"


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    return {"status": "healthy", "service": "recurring-service", "timestamp": datetime.utcnow().isoformat()}


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.
    Returns list of topics this service subscribes to.
    """
    subscriptions = [
        {
            "pubsubname": DAPR_PUBSUB_NAME,
            "topic": TASK_EVENTS_TOPIC,
            "route": "/events/task-completed"
        }
    ]
    logger.info(f"Dapr subscribe endpoint called. Returning subscriptions: {subscriptions}")
    return subscriptions


@app.post("/events/task-completed")
async def handle_task_completed(request: Request):
    """
    Handle task.completed.v1 events from task-events topic.
    Creates next recurring task instance if the completed task has recurrence.
    """
    try:
        # Parse CloudEvent
        body = await request.json()
        logger.info(f"Received task-completed event: {json.dumps(body, default=str)}")

        # Extract event data
        event_data = body.get("data", {})
        event_type = event_data.get("type")

        # Only process task.completed.v1 events
        if event_type != "task.completed.v1":
            logger.debug(f"Ignoring event type: {event_type}")
            return Response(status_code=200)

        task_id = event_data.get("task_id")
        task_data = event_data.get("task_data", {})
        recurrence = task_data.get("recurrence")
        recurrence_interval = task_data.get("recurrence_interval")
        due_date_str = task_data.get("due_date")

        # Check if task is recurring
        if not recurrence:
            logger.debug(f"Task {task_id} is not recurring. No action needed.")
            return Response(status_code=200)

        # Calculate next due date
        next_due_date = calculate_next_due_date(
            recurrence=recurrence,
            recurrence_interval=recurrence_interval,
            current_due_date=due_date_str
        )

        # Create next recurring task instance via Dapr state store
        # (In production, this would call backend API or use shared DB access)
        logger.info(
            f"Creating next recurring task instance: "
            f"parent_task_id={task_id}, recurrence={recurrence}, next_due_date={next_due_date}"
        )

        # Publish task.created.v1 event for the next instance
        # (This approach allows the backend to create the task through the event system)
        next_task_event = {
            "type": "task.recurring.next.v1",
            "parent_task_id": task_id,
            "user_id": event_data.get("user_id"),
            "task_data": {
                "title": task_data.get("title"),
                "description": task_data.get("description"),
                "priority": task_data.get("priority"),
                "tags": task_data.get("tags"),
                "due_date": next_due_date.isoformat() if next_due_date else None,
                "recurrence": recurrence,
                "recurrence_interval": recurrence_interval
            },
            "source": "recurring-service",
            "timestamp": datetime.utcnow().isoformat()
        }

        # Publish event via Dapr
        with DaprClient() as dapr:
            dapr.publish_event(
                pubsub_name=DAPR_PUBSUB_NAME,
                topic_name=TASK_EVENTS_TOPIC,
                data=json.dumps(next_task_event),
                data_content_type="application/json"
            )

        logger.info(f"Successfully published next recurring task event for parent_task_id={task_id}")
        return Response(status_code=200)

    except Exception as e:
        logger.error(f"Error handling task-completed event: {e}", exc_info=True)
        # Return 200 to avoid Dapr retries (log and monitor instead)
        return Response(status_code=200)


def calculate_next_due_date(
    recurrence: str,
    recurrence_interval: Optional[int],
    current_due_date: Optional[str]
) -> Optional[datetime]:
    """
    Calculate the next due date based on recurrence pattern.

    Args:
        recurrence: Recurrence pattern (daily, weekly, monthly, custom)
        recurrence_interval: Interval for custom recurrence (days)
        current_due_date: Current due date in ISO format

    Returns:
        Next due date as datetime object, or None if no due date
    """
    if not current_due_date:
        return None

    try:
        # Parse current due date
        current_dt = datetime.fromisoformat(current_due_date.replace('Z', '+00:00'))

        # Calculate next due date based on recurrence
        if recurrence == "daily":
            return current_dt + timedelta(days=1)
        elif recurrence == "weekly":
            return current_dt + timedelta(weeks=1)
        elif recurrence == "monthly":
            # Approximate monthly recurrence (30 days)
            return current_dt + timedelta(days=30)
        elif recurrence == "custom" and recurrence_interval:
            return current_dt + timedelta(days=recurrence_interval)
        else:
            logger.warning(f"Unknown recurrence pattern: {recurrence}")
            return None

    except Exception as e:
        logger.error(f"Error calculating next due date: {e}")
        return None


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
