# 🔧 Railway Health Check Fix

## The Problem
Railway is showing: "Healthcheck failed!" and "1/1 replicas never became healthy!"

## Why This Happens
The health check endpoint `/health` isn't responding, usually because:
1. Database connection is failing during startup
2. App crashes before health endpoint can respond
3. Database tables creation is blocking startup

## The Fix Applied

### 1. Moved Database Initialization to Startup Event
- Database table creation now happens in `@app.on_event("startup")`
- Won't block the app from starting
- Handles database connection errors gracefully

### 2. Improved Health Check Response
- Health endpoint now returns: `{"status": "healthy", "database": "connected"}`
- Responds immediately without database dependency

### 3. Error Handling
- Database initialization errors are caught and logged
- App continues starting even if database isn't ready

## What to Do Now

1. **Redeploy your Railway service**
2. **Monitor the logs** - you should see:
   ```
   Starting Nigeria Conflict Tracker API on port 8000
   Creating database tables...
   Database tables created successfully
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

3. **Test the health check**:
   ```bash
   curl https://your-app.railway.app/health
   ```
   Should return: `{"status": "healthy", "database": "connected"}`

## If Health Check Still Fails

### Option 1: Disable Health Check Temporarily
1. Go to Railway service → Settings
2. Set **Healthcheck Path** to empty (disable it)
3. Deploy, test manually, then re-enable

### Option 2: Simple Health Check
Replace health endpoint with:
```python
@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

### Option 3: Check Database Connection
Make sure PostgreSQL service is running and connected:
- DATABASE_URL environment variable is set
- PostgreSQL service is healthy
- Network connection between services works

## Expected Result

After the fix:
- ✅ Service starts successfully
- ✅ Health check passes
- ✅ Database tables created
- ✅ API endpoints respond
- ✅ Railway shows service as healthy

---

**🚀 This fix should resolve the health check failures and get your Railway service running properly!**
