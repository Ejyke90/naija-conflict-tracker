# 🔧 Railway Port Variable Fix

## The Problem
Railway is showing: `Error: Invalid value for '--port': '$PORT' is not a valid integer`

## Why This Happens
The `$PORT` environment variable isn't being properly interpolated in the command string.

## Quick Fix (2 minutes)

### Option 1: Use the Startup Script (Recommended)
I've already created a fix:

1. **Go to Railway Dashboard** → Your service → Settings
2. **Update Start Command**: Set to `./start.sh`
3. **Redeploy**: Click "Deploy"

The `start.sh` script properly handles the PORT variable.

### Option 2: Manual Command Fix
If the script doesn't work, manually set:

1. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. **Port**: Railway will automatically handle port mapping
3. **Redeploy**

### Option 3: Use Railway's Default
1. **Remove custom start command** entirely
2. **Let Railway auto-detect** the FastAPI app
3. **Redeploy**

## What the Fix Does

The `start.sh` script:
- Sets default port to 8000 if PORT is not set
- Properly expands the PORT environment variable
- Starts uvicorn with the correct port

## Verification

After fixing, you should see:
```
Starting Nigeria Conflict Tracker API on port 8000
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Test the Fix

Once deployed, test with:
```bash
curl https://your-app.railway.app/health
```

Should return: `{"status": "healthy", "database": "connected"}`

---

**🚀 After this fix, your Railway service should start successfully without port errors!**
