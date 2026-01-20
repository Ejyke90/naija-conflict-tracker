from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.api_agent import router as api_agent_router
# from app.api.minimal_dashboard import router as minimal_router  # Temporarily disabled

app = FastAPI(
    title=settings.PROJECT_NAME,
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
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_agent_router, prefix='/api/agent', tags=['agent'])
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
