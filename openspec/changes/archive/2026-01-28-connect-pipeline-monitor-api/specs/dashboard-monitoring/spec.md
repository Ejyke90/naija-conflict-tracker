## MODIFIED Requirements

### Requirement: Pipeline Status Display
The dashboard Pipeline Monitor component SHALL fetch and display real-time pipeline status data from the backend API endpoint instead of using hardcoded sample data.

**Acceptance Criteria:**
- Component calls `/api/v1/monitoring/pipeline-status` on mount
- Displays actual pipeline metrics from API response
- Shows pipeline status (running, completed, failed, idle)
- Displays last run timestamp from API
- Shows actual sources processed count
- Shows actual articles collected count
- Shows actual events extracted count
- Displays actual geocoding success rate
- Displays actual validation pass rate
- Shows system health indicators (Redis, database, API)

#### Scenario: Initial Data Load
- **GIVEN** user navigates to Dashboard
- **WHEN** user selects the "Pipeline" tab
- **THEN** component displays loading skeleton
- **AND** fetches data from `/api/v1/monitoring/pipeline-status`
- **AND** displays real-time pipeline metrics
- **AND** shows last update timestamp

#### Scenario: Auto-Refresh Updates
- **GIVEN** Pipeline Monitor is visible
- **WHEN** 30 seconds elapse since last fetch
- **THEN** component automatically refetches data
- **AND** updates displayed metrics
- **AND** shows smooth transition (no flash/flicker)

#### Scenario: API Error Handling
- **GIVEN** Pipeline Monitor attempts to fetch data
- **WHEN** backend API is unavailable or returns error
- **THEN** component displays user-friendly error message
- **AND** shows "Pipeline status unavailable" state
- **AND** continues to retry on next refresh interval

#### Scenario: Backend Recovery
- **GIVEN** Pipeline Monitor is in error state
- **WHEN** backend API becomes available again
- **THEN** component automatically recovers on next refresh
- **AND** displays current pipeline data
- **AND** clears error message

### Requirement: Loading States
The Pipeline Monitor SHALL provide visual feedback during data fetching operations to maintain good user experience.

**Acceptance Criteria:**
- Shows loading skeleton on initial mount
- Shows loading indicator during background refreshes
- Maintains previous data while fetching updates
- Transitions smoothly between states
- No layout shift during loading

#### Scenario: First Load Experience
- **GIVEN** user opens Pipeline tab for the first time
- **WHEN** component is mounting
- **THEN** displays full-page loading skeleton
- **AND** skeleton matches final layout structure
- **AND** transitions to data view when loaded

#### Scenario: Background Refresh
- **GIVEN** Pipeline Monitor displays data
- **WHEN** auto-refresh triggers (30 seconds)
- **THEN** shows subtle loading indicator
- **AND** maintains current data visibility
- **AND** updates data seamlessly when loaded

### Requirement: Error Recovery
The Pipeline Monitor SHALL gracefully handle API failures and provide automatic recovery without user intervention.

**Acceptance Criteria:**
- Displays clear error messages
- Shows last successful update timestamp if available
- Automatically retries on next interval
- Does not require user to refresh page
- Logs errors to console for debugging

#### Scenario: Transient Network Error
- **GIVEN** Pipeline Monitor is running
- **WHEN** API request fails due to network issue
- **THEN** displays "Unable to fetch pipeline status" message
- **AND** shows last successful update time if available
- **AND** automatically retries after 30 seconds
- **AND** recovers when network is restored

#### Scenario: Backend Maintenance
- **GIVEN** backend API is down for maintenance
- **WHEN** Pipeline Monitor attempts to fetch data
- **THEN** displays maintenance-friendly error message
- **AND** continues polling for recovery
- **AND** automatically displays data when backend returns

## ADDED Requirements

### Requirement: Polling Interval Configuration
The Pipeline Monitor SHALL refresh pipeline data automatically every 30 seconds to provide near real-time status updates.

**Acceptance Criteria:**
- Auto-refresh interval is 30 seconds
- Interval starts after component mount
- Interval is cleared when component unmounts
- No memory leaks from uncleaned intervals
- Polling pauses when tab is not visible (optional optimization)

#### Scenario: Active Monitoring
- **GIVEN** Pipeline Monitor is mounted and visible
- **WHEN** 30 seconds pass since last fetch
- **THEN** component automatically fetches fresh data
- **AND** updates all displayed metrics
- **AND** resets 30-second timer

#### Scenario: Component Cleanup
- **GIVEN** Pipeline Monitor has active refresh interval
- **WHEN** user navigates away from Pipeline tab
- **THEN** component clears the interval timer
- **AND** stops making API requests
- **AND** prevents memory leaks

### Requirement: Type Safety
The Pipeline Monitor SHALL use TypeScript interfaces to ensure type safety for API responses and component state.

**Acceptance Criteria:**
- Defines TypeScript interface for PipelineStatus
- Validates API response structure
- Provides type hints in IDE
- Catches type errors at compile time
- Documents expected data shape

#### Scenario: API Response Validation
- **GIVEN** Pipeline Monitor receives API response
- **WHEN** response structure is validated
- **THEN** TypeScript enforces correct property types
- **AND** prevents runtime type errors
- **AND** provides autocomplete in IDE

## Affected Files

### Modified
- `frontend/components/dashboard/PipelineMonitor.tsx` - Replace hardcoded data with API calls

### Unchanged
- `backend/app/api/v1/endpoints/monitoring.py` - Endpoint already exists
- `frontend/components/dashboard/ConflictDashboard.tsx` - Parent component unchanged
