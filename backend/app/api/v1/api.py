from fastapi import APIRouter
from app.api.v1.endpoints import conflicts, analytics, forecasts, locations

api_router = APIRouter()

api_router.include_router(conflicts.router, prefix="/conflicts", tags=["conflicts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(forecasts.router, prefix="/forecasts", tags=["forecasts"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
