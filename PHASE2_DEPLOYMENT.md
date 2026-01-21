# Phase 2 Deployment Configuration

## Environment Variables Required

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Redis (for caching and Celery)
REDIS_URL=redis://localhost:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000

# Forecasting
FORECAST_CACHE_TTL=3600  # 1 hour
FORECAST_DEFAULT_WEEKS=4

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Reports
REPORTS_OUTPUT_DIR=/app/reports

# Optional
GROQ_API_KEY=your_groq_api_key
```

## Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Add Redis service
railway add --plugin redis

# Set environment variables
railway variables set DATABASE_URL=$DATABASE_URL
railway variables set REDIS_URL=$REDIS_URL

# Deploy
railway up
```

## Docker Compose (Local Testing)

```yaml
version: '3.8'

services:
  app:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/conflicts
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  db:
    image: postgis/postgis:15-3.3
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=conflicts
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  celery-worker:
    build: ./backend
    command: celery -A app.tasks.forecast_tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/conflicts
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - db
  
  celery-beat:
    build: ./backend
    command: celery -A app.tasks.forecast_tasks beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/conflicts
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - db

volumes:
  postgres_data:
```

## Vercel Deployment (Frontend)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

Set environment variables in Vercel dashboard:
- `NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app`

## Post-Deployment Checklist

- [ ] Redis connection verified
- [ ] Database migrations run
- [ ] Celery workers running
- [ ] Celery beat scheduler running
- [ ] Forecast cache working
- [ ] PDF reports generating
- [ ] Frontend can fetch forecasts
- [ ] API documentation accessible at /docs
