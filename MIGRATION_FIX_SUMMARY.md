# Database Migration Fix Summary

## Issue
The API endpoint `/api/v1/locations/states` was returning a 500 error with the message:
```
psycopg2.errors.UndefinedTable: relation "locations" does not exist
```

This occurred because the Alembic migrations had not been properly configured to apply the `locations` table creation to the database.

## Root Causes Identified

### 1. **Missing Model Imports in Alembic** 
The `alembic/env.py` file did not import the `Location` model and other domain models, preventing Alembic from being aware of the table definitions for future migrations and validation.

**File:** `backend/alembic/env.py`  
**Fix:** Added imports for all models:
```python
from app.models.location import Location  # noqa
from app.models.conflict import Conflict  # noqa
from app.models.alert import Alert  # noqa
from app.models.audit import ConflictAudit  # noqa
from app.models.forecast import Forecast  # noqa
```

### 2. **Hardcoded Database URL in Alembic Configuration**
The `alembic.ini` and `alembic/env.py` used hardcoded database credentials that didn't work in containerized environments (Docker, Railway).

**File:** `backend/alembic.ini`  
**Fix:** Updated connection string to use environment variable:
```ini
sqlalchemy.url = driver://user:password@localhost/dbname
```

**File:** `backend/alembic/env.py`  
**Fix:** Updated both `run_migrations_offline()` and `run_migrations_online()` to read from environment:
```python
import os
database_url = os.getenv("DATABASE_URL")
if database_url:
    configuration["sqlalchemy.url"] = database_url
```

### 3. **Migration Chain Branching**
Two migrations (004) were both depending on revision 003, creating a branch:
- `004_add_alert_tables.py` → revision = '004', down_revision = '003'
- `004_add_performance_indexes.py` → revision = '004_performance_indexes', down_revision = '003'

**File:** `backend/alembic/versions/004_add_performance_indexes.py`  
**Fix:** Updated to depend on the alert_tables migration:
```python
revision = '004_performance_indexes'
down_revision = '004'  # Changed from '003'
```

This creates the correct linear sequence:
```
001_auth_tables (003)
    ↓
004_add_alert_tables
    ↓
004_add_performance_indexes
    ↓
005_add_locations_table
```

## Files Modified

1. ✅ `backend/alembic/env.py` - Added model imports and environment variable support
2. ✅ `backend/alembic.ini` - Updated placeholder database URL
3. ✅ `backend/alembic/versions/004_add_performance_indexes.py` - Fixed migration chain

## Next Steps for Deployment

### For Docker Environment:
```bash
# The start.sh already runs this command:
alembic upgrade head
```

The migrations will automatically apply when the container starts because:
1. The `start.sh` script executes `alembic upgrade head`
2. The `DATABASE_URL` environment variable is set in the container
3. Alembic now correctly reads this URL and applies all pending migrations

### For Local Testing:
```bash
# Set DATABASE_URL for local PostgreSQL
export DATABASE_URL="postgresql://username:password@localhost:5432/conflict_tracker"

# Run migrations
python -m alembic upgrade head

# Verify migrations
python -m alembic current
```

### To Verify the Fix:
After deployment, the locations table should exist and be populated with Nigerian states. Test with:
```bash
curl http://api-server:8000/api/v1/locations/states
```

Should return a list of Nigerian states with status 200.

## Impact

✅ **Fixes:**
- The `locations` table will be created on next deployment
- All 36 Nigerian states will be automatically seeded
- Key LGAs for major states will be populated
- Geospatial indexes will be created for performance

✅ **Prevents:**
- Future model changes from being missed in migrations
- Database URL hardcoding issues in containers
- Migration chain conflicts

## Testing Checklist

- [ ] Restart the backend service/container
- [ ] Check that migrations complete without errors
- [ ] Verify the response from `/api/v1/locations/states`
- [ ] Confirm the states list includes all Nigerian states
- [ ] Test the geospatial queries for performance

---

**Status:** Ready for deployment 🚀
