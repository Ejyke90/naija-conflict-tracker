# Nigeria Conflict Tracker

A data-driven platform to track, analyze, and forecast conflict/violence in Nigeria at state, LGA, and community levels.

## Platform Overview

**Mission:** Enable citizens, policymakers, and researchers to make informed decisions through real-time conflict tracking, predictive analytics, and geospatial visualization.

### Key Features
- Real-time conflict tracking with geospatial visualization
- Predictive analytics for early warning
- Gender-disaggregated data analysis
- Poverty-conflict correlation analysis
- Social media chatter monitoring

## Architecture

### Tech Stack
- **Frontend:** Next.js 14, React, Tailwind CSS, Mapbox GL JS
- **Backend:** FastAPI, Python, PostgreSQL + PostGIS
- **ML/AI:** scikit-learn, Prophet, spaCy
- **Infrastructure:** Docker, Railway (backend), Vercel (frontend)

### Data Sources
- News scraping (RSS feeds, major Nigerian news outlets)
- Social media monitoring (Twitter/X API)
- Official sources (Nigeria Police Force, NEMA)
- NGO reports and external APIs (ACLED, GDELT)
- Excel database import capabilities

## Project Structure

```
naija-conflict-tracker/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Next.js frontend
│   ├── components/         # React components
│   ├── pages/             # Next.js pages
│   ├── styles/            # CSS/Tailwind
│   └── package.json
├── database/               # Database schemas
│   ├── migrations/        # Alembic migrations
│   └── schema.sql         # Initial schema
├── scripts/               # Utility scripts
├── docs/                  # Documentation
├── docker-compose.yml     # Local development
└── railway.toml          # Railway deployment config
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.9+ (for local backend development)

### Local Development

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd naija-conflict-tracker
   ```

2. **Start with Docker Compose:**
   ```bash
   docker-compose up -d
   ```
   This starts:
   - PostgreSQL with PostGIS extension
   - Redis for caching
   - FastAPI backend on http://localhost:8000
   - Next.js frontend on http://localhost:3000

3. **Access services:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database: localhost:5432

### Development Setup

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## Deployment

### Production Architecture
- **Frontend:** Vercel (serverless, global CDN)
- **Backend:** Railway (containerized Python/FastAPI)
- **Database:** Railway PostgreSQL with PostGIS
- **Cache:** Railway Redis

### Why Both Vercel and Railway?

**Vercel (Frontend):**
- Optimized for Next.js applications
- Global CDN for fast static asset delivery
- Automatic deployments from Git
- Serverless functions for API routes (if needed)
- Free tier for static sites

**Railway (Backend):**
- Full container support for Python applications
- PostgreSQL database with PostGIS extension
- Redis caching
- Private network between services
- Better suited for ML/AI workloads

### Deploy Commands

```bash
# Deploy frontend to Vercel
cd frontend
vercel --prod

# Deploy backend to Railway
cd backend
railway up
```

## Data Import

### Excel Database Import
```bash
# Import existing Excel data
python scripts/import_excel.py --file "Nextier's Nigeria Violent Conflicts Database Original.xlsx"
```

### API Data Import
```bash
# Import from external APIs
python scripts/import_acled.py
python scripts/import_gdelt.py
```

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

- `GET /api/v1/conflicts` - List conflict events
- `GET /api/v1/conflicts/{id}` - Get specific conflict
- `POST /api/v1/conflicts` - Create new conflict
- `GET /api/v1/analytics/hotspots` - Get conflict hotspots
- `GET /api/v1/forecasts/{location}` - Get conflict forecasts
- `GET /api/v1/stats/dashboard` - Dashboard statistics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[License to be determined]

## Contact

[Contact information to be added]

---

Built with ❤️ for Nigeria's security and peacebuilding community.