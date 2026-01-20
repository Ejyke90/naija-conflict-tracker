# Phase 3: Real-Time Data Pipeline Deployment Guide

## Overview

Phase 3 transforms the Nigeria Conflict Tracker into a professional real-time monitoring system with automated "Scrape-Clean-Verify" loops, processing 15+ Nigerian news sources every 6 hours.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   News Sources  │───▶│   Celery/Redis  │───▶│   PostgreSQL    │
│   (15+ sites)   │    │   Task Queue    │    │   + PostGIS     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Monitoring    │◀───│  Data Processing│◀───│   Spatial       │
│   Dashboard     │    │   Pipeline      │    │   Analysis      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB+ minimum, 16GB+ recommended
- **Storage**: 50GB+ SSD
- **Network**: Stable internet connection for scraping

### Software Dependencies
- Docker & Docker Compose
- Python 3.9+
- Node.js 18+
- Redis 7+
- PostgreSQL 15+ with PostGIS

## Quick Start (Docker)

### 1. Clone and Setup
```bash
git clone <repository>
cd naija-conflict-tracker
```

### 2. Environment Configuration
```bash
# Backend environment
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# Frontend environment
cp frontend/.env.example frontend/.env
# Edit frontend/.env with your settings
```

### 3. Deploy Full Stack
```bash
# Start Phase 3 infrastructure
docker-compose -f docker-compose-phase3.yml up -d

# View logs
docker-compose -f docker-compose-phase3.yml logs -f
```

### 4. Access Services
- **Main Application**: http://localhost
- **API Documentation**: http://localhost:8000/docs
- **Celery Monitoring**: http://localhost:5555
- **Redis GUI**: http://localhost:8081
- **PostgreSQL GUI**: http://localhost:5050

## Manual Deployment

### 1. Database Setup
```bash
# Install PostgreSQL with PostGIS
sudo apt-get install postgresql-15-postgis-3

# Create database
sudo -u postgres createdb naija_conflict_tracker
sudo -u postgres psql -d naija_conflict_tracker -c "CREATE EXTENSION postgis;"
```

### 2. Redis Setup
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis
```

### 3. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements-phase3.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Run migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Celery Workers
```bash
# Terminal 1: Start Celery Worker
celery -A app.core.celery_app worker --loglevel=info --concurrency=4

# Terminal 2: Start Celery Beat Scheduler
celery -A app.core.celery_app beat --loglevel=info

# Terminal 3: Start Flower (Monitoring)
celery -A app.core.celery_app flower --port=5555
```

### 5. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/naija_conflict_tracker

# Celery/Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Scraping Configuration
SCRAPING_INTERVAL=21600  # 6 hours in seconds
MAX_CONCURRENT_SCRAPES=5
REQUEST_DELAY=1  # seconds between requests

# Geocoding
GEOCODING_TIMEOUT=10
GEOCODING_RATE_LIMIT=1

# Monitoring
ALERT_EMAIL_SMTP_HOST=smtp.gmail.com
ALERT_EMAIL_SMTP_PORT=587
ALERT_EMAIL_USERNAME=your-email@gmail.com
ALERT_EMAIL_PASSWORD=your-app-password

# Slack Integration (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_MAPBOX_TOKEN=your-mapbox-token
```

## News Sources Configuration

### Adding New Sources
Edit `backend/app/tasks/scraping_tasks.py`:

```python
NIGERIAN_NEWS_SOURCES['new_source'] = {
    'name': 'New Source Name',
    'rss_url': 'https://example.com/feed/',
    'base_url': 'https://example.com',
    'regions': ['national', 'politics', 'metro']
}
```

### Custom Scraping Rules
Create custom scrapers for sources without RSS feeds:

```python
class CustomScraper(NewsScraper):
    def scrape_custom_source(self, source_config):
        # Implement custom scraping logic
        pass
```

## Monitoring & Maintenance

### 1. Health Checks
```bash
# Check Celery workers
celery -A app.core.celery_app inspect active

# Check Redis
redis-cli ping

# Check database connections
psql -d naija_conflict_tracker -c "SELECT 1;"
```

### 2. Log Monitoring
```bash
# View Celery logs
tail -f logs/celery_worker.log
tail -f logs/celery_beat.log

# View application logs
tail -f logs/app.log
```

### 3. Performance Monitoring
Access Flower dashboard at http://localhost:5555 for:
- Task execution times
- Worker status
- Task success/failure rates
- Queue lengths

### 4. Database Maintenance
```sql
-- Clean old task results
DELETE FROM task_results WHERE created_at < NOW() - INTERVAL '30 days';

-- Optimize tables
VACUUM ANALYZE conflicts;
VACUUM ANALYZE locations;
```

## Scaling

### Horizontal Scaling
```bash
# Add more Celery workers
celery -A app.core.celery_app worker --loglevel=info --concurrency=8

# Use separate queues for different tasks
celery -A app.core.celery_app worker -Q scraping --loglevel=info
celery -A app.core.celery_app worker -Q processing --loglevel=info
```

### Database Scaling
- Read replicas for reporting queries
- Partitioning for large conflict tables
- Index optimization for spatial queries

## Troubleshooting

### Common Issues

#### 1. Scraping Failures
```bash
# Check robots.txt compliance
curl -s https://example.com/robots.txt

# Test individual source
python -c "from app.tasks.scraping_tasks import scrape_news_source; scrape_news_source('punch')"
```

#### 2. Memory Issues
```bash
# Monitor memory usage
ps aux | grep celery

# Reduce worker concurrency
celery -A app.core.celery_app worker --concurrency=2
```

#### 3. Database Connection Issues
```bash
# Check connection pool
psql -d naija_conflict_tracker -c "SELECT * FROM pg_stat_activity;"

# Increase pool size in settings
SQLALCHEMY_ENGINE_OPTIONS={"pool_size": 20, "max_overflow": 30}
```

### Debug Mode
```bash
# Enable debug logging
export CELERY_LOG_LEVEL=DEBUG

# Run single task for debugging
celery -A app.core.celery_app call app.tasks.scraping_tasks.scrape_news_source --args='["punch"]'
```

## Security Considerations

### 1. Rate Limiting
- Respect robots.txt files
- Implement request delays
- Use rotating user agents

### 2. Data Privacy
- Anonymize personal information
- Secure API endpoints
- Encrypt sensitive data

### 3. Access Control
```bash
# Secure Redis with password
redis-server --requirepass your-secure-password

# Use SSL for production
export CELERY_BROKER_URL=rediss://user:pass@host:port/0
```

## Production Deployment

### 1. Railway (Backend)
```bash
# Deploy to Railway
railway login
railway new
railway up

# Set environment variables
railway variables set DATABASE_URL=your-db-url
railway variables set CELERY_BROKER_URL=your-redis-url
```

### 2. Vercel (Frontend)
```bash
# Deploy to Vercel
cd frontend
vercel --prod
```

### 3. Redis Cloud
```bash
# Use Redis Cloud for production
# Sign up at https://redis.com/try-free
# Update CELERY_BROKER_URL to cloud URL
```

## Backup & Recovery

### 1. Database Backup
```bash
# Automated backups
pg_dump naija_conflict_tracker | gzip > backup_$(date +%Y%m%d).sql.gz

# Restore backup
gunzip -c backup_20240120.sql.gz | psql naija_conflict_tracker
```

### 2. Configuration Backup
```bash
# Backup environment files
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env* docker-compose*.yml
```

## Performance Optimization

### 1. Caching
- Redis for task results
- Application-level caching
- CDN for static assets

### 2. Database Optimization
- Spatial indexes for PostGIS
- Query optimization
- Connection pooling

### 3. Scraping Optimization
- Concurrent requests
- Smart retry logic
- Delta scraping (only new articles)

## Support & Monitoring

### 1. Alerts Configuration
Set up alerts for:
- High failure rates (>20%)
- Data quality degradation
- System resource issues
- Unusual conflict patterns

### 2. Dashboards
- Real-time scraping metrics
- Data quality scores
- System performance
- Conflict trend analysis

### 3. Logging
- Structured logging with JSON
- Centralized log aggregation
- Error tracking and alerting

## Next Steps

1. **Testing**: Run full pipeline tests
2. **Monitoring**: Set up comprehensive monitoring
3. **Scaling**: Plan for increased data volume
4. **Security**: Implement security best practices
5. **Documentation**: Maintain up-to-date documentation

## Support

For issues and questions:
- Check logs for error details
- Review troubleshooting section
- Monitor Celery Flower dashboard
- Contact support team

---

**Phase 3 Complete**: Your Nigeria Conflict Tracker now has professional real-time data collection capabilities with automated "Scrape-Clean-Verify" loops processing 15+ news sources every 6 hours.
