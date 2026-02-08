#!/usr/bin/env python3
"""
WebSocket Notification Service

Provides real-time notifications to connected frontend clients.
Consumes events from Dapr Pub/Sub (Kafka) and broadcasts to WebSocket connections.

Usage:
    python notification_service.py

Features:
- WebSocket connections per user
- Dapr Pub/Sub event consumption
- Automatic reconnection handling
- Heartbeat ping/pong
- Browser notification support
"""

import asyncio
import logging
import json
from typing import Dict, Set
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Notification Service",
    description="WebSocket service for real-time task notifications",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections: {user_id: set(websocket)}
connections: Dict[str, Set[WebSocket]] = {}


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "service": "Notification Service",
        "status": "running",
        "active_connections": sum(len(conns) for conns in connections.values()),
        "users_connected": len(connections)
    }


@app.post("/notify/{user_id}")
async def notify_user(user_id: str, notification: dict):
    """
    Direct notification endpoint for sending notifications to a specific user.

    This endpoint receives notifications from the backend API and broadcasts
    them to all active WebSocket connections for the specified user.

    Args:
        user_id: User ID to send notification to
        notification: Notification data to broadcast

    Returns:
        Status of notification delivery
    """
    logger.info(f"Received direct notification for user {user_id}: {notification.get('type')}")

    # Broadcast to all connections for this user
    await broadcast_to_user(user_id, notification)

    return {
        "status": "success",
        "user_id": user_id,
        "delivered": user_id in connections,
        "connection_count": len(connections.get(user_id, set()))
    }


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for user notifications.

    Args:
        websocket: WebSocket connection
        user_id: User ID to receive notifications for
    """
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for user {user_id}")

    # Add connection to user's set
    if user_id not in connections:
        connections[user_id] = set()
    connections[user_id].add(websocket)

    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": f"Connected to notification service",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep connection alive and handle ping/pong
        while True:
            try:
                # Receive messages from client
                data = await websocket.receive_json()

                # Handle ping
                if data.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })

            except Exception as e:
                logger.error(f"Error receiving message from {user_id}: {e}")
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        # Remove connection
        if user_id in connections:
            connections[user_id].discard(websocket)
            if not connections[user_id]:
                del connections[user_id]
        logger.info(f"Cleaned up connection for user {user_id}")


async def broadcast_to_user(user_id: str, message: dict):
    """
    Broadcast a message to all active connections for a user.

    Args:
        user_id: User ID to send message to
        message: Message to broadcast
    """
    if user_id not in connections:
        logger.debug(f"No active connections for user {user_id}")
        return

    # Get all connections for this user
    user_connections = connections[user_id].copy()

    # Send to all connections
    disconnected = []
    for websocket in user_connections:
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send to connection for user {user_id}: {e}")
            disconnected.append(websocket)

    # Clean up disconnected connections
    for websocket in disconnected:
        connections[user_id].discard(websocket)

    if not connections[user_id]:
        del connections[user_id]


@app.post("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.
    Tells Dapr which topics this service wants to subscribe to.
    """
    subscriptions = [
        {
            "pubsubname": "pubsub",
            "topic": "task-events",
            "route": "/events/task-events"
        },
        {
            "pubsubname": "pubsub",
            "topic": "task-updates",
            "route": "/events/task-updates"
        },
        {
            "pubsubname": "pubsub",
            "topic": "reminders",
            "route": "/events/reminders"
        }
    ]
    return subscriptions


@app.post("/events/task-events")
async def handle_task_event(event: dict):
    """
    Handle task events (created, updated, completed, deleted).

    Args:
        event: CloudEvent from Dapr
    """
    try:
        # Extract CloudEvent data
        data = event.get("data", {})
        event_type = event.get("type", "")

        user_id = data.get("user_id")
        task_id = data.get("task_id")
        task_data = data.get("task_data", {})

        logger.info(f"Received {event_type} for task {task_id}, user {user_id}")

        # Create notification message
        notification = {
            "type": "task_update",
            "event_type": event_type,
            "task_id": task_id,
            "task_data": task_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Broadcast to user
        if user_id:
            await broadcast_to_user(user_id, notification)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error handling task event: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/events/task-updates")
async def handle_task_update(event: dict):
    """
    Handle task update events.

    Args:
        event: CloudEvent from Dapr
    """
    try:
        data = event.get("data", {})
        user_id = data.get("user_id")
        task_id = data.get("task_id")

        logger.info(f"Received task update for task {task_id}, user {user_id}")

        # Create notification
        notification = {
            "type": "task_update",
            "task_id": task_id,
            "task_data": data.get("task_data", {}),
            "changes": data.get("changes", {}),
            "timestamp": datetime.utcnow().isoformat()
        }

        if user_id:
            await broadcast_to_user(user_id, notification)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error handling task update: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/events/reminders")
async def handle_reminder(event: dict):
    """
    Handle reminder events.

    Args:
        event: CloudEvent from Dapr
    """
    try:
        data = event.get("data", {})
        user_id = data.get("user_id")
        task_id = data.get("task_id")
        title = data.get("title", "Task")
        due_at = data.get("due_at")

        logger.info(f"Received reminder for task {task_id}, user {user_id}")

        # Create reminder notification
        notification = {
            "type": "reminder",
            "task_id": task_id,
            "title": title,
            "due_date": due_at,
            "message": f'Task "{title}" is due soon!',
            "priority": data.get("priority"),
            "timestamp": datetime.utcnow().isoformat()
        }

        if user_id:
            await broadcast_to_user(user_id, notification)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error handling reminder: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    """
    Run the notification service.

    The service runs on port 8002 and provides:
    - WebSocket endpoint: ws://localhost:8002/ws/{user_id}
    - Dapr subscription endpoint: POST /dapr/subscribe
    - Event handlers for task events, updates, and reminders
    """
    logger.info("Starting Notification Service on port 8002")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
