# Change: Fix Dashboard Data Fetch Resilience

## Problem Statement

Dashboard sections (Monthly Trends, Seasonal Patterns, State Comparison) fail to display data because:

1. **Missing Database Schema**: Core tables (`conflicts`, `states`, `lgas`, `actors`) are defined in SQLAlchemy models but never created by migrations. Only migrations 001-006 exist; they create auth/alerts/locations tables, not conflict data tables.

2. **Inconsistent Error Handling**: Some endpoints (monthly-trends) return graceful empty responses; others (seasonal-analysis, analytics/states) throw 404/500 HTTP errors, breaking the dashboard UI.

3. **No Optimized Data Access**: All queries read directly from database without intelligent caching, pagination, or connection pooling. No query timeouts enforced at application level despite being set at database level.

4. **Data Location Mismatch**: Production data exists in legacy `conflict_events` table, but all queries target non-existent normalized `conflicts` table with no fallback strategy.

## Current State

**Dashboard Sections:**
- ✅ Components exist (MonthlyTrendsChart, SeasonalPatternChart, StateComparisonChart)
- ✅ API endpoints exist (timeseries.py, analytics.py)
- ❌ Endpoints return no data or HTTP errors (404, 500)
- ❌ No graceful degradation when data unavailable
- ❌ Basic error handling inconsistently applied

**Database:**
- ✅ Most recent migration (006): Creates locations table
- ✅ Demo data exists (demo_heatmap.sql) for testing
- ❌ Reference data tables (states, lgas) never created by migration
- ❌ Main conflicts table never created by migration
- ❌ No migrations for actors, relationships, or other normalized schema

**Caching:**
- ✅ Redis configured and used by endpoints
- ✅ TTL-based cache keys in place (30min, 12hr, 24hr)
- ❌ No connection pooling (always creates new connections)
- ❌ No query pagination for large result sets
- ❌ No application-level query timeouts
- ❌ No stale-data fallback when database unavailable

## Proposed Solution

### Two-Phase Fix

**Phase 1: Create Missing Database Migrations** (Short-term quick fix)
- Create migration 007: Reference tables (countries, regions, conflict_types)
- Create migration 008: States and LGAs hierarchy
- Create migration 009: Conflicts table and relationships
- Create migration 010: Performance indexes

**Phase 2: Implement Hybrid Fetch Strategy** (Transform data access)
- Fix inconsistent error handling (all endpoints return graceful responses)
- Implement connection pooling (SQLAlchemy pool_size=20, max_overflow=10)
- Add query timeouts (15 second application-level timeout wrapper)
- Smart query paging (paginate state comparisons > 10 states)
- Graceful degradation (serve cached data if database unavailable)
- ETL migration function (migrate conflict_events → conflicts with state mapping)

## What Changes

### API Endpoints (3 affected)
- `GET /api/v1/timeseries/monthly-trends` - Currently works, needs connection pooling
- `GET /api/v1/timeseries/seasonal-analysis` - **BROKEN:** Throws 404 instead of returning empty data
- `GET /api/v1/timeseries/trend-comparison` - Currently works, needs query paging
- `GET /api/v1/analytics/states` - **BROKEN:** Throws 500 instead of degrading gracefully

### Database Schema (NEW)
- Create 4 migrations (007-010) for normalized schema
- Create ETL function to populate new schema from legacy data
- Create admin API endpoint to trigger migration

### Caching Strategy (ENHANCED)
- Connection pooling for multi-concurrent requests
- Smart query pagination for large state comparisons
- Graceful stale-data fallback (serve cached data with 24hr TTL if DB unavailable)
- 15-second query timeout wrapper

### Frontend Components (MINOR UPDATES - IF REQUIRED)
- Handle `"status": "degraded"` responses (cached data) in chart components
- Display visual indicator when serving cached data (timestamp badge)
- Never throw errors - always show "No data available" gracefully

## Impact

### Affected Specs
- **dashboard-monitoring**: Adds requirements for error handling, graceful degradation, caching strategy
- **api-endpoints** (new spec): Documents API error response standards and timeout behavior
- **database-schema** (new spec): Documents normalized conflict schema

### Affected Code Files
- **Backend**:
  - `backend/alembic/versions/007_*.py` (new: reference tables)
  - `backend/alembic/versions/008_*.py` (new: states/lgas)
  - `backend/alembic/versions/009_*.py` (new: conflicts table)
  - `backend/alembic/versions/010_*.py` (new: indexes)
  - `backend/app/api/v1/endpoints/timeseries.py` (fix seasonal-analysis, add timeouts)
  - `backend/app/api/v1/endpoints/analytics.py` (fix states endpoint, add graceful fallback)
  - `backend/app/db/database.py` (add connection pooling)
  - `backend/app/services/cache_strategy.py` (new: hybrid caching logic)
  - `backend/app/services/schema_migration_service.py` (new: ETL migration)

- **Frontend**:
  - `frontend/components/charts/MonthlyTrendsChart.tsx` (handle degraded status)
  - `frontend/components/charts/SeasonalPatternChart.tsx` (handle degraded status)
  - `frontend/components/charts/StateComparisonChart.tsx` (handle degraded status)

### Breaking Changes
- **None - Fully backward compatible**: New migrations are additive; old conflict_events table remains untouched until ETL migration.

### Timeline
- **Phase 1** (Migrations): 2-3 hours
- **Phase 2** (API fixes + Caching): 4-6 hours
- **Testing & Validation**: 2-3 hours
- **Total**: ~8-12 hours
