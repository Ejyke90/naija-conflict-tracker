# Capability Delta: Dashboard Monitoring & Data Fetch Resilience

## ADDED Requirements

### Requirement: Consistent Error Response Format
The system SHALL return error responses in a consistent JSON format across all dashboard data endpoints.

**Format:**
```json
{
  "status": "ok" | "degraded" | "error",
  "data": [...],
  "message": string | null,
  "cached": boolean,
  "cached_at": ISO8601 timestamp | null
}
```

**Status Values:**
- `"ok"`: Data is fresh from database
- `"degraded"`: Data is stale from Redis cache (database unavailable for >TTL period)
- `"error"`: Invalid request (bad parameters, unsupported state, etc.)

#### Scenario: Seasonal analysis with valid data
- **WHEN** client requests `/api/v1/timeseries/seasonal-analysis?state=Lagos`
- **AND** data exists in database
- **THEN** endpoint returns HTTP 200 with status="ok"
- **AND** response includes seasonal pattern data

#### Scenario: Seasonal analysis with no data
- **WHEN** client requests `/api/v1/timeseries/seasonal-analysis?state=Bayelsa`
- **AND** no conflict events exist for Bayelsa
- **THEN** endpoint returns HTTP 200 with status="ok"
- **AND** response includes empty seasonalPattern array
- **AND** message field contains "No data available for this period"
- **AND** response is NOT HTTP 404 (graceful degradation)

#### Scenario: Timeseries endpoint serving stale cache
- **WHEN** database becomes unavailable
- **AND** valid cached data exists in Redis (even if expired)
- **THEN** endpoint returns HTTP 200 with status="degraded"
- **AND** response includes cached data (up to 24 hours stale)
- **AND** cached_at timestamp indicates when data was cached
- **AND** message indicates data is from cache: "Database unavailable; serving cached data"

---

### Requirement: Query Timeout Protection
The system SHALL enforce maximum query duration across all dashboard endpoints.

**Timeout Enforcement:**
- Timeout: 15 seconds per request (application-level)
- Database statement timeout: 30 seconds (database-level fallback)

#### Scenario: Query completes within timeout
- **WHEN** client requests `/api/v1/timeseries/monthly-trends?state=Kaduna`
- **AND** query completes in <15 seconds
- **THEN** endpoint returns data in response
- **AND** response includes actual query execution time

#### Scenario: Query exceeds timeout threshold
- **WHEN** client requests `/api/v1/timeseries/monthly-trends` with complex filters
- **AND** query would take >15 seconds to complete
- **THEN** endpoint returns HTTP 200 (not 504) with status="degraded"
- **AND** returns cached data if available
- **AND** message includes: "Query timeout; serving cached data"

---

### Requirement: Hybrid Caching Strategy
The system SHALL use a multi-layer caching approach to optimize dashboard performance.

**Caching Layers:**
1. **Redis Cache** (Layer 1) - TTL varies by endpoint (30min, 12hr, 24hr)
2. **Database Connection Pool** (Layer 2) - Reuse connections, avoid "too many connections" errors
3. **Query Pagination** (Layer 3) - For state comparisons with >10 states

#### Scenario: Cache hit on monthly trends
- **WHEN** client requests `/api/v1/timeseries/monthly-trends?state=Kaduna` twice within 30 minutes
- **THEN** first request queries database and caches result (response time ~500ms)
- **AND** second request retrieves from Redis cache (response time <10ms)
- **AND** cached response includes `"cached": true`

#### Scenario: Cache miss on seasonal analysis
- **WHEN** client requests seasonal analysis for a state
- **AND** no cached result exists in Redis
- **THEN** endpoint queries database (using pooled connection)
- **AND** caches result for 24 hours
- **AND** response includes `"cached": false`

#### Scenario: State comparison with pagination
- **WHEN** client requests trend comparison for >10 states
- **THEN** endpoint returns data for top 10 states immediately
- **AND** remaining states fetched asynchronously in background
- **AND** response includes pagination metadata: `{"total_states": 36, "returned": 10, "offset": 0}`

---

### Requirement: Database Connection Pooling
The system SHALL use connection pooling to handle multiple concurrent dashboard requests.

**Pool Configuration:**
- Pool size: 20 (min connections kept open)
- Max overflow: 10 (additional connections during peaks)
- Pool pre-ping: Enabled (test connection before use)
- Total max connections: 30

#### Scenario: Multiple dashboard users loading simultaneously
- **WHEN** 5 users open the dashboard simultaneously
- **AND** each loads Monthly Trends, Seasonal Patterns, State Comparison sections
- **THEN** system creates at most 15 connections (well below max of 30)
- **AND** connection pool reuses connections across requests
- **AND** requests complete within 500ms response time

#### Scenario: Connection pool exhaustion recovery
- **WHEN** database temporarily drops 5 connections (e.g., network hiccup)
- **AND** pool_pre_ping detects dropped connections
- **THEN** connections are automatically removed from pool
- **AND** new connections created to replenish pool
- **AND** in-flight requests complete without user-facing errors

---

## MODIFIED Requirements

### Requirement: Dashboard Data Fetch (Previously: Might return 404/500)
The system SHALL provide dashboard analytics data through REST endpoints.

**Change**: Add explicit error handling to prevent HTTP 404/500 responses

**Before**:
- If no data found: Return HTTP 404
- If database error: Return HTTP 500
- Frontend receives error and shows "System Status Unavailable"

**After**:
- If no data found: Return HTTP 200 with empty data array and status="ok"
- If database error: Return HTTP 200 with cached data (if available) and status="degraded" or status="error" with helpful message
- Frontend always receives valid JSON and handles gracefully

#### Scenario: Monthly trends endpoint graceful degradation
- **WHEN** client requests monthly trends
- **AND** database connection fails
- **THEN** endpoint returns HTTP 200 (not 500)
- **AND** returns cached data if available (up to 24hr cache)
- **AND** includes status="degraded" to indicate data freshness

---

## REMOVED Requirements

### Requirement: Direct Exception Throwing
**Reason**: HTTP 404/500 exceptions break frontend error handling; replaced with graceful degradation pattern

**Migration**:
- Any endpoint that previously raised `HTTPException(status_code=404)` now returns empty data with status="ok"
- Any endpoint that previously raised `HTTPException(status_code=500)` now returns degraded response with status="degraded"
- Frontend error boundaries no longer needed for these endpoints
