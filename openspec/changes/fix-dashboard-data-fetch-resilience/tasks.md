## Implementation Checklist

### Phase 1: Create Database Migrations

- [ ] 1.1 Create `backend/alembic/versions/007_add_reference_tables.py`
  - Add `countries` table (id, name, iso_code)
  - Add `regions` table (id, name, description)
  - Add `conflict_types` table (id, name, description, active)
  - All tables use UUID primary keys with timestamps

- [ ] 1.2 Create `backend/alembic/versions/008_add_states_and_lgas.py`
  - Add `states` table (id, name, region_id FK, code, active)
  - Populate all 36 Nigerian states + FCT
  - Add `lgas` table (id, name, state_id FK, latitude, longitude, active)
  - Add indexes on (states.name), (lgas.state_id)

- [ ] 1.3 Create `backend/alembic/versions/009_add_conflicts_table.py`
  - Add `conflicts` primary table with schema
  - Add `conflict_actors` junction table
  - Add `actors` table (id, name, actor_type, description)

- [ ] 1.4 Create `backend/alembic/versions/010_add_conflict_indexes.py`
  - Index: `(state_id, incidence_date DESC)` for monthly trends queries
  - Index: `(incidence_date)` for date range queries
  - Index: `(state_id)` for state lookups
  - Index: `(verified)` for quality filtering

- [ ] 1.5 Verify migrations apply cleanly
  - Run: `alembic upgrade head`
  - Confirm: `SELECT * FROM information_schema.tables WHERE table_schema='public'`

### Phase 2: Fix Error-Throwing Endpoints

- [ ] 2.1 Fix `backend/app/api/v1/endpoints/timeseries.py` - seasonal-analysis endpoint
  - Find line 541 where it raises `HTTPException(status_code=404)`
  - Replace with graceful empty response

- [ ] 2.2 Fix `backend/app/api/v1/endpoints/analytics.py` - get_state_statistics endpoint
  - Find the `try/except` block around line 479-500
  - Change `raise HTTPException(status_code=500)` to graceful fallback

- [ ] 2.3 Add timeout decorator to all timeseries endpoints
  - Create `backend/app/utils/timeout.py` with `@with_timeout(seconds=15)` decorator
  - Apply to: monthly-trends, seasonal-analysis, trend-comparison, state-summary

### Phase 3: Implement Hybrid Caching

- [ ] 3.1 Create `backend/app/services/cache_strategy.py`
  - Class: `HybridCachingStrategy` with methods
  - `get_or_fetch(cache_key, fetch_func, ttl)` method
  - `serve_stale(cache_key, max_age_hours)` method
  - `batch_pagination(items, page_size)` method

- [ ] 3.2 Update `backend/app/db/database.py` - Add connection pooling
  - Find `create_engine()` call
  - Add parameters: `pool_size=20, max_overflow=10, pool_pre_ping=True`

- [ ] 3.3 Update all timeseries endpoints to use HybridCachingStrategy
  - monthly-trends: Use new caching wrapper
  - seasonal-analysis: Use new caching wrapper
  - trend-comparison: Add pagination for state list > 10 items
  - state-summary: Use new caching wrapper

### Phase 4: Create ETL Migration Service

- [ ] 4.1 Create `backend/app/services/schema_migration_service.py`
  - Class: `SchemaMigrationService` with methods
  - `migrate_conflict_events_to_conflicts(batch_size)` method
  - `get_migration_status()` method
  - `verify_migration()` method

- [ ] 4.2 Create admin API endpoint
  - `POST /api/v1/admin/migrate-schema` - Triggers ETL migration
  - Can be called multiple times safely (idempotent)

- [ ] 4.3 Test with sample data
  - Run ETL locally with conflict_events
  - Verify row counts match

### Phase 5: Update Frontend Components

- [ ] 5.1 Update `frontend/components/charts/MonthlyTrendsChart.tsx`
  - Handle `response.status === "degraded"` (display cached data badge)
  - Show timestamp when serving cached data

- [ ] 5.2 Update `frontend/components/charts/SeasonalPatternChart.tsx`
  - Add timeout handling (15s limit)
  - Handle empty data gracefully

- [ ] 5.3 Update `frontend/components/charts/StateComparisonChart.tsx`
  - Handle pagination (if returned data is paginated)
  - Show "Loading more states..." for deferred requests

### Phase 6: Testing & Validation

- [ ] 6.1 Test migrations apply correctly
  - Run locally: `alembic upgrade head`
  - Verify all tables created

- [ ] 6.2 Test ETL migration
  - Run ETL: `curl -X POST http://localhost:8000/api/v1/admin/migrate-schema`
  - Verify row counts match

- [ ] 6.3 Test endpoints return data
  ```bash
  curl http://localhost:8000/api/v1/timeseries/monthly-trends?state=Kaduna
  curl http://localhost:8000/api/v1/timeseries/seasonal-analysis?state=Lagos
  curl http://localhost:8000/api/v1/timeseries/trend-comparison?states=Kaduna,Lagos,Kano
  curl http://localhost:8000/api/v1/analytics/states
  ```

- [ ] 6.4 Test caching behavior
  - Call endpoint first time → `"cached": false`
  - Call same endpoint again immediately → `"cached": true`, response <10ms

- [ ] 6.5 Test timeout handling
  - Verify timeouts work gracefully

- [ ] 6.6 Test frontend dashboard
  - Open https://naija-conflict-tracker.vercel.app/dashboard
  - Verify Monthly Trends section loads with data
  - Verify Seasonal Patterns section loads with data
  - Verify State Comparison section loads with data
  - No errors in browser console

### Phase 7: Documentation & Deployment

- [ ] 7.1 Document schema migration process
  - Create `/docs/SCHEMA_MIGRATION.md` explaining migration steps

- [ ] 7.2 Update README
  - Add section: "Data Schema" explaining normalized vs legacy tables

- [ ] 7.3 Deploy to production (Railway)
  - Push code to main branch
  - Verify deployment succeeds
  - Trigger ETL migration in production
