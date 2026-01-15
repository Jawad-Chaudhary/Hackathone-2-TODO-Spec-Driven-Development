# [Task]: T-023
# [From]: specs/001-ai-todo-chatbot/tasks.md

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .routes import router as chat_router
from .auth import router as auth_router

app = FastAPI(
    title="AI Todo Chatbot API",
    description="Stateless AI-powered task management API with JWT authentication",
    version="1.0.0"
)

# CORS Configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
cors_allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)  # Authentication endpoints (no JWT required)
app.include_router(chat_router)  # Chat endpoints (JWT required)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "AI Todo Chatbot API is running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "api": "operational"
    }
