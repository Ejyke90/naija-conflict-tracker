#!/usr/bin/env bash
# Create a Neon branch for safe migration testing (uses free tier: 10 branches)
# Usage: ./create_neon_branch.sh <branch-name> <project-id>

set -euo pipefail

BRANCH_NAME=${1:-migration-test}
PROJECT_ID=${2:-}

if [ -z "$PROJECT_ID" ]; then
  echo "Usage: $0 <branch-name> <project-id>" >&2
  exit 1
fi

echo "Creating Neon branch '$BRANCH_NAME' for project '$PROJECT_ID'..."
neonctl branches create --name "$BRANCH_NAME" --project-id "$PROJECT_ID"

echo "Fetching connection string..."
neonctl connection-string "$BRANCH_NAME" --project-id "$PROJECT_ID"

echo "Done. Use the connection string above for testing migrations."
