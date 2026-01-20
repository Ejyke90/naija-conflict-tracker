# Railway Database Setup

## 1. Create PostgreSQL Service
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway new

# Add PostgreSQL
railway add postgresql
```

## 2. Get Database URL
```bash
# View connection info
railway variables

# Or in Railway UI:
# 1. Go to your project
# 2. Click PostgreSQL service
# 3. Click "Connect" tab
# 4. Copy "Connection URL"
```

## 3. Add to Environment
```bash
# Set DATABASE_URL
railway variables set DATABASE_URL="your_connection_url_here"
```

## 4. Run Migrations
```bash
# Deploy and run database setup
railway up
railway run python alembic upgrade head
```

## 5. Add to GitHub Secrets
- DATABASE_URL: Your PostgreSQL connection string
- RAILWAY_TOKEN: Your Railway API token (from Account Settings)
