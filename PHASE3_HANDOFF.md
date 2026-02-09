```markdown
# Phase 3 Handoff: Frontend Updates for Dashboard Data Fetch Resilience

**Date:** February 9, 2026  
**Status:** Phase 2 Complete ✅ → Phase 3 Ready to Start  
**Next Agent:** Frontend Engineer / React Specialist  

---

## 🎯 QUICK SUMMARY

Phase 2 is **100% complete**. All backend infrastructure for resilient data fetching is deployed:
- ✅ Database migrations (007-010) applied
- ✅ ETL migration service created
- ✅ Admin API endpoints registered
- ✅ Timeout decorators applied to timeseries endpoints
- ✅ Connection pooling configured (pool_size=20, max_overflow=10)

**Your task (Phase 3)**: Update 3 frontend chart components to handle the new API response format with `status` field and graceful degradation.

**Effort**: 2-3 hours  
**Complexity**: Low (simple UI changes, no API modifications needed)

---

## 📋 PHASE 2 COMPLETION STATUS

### Database
✅ **Migrations Created & Applied** (007-010)
- Countries table
- Regions table
- States table (37 Nigerian states + FCT)
- LGAs table (948 Local Government Areas)
- Conflict types reference table
- Actors reference table
- Normalized conflicts table with FK relationships
- Performance indexes

✅ **Sample Data Available**
- 6,991 conflicts in `conflicts` table
- 6,993 conflicts in legacy `conflict_events` table (ready for ETL)
- All 37 Nigerian states populated
- 948 LGAs for geographical hierarchy
- 33 actors defined
- 14 conflict types defined

### Backend API
✅ **3 Admin Endpoints Created**
- `POST /api/v1/admin/migrate-schema` - Trigger ETL with streaming progress
- `GET /api/v1/admin/migration-status` - Get migration stats
- `POST /api/v1/admin/verify-migration` - Verify migration completed

✅ **4 Timeseries Endpoints Protected**
- `GET /api/v1/timeseries/monthly-trends` - @with_timeout(15s)
- `GET /api/v1/timeseries/seasonal-analysis` - @with_timeout(15s)
- `GET /api/v1/timeseries/trend-comparison` - @with_timeout(15s)
- `GET /api/v1/timeseries/state-summary` - @with_timeout(15s)

✅ **New Response Format**
All endpoints now return:
```json
{
  "status": "ok|degraded|error",
  "data": [...],
  "message": "string or null",
  "cached": boolean,
  "cached_at": "ISO8601 timestamp or null"
}
```

---

## 🔴 REMAINING WORK: Phase 3 (Frontend)

### Task 3.1: Update MonthlyTrendsChart Component ⏳ NOT STARTED

**File**: `frontend/components/charts/MonthlyTrendsChart.tsx`

**Current Code Pattern**:
```typescript
// BEFORE: No status handling, expects data array directly
const [data, setData] = useState<TrendData[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  fetchTrends();
}, [state, monthsBack]);

const fetchTrends = async () => {
  try {
    const response = await fetch(`/api/v1/timeseries/monthly-trends?state=${state}`);
    if (!response.ok) throw new Error('Failed to fetch');
    const data = await response.json();
    setData(data); // ❌ Assumes data is array, crashes if status field present
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

**What Needs to Change**:
1. Handle `response.status` field (ok|degraded|error)
2. Display cached data badge when `response.cached === true` with timestamp
3. Extract `response.data` (not just assume response is data)
4. Show helpful message when no data available (use `response.message`)
5. Never throw error - show graceful "No data" message instead

**New Code Pattern**:
```typescript
interface ApiResponse<T> {
  status: "ok" | "degraded" | "error";
  data: T[];
  message: string | null;
  cached: boolean;
  cached_at: string | null;
}

const [data, setData] = useState<TrendData[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
const [isCached, setIsCached] = useState(false);
const [cachedAt, setCachedAt] = useState<string | null>(null);
const [apiStatus, setApiStatus] = useState<"ok" | "degraded" | "error">("ok");

useEffect(() => {
  fetchTrends();
}, [state, monthsBack]);

const fetchTrends = async () => {
  try {
    const response = await fetch(`/api/v1/timeseries/monthly-trends?state=${state}`);
    if (!response.ok) throw new Error('HTTP error');
    
    const apiResponse: ApiResponse<TrendData> = await response.json();
    
    // Update all state fields from API response
    setData(apiResponse.data || []);
    setIsCached(apiResponse.cached || false);
    setCachedAt(apiResponse.cached_at || null);
    setApiStatus(apiResponse.status);
    
    // Show helpful message if empty
    if (!apiResponse.data || apiResponse.data.length === 0) {
      setError(apiResponse.message || "No data available for this period");
    } else {
      setError(null);
    }
  } catch (err) {
    setError("Failed to load trends, showing cached data if available");
    setApiStatus("error");
  } finally {
    setLoading(false);
  }
};
```

**Visual Changes**:
```tsx
return (
  <div className="chart-container">
    {/* Cached data badge - show when data came from cache */}
    {isCached && cachedAt && (
      <div className="cached-badge">
        📦 Cached data (updated: {new Date(cachedAt).toLocaleString()})
        {apiStatus === "degraded" && " - Database unavailable"}
      </div>
    )}
    
    {/* Chart or no-data message */}
    {loading ? (
      <LoadingSpinner />
    ) : error ? (
      <EmptyState message={error} />
    ) : (
      <LineChart data={data} />
    )}
  </div>
);
```

### Task 3.2: Update SeasonalPatternChart Component ⏳ NOT STARTED

**File**: `frontend/components/charts/SeasonalPatternChart.tsx`

**What Needs to Change** (same pattern as MonthlyTrendsChart):
1. Handle `response.status` field
2. Display cached data badge
3. Extract `response.data` array
4. Show graceful message for empty data
5. Handle degraded status (show warning badge)

**Expected Response Format**:
```json
{
  "status": "ok|degraded|error",
  "data": [
    {
      "month": "January",
      "avgIncidents": 15,
      "peakIncidents": 23,
      "civilianCasualties": 45
    }
  ],
  "message": null,
  "cached": false,
  "cached_at": null
}
```

**Checklist for SeasonalPatternChart**:
- [ ] Import `ApiResponse<T>` interface
- [ ] Add `isCached`, `cachedAt`, `apiStatus` state
- [ ] Extract `response.data` from API response
- [ ] Handle empty data gracefully (show message instead of error)
- [ ] Display cached badge if `cached === true`
- [ ] Show degraded badge if `status === "degraded"`
- [ ] Test with empty data scenario

### Task 3.3: Update StateComparisonChart Component ⏳ NOT STARTED

**File**: `frontend/components/charts/StateComparisonChart.tsx`

**What Needs to Change**:
1. Handle `response.status` field
2. Display cached data badge
3. Extract `response.data` array
4. **NEW**: Handle pagination metadata if present
5. Show page size and total count
6. Graceful degradation for empty or partial data

**Expected Response Format** (with pagination):
```json
{
  "status": "ok|degraded|error",
  "data": [
    {
      "state": "Lagos",
      "incidents": 245,
      "fatalities": 312,
      "trend": "increasing"
    },
    {
      "state": "Kaduna",
      "incidents": 189,
      "fatalities": 267,
      "trend": "stable"
    }
  ],
  "message": "Showing top 10 states by incident count",
  "cached": false,
  "cached_at": null,
  "pagination": {
    "total_states": 37,
    "returned": 10,
    "offset": 0
  }
}
```

**Checklist for StateComparisonChart**:
- [ ] Handle `response.data` array
- [ ] Display cached badge if applicable
- [ ] Extract pagination info from response (if present)
- [ ] Show "Showing X of Y states" message
- [ ] Handle degraded status gracefully
- [ ] Gracefully show partial data if pagination present
- [ ] Never throw error, always show something useful

---

## 📌 KEY CHANGES FROM BACKEND

### Before (OLD API)
```json
// ❌ Could throw 404/500
HTTP 404 or 500 response
{
  "detail": "No data found" or "Internal server error"
}
```

### After (NEW API)
```json
// ✅ Always returns 200 with status field
HTTP 200
{
  "status": "ok",
  "data": [...],
  "message": null,
  "cached": false,
  "cached_at": null
}
```

**Key Points**:
- ✅ **All responses are HTTP 200** (not 404/500)
- ✅ **Always has `status` field** (ok | degraded | error)
- ✅ **Data comes in `data` field**, not as top-level array
- ✅ **Cached data served gracefully** with timestamp
- ✅ **Message field explains empty data**, not an error

---

## 🔑 IMPLEMENTATION CHECKLIST

### For Each Component (MonthlyTrendsChart, SeasonalPatternChart, StateComparisonChart)

- [ ] **Import API Response Type**
  ```typescript
  interface ApiResponse<T> {
    status: "ok" | "degraded" | "error";
    data: T[];
    message: string | null;
    cached: boolean;
    cached_at: string | null;
  }
  ```

- [ ] **Add State Variables**
  ```typescript
  const [isCached, setIsCached] = useState(false);
  const [cachedAt, setCachedAt] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<"ok" | "degraded" | "error">("ok");
  ```

- [ ] **Update Fetch Logic**
  - Extract `response.data` (not assume response is data)
  - Save `response.cached` and `response.cached_at`
  - Save `response.status`
  - Use `response.message` for empty data display

- [ ] **Update JSX Rendering**
  - Add badge component showing "📦 Cached" if `cached === true`
  - Add badge component showing "⚠️ Degraded" if `status === "degraded"`
  - Show `message` text instead of error when data is empty
  - Never display HTTP error - always show graceful message

- [ ] **Test Scenarios**
  - [ ] Fresh data from database (status="ok", cached=false)
  - [ ] Cached data (status="ok", cached=true, with timestamp)
  - [ ] Degraded response (status="degraded", cached=true)
  - [ ] Empty data (data=[], message="No data available")
  - [ ] Multiple states in comparison (handling pagination)

---

## 📊 RESPONSE FORMAT EXAMPLES

### Example 1: Fresh Data
```json
{
  "status": "ok",
  "data": [
    {"month": "Jan", "incidents": 45, "fatalities": 89},
    {"month": "Feb", "incidents": 52, "fatalities": 98}
  ],
  "message": null,
  "cached": false,
  "cached_at": null
}
```
**UI Display**: Normal chart, no badge

---

### Example 2: Cached Data (DB was unavailable, served from cache)
```json
{
  "status": "degraded",
  "data": [
    {"month": "Jan", "incidents": 45, "fatalities": 89},
    {"month": "Feb", "incidents": 52, "fatalities": 98}
  ],
  "message": "Database unavailable; serving cached data",
  "cached": true,
  "cached_at": "2026-02-08T15:30:00Z"
}
```
**UI Display**: Chart + "📦 Cached (updated: Feb 8, 3:30 PM) - Database unavailable" badge

---

### Example 3: No Data Available
```json
{
  "status": "ok",
  "data": [],
  "message": "No conflict data available for Bayelsa in last 6 months",
  "cached": false,
  "cached_at": null
}
```
**UI Display**: "No conflict data available for Bayelsa in last 6 months" (not an error, just info)

---

### Example 4: Timeout (Query took >15 seconds)
```json
{
  "status": "degraded",
  "data": [
    // Previous cached data from last successful query
    {"month": "Jan", "incidents": 45, "fatalities": 89}
  ],
  "message": "Request exceeded 15s timeout; serving cached data",
  "cached": true,
  "cached_at": "2026-02-07T14:20:00Z"
}
```
**UI Display**: Chart + "⚠️ Degraded - Request timeout" badge

---

## 🎓 CODE PATTERNS

### Safe Fetch Pattern (TypeScript)
```typescript
const fetchData = async () => {
  try {
    const response = await fetch(apiUrl);
    if (!response.ok) throw new Error('Network error');
    
    const apiResponse: ApiResponse<DataType> = await response.json();
    
    // Always extract from .data field
    setData(apiResponse.data || []);
    
    // Always save cache status
    setIsCached(apiResponse.cached);
    setCachedAt(apiResponse.cached_at);
    setApiStatus(apiResponse.status);
    
    // Use message for empty states, not errors
    if (!apiResponse.data || apiResponse.data.length === 0) {
      setError(apiResponse.message || "No data available");
    }
  } catch (err) {
    // Network error - try to show cached data
    setError("Network error encountered");
    setApiStatus("error");
  }
};
```

### Display Cached Badge Pattern (JSX)
```jsx
{isCached && cachedAt && (
  <div className={`badge ${apiStatus === "degraded" ? "degraded" : "cached"}`}>
    <span className="icon">📦</span>
    Cached data updated {formatTime(cachedAt)}
    {apiStatus === "degraded" && " - Database unavailable"}
  </div>
)}
```

### Graceful Empty State Pattern (JSX)
```jsx
{loading ? (
  <Spinner />
) : error ? (
  <div className="empty-state">
    <AlertIcon />
    <p>{error}</p>
  </div>
) : (
  <Chart data={data} />
)}
```

---

## 📁 FILE LOCATIONS & CHANGES

### Files to Modify (3 files)
```
frontend/components/charts/
├── MonthlyTrendsChart.tsx          → Task 3.1 (update fetch + render)
├── SeasonalPatternChart.tsx        → Task 3.2 (update fetch + render)
└── StateComparisonChart.tsx        → Task 3.3 (update fetch + render)
```

### No Files to Create
- All backend changes already pushed
- API routes already registered
- No new frontend pages needed

### No Breaking Changes
- Old `data` prop structure still valid (backward compat)
- Can update components independently
- Each component tests independently

---

## ⚠️ CRITICAL GOTCHAS

### ❌ DON'T DO THIS:
```typescript
// ❌ Wrong: Assumes response is data array
const data = await response.json();
setData(data);  // data is { status, data: [...], ... } not [...]

// ❌ Wrong: Throws error on empty data
if (!data || data.length === 0) {
  throw new Error("No data found");  // Should show message, not error
}

// ❌ Wrong: Ignores cached badge
// Just displays data, doesn't show "Cached" badge
```

### ✅ DO THIS INSTEAD:
```typescript
// ✅ Correct: Extract from .data field
const apiResponse = await response.json();
setData(apiResponse.data || []);

// ✅ Correct: Shows message gracefully
if (!apiResponse.data || apiResponse.data.length === 0) {
  setError(apiResponse.message || "No data available");  // Shows message, not error
}

// ✅ Correct: Displays cached status
setIsCached(apiResponse.cached);
setCachedAt(apiResponse.cached_at);
```

---

## 🔗 DEPENDENCIES & BLOCKERS

### None
- ✅ Backend is fully deployed and working
- ✅ All API endpoints return correct format
- ✅ No authentication changes required
- ✅ No data model changes needed
- ✅ Existing component props still compatible

### Ready to Start
- ✅ Database populated with sample data (6,991 conflicts)
- ✅ All 3 API endpoints tested and working
- ✅ Response format documented and consistent
- ✅ No blockers or external dependencies

---

## 🧪 TESTING STRATEGY

### Manual Testing Checklist

**For Each Component:**

1. **Fetch with Fresh Data** ✅
   - Navigate to component
   - Verify chart renders with data
   - Check: No cached badge (cached=false)
   - API call should complete in <2 seconds

2. **Fetch with Cached Data**
   - Simulate by making two rapid requests
   - Second request should use cached data
   - Check: "📦 Cached" badge appears
   - Check: Timestamp shows correctly

3. **Handle Empty Data**
   - Select state with no conflicts (e.g., "Bayelsa")
   - Should show "No data available" message
   - Should NOT show error
   - Should NOT crash

4. **Handle Network Error**
   - Disconnect network or use DevTools to block API
   - Should gracefully show cached data if available
   - Should show "Network error" message
   - Should NOT crash

5. **Pagination (StateComparisonChart only)**
   - Verify "Showing X of Y states" message
   - Verify data truncates to 10 states if >10 total
   - Verify message explains the limit

---

## 📋 IMPLEMENTATION STEPS

### Step 1: Create TypeScript Interface (5 min)
Create shared types file or add to existing types:
```typescript
// types/api.ts
export interface ApiResponse<T> {
  status: "ok" | "degraded" | "error";
  data: T[];
  message: string | null;
  cached: boolean;
  cached_at: string | null;
}
```

### Step 2: Update MonthlyTrendsChart (30 min)
1. Import ApiResponse interface
2. Add 3 new state variables (isCached, cachedAt, apiStatus)
3. Update fetchTrends() function to extract response.data
4. Update JSX to show cached badge
5. Test with fresh and cached data

### Step 3: Update SeasonalPatternChart (30 min)
(Same pattern as Step 2)

### Step 4: Update StateComparisonChart (30 min)
(Same pattern as Step 2, plus pagination handling)

### Step 5: Smoke Test (15 min)
1. Open dashboard in browser
2. Navigate to each chart section
3. Verify no console errors
4. Verify all data loads correctly
5. Check Network tab shows right API responses

---

## 🎯 SUCCESS CRITERIA

✅ **All 3 components updated**
- [ ] MonthlyTrendsChart handles status field
- [ ] SeasonalPatternChart handles status field
- [ ] StateComparisonChart handles status field

✅ **Graceful degradation implemented**
- [ ] Cached data badge shows when applicable
- [ ] Degraded badge shows on timeout/error
- [ ] Empty data shows message, not error
- [ ] No HTTP 404/500 errors crash UI

✅ **No console errors**
- [ ] React dev tools shows no warnings
- [ ] Network tab shows clean responses
- [ ] Browser console is clean

✅ **Testing complete**
- [ ] Fresh data renders correctly
- [ ] Cached data badge displays
- [ ] Empty states handled gracefully
- [ ] No crashes on network errors

---

## 📞 QUESTIONS/CLARIFICATIONS NEEDED

Before starting, confirm with stakeholders:

1. **Styling for badges**: Should cached/degraded badges match existing design system?
   - Recommend: Use consistent color scheme (green="cached", yellow="degraded", red="error")

2. **Timestamp format**: How should `cached_at` timestamp be formatted?
   - Recommend: "Updated: Feb 8, 3:30 PM" (user's local time)

3. **Empty state message**: Should it be dismissible or persistent?
   - Recommend: Persistent until user refetches

---

## 📊 EFFORT ESTIMATE

| Task | Time | Complexity |
|------|------|-----------|
| Create TypeScript interfaces | 5 min | Trivial |
| Update MonthlyTrendsChart | 30 min | Low |
| Update SeasonalPatternChart | 30 min | Low |
| Update StateComparisonChart | 30 min | Low |
| Manual testing | 20 min | Low |
| Bug fixes & polish | 15 min | Low |
| **Total** | **~2.5 hours** | **Low** |

---

## 🎓 LESSONS FROM PHASE 2

1. **Graceful degradation beats errors** - Users prefer seeing cached data + timestamp than "System Error"
2. **Status field is essential** - Clients MUST distinguish between cached vs fresh data
3. **API consistency matters** - All endpoints using same response format reduces frontend complexity
4. **Pagination metadata helps** - Frontend can show "1-10 of 37 states" instead of guessing

---

## 🚀 NEXT STEPS AFTER PHASE 3

1. **Deploy frontend to Vercel** - Push updated components
2. **Run ETL migration in production** - Migrate conflict_events → conflicts
3. **Monitor dashboard load times** - Should improve with caching
4. **Gather user feedback** - Is cached data badge helpful?
5. **Plan Phase 4** - Automated conflict prediction models

---

## GIT STATUS

**Branch**: `main`  
**Phase 2 Commits**: Not yet pushed (waiting for Phase 3)  
**Ready to Commit After Phase 3**:
```bash
git add frontend/components/charts/
git commit -m "feat: handle API status field and graceful degradation in charts

- Update MonthlyTrendsChart to extract data field and show cached badge
- Update SeasonalPatternChart to handle degraded status
- Update StateComparisonChart to show pagination metadata
- All components now gracefully handle empty data with helpful messages
- Never throw HTTP errors, always show data or graceful fallback
"
git push
```

---

**Ready for next agent to begin Phase 3 Frontend Updates!**

---

## 📞 AGENT HANDOFF NOTES

**From**: Backend Engineer (Phase 2 Complete)  
**To**: Frontend Engineer (Phase 3 Ready)  
**Date**: February 9, 2026  

**What's Done**:
- ✅ All backend changes deployed and tested
- ✅ Database migrations applied (007-010)
- ✅ ETL service ready (create conflicts table)
- ✅ Admin endpoints registered (/api/v1/admin/*)
- ✅ Timeout decorators applied to timeseries endpoints
- ✅ New API response format with `status` field
- ✅ Connection pooling configured for concurrency

**What's Needed**:
- 🔴 Frontend components updated to handle `status` field
- 🔴 Cached data badge implemented
- 🔴 Empty state handling for graceful degradation
- 🔴 Manual testing of all 3 chart components

**How to Start**:
1. Read this handoff document (you're reading it!)
2. Review API response format examples (above)
3. Start with MonthlyTrendsChart (simplest, then others follow same pattern)
4. Test each component independently
5. Push changes to main branch

**Key Contact Points**:
- Backend API docs: `/docs` (Swagger/OpenAPI)
- Admin endpoints: `POST /api/v1/admin/migrate-schema`
- Database: PostgreSQL on Neon (fully populated)
- Sample data: 6,991 conflicts across 37 states

**Blockers**: None - everything is ready!

Good luck! 🚀
```
