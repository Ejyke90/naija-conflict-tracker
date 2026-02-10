#!/bin/bash

# Rollback script for Monthly Trends Performance Optimizations
# Use this if the changes break anything

echo "🔄 Rolling Back Monthly Trends Performance Optimizations..."

# Get database URL from environment or config
DB_URL=${DATABASE_URL:-$(grep DATABASE_URL .env 2>/dev/null | cut -d '=' -f2)}

if [ -z "$DB_URL" ]; then
    echo "❌ DATABASE_URL not found. Please set it in .env file or environment."
    exit 1
fi

echo "⚠️  WARNING: This will remove performance optimizations and revert to original behavior"
echo "📋 Changes to be rolled back:"
echo "   • Remove materialized view: monthly_trends_summary"
echo "   • Remove composite index: idx_conflicts_reporting"
echo "   • Remove refresh function: refresh_monthly_trends()"
echo ""

read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Rollback cancelled"
    exit 1
fi

echo "🔄 Starting rollback..."

# 1. Drop materialized view
echo "📊 Dropping materialized view..."
psql $DB_URL -c "DROP MATERIALIZED VIEW IF EXISTS monthly_trends_summary;" 2>/dev/null

# 2. Drop composite index
echo "🔍 Dropping composite index..."
psql $DB_URL -c "DROP INDEX CONCURRENTLY IF EXISTS idx_conflicts_reporting;" 2>/dev/null

# 3. Drop refresh function
echo "⚙️  Dropping refresh function..."
psql $DB_URL -c "DROP FUNCTION IF EXISTS refresh_monthly_trends();" 2>/dev/null

# 4. Verify rollback
echo "✅ Verifying rollback..."
remaining_objects=$(psql $DB_URL -Atc "
    SELECT COUNT(*) FROM information_schema.views WHERE table_name = 'monthly_trends_summary';
    SELECT COUNT(*) FROM pg_indexes WHERE indexname = 'idx_conflicts_reporting';
    SELECT COUNT(*) FROM pg_proc WHERE proname = 'refresh_monthly_trends';
" | tr '\n' '+' | sed 's/+$//')

if [ "$remaining_objects" = "0+0+0" ]; then
    echo "✅ Rollback completed successfully!"
    echo ""
    echo "🔄 Next steps:"
    echo "   1. Revert code changes: git checkout HEAD~1 -- backend/app/api/v1/endpoints/timeseries.py backend/app/core/cache.py"
    echo "   2. Restart backend service"
    echo "   3. Test that monthly-trends works (but will be slower)"
else
    echo "⚠️  Some objects may still exist. Manual cleanup may be required."
fi
