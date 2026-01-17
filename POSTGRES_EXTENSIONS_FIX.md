# 🔧 PostgreSQL Extensions Fix for Railway

## The Problem
Railway PostgreSQL doesn't recognize "timescaledb" and "postgis" as extension names in the UI.

## The Solution

### Option 1: Use Template Names (Recommended)

When creating PostgreSQL service in Railway:

1. **Click "New Service" → PostgreSQL**
2. **For extensions, use these names**:
   - `postgis` (this should work)
   - For TimescaleDB: You may need to skip it initially and add later

### Option 2: Add Extensions via SQL (Most Reliable)

1. **Create PostgreSQL service first** (without extensions)
2. **Go to your service → "Query" tab**
3. **Run these SQL commands**:

```sql
-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Enable TimescaleDB (if supported)
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

### Option 3: Use Railway Environment Variables

In your Railway service settings → Variables, add:

```bash
# These will be set automatically by Railway
DATABASE_URL=${{RAILWAY_DATABASE_URL}}
POSTGRES_EXTENSIONS=postgis,timescaledb
```

## What Actually Works

Based on Railway's current setup:

1. **PostGIS**: ✅ Usually works with `postgis`
2. **TimescaleDB**: ⚠️ May not be available on Railway's standard PostgreSQL
3. **Alternative**: Use regular PostgreSQL with time-series queries

## Updated Deployment Steps

### Step 1: Create PostgreSQL Service
1. Click "New Service" → PostgreSQL
2. **Extensions**: Add `postgis` only (skip timescaledb for now)
3. Deploy database

### Step 2: Verify Extensions
1. Go to PostgreSQL service → "Query" tab
2. Run: `SELECT * FROM pg_extension;`
3. Confirm `postgis` is installed

### Step 3: Deploy Backend
1. Configure backend service with `./backend` as root
2. Deploy! The database schema will work with PostGIS

## If TimescaleDB is Critical

If you specifically need TimescaleDB:
1. Consider using a different PostgreSQL provider
2. Or use regular PostgreSQL with time-series functions
3. The conflict tracking works fine without TimescaleDB

## Verification

After setup, test with:
```bash
curl https://your-app.railway.app/health
```

Should return: `{"status": "healthy", "database": "connected"}`

---

**💡 Pro Tip**: Start with just PostGIS. The core conflict tracking functionality works perfectly without TimescaleDB. You can add TimescaleDB later if needed for advanced time-series analytics.**
