# Migration Quick Reference

**Status:** ✅ Ready for testing  
**Time Required:** 1.5-2 hours (branch test) + 30 min (production)

---

## 🏃 QUICK START

```bash
# 1. Install prerequisites
npm install -g neonctl
pip install -r backend/requirements.txt

# 2. Create test branch
export PROJECT_ID="ep-gentle-union-agwmnyzn"  # Your Neon project ID
./backend/scripts/create_neon_branch.sh migration-test-v1 $PROJECT_ID
export BRANCH_URL="<connection_string_from_output>"

# 3. Apply schema + load data
psql "$BRANCH_URL" -f database/migrations/neondb_postgres_schema.sql
python backend/scripts/load_mariadb_dump_data.py \
  --dump-file database/migrations/u503102722_conflictdb.sql \
  --db-url "$BRANCH_URL"

# 4. Validate
python backend/scripts/validate_migration.py --db-url "$BRANCH_URL"

# 5. Test API
export DATABASE_URL="$BRANCH_URL"
cd backend && uvicorn app.main:app --reload --port 8001

# 6. Test endpoints (in another terminal)
curl http://localhost:8001/api/v1/conflicts/reference/actors | jq '.'
curl http://localhost:8001/api/v1/conflicts/?limit=5 | jq '.'
curl http://localhost:8001/api/v1/conflicts/stats | jq '.'
```

---

## 📁 KEY FILES

**Execute in order:**
1. `database/migrations/neondb_postgres_schema.sql` - Create 17 tables
2. `backend/scripts/load_mariadb_dump_data.py` - Load 6000+ conflicts
3. `backend/scripts/migrate_conflict_events_to_new_schema.py` - Migrate legacy data (if exists)
4. `backend/scripts/validate_migration.py` - Verify migration

**Rollback:**
- `backend/scripts/rollback_conflicts_migration.sql` - Emergency rollback

**API:**
- `backend/app/api/v1/endpoints/conflicts_new.py` - 11 new endpoints
- `backend/app/schemas/conflict_new.py` - Pydantic schemas

---

## 🎯 SUCCESS CHECKS

After Phase 3 (Load Data):
```sql
-- Should return: actors=33, conflict_types=13, states=37, lgas=794, conflicts=6000+
SELECT 
  (SELECT COUNT(*) FROM actors) as actors,
  (SELECT COUNT(*) FROM conflict_types) as conflict_types,
  (SELECT COUNT(*) FROM states) as states,
  (SELECT COUNT(*) FROM lgas) as lgas,
  (SELECT COUNT(*) FROM conflicts) as conflicts;

-- Verify Yantumaki exists
SELECT l.name, s.name FROM lgas l 
JOIN states s ON l.state_id = s.id 
WHERE l.name ILIKE '%yantumaki%';
```

After Phase 6 (Validate):
```bash
# Should exit with code 0 (PASS)
python backend/scripts/validate_migration.py --db-url "$BRANCH_URL"
echo $?  # Should print: 0
```

After Phase 7 (Test API):
```bash
# Should return 33 actors
curl http://localhost:8001/api/v1/conflicts/reference/actors | jq '. | length'

# Should return conflicts with state names (not null)
curl "http://localhost:8001/api/v1/conflicts/?limit=5" | jq '.[].state_name'

# Should return aggregate stats
curl http://localhost:8001/api/v1/conflicts/stats | jq '.total_conflicts, .total_deaths'
```

---

## 🆘 TROUBLESHOOTING

**Problem:** Connection refused to Neon branch  
**Fix:** Check URL has `?sslmode=require` appended

**Problem:** load_mariadb_dump_data.py fails with "INSERT syntax error"  
**Fix:** Ensure PostgreSQL version ≥ 12 (check with `psql --version`)

**Problem:** validate_migration.py shows casualty mismatch  
**Fix:** Acceptable if <5% difference (old data may have NULLs)

**Problem:** API returns 500 "relationship not found"  
**Fix:** Restart uvicorn after model changes

**Problem:** Neon storage full  
**Fix:** Delete old branches: `neonctl branches delete <branch> --project-id $PROJECT_ID`

---

## 📖 DETAILED DOCS

- **Full guide:** `MIGRATION_EXECUTION_GUIDE.md` (600+ lines, step-by-step)
- **Summary:** `MIGRATION_IMPLEMENTATION_SUMMARY.md` (all deliverables, stats)
- **OpenSpec proposal:** `openspec/changes/migrate-production-database-schema/`

---

## 🔄 ROLLBACK

```bash
# If migration fails, rollback in <5 minutes:
psql "$NEON_URL" -f backend/scripts/rollback_conflicts_migration.sql

# Or delete branch and start over:
neonctl branches delete migration-test-v1 --project-id $PROJECT_ID
```

---

## 🎬 NEXT STEPS

After successful branch testing:
1. Execute production migration (follow Phase 8 in full guide)
2. Update frontend to use new API endpoints
3. Update analytics/timeseries endpoints
4. Monitor for 24 hours
5. Drop archive table after 30 days (March 10, 2026)

---

**Ready? Start with:** `MIGRATION_EXECUTION_GUIDE.md` Phase 1 🚀
