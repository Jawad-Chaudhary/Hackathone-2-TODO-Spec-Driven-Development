# [Task T014, T017, T038] FastAPI application with lifespan events and CORS

from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables at module import time
load_dotenv()

from app.config import settings
from app.database import create_db_and_tables
from app.routes import tasks, health, chat
from app.middleware.cors import configure_cors


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
    return {"message": "Todo Backend API", "status": "running"}
