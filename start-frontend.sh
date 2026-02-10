#!/bin/bash

# Start Frontend Development Server
# This script starts the Next.js frontend development server

echo "🎨 Starting Naija Conflict Tracker Frontend..."

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

echo "📦 Installing dependencies (if needed)..."
npm install

echo "🌐 Starting Next.js development server on http://localhost:3000"
echo "🎯 Dashboard: http://localhost:3000/dashboard"
echo "⏹️  Press CTRL+C to stop the server"
echo ""

# Start the development server
npm run dev
