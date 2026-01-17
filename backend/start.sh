#!/bin/bash

# Nigeria Conflict Tracker - Startup Script for Railway

# Set default port if not provided
PORT=${PORT:-8000}

# Start the FastAPI application
echo "Starting Nigeria Conflict Tracker API on port $PORT"
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
