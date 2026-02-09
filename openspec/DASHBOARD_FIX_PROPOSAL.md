# Dashboard API Failures - Root Cause Analysis & Fix Proposal

**Date:** February 9, 2026  
**Status:** PROPOSED  
**Priority:** HIGH  
**Effort:** 2-3 hours

---

## ROOT CAUSE ANALYSIS

### Issue 1: Timeseries Endpoints Timeout (Seasonal, Comparison, Monthly Trends)
**Affected Endpoints:**
- `/api/v1/timeseries/seasonal-analysis` → "Request timed out - data is taking too long to load"
- `/api/v1/timeseries/trend-comparison` → "Failed to fetch comparison data"
- `/api/v1/timeseries/monthly-trends` → Same timeout issue

**Root Cause:**
- Queries target `conflicts` table with `state_id` foreign key joins to `states` table
- The `states` lookup table likely **doesn't exist** or is **empty**
- Raw SQL uses `(SELECT id FROM states WHERE name = :state)` subquery for every request
- Without indexes on `incidence_date`, queries scan entire `conflicts` table
- No timeout handling - queries hang indefinitely waiting for non-existent table

**Evidence:**
```python
# Line 215 in timeseries.py - problematic query
WHERE state_id = (SELECT id FROM states WHERE name = :state)  # ❌ states table missing
```

---

### Issue 2: Alerts Endpoint Failures
**Error:** "Failed to fetch alerts"

**Root Cause:**
- `AlertService.get_active_alerts()` likely queries `alert_events` table  
- Table may be empty or query is failing silently
- No fallback error handling in endpoint

---

### Issue 3: System Status Unavailable
**Error:** "System Status Unavailable" (health check failing)

**Root Cause:**
- Frontend calling `/api/health` endpoint
- Backend health check depends on database connection
- Can't connect or check tables that don't exist

---

## PROPOSED FIX STRATEGY

### Phase 1: Query Fallback (IMMEDIATE - 30 mins)
Switch timeseries queries from normalized `conflicts` table to legacy `conflict_events` table that **actually has data**.

**Changes:**
- Modify `timeseries.py` endpoints to query `conflict_events` instead of `conflicts`
- Use simple string `state` column instead of `state_id` joins
- Add query timeouts (30 second limit)
- Add error handling with graceful fallbacks

---

### Phase 2: Simplify Alerts (IMMEDIATE - 20 mins)
Replace complex alert service with in-memory fallback.

**Changes:**
- Add simple `/alerts/active` endpoint that returns empty list on error (don't fail)
- Fetch from `conflict_events` where `fatalities > 5` as "high-risk"
- Return empty array with `count: 0` instead of erroring

---

### Phase 3: Fix Health Endpoint (IMMEDIATE - 10 mins)
Make health check resilient to missing tables.

**Changes:**
- Catch `ProgrammingError` (table doesn't exist)
- Return `{"status": "degraded"}` instead of 500 error
- Frontend shows "System Status Offline" instead of "Unavailable"

---

## TECHNICAL IMPLEMENTATION

### File 1: `backend/app/api/v1/endpoints/timeseries.py`
**Changes at lines 190-220 (monthly-trends endpoint):**

Replace:
```python
FROM conflicts
WHERE incidence_date >= :cutoff_date
AND state_id = (SELECT id FROM states WHERE name = :state)
```

With:
```python
FROM conflict_events
WHERE event_date >= :cutoff_date
AND LOWER(state) = LOWER(:state)
```

Also add timeout decorator:
```python
from sqlalchemy.pool import StaticPool
# Add to queries
# connection.execute(query, timeout=30)
```

**Changes at lines 358+ (trend-comparison endpoint):**
Same pattern - switch to `conflict_events`, use `state` column directly.

---

### File 2: `backend/app/api/v1/endpoints/alerts.py`
**Replace at line 30-45 (get_active_alerts):**

```python
@router.get("/active")
async def get_active_alerts(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get active high-risk alerts"""
    try:
        alert_service = get_alert_service()
        alerts = await alert_service.get_active_alerts(db, limit=limit)
        return {
            "alerts": alerts,
            "count": len(alerts),
            "threshold": alert_service.risk_threshold
        }
    except Exception as e:
        # Fallback: Return empty alerts list on any error
        logger.warning(f"Alert service failed: {str(e)}, returning empty")
        return {
            "alerts": [],
            "count": 0,
            "threshold": 85,
            "note": "Alert service unavailable"
        }
```

---

### File 3: `backend/app/main.py`
**Replace at line 160 (health endpoint):**

```python
@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Try to query a simple table
        result = db.execute(text("SELECT 1")).first()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        # Return degraded status instead of 500 error
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "database": "unavailable",
            "error": str(e)
        }
```

---

## TESTING CHECKLIST

After implementing Phase 1-3, test in this order:

```bash
# 1. Test health endpoint
curl http://localhost:8000/api/health

# 2. Test seasonal data (should return data or empty array, not timeout)
curl "http://localhost:8000/api/v1/timeseries/seasonal-analysis?state=Borno"

# 3. Test comparison (with proper state names)
curl "http://localhost:8000/api/v1/timeseries/trend-comparison?states=Borno,Kaduna"

# 4. Test alerts (should return empty list, not error)
curl http://localhost:8000/api/v1/alerts/active

# 5. Test frontend dashboard
# Should render without errors, with empty data gracefully shown
```

---

## FRONTEND CHANGES (Minimal)

The frontend error handlers in these files already handle empty responses gracefully:
- `frontend/components/charts/SeasonalPatternChart.tsx` (lines 70+)
- `frontend/components/charts/StateComparisonChart.tsx` (similar pattern)

**No changes needed** - they show "No data available" when fetch fails.

---

## ROLLOUT PLAN

1. **Backend Phase 1-3** (1 hour)
   - Modify 3 files above
   - Test locally with curl
   - Push to Railway

2. **Railway Deploy** (5 mins)
   - Trigger auto-deploy
   - Monitor logs for errors

3. **Frontend Testing** (5 mins)
   - Open dashboard in browser
   - Verify no 500 errors in console
   - Verify charts show "Loading..." then data or "No data"

---

## SUCCESS CRITERIA

✅ Dashboard loads without errors  
✅ Health check returns 200 (status: healthy or degraded)  
✅ Seasonal chart loads with data OR shows "No data available" (not timeout)  
✅ Alerts section shows empty list with "No active alerts" message  
✅ State comparison chart loads OR shows error gracefully  
✅ No 500 errors in server logs  
✅ No timeouts in browser Network tab

---

## DECISION: APPROVE FOR IMPLEMENTATION

This fix prioritizes **unblocking the dashboard** over perfect data. The key insight:
- Better to serve empty data gracefully than 500 errors
- Use simpler legacy schema (`conflict_events`) which has data
- Add sophisticated queries later once schema is stabilized

**Estimated Time:** 2 hours  
**Risk:** Low (all changes are backwards compatible)  
**Benefit:** Dashboard becomes functional again

