# Monthly Trends Performance - Rollback Plan

## 🚨 **When to Rollback**
- Monthly-trends endpoint returns errors
- Other analytics endpoints break
- Frontend fails to load dashboard
- Performance gets worse instead of better
- Database errors appear in logs

## 🔄 **Rollback Steps**

### **1. Database Rollback (Quick)**
```bash
./scripts/rollback_monthly_trends_performance.sh
```

### **2. Code Rollback (Complete)**
```bash
# Revert all code changes
git checkout HEAD~1 -- backend/app/api/v1/endpoints/timeseries.py
git checkout HEAD~1 -- backend/app/core/cache.py
git checkout HEAD~1 -- database/migrations/003_monthly_trends_performance.sql
git checkout HEAD~1 -- scripts/setup_monthly_trends_performance.sh
git checkout HEAD~1 -- test_monthly_trends_cache.py

# Remove new files
rm database/migrations/003_monthly_trends_performance.sql
rm scripts/setup_monthly_trends_performance.sh
rm scripts/rollback_monthly_trends_performance.sh
rm test_monthly_trends_cache.py
rm ROLLBACK_PLAN.md
```

### **3. Service Restart**
```bash
# Restart backend to apply code changes
# Railway: redeploy or restart service
# Local: restart FastAPI server
```

## 📋 **Rollback Verification**

### **Before Rollback**
- Note current error symptoms
- Check backend logs
- Test monthly-trends endpoint response time

### **After Rollback**
- Verify monthly-trends works (but slower)
- Check other analytics endpoints
- Confirm dashboard loads
- Monitor error logs

## ⚡ **Quick Rollback (5 minutes)**

If you need to revert FAST:

```bash
# 1. Disable caching in code (comment out cache lines)
# 2. Drop database objects
./scripts/rollback_monthly_trends_performance.sh
# 3. Restart backend
```

## 🎯 **Rollback Success Criteria**

✅ **Success Indicators**
- Monthly-trends endpoint responds (even if slow)
- No 500 errors in logs
- Dashboard loads without timeout
- Other analytics endpoints work

❌ **Failure Indicators**
- Still getting errors after rollback
- Database connection issues
- Frontend still broken

## 📞 **Support**

If rollback fails:
1. Check Railway service status
2. Verify database connection
3. Review recent deployments
4. Contact support if needed

## 📝 **Notes**

- The composite index and materialized view are **additive** - they don't modify existing data
- Original queries still work without optimizations
- Rollback is safe and doesn't affect data integrity
