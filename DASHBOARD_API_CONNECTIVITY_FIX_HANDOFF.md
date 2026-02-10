# Dashboard API Connectivity Fix - Handoff Document

## Issue Summary

**CRITICAL DATA DISCONNECT**: The Nigeria Conflict Tracker dashboard is displaying completely incorrect data (all zeros) despite having 6,993 real conflict events in the PostgreSQL database.

### Database Reality vs UI Display
| Metric | Database Reality | UI Display | Status |
|--------|------------------|------------|---------|
| Unverified Events | **6,982** | **0** | ❌ WRONG |
| Verified Events | **11** | **0** | ❌ WRONG |
| Total Database Size | **6,993** | **0** | ❌ WRONG |
| Last Activity | **Feb 9, 2026** | **NEVER** | ❌ WRONG |
| Active Alerts | **1** (92.5 risk score) | **0** | ❌ WRONG |

### Root Cause Analysis
The UI is **not connected to the actual database** or there's a **critical API failure** preventing data retrieval. The frontend is displaying default/placeholder values instead of real-time data.

## OpenSpec Change Created

**Change Location**: `openspec/changes/fix-dashboard-api-connectivity/`  
**Schema**: Spec-driven workflow  
**Progress**: 4/4 artifacts complete ✓

### Artifacts Ready for Implementation
1. **proposal.md** - Problem statement and impact analysis
2. **design.md** - Technical approach and migration plan
3. **specs/** - Detailed requirements (2 spec files)
   - `dashboard-data-accuracy/spec.md`
   - `api-connectivity-validation/spec.md`
4. **tasks.md** - 12 implementation phases with 47 specific tasks

## Technical Details

### Database Structure
- **Primary Table**: `conflicts` (5,998 records - matches original MySQL schema)
- **Dashboard View**: `conflict_events` (6,993 records - denormalized for UI)
- **Alerts Table**: `alert_events` (1 active high-risk alert)

### API Endpoints Affected
- `/api/v1/monitoring/pipeline-status` - Shows database metrics
- `/api/v1/monitoring/recent-events` - Shows recent conflict events  
- `/api/v1/monitoring/data-quality` - Shows validation metrics

### Authentication Context
- **Login**: info@thenextier.com / test12345 ✅
- **Access**: Full verification system ✅
- **URL**: https://naija-conflict-tracker.vercel.app/dashboard

## Implementation Plan

### Phase 1: Local Environment Setup
- Set up local backend with database connection
- Verify access to `conflict_events` view
- Test authentication credentials locally
- Create backup of current `monitoring.py`

### Phase 2: Database Connectivity Testing
- Test direct queries to `conflict_events` view
- Verify connection pool configuration
- Add database health check endpoint
- Test query performance with 6,993 records

### Phase 3: API Endpoint Investigation
- Test all monitoring endpoints locally
- Add detailed error logging
- Identify where data pipeline breaks

### Phase 4: Authentication Flow Validation
- Test endpoints with/without authentication
- Verify JWT token validation
- Check for authorization middleware blocks

### Phase 5: Backend Data Pipeline Fixes
- Fix database connection issues
- Ensure `conflict_events` queries return correct counts
- Update all monitoring endpoints with real data

### Phase 6-12: Testing, Deployment & Verification
- Frontend integration testing
- Performance validation
- Production deployment to Railway
- Final verification of dashboard accuracy

## Key Files to Modify

### Backend Files
- `backend/app/api/v1/endpoints/monitoring.py` - Primary API endpoints
- `backend/app/api/v1/api.py` - Router configuration
- `backend/app/tasks/monitoring_tasks.py` - Background tasks

### Frontend Files
- `frontend/components/dashboard/PerformanceDashboard.tsx` - Dashboard component
- `frontend/contexts/AuthContext.tsx` - Authentication context

## Success Criteria

### Must Achieve
1. Dashboard shows "6,982 Events awaiting verification" (not 0)
2. Dashboard shows "DATABASE SIZE 11 VERIFIED" (not 0)
3. Dashboard shows "LAST ACTIVITY Feb 9, 2026" (not "NEVER")
4. Dashboard shows "1 active high-risk alert" (not "No active high-risk alerts")
5. Monthly trends show real fatality counts (not 0.0)

### Verification Steps
1. Test locally with provided credentials
2. Compare API responses with direct database queries
3. Validate all metrics match database reality
4. Deploy to Railway and test production dashboard
5. Monitor error logs for remaining issues

## Risks & Mitigations

### High Risk
- **Database connection exhaustion** → Add connection health checks
- **Authentication blocking data** → Test with different auth contexts
- **Frontend caching stale data** → Clear cache and add cache-busting

### Medium Risk
- **Railway environment differences** → Test locally first, validate Railway config
- **Performance degradation** → Monitor response times, optimize queries

## Next Steps for Implementation

1. **Start Phase 1**: Local environment setup and database connectivity testing
2. **Work through tasks.md**: 47 specific tasks in logical order
3. **Test locally first**: Verify fixes work before deploying
4. **Deploy to production**: Use Railway deployment with monitoring
5. **Verify production dashboard**: Ensure real Nigerian conflict data is displayed

## Contact Information

**Project**: Nigeria Conflict Tracker  
**Priority**: CRITICAL - Real conflict data not visible to users  
**Impact**: Users cannot see actual Nigerian conflict monitoring data  
**Timeline**: Immediate resolution required

---

**Handoff created**: Feb 10, 2026  
**Status**: Ready for implementation  
**OpenSpec change**: `fix-dashboard-api-connectivity`  
**All artifacts complete**: Ready to start Phase 1
