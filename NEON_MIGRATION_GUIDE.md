# Neon PostgreSQL Migration Guide

## ⚠️ Important: Database Location

**The database connection should ONLY be set on the Railway backend, NOT on Vercel frontend.**

- ✅ Railway backend → Needs DATABASE_URL
- ❌ Vercel frontend → Does NOT need database credentials

## When to Use Neon

Consider Neon if you need:
- Database branching (like git branches for your database)
- Cost optimization (auto-suspend when idle)
- Better development workflow (instant test databases)
- Planning to move backend to serverless

## Migration Steps

### Step 1: Create Neon Database

1. Go to [Neon Console](https://console.neon.tech)
2. Create a new project
3. Copy the **connection string** (should look like):
   ```
   postgres://username:password@ep-xyz-123.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. Also copy the **pooled connection string** for production:
   ```
   postgres://username:password@ep-xyz-123-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### Step 2: Export Data from Railway

```bash
# SSH into Railway or use Railway CLI
railway run bash

# Export your database
pg_dump $DATABASE_URL > backup.sql

# Or export schema and data separately
pg_dump --schema-only $DATABASE_URL > schema.sql
pg_dump --data-only $DATABASE_URL > data.sql
```

### Step 3: Import Data to Neon

```bash
# Using Neon connection string
psql "postgres://username:password@ep-xyz-123.us-east-2.aws.neon.tech/neondb?sslmode=require" < backup.sql

# Or import schema first, then data
psql "NEON_CONNECTION_STRING" < schema.sql
psql "NEON_CONNECTION_STRING" < data.sql
```

### Step 4: Update Railway Backend Environment Variables

1. Go to Railway project settings
2. Update the `DATABASE_URL` environment variable to your **Neon pooled connection string**:
   ```
   postgres://username:password@ep-xyz-123-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
3. **Important:** Use the pooled connection string for better performance
4. Redeploy the Railway backend

### Step 5: Update SQLAlchemy Configuration (If Needed)

The backend config already supports any PostgreSQL connection:

```python
# backend/app/core/config.py
DATABASE_URL: str = (
    os.getenv("DATABASE_URL")
    or os.getenv("RAILWAY_DATABASE_URL")
    or os.getenv("POSTGRES_URL")
    or os.getenv("POSTGRESQL_URL")
    or "postgresql://postgres:password@localhost:5432/conflict_tracker"
)
```

For Neon with connection pooling, you may want to adjust pool settings:

```python
# backend/app/db/database.py
from sqlalchemy import create_engine

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,         # Smaller pool for serverless
    max_overflow=10,     # Max connections
    pool_recycle=300,    # Recycle connections after 5 minutes (Neon closes idle after 5 min)
)
```

### Step 6: Verify Migration

1. Check Railway backend logs for successful database connection
2. Test API endpoints:
   - `GET /health` - should show database: connected
   - `GET /api/v1/conflicts` - should return data
3. Verify data integrity:
   ```sql
   SELECT COUNT(*) FROM conflicts;
   SELECT COUNT(*) FROM users;
   SELECT COUNT(*) FROM alert_events;
   ```

## Performance Optimization with Neon

### 1. Use Pooled Connection String
Always use the pooled connection string in production:
```
postgres://user:pass@ep-xxx-pooler.region.aws.neon.tech/db
```

### 2. Adjust Pool Settings for Neon
```python
# Recommended settings for Neon
pool_size=5          # Smaller pool (Neon handles pooling)
max_overflow=10      # Allow bursts
pool_recycle=300     # Recycle before Neon closes (5 min)
pool_pre_ping=True   # Verify connections
```

### 3. Handle Cold Starts
Neon auto-suspends after 5 minutes of inactivity. First query after suspend takes ~1-2 seconds.

```python
# Add retry logic for cold starts
from sqlalchemy.exc import OperationalError
import time

def execute_with_retry(query, retries=3):
    for attempt in range(retries):
        try:
            return db.execute(query)
        except OperationalError as e:
            if "connection" in str(e).lower() and attempt < retries - 1:
                time.sleep(1)  # Wait for Neon to wake up
                continue
            raise
```

### 4. Database Branching for Development
Create development branches:
```bash
# Create a branch from main database
neon branches create --name dev

# Get branch connection string
neon connection-string dev
```

Update `.env.local` to use dev branch during development.

## Rollback Plan

If migration fails, quickly rollback:

1. Change `DATABASE_URL` on Railway back to Railway PostgreSQL
2. Redeploy Railway backend
3. Verify application works

## Cost Comparison

### Railway PostgreSQL
- Fixed monthly cost (~$5-20 depending on plan)
- Always running
- Simple, predictable billing

### Neon
- Free tier: 0.5 GB storage, 1 compute hour/day
- Pro: Pay per usage (compute + storage)
- Auto-suspend saves costs
- Can be cheaper for low-traffic apps

## Recommendations

**Use Railway PostgreSQL if:**
- You have consistent, predictable traffic
- Your app is always active
- You prefer simple, fixed pricing
- You don't need database branching

**Use Neon if:**
- You want database branching for dev/staging
- Your app has variable traffic (Neon scales automatically)
- You want cost optimization (autosuspend)
- You're planning serverless architecture
- You need instant database copies for testing

## Next Steps

1. ❌ **Remove Neon from Vercel** (frontend doesn't need it)
2. ✅ **Keep Railway PostgreSQL** for now (it's working well)
3. 📊 **Monitor performance** and traffic patterns
4. 🔄 **Consider Neon migration** only if you need its specific features

The current setup (Railway backend + Railway PostgreSQL) is solid and performant. Don't migrate unless you have a specific reason to do so.
