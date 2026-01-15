#!/bin/bash

# Render startup script for AI Todo Backend

echo "Starting AI Todo Backend..."

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the FastAPI server
echo "Starting FastAPI server..."
uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-8000}
