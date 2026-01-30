# Leaflet Heatmap Integration Guide

## Quick Start

### What Was Implemented

A fully functional Leaflet-based heatmap visualization for the Naija Conflict Tracker that shows conflict intensity across Nigeria.

### Components Modified

1. **Frontend:** `frontend/components/mapping/AdvancedConflictMap.tsx`
   - Added heatmap toggle functionality
   - Real-time data loading from backend API
   - Color gradient visualization
   - GeoJSON export capability
   - Loading states and error handling

2. **Backend API:** `backend/app/api/v1/endpoints/spatial.py` (new endpoint)
   - Added `/spatial/heatmap/data` endpoint with advanced intensity calculation
   
3. **Existing Backend:** `backend/app/api/v1/endpoints/conflicts.py`
   - Uses existing `/conflicts/heatmap/data` endpoint

## How to Use

### For Developers

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   # leaflet.heat should already be in package.json
   ```

2. **Start backend (if not running):**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

3. **Start frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

4. **Navigate to map component:**
   - Go to dashboard or any page with AdvancedConflictMap
   - Look for "Advanced Conflict Map" card

5. **Use heatmap:**
   - Click "🔥 Heatmap" button to toggle
   - Click "⬇ Export" to download as GeoJSON
   - Zoom/pan map as normal

### For End Users

1. **Enable Heatmap:**
   - Click red "🔥 Heatmap" button
   - Red and orange areas show conflict hotspots
   - Green areas show low conflict activity

2. **Understand Colors:**
   - 🟩 Green = Low conflict activity
   - 🟨 Yellow = Medium activity
   - 🟧 Orange = High activity
   - 🟥 Red = Very high conflict intensity

3. **Export Data:**
   - Click "⬇ Export" button
   - Saves as `conflict-heatmap-YYYY-MM-DD.geojson`
   - Open in GIS software or mapping applications

## API Endpoints

### Option 1: Conflicts Endpoint (Recommended)

```
GET /api/v1/conflicts/heatmap/data?days_back=30
```

**Response:**
```json
{
  "points": [
    [9.0765, 8.6753, 5.2],
    [9.0820, 8.6800, 7.5],
    [10.1234, 7.8901, 3.1]
  ],
  "bounds": {
    "north": 13.8,
    "south": 2.7,
    "east": 14.68,
    "west": 2.67
  }
}
```

### Option 2: Spatial Endpoint (Advanced)

```
GET /api/v1/spatial/heatmap/data?days_back=30
```

**Response (more detailed):**
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
    }
  ]
}
```

## Testing

### Automated Tests

```bash
# Backend tests
cd backend
python test_heatmap_integration.py

# Frontend tests
cd frontend
npm test -- __tests__/AdvancedConflictMap.test.tsx
```

### Manual Testing Checklist

- [ ] Heatmap button is visible and clickable
- [ ] Loading spinner appears when toggling heatmap
- [ ] Heatmap layer appears with color gradient
- [ ] Legend shows intensity scale
- [ ] Can zoom in/out while heatmap is active
- [ ] Can pan map while heatmap is active
- [ ] Toggling off removes heatmap layer
- [ ] Export button creates valid GeoJSON file
- [ ] Error messages display if API fails
- [ ] Component doesn't break on empty data

## Architecture

```
Frontend (Next.js + React)
    ↓
AdvancedConflictMap Component
    ├─ Leaflet.heat Layer
    ├─ Toggle State Management
    └─ API Integration
         ↓
Backend (FastAPI)
    ├─ /api/v1/conflicts/heatmap/data
    └─ /api/v1/spatial/heatmap/data
         ↓
Database (PostgreSQL)
    └─ Conflicts table with coordinates
```

## Intensity Calculation

### Conflicts Endpoint (Simple)
```
intensity = 1 + (fatalities / max_fatalities) * 9
Range: 1-10
```

### Spatial Endpoint (Advanced)
```
intensity = log(fatalities + 1) * sqrt(incident_count) / 2
Range: 0-10 (capped)
```

## Leaflet.heat Configuration

```typescript
L.heatLayer(points, {
  max: 10,              // Maximum intensity value
  maxZoom: 18,          // Zoom level to stop dissolving
  radius: 50,           // Pixel radius of each point
  blur: 30,             // Blur amount for smoothing
  gradient: {           // Color interpolation
    0.0: '#006837',     // Dark green
    0.25: '#1a9850',    // Light green
    0.5: '#91cf60',     // Yellow-green
    0.75: '#d9ef8b',    // Light yellow
    1.0: '#ff0000'      // Red
  }
})
```

## Performance Optimization Tips

### Database
```sql
-- Add index to speed up queries
CREATE INDEX idx_conflicts_date_coords 
  ON conflicts(date_occurred DESC, latitude, longitude);

-- For PostGIS spatial queries
CREATE INDEX idx_conflicts_coords_gist 
  ON conflicts USING GIST(coordinates);
```

### Frontend
1. **Cache data:**
   ```typescript
   const [cachedData, setCachedData] = useState(null);
   const [cacheTime, setCacheTime] = useState(0);
   
   if (Date.now() - cacheTime < 300000) { // 5 min cache
     return cachedData;
   }
   ```

2. **Debounce zoom/pan:**
   ```typescript
   const debouncedRefresh = debounce(() => loadHeatmapData(), 500);
   map.on('moveend', debouncedRefresh);
   ```

3. **Server-side aggregation:**
   - Aggregate incidents by zoom level
   - Reduce network payload

## Troubleshooting

### Heatmap not showing
1. Check browser console for errors
2. Verify API endpoint: `curl http://localhost:8000/api/v1/conflicts/heatmap/data`
3. Ensure database has conflict data with valid coordinates
4. Check if `leaflet.heat` library loaded correctly

### Colors incorrect
1. Check gradient values (must be valid hex colors)
2. Verify `max` parameter matches intensity range
3. Verify browser supports WebGL (check DevTools)

### Export creates empty file
1. Check if API returns data: `fetch('/api/v1/conflicts/heatmap/data')`
2. Verify browser allows blob downloads
3. Check disk space

### Performance issues with many points
1. Reduce `days_back` parameter
2. Implement server-side aggregation
3. Consider WebWorker for data processing
4. Enable browser caching

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- IE 11: ⚠️ Requires Leaflet 1.7 or newer

## Files Modified/Created

### Frontend
- `frontend/components/mapping/AdvancedConflictMap.tsx` - Main component
- `frontend/types/leaflet-heat.d.ts` - TypeScript type definitions
- `frontend/__tests__/AdvancedConflictMap.test.tsx` - Unit tests

### Backend
- `backend/app/api/v1/endpoints/spatial.py` - New heatmap endpoint
- `backend/test_heatmap_integration.py` - Integration tests

### Documentation
- `HEATMAP_IMPLEMENTATION.md` - Detailed implementation guide
- `LEAFLET_HEATMAP_INTEGRATION.md` - This file

## Future Enhancements

1. **Real-time updates via WebSocket**
   - Live heatmap updates as new incidents occur
   - Animated transitions

2. **Time-slider**
   - Animate heatmap over time period
   - Show conflict trends

3. **Interactive details**
   - Click on hotspot to see incident list
   - Drill-down by state/LGA/ward

4. **Advanced filtering**
   - Filter by conflict type
   - Filter by armed groups
   - Custom date ranges

5. **Comparison mode**
   - Side-by-side heatmaps
   - Heat difference (this month vs last month)

6. **Export formats**
   - PNG/SVG image export
   - KML for Google Earth
   - PDF report generation

## References

- [Leaflet Documentation](https://leafletjs.com/)
- [Leaflet.heat GitHub](https://github.com/Leaflet/Leaflet.heat)
- [React-Leaflet Documentation](https://react-leaflet.js.org/)
- [PostGIS Documentation](https://postgis.net/)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `HEATMAP_IMPLEMENTATION.md` for detailed info
3. Check backend/test_heatmap_integration.py for example usage
4. Review frontend/__tests__/AdvancedConflictMap.test.tsx for component testing
