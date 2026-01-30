# Leaflet Heatmap - Quick Reference

## 🎯 What It Does
Displays conflict intensity across Nigeria as a heat map with green (low) to red (high) color gradient.

## 🚀 Quick Start

### Enable in Your Project
```bash
# Already installed, just use it
npm list leaflet.heat
```

### Use in Component
```typescript
import AdvancedConflictMap from '@/components/mapping/AdvancedConflictMap';

export default function Page() {
  return <AdvancedConflictMap />;
}
```

### That's it!
The component handles all heatmap functionality.

---

## 🎮 User Controls

| Button | Action | Result |
|--------|--------|--------|
| 🔥 Heatmap | Toggle | Show/hide heatmap layer |
| ⬇ Export | Click | Download data as GeoJSON |
| Spatial Analysis | Click | View detailed spatial stats |

---

## 📊 API Endpoints

### Get Heatmap Data
```bash
GET /api/v1/conflicts/heatmap/data?days_back=30
```

**Response:**
```json
{
  "points": [[lat, lng, intensity], ...],
  "bounds": {"north": 13.8, "south": 2.7, "east": 14.68, "west": 2.67}
}
```

### Advanced Data with Details
```bash
GET /api/v1/spatial/heatmap/data?days_back=30
```

**Response:**
```json
{
  "total_locations": 45,
  "points": [[lat, lng, intensity], ...],
  "details": [{location, state, incident_count, fatalities, intensity}, ...]
}
```

---

## 🎨 Color Scale

```
Green    Yellow    Orange    Red
  ├─────┼─────┼─────┼─────┤
  0      3      6      9     10
  Low            Medium       High
```

**Meanings:**
- 🟩 Green (0-3): Low conflict activity
- 🟨 Yellow (3-6): Moderate activity
- 🟧 Orange (6-9): High activity
- 🟥 Red (9-10): Very high intensity

---

## 🔍 How Intensity is Calculated

### Simple Formula (conflicts endpoint)
```
intensity = 1 + (fatalities / max_fatalities) * 9
```

### Advanced Formula (spatial endpoint)
```
intensity = log(fatalities + 1) * sqrt(incident_count) / 2
```

---

## 🧪 Testing

### Backend Test
```bash
cd backend
python test_heatmap_integration.py
```

### Frontend Test
```bash
cd frontend
npm test -- __tests__/AdvancedConflictMap.test.tsx
```

### Manual Test
1. Start backend: `python -m uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Navigate to map component
4. Click "🔥 Heatmap" button
5. Verify heatmap appears with colors

---

## ⚙️ Configuration

### Change Colors (in AdvancedConflictMap.tsx)
```typescript
gradient: {
  0.0: '#006837',    // Dark green
  0.25: '#1a9850',   // Light green
  0.5: '#91cf60',    // Yellow
  0.75: '#d9ef8b',   // Light yellow
  1.0: '#ff0000'     // Red
}
```

### Change Settings
```typescript
const heat = L.heatLayer(data.points, {
  max: 10,       // Max intensity value
  radius: 50,    // Point radius in pixels
  blur: 30,      // Blur amount
  maxZoom: 18    // Max zoom level
});
```

---

## 🐛 Quick Fixes

### Heatmap not showing?
1. Check API returns data:
   ```bash
   curl http://localhost:8000/api/v1/conflicts/heatmap/data
   ```
2. Check browser console for errors
3. Verify leaflet.heat is in node_modules

### Colors wrong?
1. Check gradient values are valid hex colors
2. Verify `max` value is correct
3. Try browser DevTools → Reload

### Export not working?
1. Check if API returns data
2. Check browser console errors
3. Verify browser allows downloads

---

## 📈 Performance Tips

### For Many Points (1000+)
1. Reduce `days_back` parameter
2. Increase `radius` to combine nearby points
3. Add database index:
   ```sql
   CREATE INDEX idx_conflicts_date_coords 
   ON conflicts(date_occurred DESC, latitude, longitude);
   ```

### For Slow API
1. Add response caching (5 min default)
2. Reduce `days_back` for initial load
3. Implement server-side aggregation

---

## 📂 Files to Know

```
frontend/
├── components/mapping/AdvancedConflictMap.tsx    ← Main component
├── types/leaflet-heat.d.ts                       ← Type defs
└── __tests__/AdvancedConflictMap.test.tsx        ← Tests

backend/
├── app/api/v1/endpoints/conflicts.py             ← API endpoint
├── app/api/v1/endpoints/spatial.py               ← Advanced endpoint
└── test_heatmap_integration.py                   ← Backend tests

Documentation/
├── LEAFLET_HEATMAP_SUMMARY.md                   ← This summary
├── HEATMAP_IMPLEMENTATION.md                     ← Detailed guide
├── LEAFLET_HEATMAP_INTEGRATION.md                ← Integration guide
└── HEATMAP_DEPLOYMENT_CHECKLIST.md               ← Deploy checklist
```

---

## 🔗 Useful Links

- [Leaflet Docs](https://leafletjs.com/)
- [Leaflet.heat GitHub](https://github.com/Leaflet/Leaflet.heat)
- [React-Leaflet Docs](https://react-leaflet.js.org/)
- Project AGENTS.md #2-GEOSPATIAL_AGENT

---

## 💡 Common Tasks

### Show heatmap for last 7 days
Frontend: Not yet configurable (use API directly)
```bash
curl "http://localhost:8000/api/v1/conflicts/heatmap/data?days_back=7"
```

### Get intensity for specific location
Use spatial endpoint:
```bash
curl http://localhost:8000/api/v1/spatial/heatmap/data | jq '.details[] | select(.location == "Maiduguri")'
```

### Export as different format
Convert GeoJSON to KML:
```bash
# Use online converters or GDAL
ogr2ogr -f KML output.kml input.geojson
```

### Change default timeframe
Edit in AdvancedConflictMap.tsx:
```typescript
const response = await fetch(`/api/v1/conflicts/heatmap/data?days_back=60`);
```

---

## ⚠️ Common Mistakes

❌ **Don't:**
- Call heatmap endpoint too frequently (cache for 5 min)
- Send requests for huge date ranges (1000+ points)
- Ignore error responses from API
- Modify leaflet.heat directly (use config)

✅ **Do:**
- Use configurable `days_back` parameter
- Implement caching in frontend
- Handle errors gracefully
- Use provided configuration options

---

## 🚀 Next Steps

1. **Deploy:** Follow HEATMAP_DEPLOYMENT_CHECKLIST.md
2. **Monitor:** Check performance metrics
3. **Enhance:** Implement real-time updates
4. **Optimize:** Add caching and compression
5. **Extend:** Add filtering and drill-down

---

## 📞 Quick Help

| Question | Answer |
|----------|--------|
| Where's the heatmap button? | On AdvancedConflictMap component |
| How do I customize colors? | Edit gradient in component |
| What data does it need? | Conflicts with latitude/longitude |
| How long to load? | Usually < 2 seconds |
| Mobile friendly? | Yes, responsive design |
| Can I use offline? | No, requires API |

---

**Last Updated:** 2024-01-15  
**Version:** 1.0  
**Status:** ✅ Production Ready
