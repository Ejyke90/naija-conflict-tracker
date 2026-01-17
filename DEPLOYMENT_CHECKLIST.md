# 🚀 Production Deployment Checklist

## 📋 Pre-Deployment Setup

### 1. Repository Setup
- [ ] Push all code to GitHub repository
- [ ] Ensure repository is public or has proper access

### 2. Railway Setup (Backend)
- [ ] Login to [Railway Dashboard](https://railway.app)
- [ ] Connect GitHub account
- [ ] Create new project from repository
- [ ] Add Railway token to GitHub Secrets (`RAILWAY_TOKEN`)

### 3. Vercel Setup (Frontend)
- [ ] Login to [Vercel Dashboard](https://vercel.com)
- [ ] Connect GitHub account
- [ ] Import repository to Vercel
- [ ] Add Vercel secrets to GitHub:
  - `VERCEL_TOKEN`
  - `VERCEL_ORG_ID`
  - `VERCEL_PROJECT_ID`

### 4. Environment Variables
- [ ] Railway: Set backend environment variables
- [ ] Vercel: Set frontend environment variables
- [ ] Get Mapbox token for maps

## 🔧 Railway Configuration (Backend)

### Environment Variables
```bash
# Auto-provided by Railway
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

### Database Setup
1. Railway will automatically create PostgreSQL with PostGIS
2. Database schema auto-creates on first deploy
3. No manual migration needed

## 🎨 Vercel Configuration (Frontend)

### Environment Variables
```bash
# API URL (your Railway backend)
NEXT_PUBLIC_API_URL=https://your-app.railway.app

# Mapbox Token (get from mapbox.com)
NEXT_PUBLIC_MAPBOX_TOKEN=pk.your-mapbox-token-here

# App Configuration
NEXT_PUBLIC_APP_NAME=Nigeria Conflict Tracker
```

### Update vercel.json
Replace `https://your-railway-app.railway.app` with your actual Railway URL.

## 🚀 Deployment Steps

### Option 1: Automatic via GitHub Actions
1. Push to `main` branch
2. GitHub Actions will automatically deploy to both platforms
3. Monitor deployment in GitHub Actions tab

### Option 2: Manual Deployment
1. **Railway**: Click "Deploy" in Railway dashboard
2. **Vercel**: Click "Deploy" in Vercel dashboard

## ✅ Post-Deployment Verification

### Backend Tests
```bash
# Health check
curl https://your-app.railway.app/health

# API test
curl https://your-app.railway.app/api/v1/conflicts/summary/overview

# API docs
Visit https://your-app.railway.app/docs
```

### Frontend Tests
1. Visit https://your-app.vercel.app
2. Check all components load
3. Test API integration
4. Verify maps display (with Mapbox token)

## 🔗 Integration Testing

### 1. API Connection
- Frontend should successfully call backend APIs
- No CORS errors in browser console
- Data loads in dashboard components

### 2. Database Connection
- Backend connects to Railway PostgreSQL
- Sample data queries work
- Health check passes

### 3. Map Functionality
- Mapbox maps render correctly
- Location markers display
- Interactive features work

## 📊 Data Import (Production)

### Import Excel Data
```bash
# Connect to Railway service terminal
railway shell

# Run import script
cd backend
python scripts/import_excel.py --file "path/to/your/excel/file.xlsx"
```

### Setup External Data Sources
1. Configure ACLED API key (if available)
2. Setup Twitter monitoring (if desired)
3. Schedule automated data imports

## 🎯 User Demo Ready

When all checks pass, you'll have:

✅ **Live Backend API**: `https://your-app.railway.app`
✅ **Live Frontend**: `https://your-app.vercel.app`
✅ **Working Maps**: With Mapbox integration
✅ **Real Data**: Imported from Excel database
✅ **Mobile Responsive**: Works on all devices
✅ **Professional URL**: Custom domain (optional)

## 🔄 Ongoing Maintenance

### Monitoring
- Railway: Built-in metrics and logs
- Vercel: Analytics and performance
- Set up uptime monitoring (UptimeRobot)

### Updates
- Push to `main` branch for automatic deployment
- Test in staging before production
- Monitor for any issues

### Scaling
- Railway: Upgrade resources as needed
- Vercel: Automatically scales globally
- Monitor costs and usage

---

## 🎉 Success Criteria

Your Nigeria Conflict Tracker is production-ready when:

- [ ] Backend API responds at Railway URL
- [ ] Frontend loads at Vercel URL  
- [ ] Maps display with conflict data
- [ ] Mobile responsive design works
- [ ] No console errors or CORS issues
- [ ] Data imports successfully
- [ ] Ready for user demonstration

**🚀 Your conflict tracking platform will be live and ready for users!**
