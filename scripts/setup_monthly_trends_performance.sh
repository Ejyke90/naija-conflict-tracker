#!/bin/bash

# Monthly Trends Performance Setup
# This script applies the performance optimizations for the monthly-trends endpoint

echo "🚀 Setting up Monthly Trends Performance Optimizations..."

# Get database URL from environment or config
DB_URL=${DATABASE_URL:-$(grep DATABASE_URL .env 2>/dev/null | cut -d '=' -f2)}

if [ -z "$DB_URL" ]; then
    echo "❌ DATABASE_URL not found. Please set it in .env file or environment."
    exit 1
fi

echo "📊 Applying performance optimizations..."

# Apply the migration
psql $DB_URL -f database/migrations/003_monthly_trends_performance.sql

if [ $? -eq 0 ]; then
    echo "✅ Performance optimizations applied successfully!"
    echo ""
    echo "🎯 Optimizations applied:"
    echo "   • Composite index: idx_conflicts_reporting"
    echo "   • Materialized view: monthly_trends_summary"
    echo "   • Refresh function: refresh_monthly_trends()"
    echo ""
    echo "📈 Expected performance improvements:"
    echo "   • Monthly trends query: 20s → 10ms (with materialized view)"
    echo "   • Cache stampede eliminated (30-minute TTL)"
    echo "   • Composite index covers exact query pattern"
    echo ""
    echo "🔄 To refresh materialized view manually:"
    echo "   SELECT refresh_monthly_trends();"
    echo ""
    echo "⏰ Schedule automated refresh (optional):"
    echo "   Add to cron: */30 * * * * psql \$DATABASE_URL -c 'SELECT refresh_monthly_trends();'"
else
    echo "❌ Failed to apply optimizations"
    exit 1
fi
