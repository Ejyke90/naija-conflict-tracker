# Heatmap Implementation Guide

## Overview

This document describes the Leaflet-based heatmap implementation for the Naija Conflict Tracker frontend and backend.

## Architecture

### Frontend Components

**Location:** `frontend/components/mapping/AdvancedConflictMap.tsx`

**Key Features:**
- Toggle heatmap visibility on/off
- Real-time data loading from backend
- Color gradient visualization (green → red)
- Export data as GeoJSON
- Loading states and error handling
- Responsive legend

**Dependencies:**
- `leaflet` (mapping library)
- `leaflet.heat` (heatmap layer visualization)
- `react-leaflet` (React wrapper for Leaflet)
- Next.js dynamic imports (SSR disabled for browser-only code)

### Backend API Endpoint

**Primary Endpoint:** `/api/v1/conflicts/heatmap/data`

**Alternative Endpoint:** `/api/v1/spatial/heatmap/data` (redundant, added for spatial module)

**Query Parameters:**
- `days_back` (default: 30) - Number of days to look back for conflicts

**Response Format:**
```json
{
  "points": [
    [latitude, longitude, intensity],
    [latitude, longitude, intensity],
    ...
  ],
  "bounds": {
    "north": 13.8,
    "south": 2.7,
    "east": 14.68,
    "west": 2.67
  }
}
```

**Alternative Response (Spatial Endpoint):**
```json
{
  "days_back": 30,
  "data_timestamp": "2024-01-15T10:30:00",
  "total_locations": 45,
  "points": [[lat, lng, intensity], ...],
  "details": [
    {
      "location": "Maiduguri",
      "state": "Borno",
      "incident_count": 5,
      "total_fatalities": 23,
      "latest_incident": "2024-01-14T15:20:00",
      "intensity": 7.5,
      "coordinates": {"lat": 11.8469, "lng": 13.1572}
    },
    ...
  ]
}
```

## How It Works

### Data Flow

1. **User Interaction:** User clicks "🔥 Heatmap" button in AdvancedConflictMap
2. **API Request:** Component calls `/api/v1/conflicts/heatmap/data?days_back=30`
3. **Backend Processing:** 
   - Query all conflicts with valid coordinates in past N days
   - Calculate intensity: `1 + (fatalities / max_fatalities) * 9` → scale 1-10
   - Return array of [lat, lng, intensity]
4. **Frontend Visualization:** 
   - Leaflet.heat layer renders points with color gradient
   - Intensity 0-10 maps to color gradient (green → red)
5. **Export:** User can export visualized data as GeoJSON

### Intensity Calculation

The backend currently uses a simple fatalities-based calculation:
- **Current Formula:** `intensity = 1 + (fatalities / max_fatalities) * 9`
- **Range:** 1-10 (Leaflet.heat expects 0-1 or normalized 0-10)
- **Rationale:** Each incident's contribution is proportional to its fatality count

**Spatial Endpoint** uses a more sophisticated calculation:
- **Formula:** `intensity = log(fatalities + 1) * sqrt(incident_count) / 2`
- **Features:**
  - Logarithmic scale prevents extreme values
  - Square root of incident count adds frequency weighting
  - Capped at 10 for reasonable visualization

### Color Gradient

```
Intensity → Color
0.0       → #006837 (dark green)
0.25      → #1a9850 (light green)
0.5       → #91cf60 (yellow-green)
0.75      → #d9ef8b (light yellow)
1.0       → #ff0000 (red)
```

This gradient follows standard cartography practices for conflict/threat visualization.

## Frontend Implementation Details

### Component State

```typescript
const [showHeatmap, setShowHeatmap] = useState(false);
const [heatmapLayer, setHeatmapLayer] = useState<any>(null);
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
```

### Key Functions

#### `loadHeatmapData()`
- Fetches heatmap data from backend
- Creates Leaflet.heat layer instance
- Adds layer to map
- Handles loading and error states

#### `handleHeatmapToggle()`
- Toggles heatmap visibility
- Calls `loadHeatmapData()` when enabling
- Removes layer from map when disabling

#### `handleExport()`
- Fetches heatmap data
- Converts to GeoJSON FeatureCollection format
- Creates downloadable file with timestamp

### Leaflet.heat Configuration

```typescript
const heat = L.heatLayer(data.points, {
  max: 10,                    // Max intensity value
  maxZoom: 18,               // Max zoom level before dissolution
  radius: 50,                // Radius of each point in pixels
  blur: 30,                  // Amount of blur for smoothing
  gradient: {                // Color gradient mapping
    0.0: '#006837',
    0.25: '#1a9850',
    0.5: '#91cf60',
    0.75: '#d9ef8b',
    1.0: '#ff0000'
  }
});
```

## Type Definitions

Created TypeScript declarations in `frontend/types/leaflet-heat.d.ts`:

```typescript
declare module 'leaflet' {
  function heatLayer(
    latlngs: Array<[number, number, number]>,
    options?: {...}
  ): L.Layer;
}
```

This allows proper TypeScript support for `L.heatLayer()` method.

## Testing the Heatmap

### Prerequisites
1. Backend must have conflict data with valid coordinates
2. PostgreSQL/PostGIS database populated with test data
3. Frontend dependencies installed

### Manual Testing Steps

1. **Start Backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Navigate to Map Component:**
   - Go to dashboard or map page
   - Locate "Advanced Conflict Map" section

4. **Test Heatmap Button:**
   - Click "🔥 Heatmap" button
   - Observe loading spinner
   - Verify heatmap layer appears with color gradient
   - Check legend displays intensity scale

5. **Test Export:**
   - Click "⬇ Export" button
   - Verify GeoJSON file downloads
   - Inspect file content (should be valid GeoJSON)

6. **Test Interactive Features:**
   - Zoom in/out (heatmap should adapt)
   - Pan across map
   - Toggle heatmap on/off multiple times
   - Check error handling if backend is down

### Automated Testing

Create `frontend/__tests__/components/AdvancedConflictMap.test.tsx`:

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AdvancedConflictMap from '@/components/mapping/AdvancedConflictMap';

describe('AdvancedConflictMap', () => {
  it('loads and displays heatmap data', async () => {
    render(<AdvancedConflictMap />);
    
    const heatmapButton = screen.getByText(/🔥 Heatmap/i);
    fireEvent.click(heatmapButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Heatmap layer active/i)).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    global.fetch = jest.fn(() => 
      Promise.reject(new Error('Network error'))
    );
    
    render(<AdvancedConflictMap />);
    fireEvent.click(screen.getByText(/🔥 Heatmap/i));
    
    await waitFor(() => {
      expect(screen.getByText(/Failed to load heatmap data/i)).toBeInTheDocument();
    });
  });
});
```

## Performance Optimization

### Current Limitations
- All points rendered simultaneously (can be 1000+ points)
- No clustering or aggregation at map level
- Full data fetch each time (no caching)

### Recommended Optimizations

1. **Data Caching:**
   ```typescript
   const cache = useRef<{timestamp: number, data: HeatmapData | null}>({
     timestamp: 0,
     data: null
   });
   
   // Reuse cached data if < 5 minutes old
   if (Date.now() - cache.current.timestamp < 300000) {
     return cache.current.data;
   }
   ```

2. **Server-Side Aggregation:**
   - For zoom levels < 8, aggregate to state/region level
   - For zoom levels 8-12, aggregate to LGA level
   - For zoom levels > 12, show individual incidents

3. **WebSocket Updates:**
   - Subscribe to real-time conflict data
   - Update heatmap incrementally instead of full reload

4. **IndexedDB Caching:**
   - Cache heatmap data locally
   - Reduce server load
   - Faster subsequent loads

## Integration with Other Components

### Dashboard
- Heatmap can be embedded as dashboard card
- Toggle button on dashboard toolbar

### Analytics Page
- Show comparative heatmaps (week-over-week, year-over-year)
- Filter by conflict type, armed group, etc.

### Report Generation
- Export heatmap as PNG for reports
- Include intensity statistics in summaries

## Database Requirements

### Required Columns
- `conflicts.latitude` - Float
- `conflicts.longitude` - Float
- `conflicts.fatalities` - Integer (nullable)
- `conflicts.date_occurred` / `conflicts.event_date` - Timestamp
- `conflicts.coordinates` - PostGIS POINT (optional, for spatial queries)

### Recommended Indexes
```sql
-- Speed up heatmap queries
CREATE INDEX idx_conflicts_date_coords 
  ON conflicts(date_occurred, latitude, longitude);

-- For spatial queries (if using PostGIS)
CREATE INDEX idx_conflicts_coords_gist 
  ON conflicts USING GIST(coordinates);
```

## Troubleshooting

### Issue: Heatmap doesn't appear
- **Check:** Backend returning valid data: `curl http://localhost:8000/api/v1/conflicts/heatmap/data`
- **Check:** Leaflet.heat library loaded: Browser DevTools → Network tab
- **Check:** No TypeScript errors in console

### Issue: Colors not showing correctly
- **Check:** Gradient values are valid hex colors
- **Check:** Max value set correctly (should be ≥ highest intensity)
- **Check:** Browser supports WebGL (required by some gradient implementations)

### Issue: Export creates empty file
- **Check:** API endpoint returns `points` array with data
- **Check:** Browser allows blob downloads
- **Check:** Disk space available

### Issue: Performance degradation with many points
- **Solution:** Implement server-side aggregation (see Optimizations)
- **Solution:** Reduce `days_back` parameter to show fewer incidents
- **Solution:** Implement data sampling (show every Nth point)

## Future Enhancements

1. **Interactive Heatmap:**
   - Click on region to zoom and drill-down
   - Hover to show incident details
   - Time-slider for temporal analysis

2. **Advanced Analytics:**
   - Trend detection (increasing/decreasing intensity)
   - Anomaly detection (unusual hotspots)
   - Predictive heatmap (forecasted future incidents)

3. **Comparison Heatmaps:**
   - Side-by-side comparison of different time periods
   - Heat map difference (this month vs last month)

4. **Export Formats:**
   - PNG/SVG image export with legend
   - PDF report generation
   - KML for Google Earth

5. **Real-Time Updates:**
   - WebSocket connection for live updates
   - Animated transitions when data changes
   - Notification when new hotspots emerge

## Related Documentation

- [MAP_IMPLEMENTATION_SUMMARY.md](MAP_IMPLEMENTATION_SUMMARY.md) - General map setup
- [INTERACTIVE_MAP_GUIDE.md](INTERACTIVE_MAP_GUIDE.md) - Interactive features
- [GEOSPATIAL_AGENT documentation](AGENTS.md#2-geospatial_agent) - Spatial analysis tasks
