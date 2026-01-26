#!/bin/bash

# This script checks if backend is healthy before allowing Vercel to build
# Set in Vercel: Settings > Git > Ignored Build Step > bash vercel-ignore-build.sh

echo "🔍 Checking if backend is healthy before building frontend..."

API_URL="${NEXT_PUBLIC_API_URL:-https://naija-conflict-tracker-production.up.railway.app}"
HEALTH_ENDPOINT="$API_URL/health"

# Try up to 10 times with 10s intervals (total 100s wait)
MAX_ATTEMPTS=10
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  ATTEMPT=$((ATTEMPT + 1))
  echo "⏳ Attempt $ATTEMPT/$MAX_ATTEMPTS: Checking $HEALTH_ENDPOINT"
  
  # Check if endpoint responds successfully
  if curl -sf --max-time 10 "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
    echo "✅ Backend is healthy! Proceeding with build..."
    exit 1  # Exit 1 tells Vercel to proceed with build
  fi
  
  if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
    echo "❌ Backend not ready, waiting 10 seconds..."
    sleep 10
  fi
done

echo "⚠️  Backend still not healthy after $MAX_ATTEMPTS attempts"
echo "   This might be a backend issue. Check Railway deployment."
echo "   Proceeding with build anyway (frontend will retry on client-side)"

exit 1  # Exit 1 = proceed with build (0 = skip build)
