#!/bin/bash

# Start Backend Server Script
# This script ensures the backend starts with the proper virtual environment

echo "🚀 Starting Naija Conflict Tracker Backend..."

# Kill any existing uvicorn processes
echo "🔄 Cleaning up existing processes..."
pkill -f uvicorn 2>/dev/null || true
sleep 2

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Activate virtual environment and start server
echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📊 API Documentation: http://localhost:8000/docs"
echo "⏹️  Press CTRL+C to stop the server"
echo ""

# Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
