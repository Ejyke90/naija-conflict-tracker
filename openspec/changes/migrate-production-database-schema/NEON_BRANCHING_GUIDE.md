# Neon Branching Quick Start Guide

**Your Plan:** Neon Free (10 branches included) ✅  
**Cost:** $0 (all within free tier)  
**Safety:** 100% - Production untouched during testing

---

## What is Neon Branching?

Neon branching creates an **instant copy** of your database that you can test on without touching production.

**Think of it like:**
- Git branches, but for databases
- Creates a copy in seconds (not hours)
- Can test migrations safely
- Delete the branch if it fails
- Promote to production if it succeeds

**Your limits:**
- 10 branches max (you only need 1 for migration)
- 0.5 GB storage per branch (migration uses <10 MB)

---

## Step-by-Step: Safe Migration with Branching

### Step 1: Install Neon CLI

```bash
# Using npm (recommended)
npm install -g neonctl

# Or using curl
curl -fsSL https://raw.githubusercontent.com/neondatabase/neonctl/main/install.sh | sh

# Verify installation
neonctl --version
```

---

### Step 2: Login to Neon

```bash
# Login (opens browser)
neonctl auth

# Verify login
neonctl projects list
```

**Output should show:**
```
┌──────────────────────────┬─────────────────┬──────────┐
│ Id                       │ Name            │ Region   │
├──────────────────────────┼─────────────────┼──────────┤
│ ep-gentle-union-agwmnyzn │ neondb          │ eu-c...  │
└──────────────────────────┴─────────────────┴──────────┘
```

---

### Step 3: Get Your Project ID

```bash
# List projects and copy your project ID
neonctl projects list

# Or get it from your connection string:
# postgresql://neondb_owner:...@ep-gentle-union-agwmnyzn-pooler...
#                                  ^^^^^^^^^^^^^^^^^^^^^^^^
#                                  This is your project ID
```

**Save this for later:**
```bash
export NEON_PROJECT_ID="ep-gentle-union-agwmnyzn"
```

---

### Step 4: Create Migration Test Branch

```bash
# Create branch from your main/production branch
neonctl branches create \
  --name migration-test-feb2026 \
  --project-id $NEON_PROJECT_ID

# This creates an instant copy of your production database
# Your production data is UNTOUCHED
```

**Output:**
```
✔ Created branch migration-test-feb2026
  │ ID: br-...
  │ Parent: main
  │ Created: 2026-02-08 14:30:00 UTC
```

---

### Step 5: Get Connection String for Test Branch

```bash
# Get connection string
neonctl connection-string migration-test-feb2026 \
  --project-id $NEON_PROJECT_ID

# Save it
export TEST_DB_URL="postgresql://neondb_owner:npg_...@br-...-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require"
```

---

### Step 6: Test Migration on Branch (SAFE!)

Now you can test the full migration on the branch without affecting production:

```bash
# 1. Connect to test branch
psql "$TEST_DB_URL"

# 2. Verify it's a copy (should see your existing conflict_events table)
\dt

# 3. Run the new schema
\i database/migrations/neondb_postgres_schema.sql

# 4. Check what was created
\dt

# You should now see:
# - conflict_events (old table, still there)
# - actors, conflict_types, regions, states, lgas, conflicts (new tables)
```

---

### Step 7: Run Data Migration on Branch

```bash
# Create migration script (we'll build this next)
python backend/scripts/migrate_conflict_events_to_new_schema.py \
  --db-url "$TEST_DB_URL"

# This migrates data from conflict_events → conflicts
```

---

### Step 8: Validate Migration on Branch

```bash
# Run validation script
python backend/scripts/validate_migration.py \
  --db-url "$TEST_DB_URL"

# Should output:
# ✅ Row counts match: 5000 old, 5000 new
# ✅ Casualty totals preserved
# ✅ All states mapped correctly
# ✅ All actors mapped correctly
# ✅ No data loss detected
```

---

### Step 9A: If Migration Succeeds - Apply to Production

```bash
# Option 1: Manual approach (recommended for first time)
# 1. Run schema on production
psql "$PRODUCTION_DB_URL" -f database/migrations/neondb_postgres_schema.sql

# 2. Run data migration on production
python backend/scripts/migrate_conflict_events_to_new_schema.py \
  --db-url "$PRODUCTION_DB_URL"

# 3. Validate
python backend/scripts/validate_migration.py \
  --db-url "$PRODUCTION_DB_URL"

# 4. If all good, archive old table
psql "$PRODUCTION_DB_URL" -c "ALTER TABLE conflict_events RENAME TO conflict_events_archive_20260208;"

# Option 2: Advanced (zero-downtime)
# Promote test branch to production
neonctl branches set-default migration-test-feb2026 \
  --project-id $NEON_PROJECT_ID

# Update Railway DATABASE_URL to point to new branch
# (This is more complex, use Option 1 for first migration)
```

---

### Step 9B: If Migration Fails - Clean Up and Try Again

```bash
# Just delete the test branch
neonctl branches delete migration-test-feb2026 \
  --project-id $NEON_PROJECT_ID

# Your production database is 100% unchanged ✅
# Fix the migration script and create a new branch to try again
```

---

## Current State Check

Before you start, verify your current database state:

```bash
# Connect to production
psql 'postgresql://neondb_owner:YOUR_PASSWORD@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

# List tables
\dt

# Count records
SELECT COUNT(*) FROM conflict_events;

# Check table size
SELECT pg_size_pretty(pg_total_relation_size('conflict_events'));

# Sample data
SELECT * FROM conflict_events LIMIT 5;
```

**Expected:**
```
conflict_events | table | ~5000 rows | ~3 MB
(possibly) users | table | ... 
```

---

## Branching Best Practices

### ✅ DO:
- Create branch before testing migrations
- Name branches descriptively (`migration-test-feb2026`)
- Delete branches after successful migration
- Use branches for major schema changes

### ❌ DON'T:
- Make direct changes to production without testing on branch
- Keep too many old branches (you have 10 max)
- Forget to delete test branches after migration

---

## Troubleshooting

### "Branch creation failed"
```bash
# Check how many branches you have
neonctl branches list --project-id $NEON_PROJECT_ID

# If you have 10, delete old ones
neonctl branches delete old-branch-name --project-id $NEON_PROJECT_ID
```

### "Connection refused"
```bash
# Branch might be sleeping (free tier scales to zero after 5 min)
# Just connect again - it wakes up in ~1 second
psql "$TEST_DB_URL"
```

### "Not enough storage"
```bash
# Check usage
neonctl projects get $NEON_PROJECT_ID

# Your limit: 0.5 GB
# Migration needs: <10 MB
# Should have plenty of space
```

---

## Cost Breakdown (Free Tier)

| Resource | Limit | Migration Uses | Available |
|----------|-------|----------------|-----------|
| Branches | 10 | 1 test branch | 9 more |
| Storage | 0.5 GB | ~10 MB | 490 MB |
| Compute | 100 hrs/month | ~2 hours | 98 hours |
| Data transfer | 5 GB | <100 MB | 4.9 GB |

**Total Cost:** $0 ✅

---

## Timeline with Branching

### Week 1 (Feb 9-13): Testing
- Monday: Install neonctl, create test branch
- Tuesday: Test schema creation on branch
- Wednesday: Test data migration on branch
- Thursday: Fix any issues, re-test
- Friday: Final validation on branch

### Weekend (Feb 14-16): Production Migration
- Friday 22:00: Create fresh test branch, final test
- Saturday 00:00: Apply to production
- Saturday 12:00: Validation complete
- Sunday 16:00: Back online

### Post-Migration
- Feb 17-Mar 9: Monitor (keep archive table)
- Mar 10: Drop archive table if all is well

---

## Next Steps

1. **Install neonctl:**
   ```bash
   npm install -g neonctl
   ```

2. **Login:**
   ```bash
   neonctl auth
   ```

3. **Create test branch:**
   ```bash
   neonctl branches create --name migration-test-feb2026
   ```

4. **Test the schema:**
   ```bash
   # Get connection string
   neonctl connection-string migration-test-feb2026
   
   # Test schema creation
   psql <CONNECTION_STRING> -f database/migrations/neondb_postgres_schema.sql
   ```

5. **Build migration scripts** (next task after approval)

---

**Ready to start?** ✅ You have everything you need on your free tier!
