# Deployment Guide

This guide explains how to deploy the Nigeria Conflict Tracker to production using Railway (backend) and Vercel (frontend).

## Architecture Overview

### Why Railway + Vercel?

**Railway (Backend + Database):**
- ✅ Full container support for Python/FastAPI applications
- ✅ PostgreSQL with PostGIS extension for geospatial data
- ✅ Redis for caching and session management
- ✅ Private networking between services
- ✅ Better suited for ML/AI workloads and background tasks
- ✅ Environment variable management
- ✅ Automatic deployments from Git

**Vercel (Frontend):**
- ✅ Optimized specifically for Next.js applications
- ✅ Global CDN for fast static asset delivery
- ✅ Automatic deployments from Git
- ✅ Serverless functions for API routes (if needed)
- ✅ Free tier for static sites
- ✅ Preview deployments for every PR
- ✅ Edge functions for global performance

## Prerequisites

1. **Git Repository**: Code pushed to GitHub/GitLab
2. **Railway Account**: [railway.app](https://railway.app)
3. **Vercel Account**: [vercel.com](https://vercel.com)
4. **Domain Name** (optional): Custom domain for production
5. **Mapbox Token**: For map visualizations
6. **External API Keys** (optional): Twitter, ACLED, etc.

## Step 1: Deploy Backend to Railway

### 1.1 Setup Railway Project

1. Login to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will automatically detect the project structure

### 1.2 Configure Services

Railway will create three services based on your `railway.toml`:

#### API Service
```bash
# Build Command (auto-detected)
# Start Command
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### PostgreSQL Database
- Engine: PostgreSQL 15+
- Extensions: PostGIS, TimescaleDB
- Connection URL available in environment variables

#### Redis Cache
- Engine: Redis 7+
- Used for caching and session management

### 1.3 Set Environment Variables

In Railway dashboard, add these environment variables to your API service:

```bash
# Database (auto-provided by Railway)
DATABASE_URL=${{RAILWAY_DATABASE_URL}}

# Redis (auto-provided by Railway)  
REDIS_URL=${{RAILWAY_REDIS_URL}}

# Security
SECRET_KEY=your-super-secret-key-here

# CORS (update with your Vercel URL)
ALLOWED_HOSTS=["https://your-app.vercel.app", "http://localhost:3000"]

# External APIs (optional)
TWITTER_BEARER_TOKEN=your-twitter-token
MAPBOX_ACCESS_TOKEN=your-mapbox-token
```

### 1.4 Deploy

1. Click "Deploy" in Railway dashboard
2. Railway will build and deploy your application
3. Once deployed, note your Railway URL: `https://your-app.railway.app`

### 1.5 Setup Database

1. Connect to Railway PostgreSQL using the provided connection URL
2. Run database migrations:
```bash
# Connect to your Railway service terminal
railway shell

# Run migrations
cd backend
alembic upgrade head
```

## Step 2: Deploy Frontend to Vercel

### 2.1 Setup Vercel Project

1. Login to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Vercel will auto-detect Next.js

### 2.2 Configure Build Settings

Vercel will automatically use your `package.json` scripts:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

### 2.3 Set Environment Variables

In Vercel dashboard, add these environment variables:

```bash
# API URL (your Railway backend)
NEXT_PUBLIC_API_URL=https://your-app.railway.app

# Mapbox Token
NEXT_PUBLIC_MAPBOX_TOKEN=pk.your-mapbox-token-here

# Other public variables
NEXT_PUBLIC_APP_NAME=Nigeria Conflict Tracker
```

### 2.4 Configure Custom Domain (Optional)

1. In Vercel dashboard, go to "Settings" → "Domains"
2. Add your custom domain (e.g., `conflicttracker.ng`)
3. Configure DNS records as instructed by Vercel

### 2.5 Deploy

1. Click "Deploy"
2. Vercel will build and deploy your frontend
3. Once deployed, your app will be available at: `https://your-app.vercel.app`

## Step 3: Post-Deployment Configuration

### 3.1 Update CORS Settings

In Railway, update your `ALLOWED_HOSTS` to include your production Vercel URL:

```bash
ALLOWED_HOSTS=["https://your-production-domain.vercel.app", "https://your-custom-domain.com"]
```

### 3.2 Test API Integration

1. Visit your Vercel frontend
2. Check browser console for any CORS errors
3. Test API endpoints directly:
   - `https://your-app.railway.app/health`
   - `https://your-app.railway.app/api/v1/conflicts/summary/overview`

### 3.3 Setup Monitoring

#### Railway Monitoring
- Enable Railway's built-in metrics
- Set up alerting for service failures
- Monitor database performance

#### Vercel Analytics
- Enable Vercel Analytics for frontend performance
- Set up Speed Insights
- Monitor Core Web Vitals

## Step 4: Data Import and Initial Setup

### 4.1 Import Excel Data

```bash
# Connect to Railway service terminal
railway shell

# Run import script
python scripts/import_excel.py --file "Nextier's Nigeria Violent Conflicts Database Original.xlsx"
```

### 4.2 Setup External Data Sources

Configure automated data imports:

```bash
# ACLED data import
python scripts/import_acled.py --api-key your-acled-key

# Social media monitoring
python scripts/setup_twitter_monitoring.py --bearer-token your-twitter-token
```

## Production Checklist

- [ ] Railway backend deployed and healthy
- [ ] PostgreSQL database with PostGIS enabled
- [ ] Redis cache running
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] Vercel frontend deployed
- [ ] CORS properly configured
- [ ] Custom domain (if used) pointing to Vercel
- [ ] SSL certificates active
- [ ] Monitoring and alerting setup
- [ ] Backup strategy configured
- [ ] Initial data imported
- [ ] API endpoints tested
- [ ] Frontend functionality verified

## Scaling Considerations

### Railway Scaling
- **API Service**: Add more containers horizontally
- **Database**: Upgrade to larger instance
- **Redis**: Scale memory based on cache usage

### Vercel Scaling
- **Edge Functions**: Automatically scale globally
- **Bandwidth**: Pay-as-you-go scaling
- **Build Time**: Upgrade plan for faster builds

## Cost Optimization

### Railway (Estimated Monthly Cost)
- Hobby Plan: ~$20/month
  - API Service: $5-10/month
  - PostgreSQL: $5-10/month  
  - Redis: $5/month

### Vercel (Estimated Monthly Cost)
- Pro Plan: ~$20/month
  - Bandwidth: $0-10/month
  - Build Time: $0-5/month
  - Edge Functions: $5-10/month

**Total Estimated Cost**: $40-60/month for production setup

## Troubleshooting

### Common Issues

#### CORS Errors
```bash
# Check Railway environment variables
echo $ALLOWED_HOSTS

# Verify frontend URL is included
```

#### Database Connection Issues
```bash
# Test database connection from Railway shell
railway shell
psql $DATABASE_URL -c "SELECT version();"
```

#### Build Failures
```bash
# Check build logs in Railway/Vercel dashboards
# Verify all dependencies are in requirements.txt/package.json
```

#### Performance Issues
- Enable Railway metrics and Vercel Analytics
- Check database query performance
- Optimize frontend bundle size
- Consider CDN for static assets

## Security Considerations

1. **Environment Variables**: Never commit secrets to Git
2. **API Keys**: Use Railway's encrypted environment variables
3. **Database**: Use Railway's private networking
4. **HTTPS**: Both platforms enforce HTTPS by default
5. **Rate Limiting**: Implement API rate limiting in FastAPI
6. **Input Validation**: Use Pydantic models for validation

## Backup and Recovery

### Railway Backups
- PostgreSQL: Automatic daily backups
- File Storage: Use Railway's persistent volumes
- Redis: Configure persistence if needed

### Disaster Recovery
1. Restore database from Railway backup
2. Redeploy services from Git
3. Update environment variables
4. Test functionality

## Monitoring and Alerting

### Recommended Tools
- **Railway**: Built-in metrics and logs
- **Vercel**: Analytics and Speed Insights
- **Uptime monitoring**: UptimeRobot or Pingdom
- **Error tracking**: Sentry (optional)

### Key Metrics to Monitor
- API response times
- Database query performance
- Error rates
- Frontend Core Web Vitals
- User engagement metrics

---

For additional support, check the [Railway Documentation](https://docs.railway.app/) and [Vercel Documentation](https://vercel.com/docs).
