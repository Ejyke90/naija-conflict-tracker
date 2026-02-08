# Database Migration Task List

**Change ID:** migrate-production-database-schema  
**Owner:** Database Team + Backend Team  
**Timeline:** 3 days (scheduled for low-traffic weekend)

---

## Pre-Migration Phase (Day 0 - Before Maintenance Window)

### Planning & Preparation
- [ ] **TASK-001**: Review and approve proposal.md
- [ ] **TASK-002**: Review and approve design.md  
- [ ] **TASK-003**: Schedule maintenance window (Friday 22:00 - Sunday 16:00 WAT)
- [ ] **TASK-004**: Notify stakeholders (users, product team, management)
- [ ] **TASK-005**: Create communication plan (status updates, rollback notification)

### Backup & Safety
- [ ] **TASK-006**: Create full database backup (before any changes)
  - Verify backup integrity
  - Store in multiple locations (S3, local)
  - Test restoration on staging
- [ ] **TASK-007**: Set up database snapshot/replication for instant rollback
- [ ] **TASK-008**: Document rollback procedures step-by-step

### Development Environment
- [ ] **TASK-009**: Create staging database (copy of production)
- [ ] **TASK-010**: Test migration on staging database  
- [ ] **TASK-011**: Verify staging database after migration
- [ ] **TASK-012**: Performance test staging queries
- [ ] **TASK-013**: Fix any issues found in staging

### Code Preparation
- [ ] **TASK-014**: Create SQLAlchemy models for new schema
  - Actor model
  - ConflictType model
  - Region model
  - State model  
  - LGA model
  - Conflict model (new version)
- [ ] **TASK-015**: Update Alembic migration files
- [ ] **TASK-016**: Create migration Python scripts
  - `001_create_schema.py`
  - `002_populate_reference_data.py`
  - `003_migrate_conflicts.py`
  - `004_validate_data.py`
- [ ] **TASK-017**: Update API endpoints to use new models
- [ ] **TASK-018**: Update frontend queries (if direct DB access)
- [ ] **TASK-019**: Create feature flags for schema switching
- [ ] **TASK-020**: Write unit tests for new models
- [ ] **TASK-021**: Write integration tests for migration scripts

---

## Migration Execution Phase (Day 1-2 - During Maintenance Window)

### Phase 1: Schema Creation (2 hours)
- [ ] **TASK-022**: Enable maintenance mode on application
- [ ] **TASK-023**: Execute `001_create_schema.py`
  - Create actors table
  - Create conflict_types table
  - Create regions table
  - Create states table
  - Create lgas table
  - Create conflicts table
  - Create countries table
  - Create foreign key constraints
- [ ] **TASK-024**: Verify all tables created successfully
- [ ] **TASK-025**: Verify all indexes created
- [ ] **TASK-026**: Verify foreign key constraints active

### Phase 2: Reference Data Population (4 hours)
- [ ] **TASK-027**: Execute `002_populate_reference_data.py`
- [ ] **TASK-028**: Insert 1 country record (Nigeria)
- [ ] **TASK-029**: Insert 6 region records (geo-political zones)
- [ ] **TASK-030**: Insert 37 state records with region FKs
- [ ] **TASK-031**: Insert 794 LGA records with state FKs
- [ ] **TASK-032**: Insert 33 actor records (armed groups, etc.)
- [ ] **TASK-033**: Insert 13 conflict_type records
- [ ] **TASK-034**: Verify all reference data row counts match expected
- [ ] **TASK-035**: Verify foreign key relationships
- [ ] **TASK-036**: Test sample lookups (state→region, lga→state)

### Phase 3: Historical Data Migration (8 hours)
- [ ] **TASK-037**: Execute `003_migrate_conflicts.py`
- [ ] **TASK-038**: Read all records from conflict_events table
- [ ] **TASK-039**: For each record:
  - Map event_type → conflict_type_id
  - Map state → state_id (lookup)
  - Map lga → lga_id (lookup with state context)
  - Map actor1 → actor_1 (lookup or create)
  - Map actor2 → actor_2 (lookup or create)
  - Derive region_id from state_id
  - Set country_id = 1 (Nigeria)
  - Map fatalities → civilian_death_unknown
  - Map injuries → injured_unknown
  - Copy description, source, timestamps
  - Set default values for new fields
- [ ] **TASK-040**: Insert transformed records into conflicts table
- [ ] **TASK-041**: Create ID mapping table (old UUID → new BIGINT)
- [ ] **TASK-042**: Handle duplicate LGA names (use state context)
- [ ] **TASK-043**: Handle missing actors (create "Unknown" entry)
- [ ] **TASK-044**: Handle missing conflict types (create "General Violence")
- [ ] **TASK-045**: Log transformation issues for review

### Phase 4: Validation & Verification (4 hours)
- [ ] **TASK-046**: Execute `004_validate_data.py`
- [ ] **TASK-047**: Compare row counts
  - conflict_events.count == conflicts.count?
  - Allow for soft-deleted records
- [ ] **TASK-048**: Verify casualty totals match
  ```sql
  SELECT SUM(fatalities) FROM conflict_events;
  SELECT SUM(COALESCE(civilian_death_male,0) + 
             COALESCE(civilian_death_female,0) + 
             COALESCE(civilian_death_unknown,0)) FROM conflicts;
  ```
- [ ] **TASK-049**: Check for orphaned records
  - All state_id values exist in states table
  - All lga_id values exist in lgas table
  - All actor_* values exist in actors table
- [ ] **TASK-050**: Verify date ranges match
- [ ] **TASK-051**: Sample 100 random records, manually verify accuracy
- [ ] **TASK-052**: Check for NULL values in critical fields
- [ ] **TASK-053**: Verify indexes are being used (EXPLAIN queries)
- [ ] **TASK-054**: Run performance benchmarks
  - Dashboard queries <2s
  - API list endpoint <500ms
  - Filter queries <300ms

---

## Application Integration Phase (Day 2-3)

### Code Deployment
- [ ] **TASK-055**: Deploy updated SQLAlchemy models to staging
- [ ] **TASK-056**: Test API endpoints on staging
- [ ] **TASK-057**: Test frontend on staging
- [ ] **TASK-058**: Run automated test suite
- [ ] **TASK-059**: Fix any issues found
- [ ] **TASK-060**: Deploy to production (feature flagged OFF)
- [ ] **TASK-061**: Enable new schema feature flag for 10% of traffic
- [ ] **TASK-062**: Monitor errors and performance
- [ ] **TASK-063**: Gradually increase to 50% traffic
- [ ] **TASK-064**: Monitor for 2 hours
- [ ] **TASK-065**: Switch 100% traffic to new schema
- [ ] **TASK-066**: Disable old schema access

### Monitoring Setup
- [ ] **TASK-067**: Configure monitoring alerts
  - Error rate >5/min → Alert
  - Query time >2s → Warning
  - Connection pool >80% → Warning
- [ ] **TASK-068**: Set up dashboard for migration metrics
- [ ] **TASK-069**: Enable detailed query logging (temporary)
- [ ] **TASK-070**: Create Slack channel for migration updates

---

## Post-Migration Phase (Day 3+)

### Verification & Cleanup
- [ ] **TASK-071**: Monitor application for 24 hours
- [ ] **TASK-072**: Review error logs daily for 1 week
- [ ] **TASK-073**: Verify no data loss reported by users
- [ ] **TASK-074**: Run daily data integrity checks for 1 week
- [ ] **TASK-075**: Optimize slow queries if found
- [ ] **TASK-076**: Update API documentation with new schema
- [ ] **TASK-077**: Update database documentation
- [ ] **TASK-078**: Create data dictionary for new tables

### Communication
- [ ] **TASK-079**: Send "Migration Complete" notification
- [ ] **TASK-080**: Update status page
- [ ] **TASK-081**: Disable maintenance mode
- [ ] **TASK-082**: Create post-mortem document
  - What went well
  - What went wrong
  - Lessons learned
  - Metrics (downtime, data volume, issues)

### Decommissioning (After 30 days)
- [ ] **TASK-083**: Confirm no rollback needed
- [ ] **TASK-084**: Archive old conflict_events table (do not drop)
- [ ] **TASK-085**: Remove old SQLAlchemy models from codebase
- [ ] **TASK-086**: Remove feature flags
- [ ] **TASK-087**: Clean up migration scripts (move to archive)
- [ ] **TASK-088**: Update deployment documentation

---

## Rollback Tasks (If Needed)

### Emergency Rollback
- [ ] **ROLLBACK-001**: Disable new schema feature flag immediately
- [ ] **ROLLBACK-002**: Switch all traffic to old conflict_events table
- [ ] **ROLLBACK-003**: Notify stakeholders of rollback
- [ ] **ROLLBACK-004**: Investigate issues causing rollback
- [ ] **ROLLBACK-005**: Document problems found
- [ ] **ROLLBACK-006**: Fix issues on staging
- [ ] **ROLLBACK-007**: Re-test migration
- [ ] **ROLLBACK-008**: Schedule new migration window

### Partial Rollback (Data Issues)
- [ ] **ROLLBACK-009**: Identify corrupted records
- [ ] **ROLLBACK-010**: Restore from backup (specific tables)
- [ ] **ROLLBACK-011**: Re-run migration for affected records
- [ ] **ROLLBACK-012**: Verify fix
- [ ] **ROLLBACK-013**: Resume operations

---

## Validation Checklist (Sign-Off Required)

### Database Team Sign-Off
- [ ] Schema created correctly
- [ ] All foreign keys functioning
- [ ] Indexes created and optimized
- [ ] Data integrity verified (row counts, totals)
- [ ] Performance benchmarks met

### Backend Team Sign-Off
- [ ] SQLAlchemy models working
- [ ] API endpoints functional
- [ ] No breaking changes to API contracts
- [ ] Error handling tested
- [ ] Feature flags operational

### QA Team Sign-Off
- [ ] All test cases pass
- [ ] Manual testing complete
- [ ] Performance acceptable
- [ ] No critical bugs found

### Product Team Sign-Off
- [ ] Feature parity maintained
- [ ] No user-facing regressions
- [ ] Dashboard functional
- [ ] Reports accurate

---

**Critical Success Metrics:**
- ✅ Zero data loss (100% row count match)
- ✅ Casualty totals match (±1% tolerance for rounding)
- ✅ Application uptime >99.5% post-migration
- ✅ Query performance within SLA (<500ms p95)
- ✅ No critical bugs reported in first 48 hours
- ✅ Rollback capability maintained for 7 days

**Timeline:**
- **Day 0** (Thu): Preparation & staging tests
- **Day 1** (Fri 22:00 - Sat 06:00): Schema + reference data
- **Day 2** (Sat 10:00 - Sun 06:00): Historical migration + validation  
- **Day 3** (Sun 10:00 - 16:00): Application cutover + monitoring
- **Week 1**: Daily monitoring
- **Month 1**: Weekly integrity checks
