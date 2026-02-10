# intelligence-grid Specification

## Purpose
TBD - created by archiving change build-intelligence-grid. Update Purpose after archive.
## Requirements
### Requirement: Display intelligence grid with high-signal metrics
The system SHALL display a 3-column grid of intelligence cards showing key conflict metrics instead of generic charts.

#### Scenario: Load intelligence grid
- **WHEN** user navigates to dashboard or analytics page
- **THEN** system displays IntelligenceGrid component with 4 intelligence cards in responsive layout

### Requirement: Calculate and display kinetic lethality index
The system SHALL calculate kinetic lethality index as (Total Fatalities / Total Incidents) and display with trend indicator.

#### Scenario: Show lethality index
- **WHEN** intelligence grid loads
- **THEN** system displays "National Lethality: X.X" with color-coded indicator (emerald for low, rose for high)

### Requirement: Track displacement velocity
The system SHALL calculate rate of change in displaced persons and display with primary driver identification.

#### Scenario: Show displacement pulse
- **WHEN** intelligence grid loads
- **THEN** system displays "IDP Surge: +X,XXX in [State]" with driver context like "Resource competition"

### Requirement: Display data verification pulse
The system SHALL calculate percentage of verified reports and show data integrity metric.

#### Scenario: Show verification status
- **WHEN** intelligence grid loads
- **THEN** system displays "Data Integrity: XX% of reports verified" with pending confirmation count

### Requirement: Show regional risk leaderboard
The system SHALL display top 3 states by incident volume in ranked order.

#### Scenario: Show risk leaderboard
- **WHEN** intelligence grid loads
- **THEN** system displays numbered list of top 3 states with incident counts

### Requirement: Apply semantic color coding
The system SHALL use emerald colors for positive trends and rose colors for high-risk metrics.

#### Scenario: Color code metrics
- **WHEN** intelligence grid renders
- **THEN** system applies emerald to low-risk metrics and rose to high-risk indicators

### Requirement: Fetch data from analytics stats endpoint
The system SHALL retrieve conflict data from existing `/api/v1/analytics/stats` endpoint.

#### Scenario: Load analytics data
- **WHEN** intelligence grid mounts
- **THEN** system fetches data from `/api/v1/analytics/stats` and processes for display

### Requirement: Handle loading and error states
The system SHALL display appropriate loading states and error handling for intelligence grid.

#### Scenario: Show loading state
- **WHEN** data is being fetched
- **THEN** system displays skeleton loaders for each intelligence card

#### Scenario: Handle error state
- **WHEN** API call fails
- **THEN** system displays error message with retry option

### Requirement: Responsive design support
The system SHALL adapt intelligence grid layout for mobile and desktop viewports.

#### Scenario: Mobile layout
- **WHEN** viewed on mobile device
- **THEN** system displays intelligence cards in single column stack

#### Scenario: Desktop layout
- **WHEN** viewed on desktop
- **THEN** system displays intelligence cards in 3-column grid

