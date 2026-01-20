from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.api_agent import router as api_agent_router
from app.api.dashboard import router as dashboard_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Nigeria Conflict Tracker API",
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
app.include_router(dashboard_router, tags=['dashboard'])


@app.get("/")
async def root():
    return {
        "message": "Nigeria Conflict Tracker API - v1.1",
        "version": "1.1.0",
        "docs": "/docs",
        "status": "Railway deployment test"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}


@app.on_event("startup")
async def startup_event():
    try:
        print("Starting up Nigeria Conflict Tracker API...")
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
