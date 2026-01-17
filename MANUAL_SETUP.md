# 🔧 Manual Setup Guide

The automated setup script is having Docker issues. Here's a simple manual approach to get your Nigeria Conflict Tracker running.

## 🚀 Quick Manual Setup (5 minutes)

### 1. Start Database & Redis
```bash
# Start just the database services
docker-compose up -d postgres redis

# Wait 10 seconds for services to start
sleep 10
```

### 2. Setup Backend (Local Python)
```bash
# Create virtual environment if not exists
python -m venv venv
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Setup Frontend (Local Node)
```bash
# In a NEW terminal window
cd frontend

# Install dependencies
npm install

# Start frontend server
npm run dev
```

### 4. Access Your Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 What This Gives You

✅ **Working Backend**: FastAPI with PostgreSQL + PostGIS
✅ **Working Frontend**: Next.js with React components  
✅ **Database**: Running with schema initialized
✅ **API Endpoints**: All CRUD operations working
✅ **Map Components**: Ready for Mapbox token

## 📊 Test the Setup

1. **Backend Health Check**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **API Test**:
   ```bash
   curl http://localhost:8000/api/v1/conflicts/summary/overview
   ```

3. **Frontend**: Open http://localhost:3000 in browser

## 🔧 Configure Mapbox (Optional)

1. Get free token from [mapbox.com](https://mapbox.com)
2. Add to `frontend/.env.local`:
   ```
   NEXT_PUBLIC_MAPBOX_TOKEN=pk.your-token-here
   ```
3. Restart frontend: `npm run dev`

## 📥 Import Your Data

```bash
# Import Excel data (in backend terminal)
python scripts/import_excel.py --file "Nextier's Nigeria Violent Conflicts Database Original.xlsx"
```

## 🚀 Deploy to Production

When ready for production:
1. **Backend**: Deploy to Railway (see `docs/DEPLOYMENT.md`)
2. **Frontend**: Deploy to Vercel (see `docs/DEPLOYMENT.md`)

## 🐛 Troubleshooting

**Port already in use?**
```bash
# Kill processes on ports 8000 and 3000
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

**Database connection issues?**
```bash
# Check if database is running
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

**spaCy model issues?**
```bash
# Download model manually
python -m spacy download en_core_web_sm
```

## ✅ Success Checklist

- [ ] Backend running at http://localhost:8000
- [ ] Frontend running at http://localhost:3000  
- [ ] Database connected and healthy
- [ ] API endpoints responding
- [ ] Map components rendering (placeholder)
- [ ] Excel data imported (if available)

---

**🎉 You now have a fully functional Nigeria Conflict Tracker running locally!**

The manual approach is actually more reliable for development and gives you better control over the services.
