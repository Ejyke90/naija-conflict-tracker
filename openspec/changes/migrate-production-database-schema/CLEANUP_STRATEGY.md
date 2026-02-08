# Database Cleanup Strategy

**Date:** February 8, 2026  
**Decision Required:** How to handle existing Neon DB tables during migration

---

## Current Database State (Neon DB)

### Existing Tables
Based on `backend/app/models/conflict.py`, we currently have:

```sql
conflict_events (existing table)
├── id (UUID)
├── event_date, year, month
├── event_type, event_category, conflict_type
├── state, lga, location (text fields)
├── latitude, longitude
├── actor1, actor2 (text fields)
├── fatalities, injuries, properties_destroyed, displaced_persons
├── source, notes, verified, confidence_level
└── created_at, updated_at
```

**Data Volume:** ~5,000 conflict records (estimated)

### Other Tables (if any)
- Potentially: `users`, `sessions`, or other application tables
- Need to verify with: `\dt` command on Neon DB

---

## Cleanup Strategy Options

### ✅ **RECOMMENDED: Option 1 - Side-by-Side Migration with Archive**

**Approach:**
1. Keep `conflict_events` table during migration (as backup)
2. Create all new tables (actors, conflict_types, states, lgas, conflicts, etc.)
3. Migrate data from `conflict_events` → `conflicts`
4. Verify data integrity
5. **Archive old table** (rename to `conflict_events_archive_20260208`)
6. Keep archive for 30 days, then drop

**SQL Commands:**
```sql
-- Step 1: Create new schema (neondb_postgres_schema.sql)
-- (Creates: actors, conflict_types, regions, states, lgas, conflicts, etc.)

-- Step 2: Migrate data
-- (Python script transforms conflict_events → conflicts)

-- Step 3: Verify
SELECT COUNT(*) FROM conflict_events; -- Old: ~5000
SELECT COUNT(*) FROM conflicts;       -- New: ~5000 (should match)

-- Step 4: Archive old table (after successful migration)
ALTER TABLE conflict_events RENAME TO conflict_events_archive_20260208;

-- Step 5: Drop archive after 30 days (March 10, 2026)
DROP TABLE conflict_events_archive_20260208;
```

**Pros:**
- ✅ Safe - old data preserved during migration
- ✅ Easy rollback - rename archive back to conflict_events
- ✅ No data loss risk
- ✅ Can compare old vs new side-by-side

**Cons:**
- Temporary storage increase (~10-20 MB)
- Need to remember to drop archive later

**Timeline:**
- Feb 14-16: Migration (both tables exist)
- Feb 17-Mar 9: Archive period (30 days)
- Mar 10: Drop archive

---

### Option 2 - Drop and Replace (NOT RECOMMENDED)

**Approach:**
1. Drop `conflict_events` table
2. Create new schema
3. Lose ability to compare/rollback easily

**SQL Commands:**
```sql
-- DANGER: No rollback!
DROP TABLE conflict_events; -- ❌ PERMANENT DATA LOSS

-- Create new schema
-- (Creates: actors, conflicts, etc.)
```

**Pros:**
- Clean database (no old tables)

**Cons:**
- ❌ HIGH RISK - no rollback if migration fails
- ❌ Can't compare old vs new data
- ❌ Permanent data loss if script has bugs
- ❌ Violates safety principle

**Verdict:** ❌ **DO NOT USE**

---

### Option 3 - Create New Database Schema (Neon Branching)

**Approach:**
1. Use Neon's branching feature to create test branch
2. Run migration on branch
3. Verify on branch
4. Promote branch to production

**Neon Commands:**
```bash
# Create staging branch from production
neon branches create --name migration-staging --parent main

# Test migration on staging
psql $STAGING_URL -f database/migrations/neondb_postgres_schema.sql

# Verify
# ... run tests ...

# If successful, swap staging → production
neon branches set-primary migration-staging
```

**Pros:**
- ✅ Perfect testing environment
- ✅ Instant rollback (switch back to original branch)
- ✅ No impact on production during testing
- ✅ Zero-downtime cutover possible

**Cons:**
- Slightly more complex workflow (but worth it!)

**Neon Free Plan:** ✅ **AVAILABLE** - Includes up to 10 branches per project

**Verdict:** ✅ **BEST OPTION** (and you have it!)

---

## ✅ RECOMMENDED APPROACH

**Use a combination of Options 1 & 3:**

**Your Neon Plan:** Free (includes 10 branches) ✅  
**Storage Available:** 0.5 GB (using <10 MB = 2%) ✅  
**Perfect for:** Safe migration testing with branching

### Phase 1: Pre-Migration (Neon Branching - FREE tier available!)
```bash
# Install Neon CLI (if not already)
npm install -g neonctl

# Login to Neon
neonctl auth

# Create staging branch for testing (uses 1 of your 10 free branches)
neonctl branches create --name migration-feb-2026 --project-id YOUR_PROJECT_ID

# Get connection string for staging branch
neonctl connection-string migration-feb-2026

# Test full migration on staging branch
export STAGING_URL="postgresql://neondb_owner:...@ep-...-pooler.c-2.eu-central-1.aws.neon.tech/neondb"
psql $STAGING_URL -f database/migrations/neondb_postgres_schema.sql
python backend/scripts/migrate_conflict_events_to_new_schema.py --db=$STAGING_URL
python backend/scripts/validate_migration.py --db=$STAGING_URL
```

### Phase 2: Production Migration (Archive Old Table)
```bash
# Connect to production Neon DB
psql $PRODUCTION_URL

# Run new schema
\i database/migrations/neondb_postgres_schema.sql

# Migrate data (Python script handles this)
python backend/scripts/migrate_conflict_events_to_new_schema.py

# Verify
python backend/scripts/validate_migration.py

# Archive old table (don't drop yet!)
ALTER TABLE conflict_events RENAME TO conflict_events_archive_20260208;

# Add comment for future reference
COMMENT ON TABLE conflict_events_archive_20260208 IS 
  'x] Check Neon plan - ✅ Free plan with 10 branches available
- [ ] Install Neon CLI: `npm install -g neonctl`
- [ ] Login to Neon: `neonctl auth`
- [ ] Create staging branch: `neonctl branches create --name migration-feb-2026`, 2026 migration. Safe to drop after March 10, 2026.';
```

### Phase 3: Post-Migration (30-Day Archive Period)
```sql
-- After 30 days (March 10, 2026), if all is well:
DROP TABLE conflict_events_archive_20260208;
```

---

## Cleanup Checklist

### Before Migration
- [ ] Check Neon plan (Pro required for branching)
- [ ] List all existing tables: `\dt`
- [ ] Backup database: `pg_dump $NEON_URL > backup_20260214.sql`
- [ ] Document table sizes: `SELECT pg_size_pretty(pg_total_relation_size('conflict_events'));`

### During Migration
- [ ] Create Neon staging branch
- [ ] Test schema creation on staging
- [ ] Test data migration on staging
- [ ] Verify row counts match
- [ ] Test API on staging

### After Migration (Production)
- [ ] Run schema creation script
- [ ] Run data migration script
- [ ] Verify data integrity
- [ ] Rename old table to `conflict_events_archive_20260208`
- [ ] Update SQLAlchemy models
- [ ] Deploy API updates
- [ ] Monitor for 24 hours

### Archive Cleanup (30 days later)
- [ ] Verify new system stable (no issues for 30 days)
- [ ] Final backup of archive table
- [ ] Drop archive: `DROP TABLE conflict_events_archive_20260208;`

---

## Other Tables to Consider

### Application Tables (Keep These)
If these exist, **DO NOT DROP**:
- `users` - Keep (authentication)
- `sessions` - Keep (user sessions)
- `alembic_version` - Keep (migration tracking)

### New Tables (Created by Migration)
- `actors` ✅ New
- `conflict_types` ✅ New
- `regions` ✅ New
- `states` ✅ New
- `lgas` ✅ New
- `conflicts` ✅ New (replaces conflict_events)
- `countries` ✅ New
- `cache`, `cache_locks`, `jobs`, etc. ✅ New (Laravel system tables)

---

## Rollback Plan

### If migration fails DURING execution:
```sql
-- 1. Stop migration script
-- 2. Drop new tables
DROP TABLE IF EXISTS conflicts CASCADE;
DROP TABLE IF EXISTS actors CASCADE;
DROP TABLE IF EXISTS conflict_types CASCADE;
DROP TABLE IF EXISTS regions CASCADE;
DROP TABLE IF EXISTS states CASCADE;
DROP TABLE IF EXISTS lgas CASCADE;
DROP TABLE IF EXISTS countries CASCADE;

-- 3. Old conflict_events table still intact ✅
-- 4. Application continues working on old schema
```

### If issues found AFTER migration:
```sql
-- 1. Rename archive back to original name
ALTER TABLE conflict_events_archive_20260208 RENAME TO conflict_events;

-- 2. Drop new conflicts table
DROP TABLE conflicts CASCADE;

-- 3. Revert API to old models
-- 4. Application back onli (RECOMMENDED - you have 10 free branches!):
```bash
# Option 1: Just switch back to original branch
neonctl branches set-default main --project-id YOUR_PROJECT_ID

# Option 2: Delete migration branch and start over
neonctl branches delete migration-feb-2026 --project-id YOUR_PROJECT_ID

# Your production data is 100% safe - branching creates a copy

# Migration branch discarded
neon branches delete migration-feb-2026
```

---

## Storage Impact

### Current Database Size (Estimated)
```sql
-- conflict_events: ~5000 rows × ~500 bytes = ~2.5 MB
-- indexes: ~1 MB
-- Total: ~3.5 MB
```

### New Database Size (Estimated)
```sql
-- conflicts: ~5000 rows × ~800 bytes = ~4 MB (more fields)
-- actors: 33 rows × 100 bytes = ~3 KB
-- conflict_types: 13 rows × 100 bytes = ~1 KB
-- regions: 6 rows × 100 bytes = ~0.5 KB
-- states: 37 rows × 150 bytes = ~5.5 KB
-- lgas: 794 rows × 150 bytes = ~120 KB
-- indexes: ~2 MB
-- Total: ~6.5 MB
```

### With Archive (During Migration)
```
Old: 3.5 MB
New: 6.5 MB
Archive period total: 10 MB (temporary, for 30 days)
After cleanup: 6.5 MB
```

**Neon Free Tier:** 3 GB storage (we're using <0.01%)  
**Impact:** Negligible

---

## SQL Script for Cleanup

```sql
-- ================================================
-- DATABASE CLEANUP SCRIPT
-- Run AFTER successful migration
-- ================================================

-- 1. Check table sizes before cleanup
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 2. Archive old conflict_events table
ALTER TABLE conflict_events RENAME TO conflict_events_archive_20260208;

COMMENT ON TABLE conflict_events_archive_20260208 IS 
  'Archive of pre-migration conflict_events table. Created: 2026-02-08. Safe to drop after: 2026-03-10';

-- 3. Verify new tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('actors', 'conflict_types', 'regions', 'states', 'lgas', 'conflicts');

-- 4. Compare row counts (should match)
SELECT 
    'Old (archive)' AS source,
    COUNT(*) AS row_count 
FROM conflict_events_archive_20260208
UNION ALL
SELECT 
    'New (conflicts)' AS source,
    COUNT(*) AS row_count 
FROM conflicts;

-- 5. After 30 days, drop archive (March 10, 2026)
-- DROP TABLE conflict_events_archive_20260208;
```

---

## Decision Required

**Principal FullStack Engineer - Please approve cleanup strategy:**
✅ **FREE TIER AVAILABLE** (10 branches included)
- [ ] **Option 3:** Both (Neon branching + archive) ⭐ **RECOMMENDED**

**Recommended:** ✅ **Option 3** (safest approach)

**Your Neon Plan Supports:** 
- ✅ 10 branches per project (only need 1 for migration)
- ✅ 0.5 GB storage (migration uses <10 MB = 2%)
- ✅ 100 compute hours (plenty for weekend migration)

**Cost:** $0 (all within free tier limits)

---

## Quick Start with Neon Branching

```bash
# 1. Install Neon CLI
npm install -g neonctl

# 2. Login
neonctl auth

# 3. List your projects
neonctl projects list

# 4. Create migration test branch
neonctl branches create \
  --name migration-test \
  --project-id <YOUR_PROJECT_ID>

# 5. Get connection string for test branch
neonctl connection-string migration-test

# 6. Test migration on the branch (safe - production untouched!)
psql <BRANCH_CONNECTION_STRING> -f database/migrations/neondb_postgres_schema.sql

# 7. If successful, apply to production
# If failed, just delete the branch and try again
```e)

**Recommended:** ✅ **Option 3** (safest approach)

---

**Next Step:** Add this cleanup strategy to the migration tasks in `tasks.md`
