## ADDED Requirements

### Requirement: Flexible API response validation
The system SHALL validate API responses using multiple format strategies to handle varying backend response structures.

#### Scenario: Standard API response format
- **WHEN** backend returns response with `data` array property
- **THEN** frontend SHALL extract and validate the data array
- **AND** system SHALL display chart with extracted data points

#### Scenario: Direct array response format
- **WHEN** backend returns response as direct array
- **THEN** frontend SHALL wrap array in expected object structure
- **AND** system SHALL generate default summary statistics from array data

#### Scenario: Alternative data property names
- **WHEN** backend returns response with alternative data properties (results, items, records)
- **THEN** frontend SHALL detect and use the first valid data property found
- **AND** system SHALL log which property was used for debugging

#### Scenario: Empty or null data responses
- **WHEN** backend returns empty data array or null data
- **THEN** frontend SHALL display "No data available" message with retry options
- **AND** system SHALL provide suggestions for reducing time range or checking connection

### Requirement: Comprehensive error state handling
The system SHALL provide meaningful error messages and recovery options for all data validation failures.

#### Scenario: Network timeout errors
- **WHEN** API request times out after 20 seconds
- **THEN** system SHALL display "Request timed out" error message
- **AND** system SHALL provide retry button with attempt counter
- **AND** system SHALL suggest reducing time range or checking internet connection

#### Scenario: Server error responses
- **WHEN** backend returns 5xx status codes
- **THEN** system SHALL display "Service unavailable" error message
- **AND** system SHALL implement exponential backoff retry logic
- **AND** system SHALL provide manual refresh option

#### Scenario: Data structure validation failures
- **WHEN** API response data structure is unexpected
- **THEN** system SHALL log detailed validation information in development
- **AND** system SHALL display user-friendly error message
- **AND** system SHALL provide debug information in development environment

#### Scenario: Authentication failures during data fetch
- **WHEN** data request returns 401 authentication error
- **THEN** system SHALL trigger token refresh automatically
- **AND** system SHALL retry data request with new token
- **AND** system SHALL redirect to login if refresh fails

### Requirement: MonthlyTrendsChart data processing
The system SHALL process and display monthly conflict trends data with proper validation and error recovery.

#### Scenario: Successful data processing
- **WHEN** valid monthly trends data is received
- **THEN** system SHALL calculate moving averages for trend lines
- **AND** system SHALL detect and mark anomalous data points
- **AND** system SHALL generate forecast data if requested
- **AND** chart SHALL display incidents, fatalities, and trend lines correctly

#### Scenario: Data with missing values
- **WHEN** monthly data contains null or undefined values
- **THEN** system SHALL replace missing values with zeros
- **AND** system SHALL log data quality issues for monitoring
- **AND** chart SHALL display with interpolated trend lines

#### Scenario: Insufficient data for forecasting
- **WHEN** historical data has fewer than 3 data points
- **THEN** system SHALL disable forecasting functionality
- **AND** system SHALL display "Insufficient data for forecasting" message
- **AND** chart SHALL still display available historical data

#### Scenario: Large dataset handling
- **WHEN** monthly trends data exceeds 24 months
- **THEN** system SHALL limit display to most recent 24 months
- **AND** system SHALL provide option to load full dataset
- **AND** performance SHALL remain responsive with large datasets
