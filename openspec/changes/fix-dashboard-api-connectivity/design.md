# Fix Dashboard API Connectivity - Technical Design

## Context

**Current State**: The Nigeria Conflict Tracker dashboard is displaying completely incorrect data (all zeros) despite having 6,993 real conflict events in the PostgreSQL database. The `conflict_events` view contains the correct data, but the frontend dashboard at https://naija-conflict-tracker.vercel.app/dashboard shows "0 Events awaiting verification", "DATABASE SIZE 0 VERIFIED", and "No active high-risk alerts".

**Database Reality**:
- `conflict_events` view: 6,993 total records
- Unverified events: 6,982 (99.8% of database)
- Verified events: 11
- Active alerts: 1 high-risk alert (92.5 risk score)
- Last activity: Feb 9, 2026

**Technical Stack**:
- Backend: FastAPI (Python) on Railway
- Database: PostgreSQL with `conflict_events` view
- Frontend: Next.js 14 dashboard consuming REST APIs
- Authentication: JWT-based system

## Goals / Non-Goals

**Goals:**
- Restore accurate data display in dashboard showing real database values
- Fix API connectivity issues preventing data retrieval from `conflict_events` view
- Ensure authentication/authorization allows proper data access
- Validate all dashboard metrics display correct counts and timestamps
- Maintain existing UI/UX - only data values should change

**Non-Goals:**
- No changes to database schema or `conflict_events` view structure
- No frontend UI component modifications (only data updates)
- No breaking changes to existing API contracts
- No changes to authentication system (only fix access issues)

## Decisions

### 1. API Endpoint Investigation Strategy
**Decision**: Systematic testing of monitoring endpoints from database to frontend
**Rationale**: Need to identify where the data pipeline breaks - database connection, API logic, or frontend consumption
**Alternatives considered**: 
- Frontend-only fixes (rejected - backend data issue)
- Database view recreation (rejected - view contains correct data)

### 2. Database Connection Validation
**Decision**: Direct database query testing via API endpoints
**Rationale**: Verify backend can successfully connect and query `conflict_events` view
**Implementation**: Add health check endpoints that return actual database counts

### 3. Authentication Flow Analysis
**Decision**: Test dashboard data access with provided credentials (info@thenextier.com / test12345)
**Rationale**: Ensure authentication is not blocking data retrieval for authorized users
**Implementation**: Test API endpoints both with and without authentication

### 4. Error Handling Enhancement
**Decision**: Add detailed logging and error responses for debugging
**Rationale**: Current failures are silent - need visibility into where queries fail
**Implementation**: Enhanced error logging in monitoring endpoints

## Risks / Trade-offs

**[Risk]** Database connection pool exhaustion → **Mitigation**: Test connection pooling and add connection health checks
**[Risk]** Authentication middleware blocking data access → **Mitigation**: Test endpoints with different auth contexts and add bypass for debugging
**[Risk]** Frontend caching serving stale zero values → **Mitigation**: Clear browser cache and add cache-busting headers
**[Risk]** Railway deployment environment differences → **Mitigation**: Test locally first, then validate Railway configuration

**Trade-offs**: 
- Temporary debugging endpoints vs. production cleanliness → Choose debugging for rapid resolution
- Direct database queries vs. existing ORM patterns → Use existing patterns with added validation

## Migration Plan

**Phase 1: Local Testing**
1. Set up local environment with database connection
2. Test monitoring endpoints directly via curl/Postman
3. Verify `conflict_events` view queries return correct data
4. Test authentication flow with provided credentials

**Phase 2: Backend Fixes**
1. Fix any database connection issues identified
2. Resolve authentication/authorization blocks
3. Add enhanced error logging and validation
4. Test endpoints locally with real data

**Phase 3: Frontend Validation**
1. Test dashboard locally with fixed backend
2. Verify all metrics display correct values
3. Clear any caching issues
4. Validate real-time data updates

**Phase 4: Deployment**
1. Deploy backend fixes to Railway
2. Monitor deployed endpoint responses
3. Validate production dashboard shows correct data
4. Remove any temporary debugging code

**Rollback Strategy**: 
- Keep original monitoring.py backup
- Railway automatic rollback on deployment failure
- Quick revert via git if issues persist

## Open Questions

1. Are the monitoring endpoints actually being called by the frontend dashboard?
2. Is there a frontend API configuration issue (wrong base URL, CORS, etc.)?
3. Are the authentication tokens properly being passed to dashboard API calls?
4. Is there a Redis caching layer serving stale zero values?
5. Are there any Railway environment variables missing for database connectivity?
