## Why

The current dashboard displays generic charts with "No data available" messages and zero-value metrics, creating a low-signal user experience. We need to replace these ineffective visualizations with high-signal intelligence metrics that provide immediate, actionable insights derived from our existing conflict data schema.

## What Changes

- Create new `IntelligenceGrid` React component with 3-column layout of intelligence cards
- Replace seasonal patterns and state comparison sections with focused metrics
- Implement four core intelligence metrics:
  - Kinetic Lethality Index (Total Fatalities / Total Incidents)
  - Displacement Velocity (rate of change in displaced_persons)
  - Verification Pulse (percentage of verified reports)
  - Regional Risk Leaderboard (top 3 states by incident volume)
- Apply dark-mode theme with emerald (positive) and rose (high-risk) color coding
- Fetch data from existing `/api/v1/analytics/stats` endpoint

## Capabilities

### New Capabilities
- `intelligence-grid`: High-signal dashboard component displaying key conflict metrics in a clean 3-column grid layout with real-time data updates

### Modified Capabilities
- `dashboard-analytics`: Modify main dashboard to use IntelligenceGrid instead of seasonal/state comparison charts

## Impact

- **Frontend**: New IntelligenceGrid component, modified dashboard and analytics pages
- **API**: Enhanced `/api/v1/analytics/stats` endpoint to return calculated metrics
- **UI/UX**: Transition from low-signal charts to high-intelligence metrics
- **Performance**: Reduced API calls, faster page loads, better user engagement
