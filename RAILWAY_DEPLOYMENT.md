# 🚀 Railway Deployment Guide

## Why Manual Railway Deployment is Better

Railway's automatic deployment via GitHub Actions can be complex and unreliable. Manual deployment through the Railway dashboard is:
- ✅ More reliable and predictable
- ✅ Better error handling and debugging
- ✅ Easier to configure environment variables
- ✅ Full control over deployment process

## 📋 Step-by-Step Railway Deployment

### 1. Connect Your Repository
1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Click "Deploy from GitHub repo"
4. Select your `naija-conflict-tracker` repository
5. Click "Import Repo"

### 2. Configure the Service
Railway will automatically detect your Python project. Configure it as follows:

**Service Settings:**
- **Name**: `nigeria-conflict-tracker-api`
- **Root Directory**: `./backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. Add Database Service
1. Click "New Service"
2. Select "PostgreSQL"
3. **Name**: `conflict-tracker-db`
4. **Extensions**: Add `postgis` and `timescaledb`

### 4. Add Redis Service (Optional)
1. Click "New Service"  
2. Select "Redis"
3. **Name**: `conflict-tracker-redis`

### 5. Configure Environment Variables
Go to your API service settings → Variables and add:

```bash
# Database (auto-provided by Railway)
DATABASE_URL=${{RAILWAY_DATABASE_URL}}
REDIS_URL=${{RAILWAY_REDIS_URL}}

# Security
SECRET_KEY=your-production-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=4320

# CORS (update with your Vercel URL)
ALLOWED_HOSTS=["https://your-app.vercel.app"]

# External APIs (optional)
TWITTER_BEARER_TOKEN=your-twitter-token
MAPBOX_ACCESS_TOKEN=your-mapbox-token
```

### 6. Deploy!
Click "Deploy" and Railway will:
- Build your FastAPI application
- Create PostgreSQL database with PostGIS
- Setup Redis if configured
- Deploy your API

## 🎯 Post-Deployment Verification

### Health Check
```bash
curl https://your-app-name.railway.app/health
```

### API Test
```bash
curl https://your-app-name.railway.app/api/v1/conflicts/summary/overview
```

### API Documentation
Visit: `https://your-app-name.railway.app/docs`

## 🔗 Connect Frontend to Railway

### 1. Get Your Railway URL
After deployment, your Railway app will have a URL like:
`https://your-app-name.railway.app`

### 2. Update Vercel Configuration
In `frontend/vercel.json`, update:
```json
{
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://your-app-name.railway.app/api/$1"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-app-name.railway.app"
  }
}
```

### 3. Set Vercel Environment Variables
In Vercel dashboard → Settings → Environment Variables:
```bash
NEXT_PUBLIC_API_URL=https://your-app-name.railway.app
NEXT_PUBLIC_MAPBOX_TOKEN=your-mapbox-token
```

### 4. Redeploy Vercel
Push changes or trigger deployment in Vercel dashboard.

## 📊 Import Your Data

### Option 1: Railway Shell
1. Go to Railway dashboard → Your service → "Shell" tab
2. Run the import script:
```bash
cd backend
python scripts/import_excel.py --file "path/to/your/excel/file.xlsx"
```

### Option 2: API Upload
Use the API endpoints to upload data programmatically.

## 🔄 Automatic Updates

### For Future Updates
1. Push changes to GitHub
2. Go to Railway dashboard
3. Click "Deploy" on your service
4. Railway will rebuild and redeploy

### Database Migrations
Railway will automatically run database schema updates when you deploy.

## 🐛 Troubleshooting

### Build Failures
- Check the "Logs" tab in Railway dashboard
- Ensure `requirements.txt` is correct
- Verify Python version compatibility

### Database Connection Issues
- Check that `DATABASE_URL` is set correctly
- Verify PostgreSQL extensions are installed
- Check database service is running

### CORS Issues
- Update `ALLOWED_HOSTS` with your Vercel URL
- Check frontend API URL configuration

## 🎉 Success!

When everything is working:
- ✅ Backend API responding at Railway URL
- ✅ Database connected with PostGIS
- ✅ Frontend connected to backend
- ✅ Maps displaying correctly
- ✅ Data imported and visible

Your Nigeria Conflict Tracker is now live and ready for users!

---

**💡 Pro Tip**: Railway's manual deployment is actually faster and more reliable than GitHub Actions for most use cases. You get better control and debugging capabilities.
