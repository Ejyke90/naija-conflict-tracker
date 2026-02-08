# Database Migration Requirements Specification

**Change ID:** migrate-production-database-schema  
**Type:** Database Schema Migration  
**Priority:** HIGH  
**Complexity:** HIGH

---

## Functional Requirements

### FR-001: Schema Migration
**Priority:** CRITICAL  
**Description:** Successfully create new database schema from u503102722_conflictdb.sql

**Acceptance Criteria:**
- All 17 tables created without errors
- All foreign key constraints established
- All indexes created for performance
- Schema matches MariaDB structure

#### Scenario: Create actors table
```
GIVEN the production database is accessible
WHEN the migration script executes CREATE TABLE actors
THEN the actors table is created with columns: id, title, created_at, updated_at
AND the table uses InnoDB engine
AND the charset is utf8mb4_unicode_ci
```

#### Scenario: Create conflicts table with foreign keys
```
GIVEN actors, conflict_types, states, lgas tables exist
WHEN the migration script creates conflicts table
THEN all foreign key constraints are established
AND constraints reference the correct tables
AND ON DELETE CASCADE is configured where appropriate
```

---

### FR-002: Reference Data Population
**Priority:** CRITICAL  
**Description:** Populate all reference/lookup tables with accurate data

**Acceptance Criteria:**
- 1 country record (Nigeria)
- 6 region records (geo-political zones)
- 37 state records with correct region linkages
- 794 LGA records with correct state linkages
- 33 actor records (armed groups, etc.)
- 13 conflict type records

#### Scenario: Populate Nigerian states
```
GIVEN regions table is populated
WHEN the migration script inserts states
THEN all 36 states + FCT are inserted
AND each state has correct region_id foreign key
AND states are spelled correctly (e.g., "Akwa Ibom" not "Akwa-Ibom")
```

#### Scenario: Populate LGAs with state relationships
```
GIVEN states table is populated
WHEN the migration script inserts LGAs
THEN all 794 LGAs are inserted
AND each LGA has correct state_id foreign key
AND duplicate LGA names (e.g., "Obi" in Benue & Nasarawa) are handled correctly
```

---

### FR-003: Historical Data Migration
**Priority:** CRITICAL  
**Description:** Migrate all existing conflict records from old schema to new schema

**Acceptance Criteria:**
- All conflict_events records migrated to conflicts table
- Zero data loss (row count matches)
- Casualty totals preserved (±1% tolerance for NULL handling)
- Timestamps preserved
- ID mapping maintained for potential rollback

#### Scenario: Migrate basic conflict record
```
GIVEN a conflict_event with:
  - event_date = "2020-06-01"
  - event_type = "Banditry"
  - state = "Katsina"
  - lga = "Yantumaki"
  - fatalities = 1
WHEN the migration runs
THEN a new conflicts record is created with:
  - incidence_date = "2020-06-01"
  - conflict_type_id = (ID for "Banditry" in conflict_types table)
  - state_id = (ID for "Katsina" in states table)
  - lga_id = (ID for "Yantumaki" LGA in "Katsina" state)
  - civilian_death_unknown = 1
  - country_id = 1
```

#### Scenario: Handle missing reference data
```
GIVEN a conflict_event with actor1 = "Farmers"
AND "Farmers" does not exist in actors table
WHEN the migration runs
THEN create a new actor "Farmers" in actors table
AND link conflict to this new actor_id
```

---

### FR-004: Data Transformation
**Priority:** HIGH  
**Description:** Transform data from old schema format to new schema format

**Acceptance Criteria:**
- Text actor names converted to foreign keys
- Text state/LGA names converted to foreign keys
- Event types mapped to conflict types
- Default values applied for new fields

#### Scenario: Transform actor fields
```
GIVEN a conflict_event with:
  - actor1 = "Bandits"
  - actor2 = "Security Forces"
WHEN the migration runs
THEN the conflicts record has:
  - actor_1 = (ID for "Bandits" in actors table)
  - actor_2 = (ID for "Security Forces" in actors table)
  - actor_3 = NULL
```

#### Scenario: Apply default values for new fields
```
GIVEN a migrated conflict record
WHEN new fields have no source data
THEN default values are applied:
  - country_id = 1
  - civilian_death_male = NULL
  - civilian_death_female = NULL
  - security_death_male = NULL
  - displaced_persons = 'No'
  - verification_level = '1'
  - data_source = 'Historical Migration'
```

---

### FR-005: Data Validation
**Priority:** CRITICAL  
**Description:** Verify integrity and accuracy of migrated data

**Acceptance Criteria:**
- Row counts match (old vs new)
- Casualty totals match
- No orphaned foreign keys
- No NULL values in required fields
- Date ranges preserved

#### Scenario: Validate row counts
```
GIVEN migration is complete
WHEN validation script runs
THEN COUNT(*) FROM conflict_events = COUNT(*) FROM conflicts
OR document any discrepancies with explanation
```

#### Scenario: Validate casualty preservation
```
GIVEN migration is complete
WHEN comparing casualty totals
THEN SUM(fatalities) FROM conflict_events 
     ≈ SUM(civilian_death_unknown + civilian_death_male + civilian_death_female) FROM conflicts
WITH ±1% tolerance
```

#### Scenario: Check foreign key integrity
```
GIVEN migration is complete
WHEN validation runs
THEN no conflicts.state_id values are missing from states table
AND no conflicts.lga_id values are missing from lgas table
AND no conflicts.actor_1 values are missing from actors table
```

---

## Non-Functional Requirements

### NFR-001: Performance
**Priority:** HIGH  
**Description:** Migration must complete within acceptable timeframe and maintain query performance

**Acceptance Criteria:**
- Total migration time < 24 hours
- Post-migration query performance within SLAs
- Dashboard loads in <2 seconds
- API endpoints respond in <500ms

#### Scenario: Migration duration
```
GIVEN production database size is ~5MB
WHEN full migration executes
THEN total execution time is ≤18 hours
AND no single script runs longer than 8 hours
```

#### Scenario: Query performance after migration
```
GIVEN new schema is in use
WHEN common queries execute (dashboard load, conflict list, filters)
THEN p95 response time is <500ms
AND p99 response time is <1 second
```

---

### NFR-002: Data Integrity
**Priority:** CRITICAL  
**Description:** No data loss or corruption during migration

**Acceptance Criteria:**
- Zero data loss
- Checksums match for migrated records
- Referential integrity maintained
- Atomic transactions (rollback on error)

#### Scenario: Atomic migration
```
GIVEN migration is in progress
WHEN an error occurs during conflict migration
THEN entire batch is rolled back
AND database state is consistent
AND error is logged for investigation
```

---

### NFR-003: Availability
**Priority:** HIGH  
**Description:** Minimize downtime during migration

**Acceptance Criteria:**
- Planned downtime <24 hours
- Migration scheduled during low-traffic period
- Status updates every 2 hours
- Rollback capability maintained

#### Scenario: Downtime window
```
GIVEN migration is scheduled for Friday 22:00 - Sunday 16:00 WAT
WHEN migration executes
THEN application is in maintenance mode
AND users see informative maintenance page
AND status updates posted to status page
```

---

### NFR-004: Rollback Capability
**Priority:** CRITICAL  
**Description:** Ability to rollback migration if issues arise

**Acceptance Criteria:**
- Full database backup before migration
- ID mapping table for reversibility
- Old schema preserved (not dropped)
- Rollback tested on staging

#### Scenario: Emergency rollback
```
GIVEN migration is complete but critical issues found
WHEN rollback is initiated
THEN application switches back to conflict_events table
AND old schema is still functional
AND downtime is <15 minutes
```

---

### NFR-005: Observability
**Priority:** MEDIUM  
**Description:** Comprehensive logging and monitoring during migration

**Acceptance Criteria:**
- Progress logging for each migration phase
- Error logging with stack traces
- Metrics tracking (rows migrated, duration, errors)
- Alerting for critical failures

#### Scenario: Migration logging
```
GIVEN migration is executing
WHEN each phase completes
THEN log entry includes:
  - Phase name
  - Start/end timestamp
  - Row count processed
  - Success/failure status
  - Any errors encountered
```

---

## Security Requirements

### SR-001: Access Control
**Priority:** HIGH  
**Description:** Restrict migration execution to authorized personnel

**Acceptance Criteria:**
- Only DBAs and senior engineers can execute migration
- Audit log of who executed migration
- Two-person approval required

#### Scenario: Migration authorization
```
GIVEN migration scripts are ready
WHEN attempting to execute
THEN require authentication with DBA credentials
AND log user identity, timestamp, and action
```

---

### SR-002: Data Protection
**Priority:** CRITICAL  
**Description:** Protect sensitive data during migration

**Acceptance Criteria:**
- Source URLs with sensitive info handled carefully
- reporter_id links to anonymized data
- Backups encrypted at rest
- Migration logs sanitized of sensitive data

#### Scenario: Backup security
```
GIVEN database backup is created
WHEN backup file is stored
THEN backup is encrypted with AES-256
AND access is restricted to authorized personnel
AND backup is stored in multiple secure locations
```

---

## Compatibility Requirements

### CR-001: Database Engine Compatibility
**Priority:** HIGH  
**Description:** Handle differences between PostgreSQL (current) and MariaDB (target schema)

**Acceptance Criteria:**
- UUID primary keys converted to BIGINT
- PostgreSQL data types mapped to MariaDB equivalents
- Timestamp handling consistent
- ENUM types properly implemented

#### Scenario: UUID to BIGINT conversion
```
GIVEN conflict_events uses UUID primary keys
WHEN migrating to conflicts table
THEN generate sequential BIGINT IDs
AND maintain UUID→BIGINT mapping table
AND preserve UUID in metadata field for reference
```

---

### CR-002: Application Compatibility
**Priority:** CRITICAL  
**Description:** Ensure application works with new schema

**Acceptance Criteria:**
- SQLAlchemy models updated
- API contracts unchanged
- Frontend queries updated
- No breaking changes to API responses

#### Scenario: API backward compatibility
```
GIVEN frontend expects certain API response format
WHEN backend uses new schema
THEN API response format remains unchanged
AND additional fields are added, not removed
AND existing field names preserved where possible
```

---

## Constraints

### CO-001: Technology Constraints
- PostgreSQL current database (Railway)
- MariaDB schema (from Laravel application)
- Python 3.13+ for migration scripts
- SQLAlchemy 2.0+ for ORM

### CO-002: Business Constraints
- Migration must complete before end of Q1 2026
- Downtime limited to weekend (low traffic)
- Budget: Within existing infrastructure costs
- No additional paid services required

### CO-003: Data Constraints
- Historical data back to June 2020
- ~5000+ conflict records to migrate
- 794 LGAs (some with duplicate names across states)
- 37 states + FCT

---

## Out of Scope

The following are explicitly NOT included in this migration:

- **Geocoding improvements** - Will use existing lat/long from current data
- **Data cleaning** - Migration preserves data as-is (typos, inconsistencies)
- **New features** - Only schema migration, no new functionality
- **Frontend redesign** - UI changes are separate effort
- **API versioning** - No v2 API creation
- **Multi-database support** - PostgreSQL and MariaDB will not run in parallel
- **Real-time sync** - Migration is one-time, not continuous replication

---

## Assumptions

1. Railway PostgreSQL database remains stable during migration
2. Sufficient disk space available for dual schemas (if needed)
3. Internet connectivity stable for remote database access
4. Key personnel available during migration window
5. Staging environment accurately mirrors production
6. Users have been notified of maintenance window

---

## Dependencies

### External Dependencies
- Railway database uptime and performance
- Network connectivity
- Third-party backup services (S3)

### Internal Dependencies
- SQLAlchemy models (backend team)
- API endpoints (backend team)
- Frontend queries (frontend team)
- Alembic migration framework
- Python environment with required packages

---

## Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|-----------|
| Data loss during migration | CRITICAL | LOW | Full backup, testing on staging, atomic transactions |
| Extended downtime (>24hrs) | HIGH | MEDIUM | Thorough testing, rollback plan, experienced team |
| Performance degradation | MEDIUM | MEDIUM | Proper indexing, query optimization, monitoring |
| Duplicate LGA name conflicts | LOW | HIGH | Use state_id + lga name composite for lookup |
| Missing reference data | LOW | MEDIUM | Create "Unknown" entries, log for manual review |
| Foreign key constraint failures | MEDIUM | LOW | Pre-validate all lookups, handle errors gracefully |

---

**Approval Sign-Off:**

- [ ] Database Team Lead: _____________________ Date: _______
- [ ] Backend Team Lead: _____________________ Date: _______
- [ ] QA Lead: _____________________ Date: _______
- [ ] Product Owner: _____________________ Date: _______
- [ ] Project Manager: _____________________ Date: _______

**Approved to Proceed:** YES / NO

**Notes:**
_____________________________________________________________
_____________________________________________________________
