# Migration Proposal - Files Created

**Date:** February 8, 2026  
**Decision:** Stay on Neon DB PostgreSQL  
**Status:** Ready for review  
**Cleanup Strategy:** ✅ Neon branching + archive (FREE tier supported!)

---

## 📁 Created Files

### 1. OpenSpec Proposal Package (8 documents)

Located in: `/openspec/changes/migrate-production-database-schema/`

#### Core Documents
- ✅ **`proposal.md`** - Formal migration proposal
  - Executive summary
  - Problem statement & gaps
  - Proposed solution
  - Benefits & ROI
  - Risks & mitigation
  - Timeline (3-day weekend)
  - Success criteria

- ✅ **`design.md`** - Technical architecture
  - Schema comparison (old vs new)
  - 6 detailed table specifications
  - Field mapping table
  - Migration scripts structure
  - Index strategy
  - Rollback procedures

- ✅ **`tasks.md`** - Implementation checklist
  - 88 granular tasks
  - 4 phases (pre-migration, execution, integration, post-migration)
  - Team assignments
  - Dependencies
  - Rollback tasks

- ✅ **`requirements.md`** - Requirements specification
  - 5 functional requirements (FR-001 to FR-005)
  - 5 non-functional requirements (NFR-001 to NFR-005)
  - Security requirements
  - Acceptance criteria
  - Test scenarios
  - Approval signatures

#### Summary & Decision Documents
- ✅ **`EXECUTIVE_SUMMARY.md`** - Stakeholder presentation
  - Quick facts
  - Before/after comparison
  - Cost analysis
  - Risk matrix
  - FAQ
  - Sign-off section

- ✅ **`NEON_DB_UPDATE.md`** - Platform decision documentation
  - PostgreSQL vs MariaDB decision
  - Schema conversion details
  - Updated timeline (12 hours vs 18)
  - Risk reduction analysis
  - Technical details for Neon DB

- ✅ **`CLEANUP_STRATEGY.md`** - Database cleanup plan ⭐ NEW
  - Archive vs drop decision
  - Neon branching approach (FREE tier supported!)
  - Rollback procedures
  - Storage impact analysis
  - 30-day archive retention plan

- ✅ **`NEON_BRANCHING_GUIDE.md`** - Step-by-step branching tutorial ⭐ NEW
  - Install neonctl CLI
  - Create test branches
  - Safe migration testing
  - Zero-downtime deployment
  - Troubleshooting guide

---

### 2. PostgreSQL Schema File

Located in: `/database/migrations/`

- ✅ **`neondb_postgres_schema.sql`** - Converted PostgreSQL schema
  - **Format:** PostgreSQL syntax (Neon DB compatible)
  - **Source:** Converted from `u503102722_conflictdb.sql` (MariaDB)
  - **Tables:** 17 tables total
  - **Features:**
    - `actors` table (33 armed groups/security forces)
    - `conflict_types` table (13 categories)
    - `regions` table (6 geo-political zones)
    - `states` table (37 states)
    - `lgas` table (794 Local Government Areas)
    - `conflicts` table (main events with 40+ fields)
    - `countries` table (Nigeria)
    - Laravel system tables (cache, jobs, sessions, users)
  - **Indexes:** 20+ indexes for performance
  - **Triggers:** Auto-update timestamps
  - **Views:** `conflicts_with_totals` (computed casualty sums)

---

## 📊 Schema Conversion Summary

### MariaDB → PostgreSQL Changes

| MariaDB Syntax | PostgreSQL Equivalent | Example |
|----------------|----------------------|---------|
| `BIGINT(20) UNSIGNED` | `BIGSERIAL` (PKs) | `id BIGSERIAL PRIMARY KEY` |
| `ENGINE=InnoDB` | (removed) | PostgreSQL uses native storage |
| `COLLATE utf8mb4_unicode_ci` | (removed) | PostgreSQL UTF-8 default |
| `ENUM('Yes','No')` | `VARCHAR(10) CHECK (...)` | `CHECK (value IN ('Yes','No'))` |
| `` `backticks` `` | `"quotes"` or unquoted | `CREATE TABLE actors` |
| `AUTO_INCREMENT` | `SERIAL`/`BIGSERIAL` | `id BIGSERIAL` |
| `MEDIUMTEXT` | `TEXT` | `description TEXT` |

---

## 🎯 Key Database Changes

### Old Schema (Current)
```
conflict_events (PostgreSQL - Neon DB)
├── id (UUID PK)
├── event_date
├── event_type (text)
├── state (text) ❌ not normalized
├── lga (text) ❌ not normalized
├── actor1, actor2 (text) ❌ not normalized
├── fatalities (integer) ❌ no breakdown
└── injuries (integer) ❌ no breakdown
```

### New Schema (Target)
```
PostgreSQL - Neon DB (no platform change!)

countries (1)
  └── regions (6)
      └── states (37)
          └── lgas (794)

actors (33)
conflict_types (13)

conflicts (main table)
├── id (BIGSERIAL PK)
├── incidence_date
├── conflict_type_id → conflict_types
├── country_id → countries
├── region_id → regions
├── state_id → states
├── lga_id → lgas
├── community (text)
├── civilian_death_male ✅ gender-disaggregated
├── civilian_death_female ✅
├── civilian_death_unknown ✅
├── security_death_male ✅
├── security_death_female ✅
├── security_death_unknown ✅
├── injured_male ✅
├── injured_female ✅
├── injured_unknown ✅
├── kidnapped_male ✅
├── kidnapped_female ✅
├── kidnapped_unknown ✅
├── displaced_persons
├── displaced_male ✅
├── displaced_female ✅
├── actor_1 → actors (3 actors vs 2) ✅
├── actor_2 → actors
├── actor_3 → actors ✅
├── description (text)
├── verification_level ✅ data quality
├── source_url ✅ provenance
└── source_metadata ✅
```

---

## ✅ Verification Checklist

Before running migration, verify:

- [ ] All 6 OpenSpec documents reviewed
- [ ] PostgreSQL schema file validated
- [ ] Neon DB connection string confirmed
- [ ] Railway backend status checked
- [ ] Stakeholder approvals collected
- [ ] Backup strategy confirmed
- [ ] Rollback plan tested (Neon branching)

---

## 🚀 Next Actions

### Immediate (Before Migration)
1. **Review proposal documents** - All 8 files in this directory
2. **Install Neon CLI** - `npm install -g neonctl` (see [NEON_BRANCHING_GUIDE.md](NEON_BRANCHING_GUIDE.md))
3. **Create test branch** - Use Neon's FREE branching feature (10 branches included)
4. **Test PostgreSQL schema** - Run `neondb_postgres_schema.sql` on test branch
5. **Collect approvals** - Get sign-offs from 5 stakeholders (see EXECUTIVE_SUMMARY.md)

### After Approval
6. **Create data migration script** - `migrate_conflict_events_to_new_schema.py`
7. **Create validation script** - `validate_migration.py`
8. **Update SQLAlchemy models** - Match new PostgreSQL schema
9. **Test on branch** - Full end-to-end test on Neon branch (production untouched!)
10. **Execute migration** - Weekend of Feb 14-16, 2026

---

## 📞 Questions?

- **Platform decision:** See [NEON_DB_UPDATE.md](NEON_DB_UPDATE.md)
- **Cleanup strategy:** See [CLEANUP_STRATEGY.md](CLEANUP_STRATEGY.md) ⭐
- **Neon branching:** See [NEON_BRANCHING_GUIDE.md](NEON_BRANCHING_GUIDE.md) ⭐
- **Executive summary:** See [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)
- **Technical details:** See [design.md](design.md)
- **Task breakdown:** See [tasks.md](tasks.md)
- **Requirements:** See [requirements.md](requirements.md)

---

## ✅ Safety Features (Neon Free Tier)

**Your plan includes:**
- ✅ 10 branches (only need 1 for testing)
- ✅ 0.5 GB storage (migration uses <10 MB = 2%)
- ✅ 100 compute hours (plenty for weekend work)
- ✅ Instant rollback (just switch branches)
- ✅ $0 cost (all within free tier)

**Migration approach:**
1. Test on branch (production untouched)
2. Validate everything works
3. Apply to production
4. Keep old `conflict_events` as archive for 30 days
5. Delete archive after confirmation (March 10, 2026)

---

**Ready for review!** All proposal documents are complete and optimized for your Neon Free tier.
