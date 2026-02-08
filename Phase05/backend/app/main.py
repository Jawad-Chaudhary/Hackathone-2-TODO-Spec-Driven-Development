# [Task T014, T017, T038] FastAPI application with lifespan events and CORS
# WebSocket notifications integrated

from contextlib import asynccontextmanager
from typing import Dict, Set
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
import logging

# Load environment variables at module import time
load_dotenv()

from app.config import settings
from app.database import create_db_and_tables
from app.routes import tasks, health, chat
from app.middleware.cors import configure_cors

logger = logging.getLogger(__name__)

# Store active WebSocket connections: {user_id: set(websocket)}
connections: Dict[str, Set[WebSocket]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for application startup and shutdown.
    Creates database tables on startup.
    """
    # Startup: Create database tables
    await create_db_and_tables()
    yield
    # Shutdown: cleanup if needed


# Initialize FastAPI application
app = FastAPI(
    title="Todo Backend API",
    description="Full-stack Todo application backend with JWT authentication",
    version="0.1.0",
    lifespan=lifespan,
)

# [Task T038] Configure CORS middleware with environment-based origins
configure_cors(app)

# Register routers
app.include_router(health.router)  # [Task T074] Health check endpoint
app.include_router(tasks.router)
app.include_router(chat.router)  # [Task T055-T062] Chat API endpoint


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "Todo Backend API",
        "status": "running",
        "websocket_connections": sum(len(conns) for conns in connections.values())
    }


# ============================================
# WebSocket Notification System
# ============================================

async def broadcast_to_user(user_id: str, message: dict):
    """Broadcast a message to all active connections for a user."""
    if user_id not in connections:
        return

    user_connections = connections[user_id].copy()
    disconnected = []

    for websocket in user_connections:
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send to connection for user {user_id}: {e}")
            disconnected.append(websocket)

    for websocket in disconnected:
        connections[user_id].discard(websocket)

    if not connections[user_id]:
        del connections[user_id]


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for user notifications."""
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for user {user_id}")

    if user_id not in connections:
        connections[user_id] = set()
    connections[user_id].add(websocket)

    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to notifications",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        while True:
            try:
                data = await websocket.receive_json()
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
        if user_id in connections:
            connections[user_id].discard(websocket)
            if not connections[user_id]:
                del connections[user_id]
        logger.info(f"Cleaned up connection for user {user_id}")


@app.post("/notify/{user_id}")
async def notify_user(user_id: str, notification: dict):
    """Direct notification endpoint for broadcasting to WebSocket clients."""
    logger.info(f"Sending notification to user {user_id}: {notification.get('type')}")
    await broadcast_to_user(user_id, notification)
    return {
        "status": "success",
        "user_id": user_id,
        "delivered": user_id in connections
    }
