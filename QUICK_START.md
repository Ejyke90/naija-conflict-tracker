# 🚀 Quick Start Guide

Get your Nigeria Conflict Tracker running in 5 minutes!

## 🎯 What You Get

A complete MVP for tracking and forecasting conflicts in Nigeria:
- **Backend**: FastAPI + PostgreSQL + PostGIS + Redis
- **Frontend**: Next.js + Tailwind CSS + Mapbox
- **Deployment**: Railway (backend) + Vercel (frontend)
- **Data Import**: Excel database import ready

## ⚡ Local Development (5 minutes)

### 1. Clone & Setup
```bash
git clone <your-repo-url>
cd naija-conflict-tracker
```

### 2. Run Setup Script
```bash
./scripts/setup.sh
```

This script will:
- ✅ Check prerequisites (Docker, Docker Compose)
- ✅ Create environment files
- ✅ Build and start all services
- ✅ Setup database with PostGIS
- ✅ Install frontend dependencies
- ✅ Test everything works

### 3. Access Your App
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🌐 Production Deployment (15 minutes)

### Deploy Backend to Railway
1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Add environment variables:
   - `SECRET_KEY` (generate a random string)
   - `ALLOWED_HOSTS` (add your Vercel URL)
5. Deploy! 🎉

### Deploy Frontend to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project" → Import your GitHub repo
3. Add environment variables:
   - `NEXT_PUBLIC_API_URL` (your Railway URL)
   - `NEXT_PUBLIC_MAPBOX_TOKEN` (get from mapbox.com)
4. Deploy! 🎉

## 📊 Import Your Data

```bash
# Import the Excel database
python scripts/import_excel.py --file "Nextier's Nigeria Violent Conflicts Database Original.xlsx"
```

## 🛠️ Development Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Access database
docker-compose exec postgres psql -U postgres -d conflict_tracker

# Backend development
cd backend
uvicorn app.main:app --reload

# Frontend development
cd frontend
npm run dev
```

## 📁 Project Structure

```
naija-conflict-tracker/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   └── services/       # Business logic
│   └── requirements.txt
├── frontend/               # Next.js frontend
│   ├── components/         # React components
│   ├── pages/             # Next.js pages
│   └── package.json
├── database/               # Database schemas
├── scripts/               # Utility scripts
├── docker-compose.yml     # Local development
├── railway.toml          # Railway deployment
└── README.md             # Full documentation
```

## 🔧 Configuration

### Backend Environment (.env)
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/conflict_tracker
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=["http://localhost:3000"]
```

### Frontend Environment (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAPBOX_TOKEN=your-mapbox-token
```

## 🚨 Next Steps

1. **Get Mapbox Token**: Sign up at [mapbox.com](https://mapbox.com) for map visualizations
2. **Import Data**: Run the Excel import script with your conflict data
3. **Configure APIs**: Add Twitter, ACLED, or other data source API keys
4. **Customize**: Modify the frontend components and API endpoints
5. **Deploy**: Follow the deployment guide for production setup

## 📚 Key Features Ready

- ✅ **Conflict Tracking**: CRUD operations for conflict events
- ✅ **Geospatial Analysis**: PostGIS database with coordinates
- ✅ **Data Visualization**: Interactive maps and charts
- ✅ **API Documentation**: Auto-generated OpenAPI docs
- ✅ **Gender Disaggregation**: Separate tracking for male/female casualties
- ✅ **Location Hierarchy**: State → LGA → Community structure
- ✅ **Real-time Updates**: WebSocket support ready
- ✅ **Mobile Responsive**: Works on all devices

## 🤝 Need Help?

- 📖 **Full Documentation**: See `README.md`
- 🚀 **Deployment Guide**: See `docs/DEPLOYMENT.md`
- 🐛 **Issues**: Check Docker logs: `docker-compose logs`
- 💬 **Support**: Check the documentation or create an issue

## 🎉 You're Ready!

You now have a complete, production-ready conflict tracking platform for Nigeria. The system is designed to scale and can handle real-time data from multiple sources.

**Built with ❤️ for Nigeria's security and peacebuilding community.**

---

*This MVP was scaffolded by the SCAFFOLDING_AGENT as part of the AI Agent Orchestration system.*
