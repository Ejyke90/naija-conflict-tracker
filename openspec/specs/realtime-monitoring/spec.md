# Real-Time Monitoring Infrastructure

**Status:** Proposed  
**Created:** 2026-01-28  
**Author:** AI Agent  
**Related:** dashboard-monitoring

## Purpose

Upgrade the Pipeline Monitor from 30-second polling to true real-time WebSocket updates and configure database-backed data quality metrics instead of mock data.

**Current Limitations:**
- Frontend polls every 30 seconds (inefficient, delayed updates)
- Data quality metrics return mock error (no database connection)
- No instant notification of pipeline events/anomalies
- Unnecessary network overhead from continuous polling

**Proposed Solution:**
- WebSocket endpoint pushing live pipeline status updates
- PostgreSQL database configured for real data_quality calculations
- Automatic fallback to polling if WebSocket unavailable
- Real geocoding and validation metrics from actual database queries

## Requirements

### 1. WebSocket Server Infrastructure

**Backend (FastAPI):**
- New WebSocket endpoint: `/ws/monitoring/pipeline-status`
  - Development: `ws://localhost:8000/ws/monitoring/pipeline-status`
  - Production (Railway): `wss://naija-conflict-tracker-production.up.railway.app/ws/monitoring/pipeline-status`
- Broadcast pipeline status updates every 5 seconds to connected clients
- Handle client connections/disconnections gracefully
- Support multiple concurrent WebSocket clients
- Emit events on: status changes, new anomalies, quality threshold breaches

**Dependencies:**
```python
# requirements.txt additions
websockets>=12.0
```

**Acceptance Criteria:**
- WebSocket server starts with FastAPI app
- Clients can connect to `/ws/monitoring/pipeline-status` endpoint
- WebSocket URL derived from environment variables (NEXT_PUBLIC_WS_URL or NEXT_PUBLIC_API_URL)
- Server broadcasts JSON pipeline status every 5 seconds
- Connection state properly managed (connect/disconnect/reconnect)
- Supports both `ws://` (development) and `wss://` (production) protocols

**Test Scenario:**
```javascript
// Client connects via WebSocket with environment-aware URL
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsHost = process.env.NEXT_PUBLIC_WS_URL || process.env.NEXT_PUBLIC_API_URL?.replace('http', 'ws') || 'ws://localhost:8000';
const ws = new WebSocket(`${wsHost}/ws/monitoring/pipeline-status`);

ws.onmessage = (event) => {
  const status = JSON.parse(event.data);
  // Receives updates every 5 seconds
  console.log(status.timestamp); // Real-time timestamp
};
```

---

### 2. Database Configuration for Data Quality

**PostgreSQL Setup:**
- Ensure database connection configured (DATABASE_URL)
- Create `data_quality_metrics` table if not exists
- Store geocoding success/failure counts
- Store validation pass/fail counts
- Calculate real-time percentages from actual data

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    geocoding_attempts INTEGER DEFAULT 0,
    geocoding_successes INTEGER DEFAULT 0,
    validation_attempts INTEGER DEFAULT 0,
    validation_passes INTEGER DEFAULT 0,
    metric_type VARCHAR(50),
    source VARCHAR(100)
);

CREATE INDEX idx_quality_timestamp ON data_quality_metrics(timestamp DESC);
```

**Acceptance Criteria:**
- Database initializes automatically on startup
- Real geocoding_success_rate calculated: `(successes / attempts) * 100`
- Real validation_pass_rate calculated: `(passes / attempts) * 100`
- No more "connection refused" errors in data_quality response
- Historical metrics stored for trending

**Test Scenario:**
```bash
# Development
curl http://localhost:8000/api/v1/monitoring/pipeline-status

# Production (Railway)
curl https://naija-conflict-tracker-production.up.railway.app/api/v1/monitoring/pipeline-status

# Response:
{
  "data_quality": {
    "status": "healthy",
    "geocoding_success_rate": 87.3,  # Real from DB
    "validation_pass_rate": 92.1,    # Real from DB
    "total_geocoded": 1523,
    "total_validated": 1489
  }
}
```

---

### 3. Frontend WebSocket Client

**React Component Updates:**
- Replace `setInterval` polling with WebSocket connection
- Maintain polling as fallback when WebSocket unavailable
- Auto-reconnect on disconnection with exponential backoff
- Show connection status indicator (connected/reconnecting/polling)

**Implementation:**
```typescript
useEffect(() => {
  // Build WebSocket URL from environment variables
  const getWebSocketUrl = () => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL;
    if (wsUrl) return `${wsUrl}/ws/monitoring/pipeline-status`;
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const wsProtocol = apiUrl.startsWith('https') ? 'wss:' : 'ws:';
    const wsHost = apiUrl.replace(/^https?:/, wsProtocol);
    return `${wsHost}/ws/monitoring/pipeline-status`;
  };
  
  const ws = new WebSocket(getWebSocketUrl());
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    setStatus(data);
    setLastUpdate(new Date());
  };
  
  ws.onerror = () => {
    // Fallback to polling
    console.warn('WebSocket failed, using polling fallback');
    startPolling();
  };
  
  return () => ws.close();
}, []);
```

**Acceptance Criteria:**
- WebSocket connection established on component mount
- Real-time updates received without manual refresh
- Graceful fallback to 30-second polling if WebSocket fails
- Visual indicator shows connection status
- Component cleans up connection on unmount

**Test Scenario:**
```
# Development (http://localhost:3000)
1. Load dashboard → WebSocket connects to ws://localhost:8000
2. Backend updates pipeline → Frontend updates within 1 second
3. Stop backend → Frontend falls back to polling
4. Restart backend → Frontend reconnects to WebSocket

# Production (https://naija-conflict-tracker.vercel.app)
1. Load dashboard → WebSocket connects to wss://naija-conflict-tracker-production.up.railway.app
2. Backend broadcasts updates → All connected clients update within 1 second
3. Network interruption → Automatic reconnection with exponential backoff
4. Connection restored → WebSocket re-established, polling stops
```

---

### 4. Monitoring Endpoint Enhancements

**Update `/api/v1/monitoring/pipeline-status`:**
- Query real database for data_quality metrics
- Return actual geocoding/validation statistics
- Calculate success rates from database aggregations
- Remove mock error responses

**Database Queries:**
```python
# Calculate real-time metrics
geocoding_stats = db.query(
    func.sum(DataQualityMetric.geocoding_successes),
    func.sum(DataQualityMetric.geocoding_attempts)
).filter(
    DataQualityMetric.timestamp >= datetime.now() - timedelta(hours=24)
).first()

success_rate = (geocoding_stats[0] / geocoding_stats[1]) * 100 if geocoding_stats[1] > 0 else 0
```

**Acceptance Criteria:**
- Endpoint queries database successfully
- Returns real success rates (not hardcoded/mocked)
- Performance remains under 200ms response time
- Handles empty database gracefully (returns 0% rates)

---

## Implementation Plan

### Phase 1: Database Configuration (2 hours)
1. Create database migration script for `data_quality_metrics` table
2. Add database initialization to app startup
3. Create SQLAlchemy model for DataQualityMetric
4. Add database query functions for metric calculations
5. Update monitoring endpoint to use real database queries

**Files to Modify:**
- `backend/app/models/` - New model file
- `backend/alembic/versions/` - New migration
- `backend/app/api/v1/endpoints/monitoring.py` - Update endpoint
- `backend/app/core/database.py` - Ensure connection configured

### Phase 2: WebSocket Backend (3 hours)
1. Install websockets dependency
2. Create WebSocket manager class (connection pool)
3. Add WebSocket endpoint to FastAPI app
4. Implement broadcast logic (5-second interval)
5. Add error handling and reconnection logic

**Files to Create:**
- `backend/app/websockets/manager.py` - WebSocket connection manager
- `backend/app/websockets/monitoring.py` - Monitoring WebSocket handler
- `backend/app/api/v1/websockets.py` - WebSocket routes

**Files to Modify:**
- `backend/app/main.py` - Register WebSocket routes
- `backend/requirements.txt` - Add websockets dependency

### Phase 3: Frontend WebSocket Client (2 hours)
1. Create WebSocket hook (`useWebSocket`)
2. Update PipelineMonitor to use WebSocket
3. Add connection status UI indicator
4. Implement polling fallback logic
5. Add reconnection with exponential backoff

**Files to Modify:**
- `frontend/hooks/useWebSocket.ts` - New custom hook
- `frontend/components/dashboard/PipelineMonitor.tsx` - WebSocket integration
- `frontend/components/ui/ConnectionStatus.tsx` - New status indicator

### Phase 4: Testing & Documentation (1 hour)
1. Test WebSocket connection lifecycle
2. Verify real database metrics display correctly
3. Test fallback to polling on connection failure
4. Update API documentation
5. Document WebSocket connection details

**Files to Create/Update:**
- `backend/tests/test_websocket_monitoring.py` - WebSocket tests
- `README.md` or `DEPLOYMENT_NOTES.md` - WebSocket setup docs

---

## Technical Specifications

### WebSocket Message Format
```json
{
  "type": "pipeline_status_update",
  "timestamp": "2026-01-28T12:34:56.789Z",
  "data": {
    "timestamp": "2026-01-28T12:34:56.789Z",
    "scraping_health": { /* ... */ },
    "data_quality": {
      "status": "healthy",
      "geocoding_success_rate": 87.3,
      "validation_pass_rate": 92.1,
      "total_geocoded": 1523,
      "total_validated": 1489,
      "last_updated": "2026-01-28T12:34:50.000Z"
    },
    "anomalies": [ /* ... */ ],
    "alerts": [ /* ... */ ],
    "overall_status": "healthy"
  }
}
```

### Environment Variables
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:password@localhost:5432/conflict_tracker
WEBSOCKET_BROADCAST_INTERVAL=5  # seconds
WEBSOCKET_MAX_CONNECTIONS=100

# Frontend (.env.local)
# Development
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Production (Vercel → Railway)
NEXT_PUBLIC_API_URL=https://naija-conflict-tracker-production.up.railway.app
NEXT_PUBLIC_WS_URL=wss://naija-conflict-tracker-production.up.railway.app

# Or let frontend auto-detect from NEXT_PUBLIC_API_URL
# wss://naija-conflict-tracker-production.up.railway.app derived from https://naija-conflict-tracker-production.up.railway.app
# Frontend URL (Vercel): https://naija-conflict-tracker.vercel.app
```

### Database Connection String
```python
# Default for local development
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/conflict_tracker"

# Production (Railway/Heroku)
DATABASE_URL = os.getenv("DATABASE_URL")
```

---

## Migration Strategy

**Step 1: Database First (No Breaking Changes)**
- Deploy database schema
- Update monitoring endpoint to use real queries
- Existing polling continues to work

**Step 2: WebSocket Backend (Additive)**
- Add WebSocket endpoint
- Existing HTTP endpoint remains functional
- No frontend changes yet

**Step 3: Frontend Update (Graceful Degradation)**
- Deploy WebSocket client with polling fallback
- Works with or without WebSocket support
- Zero downtime migration

**Rollback Plan:**
- Frontend: Remove WebSocket code, keep polling
- Backend: Disable WebSocket endpoint (comment out route)
- Database: No rollback needed (additive schema)

---

## Success Metrics

**Performance:**
- WebSocket updates arrive within 1 second of backend change
- Database queries complete in <100ms
- Frontend memory usage stable (no WebSocket leaks)
- Support 50+ concurrent WebSocket connections

**Reliability:**
- 99%+ WebSocket uptime
- Automatic reconnection on disconnection
- Zero data loss during connection transitions
- Polling fallback activates within 5 seconds

**User Experience:**
- Real-time updates visible immediately
- Clear connection status indicator
- No page refresh needed for updates
- Smooth transition between WebSocket/polling

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Database connection fails | High | Graceful error handling, return empty metrics |
| WebSocket library conflicts | Medium | Pin websockets version, test dependencies |
| Too many connections crash server | High | Implement connection limits (max 100) |
| Polling fallback doesn't trigger | Medium | Comprehensive error handling, timeout detection |
| Database query slow | Medium | Add indexes, cache recent metrics in Redis |

---

## Open Questions

1. **Redis Integration:** Should we cache data_quality metrics in Redis for faster WebSocket broadcasts?
   - **Recommendation:** Start with direct DB queries, add Redis if latency >200ms

2. **Authentication:** Should WebSocket connections require auth tokens?
   - **Recommendation:** Yes for production, use JWT token in connection URL

3. **Historical Data:** How long to retain data_quality_metrics?
   - **Recommendation:** 90 days, add cleanup job

4. **Alert System:** Should critical anomalies trigger instant WebSocket push notifications?
   - **Recommendation:** Yes, add priority messaging for alerts

---

## Approval Required

**Proposed Changes:**
- ✅ Add WebSocket real-time updates
- ✅ Configure PostgreSQL for data_quality metrics
- ✅ Maintain backward compatibility with polling
- ✅ ~8 hours estimated implementation time

**Breaking Changes:** None (graceful degradation ensures compatibility)

**Dependencies:** PostgreSQL database, websockets library

**Deployment Requirements:**
- DATABASE_URL must be configured
- PostgreSQL server accessible from backend
- WebSocket protocol allowed through firewall/proxy

---

**Ready to proceed?** Reply with:
- **"Approved"** to begin implementation
- **"Approved with changes: [specify]"** for modifications
- **"Rejected"** with feedback for revision
