## ADDED Requirements

### Requirement: SQL Export Data Import
The system SHALL provide functionality to parse and import conflict data from MariaDB SQL export files.

#### Scenario: Parse MariaDB export file
- **WHEN** system processes MariaDB SQL export file
- **THEN** system extracts INSERT statements for conflicts table
- **AND** system parses victim counts (kidnapped_male, kidnapped_female, kidnapped_unknown)
- **AND** system handles NULL values and quoted strings correctly

#### Scenario: Validate parsed data
- **WHEN** parsing completes
- **THEN** system validates total record count matches expected
- **AND** system verifies kidnapping victim totals are calculated correctly
- **AND** system flags any records with missing critical fields

### Requirement: Kidnapping Data Migration
The system SHALL migrate kidnapping records from MariaDB export to PostgreSQL database.

#### Scenario: Update existing conflict records
- **WHEN** matching conflict record exists in PostgreSQL
- **THEN** system updates kidnapped_male, kidnapped_female, kidnapped_unknown fields
- **AND** system preserves existing death and injury data
- **AND** system logs successful updates

#### Scenario: Create new conflict records
- **WHEN** no matching record exists in PostgreSQL
- **THEN** system creates new conflict record with kidnapping data
- **AND** system assigns appropriate conflict_type_id and location data
- **AND** system maintains referential integrity with states and LGAs tables

#### Scenario: Migration transaction safety
- **WHEN** migration process runs
- **THEN** system executes all updates within a single database transaction
- **AND** system rolls back completely if any error occurs
- **AND** system provides detailed error logging for failed records

### Requirement: Migration Data Integrity
The system SHALL ensure data integrity during and after migration process.

#### Scenario: Pre-migration validation
- **WHEN** migration starts
- **THEN** system creates database backup
- **AND** system records baseline statistics (total records, kidnapping counts)
- **AND** system verifies target database connectivity

#### Scenario: Post-migration verification
- **WHEN** migration completes
- **THEN** system compares imported record counts with source data
- **AND** system verifies kidnapping victim totals match exactly
- **AND** system runs regression tests on existing analytics endpoints

#### Scenario: Dashboard data verification
- **WHEN** migration completes
- **THEN** kidnapping analytics dashboard displays non-zero values
- **AND** dashboard shows correct victim counts by gender
- **AND** dashboard displays affected states and incidents
