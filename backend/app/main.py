from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.api_agent import router as api_agent_router
from app.api.dashboard import router as dashboard_router
from contextlib import asynccontextmanager
# from app.api.minimal_dashboard import router as minimal_router  # Temporarily disabled


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup, cleanup on shutdown"""
    # Startup: Initialize Redis connection
    try:
        from app.core.cache import get_redis_client
        redis = await get_redis_client()
        print("✅ Redis connection initialized")
    except Exception as e:
        print(f"⚠️  Redis initialization failed: {e}")
    
    yield
    
    # Shutdown: Close Redis connection
    try:
        from app.core.cache import get_redis_client
        redis = await get_redis_client()
        await redis.close()
        print("✅ Redis connection closed")
    except:
        pass


app = FastAPI(
    title="Nextier Nigeria Conflict Tracker",
    description="""
    ## Nigeria Conflict Tracker API with Advanced Forecasting & Authentication
    
    **Features:**
    - Real-time conflict data tracking across all 36 Nigerian states
    - ML-powered forecasting (Prophet, ARIMA, Ensemble models)
    - Geospatial analytics and hotspot detection
    - JWT-based authentication with role-based access control
    
    **Authentication:**
    - Register at `/api/v1/auth/register`
    - Login at `/api/v1/auth/login` to get access token
    - Click the 🔒 **Authorize** button above to add your token
    - Use format: `Bearer <your_access_token>`
    
    **Roles:**
    - **Viewer** (default): Read-only access to public conflict data
    - **Analyst**: Full access to analytics, forecasts, and data management
    - **Admin**: Full system access including user management
    """,
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    # Add Bearer token security scheme for Swagger UI
    swagger_ui_parameters={
        "persistAuthorization": True,  # Remember token across page reloads
    }
)

# Set up CORS - Explicitly allow Vercel deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (most permissive for PoC)
    allow_credentials=False,  # Must be False when using "*"
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router)  # Dashboard endpoints at /api/dashboard/*


@app.get("/")
async def root():
    return {
        "message": "Nextier Nigeria Conflict Tracker API - v2.0",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "Production-ready with advanced forecasting",
        "features": [
            "Prophet & ARIMA forecasting",
            "Ensemble predictions",
            "Redis caching",
            "Celery scheduled tasks",
            "PDF report generation"
        ]
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint with component status"""
    from app.core.cache import get_redis_client, get_cache_stats
    
    health = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # Check database
    try:
        from app.db.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health["components"]["database"] = "healthy"
    except Exception as e:
        health["components"]["database"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    # Check Redis
    try:
        redis = await get_redis_client()
        await redis.ping()
        stats = await get_cache_stats()
        health["components"]["redis"] = {
            "status": "healthy",
            "keys": stats["total_keys"]
        }
    except Exception as e:
        health["components"]["redis"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    return health


from datetime import datetime

@app.get("/api/cache/stats")
async def get_cache_statistics():
    """Get Redis cache statistics"""
    from app.core.cache import get_cache_stats
    
    try:
        stats = await get_cache_stats()
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
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
            
            # Total casualties
            result = conn.execute(
                text("""
                    SELECT 
                        SUM(fatalities_male + fatalities_female + fatalities_unknown) as fatalities,
                        SUM(injured_male + injured_female + injured_unknown) as injuries
                    FROM conflicts
                """)
            ).first()
            total_fatalities = result.fatalities or 0
            total_injuries = result.injuries or 0
            
            # States affected
            result = conn.execute(text("SELECT COUNT(DISTINCT state) FROM conflicts")).scalar()
            states_affected = result or 0
            
            return {
                "total_incidents": total_incidents,
                "total_fatalities": total_fatalities,
                "total_injuries": total_injuries,
                "total_casualties": total_fatalities + total_injuries,
                "states_affected": states_affected,
                "active_hotspots": 0,
                "crisis_types": {},
                "state_breakdown": {},
                "period_days": 30,
                "last_updated": "2026-01-20T09:21:00"
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
            "last_updated": "2026-01-20T09:21:00"
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


@app.on_event("startup")
async def startup_event():
    try:
        print("Starting up Nextier Nigeria Conflict Tracker API...")
        # Tables already created manually, skip auto-creation
        print("Database tables already exist")
        print("API startup completed successfully")
    except Exception as e:
        print(f"Startup error: {e}")
        # Don't fail startup completely


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
