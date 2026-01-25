# Supabase Setup Guide for Nextier Conflict Tracker

## Prerequisites
1. Supabase account (create at https://supabase.com)
2. Existing data in Railway PostgreSQL (to migrate)

## Step 1: Create Supabase Project

1. Go to https://app.supabase.com
2. Click "New Project"
3. Fill in details:
   - **Name**: `naija-conflict-tracker`
   - **Database Password**: (generate strong password)
   - **Region**: Choose closest to Nigeria (e.g., `eu-west-2` London or `ap-south-1` Mumbai)
   - **Pricing Plan**: Free tier for development, Pro for production
4. Click "Create new project"
5. Wait 2-3 minutes for provisioning

## Step 2: Run Schema Migration

1. In Supabase Dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy contents of `migrations/001_initial_schema.sql`
4. Paste and click **RUN**
5. Verify tables created in **Table Editor**

## Step 3: Export Data from Railway

### Option A: Using pg_dump (Recommended)
```bash
# Export from Railway
pg_dump $RAILWAY_DATABASE_URL \
  --table=conflicts \
  --data-only \
  --column-inserts \
  > railway_data.sql

# Transform and import (manual editing may be needed)
```

### Option B: Using Python Script
```bash
cd /Users/ejikeudeze/AI_Projects/naija-conflict-tracker/database
python migrate_railway_to_supabase.py
```

## Step 4: Get Supabase Connection Details

In Supabase Dashboard:
1. Go to **Settings** → **Database**
2. Copy these values:

**Connection String (Session Mode)**:
```
postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-REF].supabase.co:5432/postgres
```

**API URL**:
```
https://[YOUR-REF].supabase.co
```

**Anon/Public Key**:
```
eyJhbGc...
```

**Service Role Key** (keep secret):
```
eyJhbGc...
```

## Step 5: Update Backend Environment Variables

Update `backend/.env.production`:
```bash
# Supabase Database
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres

# Supabase API (optional, for direct client access)
SUPABASE_URL=https://[YOUR-REF].supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...  # Server-side only
```

## Step 6: Update Railway Deployment

```bash
# Set environment variables in Railway dashboard
# Or use Railway CLI:
railway variables set DATABASE_URL="postgresql://postgres:..."
railway variables set SUPABASE_URL="https://..."
railway variables set SUPABASE_ANON_KEY="..."

# Redeploy
railway up
```

## Step 7: Update Frontend Environment Variables

Update `frontend/.env.production`:
```bash
# API URL (Railway backend still used, now connected to Supabase)
NEXT_PUBLIC_API_URL=https://naija-conflict-tracker-production.up.railway.app

# Optional: Direct Supabase client (for real-time features)
NEXT_PUBLIC_SUPABASE_URL=https://[YOUR-REF].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
```

## Step 8: Run Migration Script

```sql
-- In Supabase SQL Editor, run:
-- migrations/002_migrate_old_data.sql
```

## Step 9: Verify Data

```sql
-- Check record count
SELECT COUNT(*) FROM conflict_events;

-- Check recent events
SELECT * FROM conflict_events 
ORDER BY event_date DESC 
LIMIT 10;

-- Check dashboard stats
SELECT * FROM dashboard_statistics
ORDER BY month DESC
LIMIT 12;
```

## Step 10: Enable Real-time (Optional)

In Supabase Dashboard:
1. Go to **Database** → **Replication**
2. Enable replication for `conflict_events` table
3. Select which events to broadcast (INSERT, UPDATE, DELETE)

## Benefits After Migration

✅ **Performance**: 
- Automatic connection pooling
- CDN-cached API responses
- Geographic replication

✅ **Real-time**: 
- Live dashboard updates
- WebSocket subscriptions

✅ **Security**: 
- Row-level security policies
- API key management
- Built-in auth ready

✅ **Scalability**: 
- Automatic backups
- Point-in-time recovery
- Easy scaling

✅ **Developer Experience**: 
- Auto-generated REST API
- Auto-generated GraphQL API
- Database GUI
- SQL Editor

## Rollback Plan

If issues occur:
1. Keep Railway database running
2. Update `DATABASE_URL` back to Railway
3. Redeploy backend
4. No data loss (old DB still intact)

## Cost Estimate

**Free Tier**: 
- 500MB database
- 1GB file storage
- 2GB bandwidth
- Sufficient for MVP

**Pro Tier** ($25/month):
- 8GB database
- 100GB file storage
- 50GB bandwidth
- Suitable for production

## Monitoring

After migration, monitor:
- Query performance in Supabase Dashboard
- API response times
- Error logs
- Database size growth
