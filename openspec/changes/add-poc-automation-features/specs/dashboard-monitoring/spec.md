# Dashboard Monitoring Specification

## MODIFIED Requirements

### Requirement: Real-Time System Heartbeat Display
The dashboard SHALL display live operational status of the automation system with real-time updates.

**MODIFIED FROM**: Static status indicators
**MODIFIED TO**: Live heartbeat monitor with countdown and health indicators

#### Scenario: Display Scheduler Status
- **GIVEN** the scheduler is running normally
- **WHEN** user views dashboard
- **THEN** the system SHALL display:
  - Green "ACTIVE" status indicator
  - Next scheduled run countdown timer (e.g., "Next scrape in 12:34")
  - Last successful run timestamp
  - Current schedule configuration ("Every 15 minutes")
  - Total successful runs in last 24 hours
- **AND** SHALL update countdown every second

#### Scenario: Scheduler Stopped or Failed
- **GIVEN** the scheduler is not running
- **WHEN** user views dashboard
- **THEN** the system SHALL display:
  - Red "STOPPED" status indicator
  - Reason for stoppage (if available)
  - Last known run time
  - Alert banner prompting action
- **AND** SHALL provide "Restart" button for authorized users

#### Scenario: Real-Time Status Updates
- **GIVEN** dashboard is displaying heartbeat
- **WHEN** scheduler status changes
- **THEN** UI SHALL reflect new status within 10 seconds
- **AND** SHALL update without page refresh
- **AND** SHALL show smooth transitions between states

## ADDED Requirements

### Requirement: Live High-Risk Alert Monitor
The dashboard SHALL display active high-risk alerts with toast notifications.

#### Scenario: Display Active Alerts
- **GIVEN** high-risk alerts exist
- **WHEN** user views dashboard
- **THEN** the system SHALL display alert panel showing:
  - Count of active alerts
  - List of most recent 5 alerts
  - Color-coded by priority (red=CRITICAL, orange=HIGH)
  - Time since alert created
  - Brief event summary
- **AND** SHALL allow click to view full details

#### Scenario: Toast Notification for New Alert
- **GIVEN** user has dashboard open
- **WHEN** a new high-risk alert is triggered
- **THEN** the system SHALL display toast notification:
  - Slide-in animation from top-right
  - Alert summary and risk score
  - "View Details" button
  - Auto-dismiss after 10 seconds (unless critical)
- **AND** SHALL play notification sound (if enabled)
- **AND** SHALL stack multiple toasts if many arrive

#### Scenario: Alert Acknowledgment from Dashboard
- **GIVEN** an active alert is displayed
- **WHEN** user clicks "Acknowledge" button
- **THEN** the system SHALL mark alert as acknowledged
- **AND** SHALL prompt for optional notes
- **AND** SHALL remove from active alerts list
- **AND** SHALL update alert badge count

### Requirement: Live Signal Ticker
The dashboard SHALL display a scrolling ticker of latest conflict events.

#### Scenario: Display Recent Events Ticker
- **GIVEN** recent conflict events exist
- **WHEN** dashboard loads
- **THEN** the system SHALL display scrolling ticker showing:
  - Last 10 events
  - Event location, type, and severity
  - Color-coded by risk level
  - Continuous auto-scroll animation
- **AND** SHALL update with new events every 5 seconds

#### Scenario: Ticker Interaction
- **GIVEN** ticker is scrolling
- **WHEN** user hovers over an event
- **THEN** the system SHALL pause scrolling
- **AND** SHALL highlight hovered event
- **AND** SHALL show quick preview popup
- **AND** SHALL allow click to view full details

### Requirement: Automation Execution Log Viewer
The dashboard SHALL provide visibility into scheduled task execution history.

#### Scenario: View Recent Executions
- **GIVEN** automation logs exist
- **WHEN** user opens log viewer
- **THEN** the system SHALL display:
  - Last 20 executions
  - Execution timestamp
  - Job name and ID
  - Duration
  - Status (success/failure)
  - Result summary (articles scraped, events created)
- **AND** SHALL highlight failures in red
- **AND** SHALL allow expanding for full details

#### Scenario: Filter Execution Logs
- **GIVEN** execution logs are displayed
- **WHEN** user applies filters
- **THEN** the system SHALL support filtering by:
  - Date range
  - Status (success/failure/all)
  - Job name
- **AND** SHALL update results immediately

#### Scenario: Execution Performance Metrics
- **GIVEN** execution history exists
- **WHEN** user views metrics dashboard
- **THEN** the system SHALL display:
  - Success rate percentage
  - Average execution time
  - Trend chart (last 7 days)
  - Failure alerts if rate drops below threshold

### Requirement: Intelligence Depth Indicators
The dashboard SHALL display metrics on LLM extraction and categorization performance.

#### Scenario: Display Categorization Statistics
- **GIVEN** categorized events exist
- **WHEN** user views intelligence dashboard
- **THEN** the system SHALL display:
  - Total articles categorized today
  - Breakdown by conflict archetype (pie chart)
  - Average confidence scores
  - Articles pending categorization
- **AND** SHALL update in real-time

#### Scenario: Categorization Confidence Distribution
- **GIVEN** categorized events with confidence scores
- **WHEN** displaying statistics
- **THEN** the system SHALL show:
  - Distribution histogram (0-100% confidence)
  - Count of low-confidence items (<70%)
  - Percentage of high-confidence items (>85%)
- **AND** SHALL allow filtering by confidence threshold

### Requirement: Interactive Map Layer Controls
The dashboard map SHALL provide toggle controls for multiple data layers.

#### Scenario: Toggle Climate Stress Layer
- **GIVEN** climate data is available
- **WHEN** user toggles "Climate Stress" layer
- **THEN** the system SHALL display flood/drought indicators
- **AND** SHALL color-code regions by stress level
- **AND** SHALL show legend explaining colors
- **AND** SHALL persist toggle state in user preferences

#### Scenario: Toggle Mining Zone Layer
- **GIVEN** mining zone data is available
- **WHEN** user toggles "Mining Zones" layer
- **THEN** the system SHALL display mining activity areas
- **AND** SHALL show proximity circles around conflict events
- **AND** SHALL highlight overlaps between conflicts and mining zones

#### Scenario: Layer Performance
- **GIVEN** multiple layers are enabled
- **WHEN** rendering map
- **THEN** map load time SHALL remain under 2 seconds
- **AND** SHALL use progressive rendering for large datasets
- **AND** SHALL maintain smooth pan/zoom interactions

### Requirement: Policymaker Executive Dashboard
The dashboard SHALL provide an executive summary view for decision-makers.

#### Scenario: Executive Summary View
- **GIVEN** conflict data for current week
- **WHEN** policymaker views dashboard
- **THEN** the system SHALL display:
  - Total incidents this week vs last week
  - Hotspot states with highest activity
  - Trending conflict types
  - High-risk areas requiring attention
  - Recommended priority actions
- **AND** SHALL use clear visualizations (no technical jargon)

#### Scenario: Actionable Recommendations
- **GIVEN** high-risk patterns detected
- **WHEN** generating recommendations
- **THEN** the system SHALL provide:
  - Specific geographic areas to focus on
  - Suggested intervention types
  - Priority ranking (1-5)
  - Supporting evidence (recent events)
- **AND** SHALL allow exporting as PDF report

## Configuration

### Environment Variables
```bash
# Dashboard Updates
DASHBOARD_HEARTBEAT_POLL_INTERVAL=10  # seconds
DASHBOARD_ALERT_POLL_INTERVAL=5       # seconds
DASHBOARD_TICKER_UPDATE_INTERVAL=5    # seconds

# UI Preferences
DASHBOARD_ENABLE_SOUND_NOTIFICATIONS=true
DASHBOARD_TOAST_AUTO_DISMISS=10       # seconds
DASHBOARD_MAX_TICKER_ITEMS=10

# Layer Defaults
DASHBOARD_DEFAULT_LAYERS=heatmap,markers,climate
DASHBOARD_ENABLE_CLIMATE_LAYER=true
DASHBOARD_ENABLE_MINING_LAYER=true
DASHBOARD_ENABLE_BORDER_LAYER=true
```

### Frontend Components Structure
```
frontend/src/components/dashboard/
├── SystemHeartbeat.tsx          # Live scheduler status
├── HighRiskAlertMonitor.tsx     # Alert panel & toasts
├── LiveSignalTicker.tsx         # Scrolling event ticker
├── AutomationLogViewer.tsx      # Execution history
├── IntelligenceDepthPanel.tsx   # Categorization stats
├── PolicymakerAlert.tsx         # Executive dashboard
├── LayerToggleControl.tsx       # Map layer switches
└── ConflictArchetypeChart.tsx   # Pie/bar charts
```

### API Endpoints
```
GET /api/v1/system/heartbeat       # Scheduler status
GET /api/v1/alerts/active          # Active alerts
GET /api/v1/alerts/recent          # Recent alerts for ticker
GET /api/v1/automation/logs        # Execution history
GET /api/v1/stats/categorization   # Intelligence metrics
GET /api/v1/stats/executive        # Policymaker summary
POST /api/v1/alerts/{id}/acknowledge  # Acknowledge alert
```

## Dependencies

- React for frontend components
- Chart.js or Recharts for visualizations
- Mapbox GL or Leaflet for map layers
- Toast notification library (react-toastify)
- WebSocket or polling for real-time updates
