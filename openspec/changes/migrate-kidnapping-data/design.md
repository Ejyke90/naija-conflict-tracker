## Context

The Nigeria Conflict Tracker's kidnapping analytics dashboard displays "No data" because 13 kidnapping records with 78 victims are missing from the PostgreSQL database. The MariaDB export (`u503102722_conflictdb (1).sql`) contains this missing data, but it wasn't migrated during the initial database setup. The current PostgreSQL database has 6,991 conflict records but zero kidnapping data.

## Goals / Non-Goals

**Goals:**
- Extract 13 kidnapping records from MariaDB SQL export
- Import kidnapping victim data (male/female/unknown breakdown) into PostgreSQL
- Enable kidnapping analytics dashboard to display real data
- Ensure existing conflict analytics remain functional
- Create reusable data migration framework

**Non-Goals:**
- Complete database re-migration (only kidnapping records)
- Schema changes to existing tables
- Frontend dashboard modifications (data should flow automatically)

## Decisions

**SQL Parsing Approach:**
- Use regex-based parsing instead of database import to avoid MySQL compatibility issues
- Parse raw INSERT statements to extract kidnapping victim counts
- Handle quoted strings and NULL values properly

**Migration Strategy:**
- Update existing conflict records rather than creating new ones
- Use record ID matching where possible, create new IDs for conflicts
- Preserve existing death and injury data in PostgreSQL

**Data Validation:**
- Compare totals before/after migration
- Run regression tests on existing analytics endpoints
- Verify dashboard displays correct kidnapping statistics

## Risks / Trade-offs

**Data Integrity Risk** → Mitigation: Backup database before migration, validate record counts
**Parsing Complexity** → Mitigation: Use tested regex patterns, handle edge cases gracefully
**Performance Impact** → Mitigation: Run migration during low-traffic periods, use transactions

## Migration Plan

1. Create migration script with SQL parsing logic
2. Backup current PostgreSQL database
3. Run migration in transaction with rollback capability
4. Validate data integrity and run regression tests
5. Monitor dashboard for correct kidnapping data display

## Open Questions

- Should missing location data (state/LGA) be geocoded or left as NULL?
- How to handle duplicate record IDs between MariaDB and PostgreSQL?
