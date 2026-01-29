from fastapi import APIRouter
from app.api.v1.endpoints import analytics, forecasts, locations, spatial, monitoring, conflict_index, timeseries, conflicts, auth, public, predictions

api_router = APIRouter()

# Public routes (no authentication required)
api_router.include_router(public.router, prefix="/public", tags=["public"])

# Authentication routes (no prefix, already has /auth in router)
api_router.include_router(auth.router, tags=["authentication"])

# Protected routes (will be protected in Phase 2)
api_router.include_router(conflicts.router, prefix="/conflicts", tags=["conflicts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(forecasts.router, prefix="/forecasts", tags=["forecasts"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(spatial.router, prefix="/spatial", tags=["spatial"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(conflict_index.router, tags=["conflict-index"])
api_router.include_router(timeseries.router, prefix="/timeseries", tags=["timeseries"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
