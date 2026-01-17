#!/usr/bin/env python3
import os
import uvicorn

# Get port from environment or default to 8000
port = int(os.environ.get("PORT", 8000))

print(f"Starting Nigeria Conflict Tracker API on port {port}")

# Start the server
uvicorn.run("app.main:app", host="0.0.0.0", port=port)
