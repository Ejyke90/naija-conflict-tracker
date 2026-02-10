## Why

The kidnapping analytics dashboard shows "No data available" with 0 victims and 0 incidents, despite having conflict data in the database. Analysis revealed that 13 kidnapping records with 78 total victims from the MariaDB export are completely missing from the PostgreSQL database, causing this critical data gap.

## What Changes

- Extract and parse 13 kidnapping records from MariaDB SQL export file
- Create migration script to import kidnapping data into PostgreSQL database
- Update existing conflict records with kidnapping victim counts (male/female/unknown)
- Validate data integrity and run regression tests to ensure existing functionality remains intact

## Capabilities

### New Capabilities
- `data-migration`: Framework for importing historical conflict data from SQL exports into PostgreSQL
- `kidnapping-analytics`: Complete kidnapping victim tracking and dashboard functionality

### Modified Capabilities
- `conflict-data`: Enhanced to support kidnapping victim data (male/female/unknown breakdown)

## Impact

- **Backend**: New migration script, database updates to conflicts table
- **Frontend**: Kidnapping dashboard will display actual data instead of "No data"
- **Database**: 13 records updated with kidnapping victim information
- **API**: Existing endpoints will return kidnapping data for analytics
- **Testing**: Regression tests required to ensure existing conflict analytics remain functional
