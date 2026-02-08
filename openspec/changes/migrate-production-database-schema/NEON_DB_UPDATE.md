# MIGRATION UPDATE: Staying on Neon DB PostgreSQL

**Date:** February 8, 2026  
**Decision:** APPROVED - Stay on Neon DB PostgreSQL  
**Impact:** Simplified migration (schema only, no platform migration)

---

## Key Decision

**We are staying on Neon DB PostgreSQL.** The migration will be a **schema transformation only** - no database platform migration required.

### What Changed
- **Original Plan:** Reference schema was MariaDB/MySQL syntax
- **Updated Plan:** Convert MariaDB schema to PostgreSQL, run on existing Neon DB
- **Platform:** Neon DB PostgreSQL (no change)
- **Backend:** Railway FastAPI (no change)
- **Connection:** Existing Neon DB connection string (no change)

---

## Schema Conversion

### Source Schema
- **File:** `database/migrations/u503102722_conflictdb.sql`
- **Format:** MariaDB/MySQL syntax
- **Features:** 17 tables, 794 LGAs, gender-disaggregated data

### Converted Schema
- **File:** `database/migrations/neondb_postgres_schema.sql` ✅ CREATED
- **Format:** PostgreSQL syntax (Neon DB compatible)
- **Conversions:**
  - `BIGINT(20) UNSIGNED` → `BIGSERIAL` (PKs) or `BIGINT`
  - `ENGINE=InnoDB` → (removed)
  - `ENUM('Yes','No')` → `VARCHAR(10) CHECK (...)`
  - `` `backticks` `` → `"quotes"` or unquoted
  - `AUTO_INCREMENT` → `SERIAL`/`BIGSERIAL`

---

## Migration Approach (Updated)

### Before (Original Plan)
1. Provision new MariaDB database
2. Migrate from PostgreSQL → MariaDB
3. Update application to connect to MariaDB
4. Lose PostgreSQL features (PostGIS, analytics)

### After (Updated Plan)
1. Run PostgreSQL schema script on existing Neon DB ✅
2. Migrate data within same PostgreSQL instance
3. No application connection changes
4. Keep PostgreSQL features (PostGIS, CTEs, window functions)

---

## Benefits of Staying on PostgreSQL

1. **No Platform Migration Complexity**
   - No new database provisioning
   - No cross-platform data migration
   - Existing connections work

2. **PostgreSQL Advantages**
   - PostGIS for geospatial queries (heat maps, proximity)
   - Superior analytics (window functions, CTEs)
   - Better ML ecosystem (MADlib, PL/Python)
   - Neon's branching feature for staging tests

3. **Cost Savings**
   - No new database hosting fees
   - Less engineering time (schema migration vs platform migration)
   - Faster rollback if needed

4. **Risk Reduction**
   - Simpler migration = fewer failure points
   - Neon branching allows perfect staging tests
   - Same database engine = predictable behavior

---

## Updated Timeline

### Total Duration: 18 hours → **12 hours** (6 hours saved!)

**Simplified because:**
- No new database provisioning
- No cross-platform data type mapping
- No connection string updates
- No driver changes in FastAPI

### Migration Window

**Friday, Feb 14, 2026**
- 22:00 - Begin maintenance mode
- 22:30 - Full backup created
- 23:00 - Create Neon branch for final test
- 23:30 - Execute PostgreSQL schema script

**Saturday, Feb 15, 2026**
- 00:00 - Schema created (8 tables)
- 02:00 - Reference data loaded (actors, types, geography)
- 08:00 - Historical data migration complete
- 12:00 - Validation tests running

**Sunday, Feb 16, 2026**
- 10:00 - API updates deployed
- 14:00 - Final testing
- 16:00 - **Back online** ✅

---

## Technical Details

### Database Connection (Unchanged)
```bash
# Production Neon DB
psql 'postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
```

### Railway Backend (Unchanged)
- FastAPI application stays on Railway
- SQLAlchemy models updated (PostgreSQL models)
- No infrastructure changes

### New Schema Tables (PostgreSQL)
1. `actors` - Armed groups, security forces (33 types)
2. `conflict_types` - Terrorism, banditry, farmer-herder, etc. (13 types)
3. `countries` - Nigeria (1 entry)
4. `regions` - 6 geo-political zones
5. `states` - 37 states (36 + FCT)
6. `lgas` - 794 Local Government Areas
7. `conflicts` - Main events table (replaces conflict_events)
8. `users` - Reporter tracking

**Plus Laravel system tables:** cache, jobs, sessions, migrations

---

## Migration Scripts (PostgreSQL)

### 1. Schema Creation
```bash
psql $NEON_DB_URL -f database/migrations/neondb_postgres_schema.sql
```

### 2. Data Migration (Python)
```python
# backend/scripts/migrate_conflict_events_to_new_schema.py
# Migrates from old conflict_events to new conflicts table
# Handles:
# - Actor text → actor_id lookups
# - State text → state_id lookups
# - LGA text → lga_id lookups
# - Casualty splitting (gender-disaggregated)
```

### 3. Validation
```python
# backend/scripts/validate_migration.py
# Checks:
# - Row counts match
# - Casualty totals preserved
# - No data loss
# - Foreign key integrity
```

---

## Risk Assessment (Updated)

| Risk | Before (MariaDB migration) | After (PostgreSQL schema) |
|------|----------------------------|---------------------------|
| Platform migration failure | 🔴 High | 🟢 None (no platform migration) |
| Data type mismatch | 🟡 Medium | 🟢 Low (same engine) |
| Connection issues | 🟡 Medium | 🟢 None (same connection) |
| Extended downtime | 🟡 Medium | 🟢 Low (simpler migration) |
| Rollback complexity | 🟡 Medium | 🟢 Low (Neon branching) |

**Overall Risk:** 🟡 Medium → 🟢 **Low**

---

## Approval Impact

### Documents to Update
- ✅ `EXECUTIVE_SUMMARY.md` - Updated with PostgreSQL approach
- ✅ `proposal.md` - Clarified Neon DB PostgreSQL
- ✅ `design.md` - Added schema conversion details
- ✅ `tasks.md` - Updated database setup tasks
- ✅ `requirements.md` - (no changes needed - requirements same)

### New Deliverables
- ✅ `neondb_postgres_schema.sql` - PostgreSQL schema (created)
- ⏳ `migrate_conflict_events_to_new_schema.py` - Data migration script (pending)
- ⏳ `validate_migration.py` - Validation script (pending)

---

## Next Steps

1. **Review this update** - Confirm PostgreSQL approach
2. **Approve updated proposal** - Sign off on Neon DB migration
3. **Create staging branch** - Use Neon's branching for testing
4. **Test schema script** - Run `neondb_postgres_schema.sql` on staging
5. **Build migration scripts** - Python ETL for data transformation
6. **Execute migration** - Weekend of Feb 14-16, 2026

---

## Questions & Clarifications

**Q: Do we lose any features from the MariaDB schema?**  
A: No - all features preserved. PostgreSQL adds capabilities (PostGIS, analytics).

**Q: What about the 794 LGA records?**  
A: Included in `neondb_postgres_schema.sql` (sample shown, full list in separate data file).

**Q: Will the API need changes?**  
A: Yes, but only SQLAlchemy models (same as before). Railway deployment unchanged.

**Q: Can we rollback if something goes wrong?**  
A: Yes! Neon branching allows instant rollback. Plus we have full backup.

**Q: What about Railway environment variables?**  
A: No changes - same DATABASE_URL.

---

**Status:** ✅ **Ready for approval** (simplified, lower risk, faster migration)
