# Fix Dashboard API Connectivity

## Why

The Nigeria Conflict Tracker dashboard is displaying completely incorrect data, showing "0 Events awaiting verification" and "DATABASE SIZE 0 VERIFIED" when the database actually contains 6,993 conflict events with 6,982 unverified events and 1 active high-risk alert. This critical data disconnect prevents users from seeing real Nigerian conflict data that is essential for monitoring and decision-making. The dashboard at https://naija-conflict-tracker.vercel.app/dashboard must reflect accurate database values for this real-world conflict monitoring system.

## What Changes

- **API Data Pipeline Fix**: Ensure dashboard APIs properly connect to and query the `conflict_events` view (6,993 records) instead of returning zero values
- **Authentication/Authorization Resolution**: Fix any auth issues preventing data access to dashboard endpoints
- **Database Connection Validation**: Verify backend services can successfully query the PostgreSQL database
- **Data Accuracy Verification**: Ensure all dashboard metrics show actual database values:
  - Events awaiting verification: 6,982 (not 0)
  - Database size verified: 11 (not 0) 
  - Last activity: Feb 9, 2026 (not "NEVER")
  - Active high-risk alerts: 1 (not "No active high-risk alerts")

## Capabilities

### New Capabilities
- `dashboard-data-accuracy`: Ensure dashboard displays real database values instead of placeholder/zero values
- `api-connectivity-validation`: Verify all dashboard API endpoints successfully connect to database and return accurate data

### Modified Capabilities
- `monitoring-endpoints`: Fix existing `/api/v1/monitoring/*` endpoints to properly query `conflict_events` view
- `authentication-flow`: Ensure dashboard data access is not blocked by authentication issues

## Impact

**Affected Components**:
- Backend: `/app/api/v1/endpoints/monitoring.py` - API endpoints serving dashboard data
- Backend: Database connection and query execution for `conflict_events` view
- Frontend: Dashboard components expecting real data from API endpoints
- Authentication: Any auth middleware blocking data access

**Critical Systems**:
- Dashboard validation queue metrics
- High-risk alerts display
- Monthly trends and forecasting data
- Real-time conflict monitoring capabilities

**User Impact**: Users currently see a completely empty/inactive system when there is substantial real conflict data requiring attention and verification.
