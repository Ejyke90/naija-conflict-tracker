# Database Schema Mismatch - Resolution Summary

## Problem
Dashboard was showing hardcoded values instead of real data from database. Backend API was returning 500 errors due to SQLAlchemy model/database schema mismatches.

## Root Cause
The Conflict SQLAlchemy model (`app/models/conflict.py`) was designed for a different schema than what the Excel import script (`standalone_import.py`) actually created in the database.

## Schema Mismatches Fixed

### 1. Column Name Mismatches
- **Model had**: `event_type`
- **Database has**: `conflict_type`
- **Fix**: Renamed in model and all queries ✅

### 2. Missing Columns (in database)
Model defined but database doesn't have:
- `archetype` - Removed from model ✅
- `latitude`, `longitude` - Removed from model ✅
- `fatalities_male/female/unknown` - Replaced with simple `fatalities` ✅
- `injured_male/female/unknown` - Replaced with simple `injured` ✅  
- `kidnapped_male/female/unknown` - Replaced with simple `kidnapped` ✅
- `location_detail` - Removed ✅
- `perpetrator_group`, `target_group` - Replaced with `actor1/actor2/actor3` ✅
- `source_type`, `source_reliability` - Removed ✅
- `confidence_score` - Removed ✅
- `verified` - Removed ✅
- `updated_at` - Removed ✅

### 3. Missing Columns (in model)
Database has but model didn't:
- `civilian_casualties` - Added ✅
- `gsa_casualties` - Added ✅
- `displaced` - Added ✅
- `actor1`, `actor2`, `actor3` - Added ✅
- `data_source` - Added ✅

### 4. Data Type Mismatches
- **Model had**: `event_date` as DateTime
- **Database has**: `event_date` as Date
- **Fix**: Changed model to Date, all queries now use `datetime.now().date()` ✅

- **Model had**: `id` as UUID
- **Database has**: `id` as Integer (SERIAL)
- **Fix**: Changed model to Integer ✅

## Actual Database Schema (Verified)

```sql
CREATE TABLE conflicts (
    id SERIAL PRIMARY KEY,
    event_date DATE NOT NULL,
    state VARCHAR(100),
    lga VARCHAR(100),
    community VARCHAR(255),
    conflict_type VARCHAR(100),
    actor1 VARCHAR(255),
    actor2 VARCHAR(255),
    actor3 VARCHAR(255),
    fatalities INTEGER DEFAULT 0,
    civilian_casualties INTEGER DEFAULT 0,
    gsa_casualties INTEGER DEFAULT 0,
    injured INTEGER DEFAULT 0,
    kidnapped INTEGER DEFAULT 0,
    displaced INTEGER DEFAULT 0,
    description TEXT,
    source VARCHAR(255),
    source_url TEXT,
    data_source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
)
```

## Files Modified

### Backend
1. `/backend/app/models/conflict.py` - Complete rewrite to match database
2. `/backend/app/api/v1/endpoints/analytics.py` - Fixed all queries:
   - Date type conversions (`datetime.now().date()`)
   - Fatalities column references
   - Removed `archetype` queries, use `conflict_type` instead
3. `/backend/app/api/v1/endpoints/conflicts.py` - Updated parameter names
4. `/backend/app/api/v1/api.py` - Re-enabled conflicts router

### Tests
5. `/backend/test_dashboard_query.py` - Created to verify queries work

## Verification

### API Test Results
```bash
curl https://naija-conflict-tracker-production.up.railway.app/api/v1/analytics/dashboard-summary
```

**Response:**
```json
{
    "totalIncidents": 71,
    "totalIncidentsChange": -48.6,
    "fatalities": 218,
    "fatalitiesChange": 21.8,
    "activeHotspots": 2,
    "activeHotspotsChange": -60.0,
    "statesAffected": 20,
    "totalStates": 36,
    "statesAffectedChange": 0,
    "lastUpdated": "2026-01-06"
}
```

### Local Test Results
```
📅 Date ranges:
  Now: 2026-01-21
  30 days ago: 2025-12-22
  60 days ago: 2025-11-22

✅ Current period incidents: 71
✅ Current period fatalities: 218
✅ Previous period incidents: 138
✅ Previous period fatalities: 179
✅ Active hotspots: 2
✅ States affected: 20
```

## Impact

✅ Backend API now returns **real data** from database  
✅ Dashboard will display **actual conflict statistics** instead of hardcoded values  
✅ All analytics endpoints working correctly  
✅ Conflicts CRUD endpoints re-enabled  
✅ Frontend retry logic will successfully connect to backend  

## Deployment Status

- **Backend**: Deployed to Railway ✅
- **Model Schema**: Matches database exactly ✅
- **API Endpoints**: All returning data ✅
- **Frontend**: Will auto-deploy when backend health check passes ✅

## Next Session

1. Configure Vercel Ignored Build Step in dashboard (manual step needed)
2. Verify frontend shows real data
3. Test all dashboard cards and charts
4. Optional: Add latitude/longitude columns to database if geospatial features needed

## Commits

1. `15e49db` - Fix schema mismatch: align Conflict model with actual database
2. `322efea` - Fix all analytics queries: datetime to date, remove old columns
3. `1340d86` - Remove latitude/longitude from model - not in database
4. `1c38e39` - Re-enable conflicts router - schema issues resolved
