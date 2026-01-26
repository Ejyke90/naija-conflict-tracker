#!/bin/bash

# Nigeria Conflict Tracker - Startup Script for Railway

# Set default port if not provided
PORT=${PORT:-8000}

echo "Starting Nigeria Conflict Tracker API on port $PORT"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the FastAPI application
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
