# 🗺️ Interactive Map - Quick Reference

## Setup (1 minute)

```bash
# 1. Install dependencies
cd frontend && npm install supercluster @types/supercluster

# 2. Add environment variables
echo "NEXT_PUBLIC_MAPBOX_TOKEN=pk.your_token" >> .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" >> .env.local

# 3. Start server
npm run dev

# 4. Visit map
open http://localhost:3000/map
```

## Import & Use

```tsx
// Fullscreen map page
import { ConflictMap } from '@/components/map';
<ConflictMap fullscreen />

// Dashboard widget
import DashboardMapWidget from '@/components/DashboardMapWidget';
<DashboardMapWidget />

// With filters
import { useMapFilters } from '@/hooks/useMapFilters';
const { setStates } = useMapFilters();
setStates(['Borno', 'Kaduna']);
```

## File Locations

```
components/map/    # All map components
hooks/             # useMapData, useMapFilters, useGeocoding
lib/map/           # colors, utils, clustering
pages/map.tsx      # Fullscreen map page
styles/map.css     # Custom styles
```

## Key Components

| Component | Purpose |
|-----------|---------|
| `ConflictMap` | Main map container |
| `EventMarker` | Individual event markers |
| `ClusterMarker` | Grouped event clusters |
| `EventPopup` | Event detail popup |
| `MapFilters` | Filter sidebar |
| `MapLegend` | Color/size legend |
| `MapControls` | Search & controls |

## Key Hooks

| Hook | Purpose |
|------|---------|
| `useMapData` | Fetch & filter events |
| `useMapFilters` | Manage filter state |
| `useGeocoding` | Location search |

## Customization

```typescript
// Change colors (lib/map/colors.ts)
EVENT_COLORS['Armed Conflict'] = '#FF0000';

// Change clustering (lib/map/clustering.ts)
radius: 80, maxZoom: 14

// Change refresh interval (hooks/useMapData.ts)
refreshInterval: 120000 // 2 minutes
```

## Data Format

```json
{
  "id": "uuid",
  "latitude": 10.8989,
  "longitude": 13.6865,
  "event_type": "Armed Conflict",
  "state": "Borno",
  "fatalities": 12,
  "event_date": "2024-01-15"
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Gray map | Check Mapbox token in `.env.local` |
| No markers | Verify backend running at `localhost:8000` |
| No clustering | Zoom out to < 8 |
| Filters not working | Check backend supports query params |

## Performance Tips

- Keep marker count < 10,000 for optimal performance
- Use clustering for dense areas
- Increase clustering radius for better performance
- Filter events server-side when possible

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Navigate controls |
| `Enter` | Activate control |
| `Esc` | Close popup |
| `+/-` | Zoom in/out |
| `Arrow keys` | Pan map |

## Links

- [Full Guide](./INTERACTIVE_MAP_GUIDE.md)
- [Implementation Summary](./MAP_IMPLEMENTATION_SUMMARY.md)
- [Component README](./frontend/components/map/README.md)
