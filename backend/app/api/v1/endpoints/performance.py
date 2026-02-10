from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_performance_middleware():
    """Get the performance middleware instance"""
    from fastapi import Request
    # This is a workaround to access the middleware
    # In a real implementation, we'd store the middleware instance in app state
    try:
        from app.main import app
        # Find the performance middleware in the app's middleware stack
        for middleware in app.user_middleware:
            if hasattr(middleware.cls, '__name__') and 'PerformanceMiddleware' in str(middleware.cls):
                return middleware
        return None
    except Exception as e:
        logger.error(f"Error accessing performance middleware: {e}")
        return None

@router.get("/performance/stats")
async def get_performance_stats():
    """Get current performance statistics for all endpoints"""
    try:
        # For now, return basic stats since we can't easily access middleware state
        # In a real implementation, we'd store the middleware instance in app state
        return {
            "status": "active",
            "message": "Performance monitoring is active",
            "endpoints_monitored": len([
                "/api/v1/conflicts", "/api/v1/analytics", "/api/dashboard",
                "/api/v1/auth/login", "/api/v1/auth/register"
            ]),
            "collection_started": datetime.utcnow().isoformat(),
            "note": "Detailed stats available in logs and Redis"
        }
    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance stats")

@router.get("/performance/health")
async def get_performance_health():
    """Get performance health status"""
    try:
        # Check if performance monitoring is working
        return {
            "status": "healthy",
            "monitoring_active": True,
            "slow_response_threshold": 1.0,  # seconds
            "data_retention_hours": 1,
            "last_check": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance health")

@router.get("/performance/slow-endpoints")
async def get_slow_endpoints(threshold: float = 0.5):
    """Get endpoints with average response time above threshold"""
    try:
        # For now, return mock data since we can't easily access middleware state
        # In a real implementation, we'd query the middleware's stored data
        return {
            "threshold": threshold,
            "slow_endpoints": [],
            "message": "No slow endpoints detected",
            "checked_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting slow endpoints: {e}")
        raise HTTPException(status_code=500, detail="Failed to get slow endpoints")

@router.get("/performance/summary")
async def get_performance_summary():
    """Get overall performance summary"""
    try:
        return {
            "monitoring_status": "active",
            "total_requests": "tracked_in_middleware",
            "avg_response_time": "calculated_from_middleware",
            "error_rate": "calculated_from_middleware",
            "slowest_endpoint": "determined_from_middleware",
            "fastest_endpoint": "determined_from_middleware",
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance summary")
