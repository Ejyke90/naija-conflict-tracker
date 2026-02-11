#!/bin/bash
# Monthly Trends Materialized View Refresh Script
# Schedule this to run every 30 minutes via cron

echo "🔄 Refreshing Monthly Trends Materialized View - $(date)"

# Change to backend directory
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Call the refresh endpoint
response=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{}' \
  http://localhost:8000/api/v1/timeseries/refresh-materialized-view 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$response" ]; then
    echo "✅ Materialized view refreshed successfully"
    echo "$response" | jq -r '.message // "Refresh completed"'
    
    # Log the duration for monitoring
    duration=$(echo "$response" | jq -r '.duration_seconds // 0')
    echo "⏱️  Duration: ${duration}s"
else
    echo "❌ Failed to refresh materialized view"
    echo "Response: $response"
    exit 1
fi

echo "✨ Refresh completed at $(date)"
