# 🔧 Railway Deployment Fix

## The Problem
Railway is failing to build because it's trying to build from the root directory instead of the backend directory.

## Quick Fix (2 minutes)

### Option 1: Configure Railway Manually (Recommended)

1. **Go to Railway Dashboard**: https://railway.app
2. **Click on your project**: `naija-conflict-tracker`
3. **Click on the service** (the one that's failing)
4. **Click "Settings" tab**
5. **Update Root Directory**: Set to `./backend`
6. **Update Build Command**: Set to `pip install -r requirements.txt`
7. **Update Start Command**: Set to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
8. **Click "Deploy"**

### Option 2: Recreate Service (Clean Slate)

1. **Delete the failing service** in Railway dashboard
2. **Click "New Service"**
3. **Select "Deploy from GitHub repo"**
4. **Configure manually**:
   - Root Directory: `./backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Add Database**: Click "New Service" → PostgreSQL
6. **Deploy!**

## Why This Happens

Railway's Nixpacks tries to auto-detect the project type. When it sees mixed frontend/backend files in the root, it gets confused. By specifying the backend directory explicitly, we tell Railway exactly where to find the Python app.

## Verification

After fixing, your Railway deployment should:
- ✅ Build successfully
- ✅ Show health check at `/health`
- ✅ Serve API at `/api/v1/...`
- ✅ Connect to PostgreSQL database

## Next Steps

Once Railway is working:
1. Get your Railway URL
2. Update Vercel environment variables
3. Test the full application

---

**🚀 After this fix, your Railway deployment should work perfectly!**
