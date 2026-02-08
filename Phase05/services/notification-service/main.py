# [Task T040-T042] Notification Service microservice for handling due date reminders
#
# This service:
# - Subscribes to Dapr cron binding to check for due tasks every 5 minutes
# - Queries tasks with due_date within next hour from state store
# - Publishes reminder.scheduled.v1 events to reminders topic
# - Provides WebSocket endpoint for real-time browser notifications

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dapr.clients import DaprClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Notification Service",
    description="Microservice for handling due date reminders and real-time notifications",
    version="1.0.0"
)

# CORS middleware for WebSocket connections from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dapr configuration
DAPR_PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "pubsub")
DAPR_STATE_STORE = os.getenv("DAPR_STATE_STORE", "statestore")
REMINDERS_TOPIC = "reminders"
TASK_UPDATES_TOPIC = "task-updates"

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time notifications."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection and register user."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove WebSocket connection for user."""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to all WebSocket connections for a specific user."""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    disconnected.append(connection)

            # Clean up disconnected connections
            for connection in disconnected:
                self.disconnect(connection, user_id)

manager = ConnectionManager()


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    return {
        "status": "healthy",
        "service": "notification-service",
        "timestamp": datetime.utcnow().isoformat(),
        "active_websocket_users": len(manager.active_connections)
    }


@app.post("/cron/check-reminders")
async def check_reminders(request: Request):
    """
    Dapr cron binding endpoint - triggered every 5 minutes.
    Checks for tasks due within the next hour and sends reminders.
    """
    try:
        logger.info("Cron triggered: Checking for due tasks")

        # TODO: Query state store or backend API for tasks due within next hour
        # For now, this is a placeholder that demonstrates the flow

        now = datetime.utcnow()
        one_hour_later = now + timedelta(hours=1)

        # In production, this would query the database through Dapr state store
        # or call the backend API to get tasks due within the next hour
        # Example query: tasks where due_date > now AND due_date < one_hour_later AND completed = False

        # Mock data for demonstration
        due_tasks = [
            # {
            #     "id": 123,
            #     "user_id": "user456",
            #     "title": "Team meeting",
            #     "due_date": "2026-01-22T16:00:00Z",
            #     "priority": "high"
            # }
        ]

        # Publish reminder events for each due task
        with DaprClient() as dapr:
            for task in due_tasks:
                reminder_event = {
                    "type": "reminder.scheduled.v1",
                    "task_id": task["id"],
                    "user_id": task["user_id"],
                    "task_title": task["title"],
                    "due_date": task["due_date"],
                    "priority": task.get("priority"),
                    "source": "notification-service",
                    "timestamp": datetime.utcnow().isoformat()
                }

                # Publish to reminders topic
                dapr.publish_event(
                    pubsub_name=DAPR_PUBSUB_NAME,
                    topic_name=REMINDERS_TOPIC,
                    data=json.dumps(reminder_event),
                    data_content_type="application/json"
                )

                # Send real-time notification via WebSocket
                await manager.send_personal_message(
                    {
                        "type": "reminder",
                        "task_id": task["id"],
                        "title": task["title"],
                        "due_date": task["due_date"],
                        "priority": task.get("priority"),
                        "message": f"Reminder: '{task['title']}' is due soon!"
                    },
                    user_id=task["user_id"]
                )

                logger.info(f"Reminder sent for task {task['id']} to user {task['user_id']}")

        logger.info(f"Cron check completed. {len(due_tasks)} reminders sent.")
        return Response(status_code=200)

    except Exception as e:
        logger.error(f"Error in cron check-reminders: {e}", exc_info=True)
        # Return 200 to avoid Dapr retries
        return Response(status_code=200)


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.
    Subscribes to task-updates topic for real-time task changes.
    """
    subscriptions = [
        {
            "pubsubname": DAPR_PUBSUB_NAME,
            "topic": TASK_UPDATES_TOPIC,
            "route": "/events/task-updated"
        }
    ]
    logger.info(f"Dapr subscribe endpoint called. Returning subscriptions: {subscriptions}")
    return subscriptions


@app.post("/events/task-updated")
async def handle_task_updated(request: Request):
    """
    Handle task.updated.v1 events from task-updates topic.
    Broadcasts real-time updates to connected WebSocket clients.
    """
    try:
        body = await request.json()
        logger.info(f"Received task-updated event: {json.dumps(body, default=str)}")

        event_data = body.get("data", {})
        event_type = event_data.get("type")

        # Only process task.updated.v1 events
        if event_type not in ["task.updated.v1", "task.created.v1", "task.completed.v1", "task.deleted.v1"]:
            logger.debug(f"Ignoring event type: {event_type}")
            return Response(status_code=200)

        task_id = event_data.get("task_id")
        user_id = event_data.get("user_id")
        task_data = event_data.get("task_data", {})

        # Send real-time update via WebSocket
        await manager.send_personal_message(
            {
                "type": "task_update",
                "event_type": event_type,
                "task_id": task_id,
                "task_data": task_data
            },
            user_id=user_id
        )

        logger.info(f"Real-time update sent for task {task_id} to user {user_id}")
        return Response(status_code=200)

    except Exception as e:
        logger.error(f"Error handling task-updated event: {e}", exc_info=True)
        return Response(status_code=200)


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time notifications.
    Frontend connects here to receive instant updates.
    """
    await manager.connect(websocket, user_id)
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to notification service",
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received from user {user_id}: {data}")

            # Echo back for heartbeat/ping-pong
            await websocket.send_json({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"User {user_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8002"))
    uvicorn.run(app, host="0.0.0.0", port=port)
