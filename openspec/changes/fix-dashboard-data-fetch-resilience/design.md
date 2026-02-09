# Technical Design: Dashboard Data Fetch Resilience

## Context

The dashboard fetches conflict analytics from 4 backend endpoints that query a normalized schema (conflicts, states, lgas, actors). However, these tables don't exist in the production database - they're only defined in SQLAlchemy models. All real data exists in the legacy `conflict_events` table with a different structure.

This design addresses the schema gap while implementing a production-grade data fetch strategy with caching, timeouts, pagination, and graceful degradation.

## Goals

- ✅ **Restore data visibility**: Dashboard sections display real conflict data from production database
- ✅ **Improve reliability**: All endpoints handle failures gracefully (no 404/500 errors exposed to frontend)
- ✅ **Enhance performance**: Implement caching layers and query optimization for <500ms response times
- ✅ **Support scalability**: Connection pooling and pagination enable concurrent requests from 100+ dashboard users
- ✅ **Maintain backward compatibility**: Legacy conflict_events table remains functional during migration

## Non-Goals

- ❌ Replace PostgreSQL with TimescaleDB (separate effort)
- ❌ Implement real-time WebSocket updates (use polling with caching)
- ❌ Build automated ML-based duplicate detection (manual review sufficient)

## Architecture Decisions

### Decision 1: Schema Strategy - Create Normalized Schema with ETL

**Chosen**: Create missing migrations (007-010) to complete normalized schema, then use ETL to populate from conflict_events

**Alternatives Considered**:
1. **Rewrite all queries to use conflict_events** - Quick (2 hours) but perpetuates legacy schema; requires query rewrite across codebase
2. **Dual queries with fallback** - Safe but complex; maintains technical debt long-term
3. **Create normalized schema with ETL** (CHOSEN) - Best long-term; enables proper relationships and indexing; requires migration patience

**Rationale**: Normalized schema allows:
- Proper foreign key relationships (state_id, lga_id, actor_id)
- Efficient geospatial queries (LGA hierarchies, proximity searches)
- Time-series aggregations with proper grouping
- Future ML features (state-level forecasting, actor tracking)
- Clean API response contracts (respects frontend expectations)

**Risk**: Migration process takes ~30 min if conflict_events has 100k+ records

**Mitigation**: ETL is idempotent and can be re-run; old table remains untouched for rollback

### Decision 2: Caching Strategy - Hybrid (Redis + Query Paging + Connection Pooling)

**Chosen**: Redis (existing) + application-level query paging + SQLAlchemy connection pooling

**Rationale**:
- Redis: ✅ Already deployed, ✅ Handles forecast cache (expensive to compute), ✅ 30min/12hr/24hr TTLs sufficient
- Connection pooling: ✅ Prevents "too many connections" errors at scale, ✅ Minimal config change
- Query paging: ✅ Solves N+1 queries for state comparisons, ✅ Enables incremental frontend rendering
- Graceful fallback: ✅ Serve stale Redis data (with timestamp) if database unavailable, better UX than error

### Decision 3: Consistent Error Handling - Graceful Degradation Over Exceptions

**Chosen**: All endpoints return valid JSON with `"status"` field (ok|degraded|error) instead of HTTP 404/500

**Rationale**:
- ✅ Frontend receives valid JSON (doesn't crash parsing)
- ✅ Can distinguish between "no data" vs "database error" via status field
- ✅ Enables graceful fallback (show "No data" message instead of error)
- ✅ Works with browser error boundaries and error logging

## Migration Plan

### Phase 1: Pre-Migration Checklist (30 minutes)
- Backup production PostgreSQL database
- Test migrations locally on dev database
- Verify ETL mapping (state names match exactly)
- Prepare rollback plan

### Phase 2: Create Migrations (30 minutes)
- Run migration 007 (reference tables)
- Run migration 008 (states, lgas)
- Run migration 009 (conflicts table)
- Run migration 010 (indexes)
- Verify tables created

### Phase 3: Populate Data (15-30 minutes)
- Trigger ETL migration via admin API
- Monitor progress
- Verify row counts match

### Phase 4: Update Configuration (5 minutes)
- Update SQLAlchemy connection pool: pool_size=20, max_overflow=10
- Deploy updated backend code

### Phase 5: Validation (30 minutes)
- Test endpoints return data
- Open dashboard in browser; verify all sections load
- Monitor logs for errors

## Open Questions

1. **State name normalization**: Should states table use exact names from conflict_events (e.g., "Lagos") or official names (e.g., "Lagos State")? → **Answer needed before migration**
2. **Historical data cleanup**: Keep demo_heatmap.sql data in conflicts table or filter it out during ETL? → **Recommend: filter out (demo only)**
3. **Cascade delete policy**: If state is deleted, should conflicts be deleted? → **Recommend: SET NULL (preserve conflict records)**
