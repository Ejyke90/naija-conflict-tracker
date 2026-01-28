# Proposal: Connect Pipeline Monitor to Real-Time API

## Intent

Connect the Pipeline Monitor component in the dashboard to the backend API to display real-time pipeline status data instead of hardcoded sample values. This will enable administrators to monitor the actual health and performance of the data collection and processing pipeline.

## Problem Statement

### Current State
The Pipeline Monitor component displays **static, hardcoded sample data** that never changes:
- ❌ Shows fixed timestamp from 2026-01-20
- ❌ Always displays "running" status regardless of actual pipeline state
- ❌ Static metrics: 12/15 sources, 247 articles, 23 events
- ❌ No real-time updates or refresh capability
- ❌ Cannot diagnose actual pipeline issues
- ❌ Backend API endpoint exists (`/api/v1/monitoring/pipeline-status`) but is unused

### Impact
**Reduced operational visibility** - Administrators cannot:
- Monitor actual pipeline health and performance
- Detect when scraping jobs fail
- Track data processing throughput
- Identify geocoding or validation issues
- Respond to pipeline problems in real-time
- Optimize resource usage based on actual metrics

### Business Value
1. **Operational Excellence:** Real-time visibility into data pipeline health
2. **Problem Detection:** Identify and resolve pipeline issues before data quality degrades
3. **Resource Optimization:** Monitor system performance and optimize accordingly
4. **Data Quality:** Track validation rates and geocoding success in real-time
5. **Accountability:** Demonstrate system reliability to stakeholders

## Scope

### In Scope
**Frontend (React/Next.js):**
- Update `PipelineMonitor.tsx` to fetch data from API
- Add loading states during API calls
- Add error handling for failed requests
- Implement auto-refresh (every 30 seconds)
- Display real-time metrics:
  - Pipeline status (running, completed, failed, idle)
  - Last run timestamp (actual)
  - Sources processed (actual count)
  - Articles collected (actual count)
  - Events extracted (actual count)
  - Geocoding success rate (actual percentage)
  - Validation pass rate (actual percentage)
  - System health indicators (Redis, database, API)

**Backend (FastAPI):**
- Ensure `/api/v1/monitoring/pipeline-status` endpoint is functioning
- Verify response schema matches frontend expectations
- Add CORS headers if needed for local development

**Data Flow:**
- Component mounts → Fetch initial data
- Display loading skeleton
- Show data or error state
- Set up 30-second polling interval
- Clean up interval on unmount

### Out of Scope
❌ Modifying the backend endpoint structure (use existing endpoint as-is)
❌ Adding new pipeline metrics not already in the API
❌ Real-time WebSocket connection (use polling for simplicity)
❌ Pipeline control features (start/stop pipeline)
❌ Historical pipeline metrics or trends
❌ Email alerts for pipeline failures

## Approach

### Technical Implementation

1. **API Integration Pattern:**
```typescript
const fetchPipelineStatus = async () => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const response = await fetch(`${apiUrl}/api/v1/monitoring/pipeline-status`);
  if (!response.ok) throw new Error('Failed to fetch pipeline status');
  return await response.json();
};
```

2. **State Management:**
```typescript
const [status, setStatus] = useState<PipelineStatus | null>(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
```

3. **Auto-Refresh:**
```typescript
useEffect(() => {
  fetchData();
  const interval = setInterval(fetchData, 30000); // 30 seconds
  return () => clearInterval(interval);
}, []);
```

4. **Error Handling:**
- Display user-friendly error messages
- Fall back to "Pipeline status unavailable" if API fails
- Show last successful update timestamp
- Retry on error after interval

### User Experience Flow

1. User opens Dashboard → "Pipeline" tab
2. Component shows loading skeleton (1-2 seconds)
3. Real-time data populates all metrics
4. Auto-refreshes every 30 seconds
5. If error occurs: Shows error message, retries automatically
6. Visual indicators: Green (healthy), Yellow (warning), Red (error)

## Changes

### Modified Components
- `frontend/components/dashboard/PipelineMonitor.tsx` - Add API integration
- No backend changes required (endpoint already exists)

### Dependencies
- No new dependencies required
- Uses existing `fetch` API
- Uses existing React hooks (`useState`, `useEffect`)

## Migration Path

**Phase 1: Implementation (1 hour)**
- Update PipelineMonitor component with API calls
- Add loading and error states
- Test with backend running locally

**Phase 2: Testing (30 minutes)**
- Verify data displays correctly
- Test error handling (backend offline)
- Verify auto-refresh works
- Check performance (no memory leaks)

**Phase 3: Deployment**
- Deploy frontend changes
- Verify production API endpoint is accessible
- Monitor for errors in production

## Success Criteria

✅ Pipeline Monitor displays real-time data from backend API
✅ Component shows loading state during fetch
✅ Error messages display when API is unavailable
✅ Data auto-refreshes every 30 seconds
✅ No console errors or warnings
✅ Performance: Component does not cause memory leaks
✅ UX: Smooth transitions between loading/loaded/error states

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Backend API offline | Component shows error | Graceful error handling, fallback message |
| API returns unexpected schema | Component crashes | Add schema validation, TypeScript types |
| Auto-refresh causes performance issues | UI lag | Use cleanup in useEffect, debounce if needed |
| CORS issues in development | API calls fail | Add CORS headers to backend, document setup |

## Testing Plan

**Manual Testing:**
1. Start backend server
2. Open dashboard → Pipeline tab
3. Verify real-time data displays
4. Stop backend → Verify error handling
5. Restart backend → Verify recovery
6. Wait 30 seconds → Verify auto-refresh

**Automated Testing:**
- Not required for this targeted fix (component-level change only)

## Rollback Plan

If issues arise:
1. Revert `PipelineMonitor.tsx` to previous version (hardcoded data)
2. Component continues to work with static data
3. No database or backend changes to rollback
