## Why

The kidnapping dashboard is completely non-functional, showing "No data available" despite having a production dataset of 1,260 kidnapping records with 10,316 victims. The current migration only processed 1% of available data (13 records, 78 victims), making the dashboard statistically insignificant and useless for operational monitoring. This is a critical production data integrity issue that prevents the platform from delivering its core functionality.

## What Changes

- **Fix MariaDB parser to handle all INSERT statements** - Current parser only processes first INSERT statement but file contains 54 INSERT statements with kidnapping data
- **Re-run complete migration with full dataset** - Import all 1,260 kidnapping records and 10,316 victims instead of current 13 records
- **Update migration validation** - Add comprehensive checks to verify complete data transfer
- **Fix dashboard date range handling** - Ensure dashboard can display historical data from 2020-2025 timeframe
- **Add data integrity verification** - Implement post-migration validation to ensure no data loss

## Capabilities

### New Capabilities
- `complete-kidnapping-migration`: Full data migration from MariaDB production database to PostgreSQL with all 1,260 records
- `data-integrity-validation`: Comprehensive validation system to verify complete migration success
- `multi-insert-parser`: Enhanced SQL parser capable of handling multiple INSERT statements in single file

### Modified Capabilities
- `kidnapping-analytics`: Update requirements to handle complete dataset instead of sample data
- `data-migration`: Modify migration requirements to ensure 100% data coverage instead of partial migration

## Impact

**Critical Systems Affected:**
- Kidnapping dashboard (completely non-functional)
- API endpoints for kidnapping statistics (returning empty results)
- Data analytics and reporting (statistically insignificant)
- User confidence in platform data integrity

**Backend Components:**
- `mariadb_parser.py` - Requires complete rewrite to handle multiple INSERT statements
- `kidnapping_migration.py` - Update to process full dataset
- Database schema validation scripts
- API endpoint testing with complete dataset

**Frontend Components:**
- Dashboard components expecting meaningful data
- Date range filters for historical data
- Statistical visualization components

**Data Volume Impact:**
- Current: 13 records, 78 victims
- Required: 1,260 records, 10,316 victims  
- Increase: 9,700% more records, 13,200% more victim data
