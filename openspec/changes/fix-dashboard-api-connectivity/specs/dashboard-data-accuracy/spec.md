# Dashboard Data Accuracy Specification

## ADDED Requirements

### Requirement: Dashboard displays real database counts
The dashboard SHALL display actual database values from the conflict_events view instead of zero values.

#### Scenario: Validation queue shows correct count
- **WHEN** user loads the dashboard
- **THEN** "Events awaiting verification" SHALL display 6,982 (not 0)

#### Scenario: Database size shows verified count
- **WHEN** user views the dashboard
- **THEN** "DATABASE SIZE VERIFIED" SHALL display 11 (not 0)

#### Scenario: Last activity shows real timestamp
- **WHEN** user checks dashboard metrics
- **THEN** "LAST ACTIVITY" SHALL display "Feb 9, 2026" (not "NEVER")

### Requirement: High-risk alerts display active alerts
The dashboard SHALL show all active high-risk alerts from the alert_events table.

#### Scenario: Active alerts displayed
- **WHEN** user views High-Risk Alerts section
- **THEN** system SHALL display 1 active alert (not "No active high-risk alerts")

#### Scenario: Alert details shown
- **WHEN** active alerts exist
- **THEN** system SHALL display alert title, priority, and risk score

### Requirement: API endpoints return real data
All monitoring API endpoints SHALL return actual database query results.

#### Scenario: Pipeline status endpoint
- **WHEN** frontend calls /api/v1/monitoring/pipeline-status
- **THEN** response SHALL contain total_records: 6993 and recent_incidents > 0

#### Scenario: Recent events endpoint
- **WHEN** frontend calls /api/v1/monitoring/recent-events
- **THEN** response SHALL contain events array with actual conflict event data

#### Scenario: Data quality endpoint
- **WHEN** frontend calls /api/v1/monitoring/data-quality
- **THEN** response SHALL contain validation metrics based on real database data

### Requirement: Database connectivity validation
The system SHALL validate database connectivity and query execution.

#### Scenario: Database health check
- **WHEN** system performs health check
- **THEN** database connection SHALL be healthy and responsive

#### Scenario: Query execution validation
- **WHEN** system executes conflict_events view queries
- **THEN** queries SHALL return expected record counts without errors

### Requirement: Authentication allows data access
Authenticated users SHALL be able to access dashboard data without authorization blocks.

#### Scenario: Authenticated user access
- **WHEN** user logs in with valid credentials (info@thenextier.com / test12345)
- **THEN** dashboard SHALL load with real data (not zeros)

#### Scenario: API token validation
- **WHEN** frontend makes authenticated API calls
- **THEN** backend SHALL accept tokens and return data successfully
