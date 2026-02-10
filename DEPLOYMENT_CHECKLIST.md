# Monthly Trends Performance - Deployment Checklist

## ✅ **Pre-Deployment (Complete)**
- [x] **Rollback plan created** - `ROLLBACK_PLAN.md` + rollback script
- [x] **Local testing passed** - All 4/4 tests successful
- [x] **Database migration applied** - Composite index + materialized view created
- [x] **Code changes tested** - Imports work, no breaking changes
- [x] **Other endpoints verified** - Analytics endpoints unaffected

## 🚀 **Ready to Deploy**

### **Step 1: Commit Changes**
```bash
git add .
git commit -m "feat: Enable caching for monthly-trends endpoint

- Add 30-minute cache TTL for monthly-trends
- Enable caching in timeseries.py (was disabled)
- Add materialized view support with fallback
- Add composite index for performance
- Add rollback scripts and documentation

Fixes cache stampede issue causing frontend timeouts"
```

### **Step 2: Deploy to Railway**
```bash
git push origin main
# Railway will auto-deploy
```

### **Step 3: Post-Deployment Verification**
```bash
# Test the endpoint performance
python test_monthly_trends_cache.py

# Or manually test:
curl -w "@curl-format.txt" "https://naija-conflict-tracker-production.up.railway.app/api/v1/analytics/monthly-trends?months_back=12&include_forecast=true"
```

## 📊 **Expected Results**

### **Before Fix**
- Monthly-trends: 20+ seconds (timeout)
- Cache stampede every few minutes
- Frontend shows "No data to load"

### **After Fix**
- First request: ~10ms (materialized view) or ~2s (cache miss)
- Subsequent requests: ~500ms (cache hit)
- No more cache stampede
- Dashboard loads consistently

## 🔍 **Monitoring Checklist**

### **Immediately After Deploy**
- [ ] Backend service starts successfully
- [ ] No 500 errors in logs
- [ ] Monthly-trends endpoint responds
- [ ] Dashboard loads without timeout

### **Performance Verification**
- [ ] First request < 5 seconds
- [ ] Second request < 1 second  
- [ ] Consistent responses over time
- [ ] No timeout errors in frontend

### **Functionality Verification**
- [ ] Other analytics endpoints work
- [ ] State filtering works
- [ ] Forecast generation works
- [ ] Error handling graceful

## ⚠️ **Rollback Triggers**

Roll back immediately if:
- Monthly-trends returns 500 errors
- Other analytics endpoints break
- Frontend fails to load dashboard
- Performance gets worse
- Database errors in logs

## 🔄 **Rollback Commands**

### **Quick Rollback (5 minutes)**
```bash
# 1. Revert code
git checkout HEAD~1 -- backend/app/api/v1/endpoints/timeseries.py backend/app/core/cache.py

# 2. Drop database objects (optional)
./scripts/rollback_monthly_trends_performance.sh

# 3. Restart Railway service
# Railway will auto-restart on code push
```

### **Complete Rollback**
```bash
# Reset to before changes
git reset --hard HEAD~1
git push origin main --force
```

## 📞 **Support**

If issues arise:
1. Check Railway service logs
2. Verify database connectivity
3. Run rollback script if needed
4. Monitor error patterns

---

**Status**: ✅ Ready for deployment
**Risk Level**: 🟢 Low (with rollback plan)
