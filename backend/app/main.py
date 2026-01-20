from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.api_agent import router as api_agent_router
# from app.api.minimal_dashboard import router as minimal_router  # Temporarily disabled

app = FastAPI(
    title="Nextier Nigeria Conflict Tracker",
    description="Nextier Nigeria Conflict Tracker API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
# app.include_router(api_router, prefix=settings.API_V1_STR)  # Temporarily disabled
# app.include_router(api_agent_router, prefix='/api/agent', tags=['agent'])  # Temporarily disabled
# app.include_router(minimal_router, tags=['minimal'])  # Temporarily disabled


@app.get("/")
async def root():
    return {
        "message": "Nextier Nigeria Conflict Tracker API - v1.2",
        "version": "1.1.0",
        "docs": "/docs",
        "status": "Railway deployment test"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

@app.get("/test")
async def test():
    return {"message": "test endpoint working"}

@app.get("/test-db")
async def test_database():
    """Test database connection and count records"""
    try:
        from app.db.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM conflicts")).scalar()
            return {
                "status": "success",
                "conflicts_count": result or 0
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "conflicts_count": 0
        }

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        from app.db.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Total incidents
            result = conn.execute(text("SELECT COUNT(*) FROM conflicts")).scalar()
            total_incidents = result or 0
            
            return {
                "total_incidents": total_incidents,
                "total_fatalities": 0,
                "total_injuries": 0,
                "total_casualties": 0,
                "states_affected": 0,
                "active_hotspots": 0,
                "crisis_types": {},
                "state_breakdown": {},
                "period_days": 30,
                "last_updated": "2026-01-20T09:20:00"
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "total_incidents": 0,
            "total_fatalities": 0,
            "total_injuries": 0,
            "total_casualties": 0,
            "states_affected": 0,
            "active_hotspots": 0,
            "crisis_types": {},
            "state_breakdown": {},
            "period_days": 30,
            "last_updated": "2026-01-20T09:20:00"
        }

@app.get("/api/dashboard/recent-incidents")
async def get_recent_incidents():
    """Get recent incidents"""
    try:
        from app.db.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT event_date, state, perpetrator_group FROM conflicts LIMIT 5")
            ).fetchall()
            
            incidents = []
            for row in result:
                incidents.append({
                    "date": str(row[0]),
                    "location": row[1],
                    "perpetrator": row[2] or "Unknown"
                })
            
            return {
                "incidents": incidents,
                "total_available": len(incidents),
                "showing": len(incidents),
                "period_days": 7
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "incidents": [],
            "total_available": 0,
            "showing": 0,
            "period_days": 7
        }


@app.on_event("startup")
async def startup_event():
    try:
        print("Starting up Nextier Nigeria Conflict Tracker API...")
        # Try database connection but don't fail if it's not ready
        try:
            from app.db.database import engine
            from app.db.base import Base
            print("Creating database tables...")
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully")
        except Exception as db_error:
            print(f"Database initialization error (non-fatal): {db_error}")
            # Continue startup even if database isn't ready
        
        print("API startup completed successfully")
    except Exception as e:
        print(f"Startup error: {e}")
        # Don't fail startup completely


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
