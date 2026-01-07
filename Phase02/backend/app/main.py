# [Task T014, T017] FastAPI application with lifespan events and CORS

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_db_and_tables
from app.routes import tasks, health


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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # From environment variable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)  # [Task T074] Health check endpoint
app.include_router(tasks.router)


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "Todo Backend API", "status": "running"}
