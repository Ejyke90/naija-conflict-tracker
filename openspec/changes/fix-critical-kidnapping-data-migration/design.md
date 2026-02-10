## Context

**Current State:**
- MariaDB production dump contains 54 INSERT statements with kidnapping data
- Current parser only processes first INSERT statement, resulting in 1% data migration
- Dashboard shows "No data" due to insufficient dataset (13 records vs 1,260 available)
- Production dataset spans 2020-2025 with 10,316 kidnapping victims across Nigeria

**Technical Constraints:**
- SQL file contains complex multi-statement INSERT format with quoted values and NULL handling
- PostgreSQL schema differs from MariaDB structure requiring field mapping
- Dashboard expects recent data but production data is primarily historical (2020-2025)
- Migration must maintain data integrity and relationships

**Stakeholders:**
- End users needing functional kidnapping dashboard
- Data analysts requiring accurate statistics
- System administrators maintaining data integrity

## Goals / Non-Goals

**Goals:**
- Achieve 100% data migration from MariaDB production dump (1,260 records, 10,316 victims)
- Fix parser to handle all 54 INSERT statements in single SQL file
- Ensure dashboard displays meaningful statistics with complete dataset
- Implement robust validation to prevent future data loss
- Maintain backward compatibility with existing API endpoints

**Non-Goals:**
- Modifying dashboard UI/UX (focus on data functionality)
- Changing database schema structure
- Adding new data sources or collection methods
- Implementing real-time data synchronization

## Decisions

### Parser Architecture
**Decision:** Rewrite parser to use iterative INSERT statement processing instead of single regex match
**Rationale:** Current regex approach only captures first INSERT statement. Iterative processing ensures all 54 statements are handled.
**Alternatives considered:**
- Multi-regex approach: Complex and fragile with nested quotes
- SQL parsing library: Overkill for this specific use case

### Data Validation Strategy
**Decision:** Implement pre and post-migration validation with record counts and checksums
**Rationale:** Ensures data integrity and provides confidence in migration success
**Alternatives considered:**
- Post-migration only: Risk of undetected data loss
- No validation: Unacceptable for production data

### Error Handling
**Decision:** Continue processing on individual record failures but log and track errors
**Rationale:** Some records may have data quality issues but shouldn't block entire migration
**Alternatives considered:**
- Fail-fast approach: Could leave majority of data unmigrated
- Silent failures: Unacceptable for production system

### Date Range Handling
**Decision:** Migrate all historical data but update dashboard to handle extended date ranges
**Rationale:** Preserves all available data while maintaining dashboard functionality
**Alternatives considered:**
- Filter to recent data only: Would lose valuable historical context
- Data modification: Risks altering original production data

## Risks / Trade-offs

**Performance Risk:** Processing 1,260 records may exceed memory limits with current parser
→ **Mitigation:** Implement streaming processing and batch record handling

**Data Quality Risk:** Some records may have malformed data or invalid values
→ **Mitigation:** Add comprehensive validation and error tracking with fallback values

**Schema Mismatch Risk:** MariaDB and PostgreSQL schemas may have incompatible field types
→ **Mitigation:** Add type conversion and validation for each field mapping

**Dashboard Impact Risk:** Large dataset may affect dashboard loading performance
→ **Mitigation:** Implement pagination and caching in API endpoints

**Rollback Complexity Risk:** Full migration may be difficult to rollback if issues occur
→ **Mitigation:** Implement backup strategy and staged migration approach

## Migration Plan

### Phase 1: Parser Enhancement (Critical)
1. Backup current database state
2. Rewrite `mariadb_parser.py` to handle multiple INSERT statements
3. Add comprehensive logging and error tracking
4. Test parser with sample of all INSERT statements

### Phase 2: Data Validation (Critical)
1. Implement pre-migration validation of source data
2. Add post-migration integrity checks
3. Create validation reports with record counts and statistics
4. Test validation with small dataset first

### Phase 3: Full Migration (Critical)
1. Execute complete migration with all 1,260 records
2. Monitor migration progress and error rates
3. Validate migration success with comprehensive checks
4. Update dashboard to handle historical date ranges

### Phase 4: Verification (Important)
1. Test dashboard functionality with complete dataset
2. Verify API endpoints return correct statistics
3. Performance testing with full dataset
4. User acceptance testing

### Rollback Strategy
- Database backup before migration
- Staged migration approach for easy rollback
- Validation checkpoints at each phase
- Emergency restore procedures documented

## Open Questions

- Dashboard date range optimization for historical data display
- Performance impact on API endpoints with 100x more data
- Whether to implement data archiving for very old records
- User notification strategy for improved dashboard functionality
