# Performance Optimization - Quick Implementation Guide

## 🎯 Objective
Reduce dashboard load time from **2+ minutes → 2-5 seconds** (95% improvement)

---

## ✅ Step-by-Step Implementation (30-60 minutes)

### **Step 1: Apply Database Indexes** (5 minutes)

```bash
cd backend

# Apply migration
alembic upgrade head

# Verify indexes created
psql $DATABASE_URL -c "
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'conflicts' 
ORDER BY indexname;
"
```

**Expected Output:**
```
idx_conflicts_incidence_date
idx_conflicts_state_id
idx_conflicts_lga_id
idx_conflicts_conflict_type_id
idx_conflicts_composite_state_date
idx_conflicts_composite_lga_date
```

---

### **Step 2: Deploy Backend Changes** (10 minutes)

#### **Option A: Local Development**
```bash
cd backend

# Restart backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### **Option B: Docker**
```bash
docker-compose restart backend

# Verify endpoint is available
curl http://localhost:8000/api/v1/dashboard/overview
```

#### **Option C: Railway/Production**
```bash
git add backend/
git commit -m "feat: add optimized dashboard endpoint and indexes"
git push origin main

# Wait for deployment (auto-deploys on Railway)
```

**Verification:**
```bash
# Test new endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/dashboard/overview?months_back=12"
```

---

### **Step 3: Install Frontend Dependencies** (5 minutes)

```bash
cd frontend

# Install if not already present
npm install @tanstack/react-query

# Verify installation
npm list @tanstack/react-query
```

---

### **Step 4: Update Dashboard Page** (15 minutes)

#### **Option A: Replace Existing Dashboard** (Recommended)

```bash
cd frontend/pages/dashboard

# Backup current version
cp index.tsx index-backup.tsx

# Replace with optimized version
cp index-optimized.tsx index.tsx

# Remove backup after testing
# rm index-optimized.tsx index-backup.tsx
```

#### **Option B: Test Separately First**

Access optimized dashboard at: `/dashboard/index-optimized`

Compare performance, then replace `index.tsx` when satisfied.

---

### **Step 5: Add Login Prefetching** (10 minutes)

Update your AuthContext to prefetch dashboard data after login:

```typescript
// frontend/contexts/AuthContext.tsx
import { prefetchDashboardData } from '@/hooks/useDashboardData';

const login = useCallback(async (credentials: LoginCredentials) => {
  setIsLoading(true);
  setError(null);
  
  try {
    const response: LoginResponse = await authAPI.login(credentials);
    
    storeTokens(response.access_token, response.refresh_token);
    storeUser(response.user);
    
    // ✨ PREFETCH DASHBOARD DATA (happens in background)
    prefetchDashboardData().catch(err => {
      console.warn('Dashboard prefetch failed:', err);
      // Non-critical - dashboard will fetch on mount anyway
    });
    
    router.push('/dashboard');
  } catch (err: any) {
    setError(err.message || 'Login failed');
    throw err;
  } finally {
    setIsLoading(false);
  }
}, [router, storeTokens, storeUser]);
```

---

### **Step 6: Test Performance** (10 minutes)

#### **Before Optimization Baseline:**
1. Clear browser cache
2. Log out
3. Open DevTools Network tab
4. Log in
5. **Measure:** Time from login click → dashboard fully loaded

**Expected:** 60-120 seconds ❌

#### **After Optimization:**
1. Clear cache again
2. Log out  
3. Open DevTools Network tab
4. Log in (with prefetching)
5. **Measure:** Time from login click → dashboard fully loaded

**Expected:** 2-5 seconds ✅

#### **Network Analysis:**
- **Before:** 5-6 API calls (serial waterfall)
- **After:** 1 API call (`/api/v1/dashboard/overview`)

---

## 🔍 Verification Checklist

### **Backend**
- [ ] Migration applied successfully
- [ ] Indexes exist in database
- [ ] `/api/v1/dashboard/overview` endpoint responds
- [ ] Response includes: `monthlyTrends`, `hotspots`, `archetypes`, `statistics`
- [ ] Redis cache is working (check `cached: true` in response after 2nd request)

### **Frontend**
- [ ] `@tanstack/react-query` installed
- [ ] `useDashboardData` hook created
- [ ] Dashboard component uses new hook
- [ ] Login prefetching implemented
- [ ] No console errors

### **Performance**
- [ ] Dashboard loads in <5 seconds
- [ ] Only 1 API call made on dashboard load
- [ ] State/time filter changes use cached data
- [ ] Prefetching works (instant dashboard on navigation)

---

## 📊 Performance Monitoring

### **Check Backend Response Time:**

```bash
# Test dashboard endpoint performance
time curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/dashboard/overview?months_back=12"
```

**Target:** <500ms

### **Check Database Query Time:**

```sql
-- Enable query timing
SET track_io_timing = ON;

-- Run dashboard query manually
EXPLAIN ANALYZE ...your query...

-- Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE query LIKE '%dashboard%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Target:** <100ms per query

### **Check Cache Hit Rate:**

```python
# In Python console
import asyncio
from app.core.cache import get_redis_client

async def check_cache():
    cache = await get_redis_client()
    if cache:
        info = await cache.info('stats')
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        hit_rate = (hits / total * 100) if total > 0 else 0
        print(f"Cache hit rate: {hit_rate:.2f}%")

asyncio.run(check_cache())
```

**Target:** >70% hit rate after warming up

---

## 🐛 Troubleshooting

### **"Dashboard endpoint returns 500 error"**

Check backend logs:
```bash
docker-compose logs backend --tail=50
```

Common causes:
- Missing database indexes (run migration)
- Redis connection failed (check `REDIS_URL`)
- Database timeout (increase `pool_timeout`)

### **"React Query hook not working"**

Ensure QueryClientProvider is setup:
```tsx
// pages/_app.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

function MyApp({ Component, pageProps }) {
  return (
    <QueryClientProvider client={queryClient}>
      <Component {...pageProps} />
    </QueryClientProvider>
  );
}
```

### **"Dashboard still slow after optimization"**

1. **Check database connection:**
   ```bash
   psql $DATABASE_URL -c "SELECT version();"
   ```

2. **Check indexes are being used:**
   ```sql
   EXPLAIN ANALYZE
   SELECT * FROM conflicts WHERE incidence_date >= NOW() - INTERVAL '12 months';
   ```
   Should show `Index Scan using idx_conflicts_incidence_date`

3. **Check connection pool:**
   ```bash
   curl http://localhost:8000/api/v1/monitoring/metrics
   ```
   Look for `db_pool_size` and `db_pool_available`

4. **Clear cache and restart:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

---

## 🎉 Success Metrics

After implementation, you should see:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Dashboard Load Time | 60-120s | 2-5s | **95%** ↓ |
| API Calls on Load | 5-6 | 1 | **83%** ↓ |
| DB Query Time | ~1000ms | ~50ms | **95%** ↓ |
| Time to Interactive | 2+ min | <5s | **95%** ↓ |
| User Complaints | Many | None | **100%** ↓ |

---

## 📝 Post-Implementation Tasks

- [ ] Add performance monitoring alerts
- [ ] Document cache clearing procedure for admins
- [ ] Update user documentation
- [ ] Train team on new architecture
- [ ] Schedule monthly performance review
- [ ] Consider adding APM (Application Performance Monitoring)

---

## 🚀 Next Optimizations (Future)

1. **Server-Side Rendering (SSR)** - Pre-render dashboard on server
2. **Service Worker Caching** - Offline-first approach
3. **Incremental Static Regeneration** - Static pages with revalidation
4. **Edge Functions** - Deploy API closer to users
5. **Database Read Replicas** - Separate read/write databases

---

**Need Help?**
- Check [PERFORMANCE_OPTIMIZATION.md](./PERFORMANCE_OPTIMIZATION.md) for detailed explanations
- Review backend logs: `docker-compose logs backend`
- Enable React Query DevTools for debugging
- Contact team lead if issues persist

---

**Implementation Date:** _____________  
**Implemented By:** _____________  
**Performance Before:** _____ seconds  
**Performance After:** _____ seconds  
**Success:** ☐ Yes ☐ No
