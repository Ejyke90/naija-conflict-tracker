# Production Deployment Guide - Monthly Trends Optimization

## 🚨 IMPORTANT: Production Deployment Required

Yes, you **must** run the SQL commands on Neon SQL Editor for production. Railway and Neon are separate databases, so the optimizations need to be applied to both environments.

## 📋 Deployment Steps

### 1. **Neon SQL Editor Deployment**

1. Open Neon Console: https://console.neon.tech/
2. Select your production database
3. Open SQL Editor
4. Copy and paste the entire contents of `005_monthly_trends_production_optimization.sql`
5. Execute all commands

### 2. **Verify Deployment**

After running the SQL, verify with these queries in Neon SQL Editor:

```sql
-- Check indexes were created
SELECT indexname, tablename 
FROM pg_indexes 
WHERE tablename IN ('conflicts', 'states') 
AND indexname LIKE 'idx_%';

-- Check materialized view
SELECT COUNT(*) as rows FROM monthly_trends_view;

-- Test performance
EXPLAIN (ANALYZE, BUFFERS)
SELECT month, SUM(count) as incidents
FROM monthly_trends_view
WHERE month >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY month
LIMIT 24;
```

### 3. **Railway Backend Update**

The backend code is already updated, but ensure Railway has the latest version:

```bash
git add .
git commit -m "Optimize monthly trends API - materialized view and indexes"
git push origin main
```

### 4. **Test Production Performance**

After deployment, test the production endpoint:

```bash
curl -w "Response Time: %{time_total}s\n" \
  https://your-railway-app.railway.app/api/v1/timeseries/monthly-trends
```

Expected: **< 0.1s** (previously 8.4s)

## 🔍 Environment Differences

| Component | Local/Railway | Production (Neon) |
|-----------|----------------|-------------------|
| Database | PostgreSQL | Neon PostgreSQL |
| Optimizations | ✅ Applied | ❌ Needs Deployment |
| Performance | < 1ms | Still 8,396ms |

## ⚠️ Critical Notes

### **CONCURRENTLY vs Regular CREATE INDEX**
- Production uses `CREATE INDEX CONCURRENTLY` to avoid blocking
- This prevents downtime during index creation
- Takes longer but doesn't lock the table

### **Materialized View Data**
- Initial creation may take a few minutes
- Contains 5 years of historical data
- Refreshes every 30 minutes automatically

### **Permissions**
- Ensure your Neon database user has access to the new materialized view
- Check Railway environment variables for database credentials

## 🚀 Post-Deployment Checklist

- [ ] Run SQL script on Neon SQL Editor
- [ ] Verify all 5 indexes created
- [ ] Confirm materialized view exists with data
- [ ] Test refresh function works
- [ ] Push code changes to Railway
- [ ] Test production API performance
- [ ] Set up automated refresh schedule

## 📊 Expected Results

After deployment:
- **Response Time**: 8,396ms → < 100ms
- **Query Cost**: 51,804 → < 100
- **User Experience**: No more timeout errors
- **Scalability**: 10x more concurrent users

## 🔄 Automated Refresh Setup

For production, set up a cron job or Railway cron to call:

```bash
curl -X POST https://your-railway-app.railway.app/api/v1/timeseries/refresh-materialized-view
```

Schedule: Every 30 minutes

## 🆘 Troubleshooting

### If Materialized View Creation Fails:
```sql
-- Check conflicts table structure
\d conflicts

-- Verify data exists
SELECT COUNT(*) FROM conflicts;
```

### If Index Creation Fails:
```sql
-- Check for long-running queries
SELECT * FROM pg_stat_activity WHERE state = 'active';

-- Kill blocking sessions if needed
SELECT pg_terminate_backend(pid);
```

### If API Still Slow:
1. Verify Railway is using latest code
2. Check Neon connection string in Railway env vars
3. Test materialized view query directly in Neon
4. Check Redis cache connectivity

## 📞 Emergency Rollback

If issues occur:
```sql
-- Drop materialized view
DROP MATERIALIZED VIEW IF EXISTS monthly_trends_view;

-- Drop indexes (if needed)
DROP INDEX IF EXISTS idx_conflicts_incidence_date;
DROP INDEX IF EXISTS idx_conflicts_monthly_trends;
-- etc.
```

---

**⚠️ ACTION REQUIRED**: Run the SQL script on Neon SQL Editor NOW to complete production optimization.
