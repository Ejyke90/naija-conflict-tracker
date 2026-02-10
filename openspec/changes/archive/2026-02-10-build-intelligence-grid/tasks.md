## 1. Component Setup

- [x] 1.1 Create IntelligenceGrid component file structure
- [x] 1.2 Set up TypeScript interfaces for analytics data
- [x] 1.3 Create intelligence card subcomponents

## 2. Data Layer Implementation

- [x] 2.1 Implement data fetching from /api/v1/analytics/stats endpoint
- [x] 2.2 Create data transformation utilities for metric calculations
- [x] 2.3 Add error handling and retry logic

## 3. Metric Calculations

- [x] 3.1 Implement kinetic lethality index calculation (fatalities/incidents)
- [x] 3.2 Implement displacement velocity calculation (rate of change)
- [x] 3.3 Implement verification pulse calculation (verified percentage)
- [x] 3.4 Implement regional risk leaderboard (top 3 states)

## 4. UI Implementation

- [x] 4.1 Create responsive 3-column grid layout with Tailwind CSS
- [x] 4.2 Implement semantic color coding (emerald/rose)
- [x] 4.3 Add loading skeleton states for each card
- [x] 4.4 Implement error state with retry functionality

## 5. Integration

- [x] 5.1 Replace seasonal patterns section in dashboard with IntelligenceGrid
- [x] 5.2 Replace state comparison section in analytics page with IntelligenceGrid
- [x] 5.3 Remove unused chart component imports
- [x] 5.4 Test responsive behavior on mobile and desktop

## 6. Testing & Verification

- [x] 6.1 Test component renders with mock data
- [x] 6.2 Test API integration with real analytics endpoint
- [x] 6.3 Test error handling and loading states
- [x] 6.4 Test responsive design across viewports
- [x] 6.5 Verify semantic color coding works correctly

## 7. Cleanup & Documentation

- [x] 7.1 Remove unused SeasonalPatternChart and StateComparisonChart components
- [x] 7.2 Update component documentation and props interfaces
- [x] 7.3 Add JSDoc comments for metric calculation functions
- [x] 7.4 Verify no console errors or warnings
