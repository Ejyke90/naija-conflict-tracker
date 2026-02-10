# Dashboard Components

## ValidationQueueCard

Replaces the System Heartbeat component with a high-performance validation queue monitor.

### Features
- **Real-time Updates**: Auto-refreshes every 30 seconds
- **Urgency Detection**: Shows URGENT banner when high-priority items exist
- **Performance Metrics**: Displays database size and last activity
- **Action Button**: Direct access to review interface
- **Error Handling**: Graceful degradation for API failures

### Props
None - component is self-contained and fetches its own data.

### Data Source
Queries `/api/v1/system/validation/summary` endpoint which serves pre-computed data from Neon PostgreSQL view.

### Styling
- Uses Tailwind CSS classes
- Responsive design
- Animated indicators for urgent items
- Professional card layout with proper visual hierarchy

### Usage
```tsx
import ValidationQueueCard from './ValidationQueueCard';

// In dashboard
<ValidationQueueCard />
```

### Integration Notes
- Replaced `SystemHeartbeat` component in dashboard
- Uses React Query v5 for data fetching
- Requires no authentication (public endpoint)
- Compatible with existing dashboard layout
