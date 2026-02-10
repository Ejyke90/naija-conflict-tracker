## Context

The current dashboard displays low-signal charts that consistently show "No data available" or zero values, creating poor user experience. Our existing `/api/v1/analytics/stats` endpoint contains rich conflict data (fatalities, displaced_persons, verification status) but isn't being leveraged effectively. We need to transform this data into high-signal intelligence metrics that provide immediate actionable insights.

## Goals / Non-Goals

**Goals:**
- Replace ineffective seasonal/state comparison charts with high-signal intelligence metrics
- Create a responsive 3-column grid layout that works on mobile and desktop
- Implement real-time data fetching with proper loading and error states
- Use semantic color coding (emerald for positive trends, rose for high-risk metrics)
- Leverage existing API endpoints without requiring backend changes initially

**Non-Goals:**
- Complete redesign of the entire dashboard architecture
- New backend API endpoints (will enhance existing ones in future iterations)
- Complex data visualization libraries (keeping it simple with cards and metrics)
- Historical data analysis or forecasting in this component

## Decisions

### Component Architecture
- **Decision**: Create standalone `IntelligenceGrid` component with internal state management
- **Rationale**: Keeps component self-contained, reusable across dashboard and analytics pages
- **Alternative**: Integrate into existing dashboard component - rejected for maintainability

### Data Fetching Strategy
- **Decision**: Use existing `/api/v1/analytics/stats` endpoint with client-side calculations
- **Rationale**: Faster implementation, leverages proven endpoint, allows immediate deployment
- **Alternative**: Create new specialized endpoint - rejected for complexity and timeline

### Styling Approach
- **Decision**: Use Tailwind CSS with dark-mode support and semantic color tokens
- **Rationale**: Consistent with existing design system, better accessibility
- **Alternative**: CSS-in-JS - rejected for bundle size and consistency

### Metric Calculations
- **Decision**: Perform calculations client-side (lethality index, displacement velocity)
- **Rationale**: Reduces backend complexity, allows real-time updates without cache invalidation
- **Alternative**: Backend calculations - considered for future optimization

## Risks / Trade-offs

**Performance Risk**: Client-side calculations may impact mobile performance
- **Mitigation**: Use React.memo for expensive calculations, implement debounced updates

**Data Freshness**: Relying on existing endpoint may have cache delays
- **Mitigation**: Implement WebSocket integration for real-time updates in future iteration

**API Dependency**: If existing endpoint changes, component may break
- **Mitigation**: Add comprehensive error handling and fallback displays

**Complexity Trade-off**: Simplified metrics may lose nuance compared to detailed charts
- **Mitigation**: Include drill-down links to detailed analytics for power users

## Migration Plan

1. **Phase 1**: Create IntelligenceGrid component alongside existing charts
2. **Phase 2**: Replace seasonal/state comparison sections in dashboard and analytics pages
3. **Phase 3**: Remove unused chart components and clean up imports
4. **Rollback**: Keep old components in separate branch for quick rollback if needed

## Open Questions

- Should we implement real-time updates via WebSocket or stick with periodic polling?
- What refresh interval provides optimal balance between freshness and performance?
- Should we add user preferences for metric selection or keep fixed set?
