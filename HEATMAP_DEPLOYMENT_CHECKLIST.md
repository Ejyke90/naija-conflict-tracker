# Heatmap Implementation Checklist

## ✅ Implementation Complete

### Frontend
- [x] Enhanced AdvancedConflictMap component with heatmap functionality
- [x] Toggle button for heatmap visibility
- [x] Loading state indicators
- [x] Error handling and user feedback
- [x] Color legend for intensity scale
- [x] Export to GeoJSON functionality
- [x] TypeScript type definitions for leaflet.heat
- [x] Responsive design for different screen sizes
- [x] Accessibility features (button titles, aria labels)

### Backend
- [x] Heatmap data endpoint in `/conflicts/heatmap/data`
- [x] Advanced heatmap endpoint in `/spatial/heatmap/data`
- [x] Intensity calculation based on fatalities
- [x] Proper error handling and status codes
- [x] Support for configurable time window (days_back parameter)

### Testing
- [x] Backend integration test script
- [x] Frontend unit tests
- [x] Manual testing procedures documented
- [x] Test cases for all major features

### Documentation
- [x] Detailed implementation guide
- [x] Integration guide with quick start
- [x] Troubleshooting guide
- [x] API endpoint documentation
- [x] Performance optimization tips
- [x] Code examples and usage patterns

---

## 🚀 Deployment Checklist

### Prerequisites
- [ ] PostgreSQL database has conflict data with valid coordinates
- [ ] Backend has all dependencies installed
- [ ] Frontend has leaflet and leaflet.heat installed
- [ ] Environment variables configured

### Deployment Steps

#### Backend
1. [ ] Run database migrations if needed
   ```bash
   cd backend
   alembic upgrade head
   ```

2. [ ] Verify database has spatial data
   ```bash
   # Check for conflicts with coordinates
   psql -c "SELECT COUNT(*) FROM conflicts WHERE latitude IS NOT NULL AND longitude IS NOT NULL"
   ```

3. [ ] Start backend server
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

4. [ ] Test heatmap endpoint
   ```bash
   curl http://localhost:8000/api/v1/conflicts/heatmap/data
   ```

#### Frontend
1. [ ] Install dependencies
   ```bash
   cd frontend
   npm install
   ```

2. [ ] Build frontend
   ```bash
   npm run build
   ```

3. [ ] Start frontend
   ```bash
   npm run dev
   ```

4. [ ] Test heatmap in browser
   - Navigate to map component
   - Click "🔥 Heatmap" button
   - Verify visualization appears

### Production Deployment

#### Environment Variables (Backend)
```
DATABASE_URL=postgresql://user:pass@host/db
API_V1_STR=/api/v1
CORS_ORIGINS=["https://yourdomain.com"]
```

#### Environment Variables (Frontend)
```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

#### Database Optimization
```sql
-- Create indexes for faster queries
CREATE INDEX idx_conflicts_date_coords 
  ON conflicts(date_occurred DESC, latitude, longitude);

CREATE INDEX idx_conflicts_coords_gist 
  ON conflicts USING GIST(coordinates);

-- Analyze to update statistics
ANALYZE conflicts;
```

#### CDN Setup (Optional)
- [ ] Configure CDN for static assets
- [ ] Enable gzip compression
- [ ] Cache API responses (configurable, default: 5 minutes)

---

## 📊 Verification Steps

After deployment, verify:

### Backend Verification
- [ ] Heatmap endpoint returns valid data
  ```bash
  curl http://localhost:8000/api/v1/conflicts/heatmap/data?days_back=30 | jq .
  ```

- [ ] Response contains required fields:
  - [ ] `points` array with [lat, lng, intensity] format
  - [ ] `bounds` object with Nigeria coordinates
  - [ ] No null intensities

- [ ] Performance is acceptable (< 1s response time)

### Frontend Verification
- [ ] Heatmap button is visible and clickable
- [ ] Clicking button fetches data without errors
- [ ] Leaflet.heat layer renders correctly
- [ ] Color gradient displays properly
- [ ] Legend shows intensity scale
- [ ] Export button creates valid GeoJSON file
- [ ] Zoom/pan functionality works with heatmap
- [ ] Responsive on mobile devices

### Integration Testing
- [ ] Run backend test suite
  ```bash
  cd backend
  python test_heatmap_integration.py
  ```

- [ ] Run frontend tests
  ```bash
  cd frontend
  npm test -- __tests__/AdvancedConflictMap.test.tsx
  ```

---

## 🔧 Configuration Options

### Backend
In `backend/app/config/settings.py`:
```python
# Heatmap settings
HEATMAP_DEFAULT_DAYS = 30
HEATMAP_MAX_INTENSITY = 10
HEATMAP_DEFAULT_RADIUS = 50
```

### Frontend
In `frontend/components/mapping/AdvancedConflictMap.tsx`:
```typescript
// Adjust these values to customize visualization
const heat = L.heatLayer(data.points, {
  max: 10,           // Change max intensity
  maxZoom: 18,       // Change max zoom
  radius: 50,        // Change point radius
  blur: 30,          // Change blur amount
  gradient: {...}    // Change color gradient
});
```

---

## 📈 Performance Metrics

### Target Metrics
- API response time: < 1 second
- Heatmap render time: < 2 seconds
- Export file size: < 500 KB
- Browser memory usage: < 100 MB

### Monitoring
Setup monitoring in production:
```bash
# Monitor API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/conflicts/heatmap/data

# Monitor database query times
EXPLAIN ANALYZE SELECT * FROM conflicts WHERE date_occurred >= NOW() - INTERVAL '30 days';
```

---

## 🐛 Common Issues & Solutions

### Issue: Heatmap doesn't appear
**Solution:** 
1. Check backend is returning data: `curl http://localhost:8000/api/v1/conflicts/heatmap/data`
2. Check browser console for errors
3. Verify leaflet.heat library is loaded
4. Check if database has conflicts with coordinates

### Issue: Slow performance with many points
**Solution:**
1. Reduce `days_back` parameter
2. Implement server-side aggregation by zoom level
3. Add database indexes (see Database Optimization)
4. Enable response caching

### Issue: Export creates empty file
**Solution:**
1. Check if API returns data
2. Verify browser allows blob downloads
3. Check disk space and permissions

---

## 📝 Rollback Plan

If issues occur:

1. **Quick Rollback:**
   ```bash
   # Revert to previous component
   git checkout HEAD^ -- frontend/components/mapping/AdvancedConflictMap.tsx
   npm run build
   ```

2. **Database Rollback:**
   ```bash
   # Restore from backup if data issues
   pg_restore -d naija_conflict backup.dump
   ```

3. **API Fallback:**
   - Keep old `/conflicts/heatmap/data` endpoint active
   - Frontend can fallback to simpler visualization

---

## 📚 Related Documentation

- [HEATMAP_IMPLEMENTATION.md](HEATMAP_IMPLEMENTATION.md) - Detailed implementation
- [LEAFLET_HEATMAP_INTEGRATION.md](LEAFLET_HEATMAP_INTEGRATION.md) - Integration guide
- [MAP_IMPLEMENTATION_SUMMARY.md](MAP_IMPLEMENTATION_SUMMARY.md) - General map setup
- [AGENTS.md#2-geospatial_agent](AGENTS.md#2-geospatial_agent) - Spatial analysis tasks

---

## ✨ Next Steps

After successful deployment:

1. [ ] Monitor performance in production
2. [ ] Gather user feedback
3. [ ] Implement performance optimizations if needed
4. [ ] Add real-time updates via WebSocket
5. [ ] Implement advanced filtering options
6. [ ] Add drill-down functionality
7. [ ] Create comparison mode (week-over-week, YoY)

---

**Last Updated:** 2024-01-15
**Version:** 1.0
**Status:** ✅ Ready for Production
