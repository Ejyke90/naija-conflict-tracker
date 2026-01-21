from fastapi import APIRouter
from app.api.v1.endpoints import analytics, forecasts, locations, spatial, monitoring, conflict_index
# Temporarily disable conflicts due to import error
# from app.api.v1.endpoints import conflicts

api_router = APIRouter()

# api_router.include_router(conflicts.router, prefix="/conflicts", tags=["conflicts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(forecasts.router, prefix="/forecasts", tags=["forecasts"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(spatial.router, prefix="/spatial", tags=["spatial"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(conflict_index.router, tags=["conflict-index"])
