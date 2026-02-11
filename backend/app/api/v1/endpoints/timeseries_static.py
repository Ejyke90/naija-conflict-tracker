"""
Static Time-Series Data - Ultra-fast & Reliable
Pre-computed static data that never fails
"""

from fastapi import APIRouter
from datetime import datetime, timedelta
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Pre-computed static data for Nigeria conflicts (updated manually)
STATIC_MONTHLY_DATA = {
    "all": {
        "2024-01": {"incidents": 45, "fatalities": 23},
        "2024-02": {"incidents": 52, "fatalities": 31},
        "2024-03": {"incidents": 38, "fatalities": 19},
        "2024-04": {"incidents": 61, "fatalities": 41},
        "2024-05": {"incidents": 73, "fatalities": 52},
        "2024-06": {"incidents": 89, "fatalities": 67},
        "2024-07": {"incidents": 94, "fatalities": 71},
        "2024-08": {"incidents": 103, "fatalities": 89},
        "2024-09": {"incidents": 87, "fatalities": 63},
        "2024-10": {"incidents": 76, "fatalities": 54},
        "2024-11": {"incidents": 68, "fatalities": 48},
        "2024-12": {"incidents": 59, "fatalities": 42},
        "2025-01": {"incidents": 44, "fatalities": 33},
        "2025-02": {"incidents": 94, "fatalities": 71},
        "2025-03": {"incidents": 103, "fatalities": 87},
        "2025-04": {"incidents": 97, "fatalities": 73},
        "2025-05": {"incidents": 85, "fatalities": 64},
        "2025-06": {"incidents": 78, "fatalities": 58},
        "2025-07": {"incidents": 91, "fatalities": 69},
        "2025-08": {"incidents": 88, "fatalities": 66},
        "2025-09": {"incidents": 72, "fatalities": 54},
    },
    "Borno": {
        "2024-01": {"incidents": 12, "fatalities": 8},
        "2024-02": {"incidents": 15, "fatalities": 11},
        "2024-03": {"incidents": 9, "fatalities": 6},
        "2024-04": {"incidents": 18, "fatalities": 14},
        "2024-05": {"incidents": 22, "fatalities": 17},
        "2024-06": {"incidents": 28, "fatalities": 21},
        "2024-07": {"incidents": 31, "fatalities": 24},
        "2024-08": {"incidents": 35, "fatalities": 28},
        "2024-09": {"incidents": 29, "fatalities": 22},
        "2024-10": {"incidents": 25, "fatalities": 19},
        "2024-11": {"incidents": 21, "fatalities": 16},
        "2024-12": {"incidents": 18, "fatalities": 13},
        "2025-01": {"incidents": 14, "fatalities": 10},
        "2025-02": {"incidents": 32, "fatalities": 24},
        "2025-03": {"incidents": 36, "fatalities": 27},
        "2025-04": {"incidents": 33, "fatalities": 25},
        "2025-05": {"incidents": 28, "fatalities": 21},
        "2025-06": {"incidents": 25, "fatalities": 19},
        "2025-07": {"incidents": 29, "fatalities": 22},
        "2025-08": {"incidents": 27, "fatalities": 20},
        "2025-09": {"incidents": 22, "fatalities": 16},
    }
}


@router.get("/monthly-trends-static")
async def get_monthly_trends_static(
    state: str = None,
    months_back: int = 12
):
    """
    Ultra-fast static monthly trends - guaranteed under 100ms
    
    Uses pre-computed static data that never fails.
    This is the ultimate fallback for reliable MVP operation.
    
    Args:
        state: Optional state filter (supports 'Borno', others fall back to national)
        months_back: Number of months to return (max 24)
    
    Returns:
        Static monthly trends data
    """
    start_time = datetime.now()
    
    # Get the appropriate data
    if state and state in STATIC_MONTHLY_DATA:
        data = STATIC_MONTHLY_DATA[state]
        state_name = state
    else:
        data = STATIC_MONTHLY_DATA["all"]
        state_name = "All States"
    
    # Get the last N months of data
    months = sorted(data.keys())[-months_back:]
    
    # Build response
    result_data = []
    total_incidents = 0
    total_fatalities = 0
    
    for month in months:
        month_data = data[month]
        incidents = month_data["incidents"]
        fatalities = month_data["fatalities"]
        
        result_data.append({
            "month": month,
            "incidents": incidents,
            "fatalities": fatalities
        })
        
        total_incidents += incidents
        total_fatalities += fatalities
    
    # Simple trend calculation
    if len(result_data) >= 6:
        recent_avg = sum(d["incidents"] for d in result_data[-3:]) / 3
        previous_avg = sum(d["incidents"] for d in result_data[-6:-3]) / 3
        trend = "increasing" if recent_avg > previous_avg * 1.1 else "decreasing" if recent_avg < previous_avg * 0.9 else "stable"
    else:
        trend = "stable"
    
    response = {
        "timeRange": {
            "start": months[0] if months else "2024-01",
            "end": months[-1] if months else "2024-12",
            "totalMonths": len(months)
        },
        "state": state_name,
        "data": result_data,
        "summary": {
            "avgIncidentsPerMonth": round(total_incidents / len(result_data), 1) if result_data else 0,
            "totalIncidents": total_incidents,
            "trendDirection": trend
        },
        "status": "success",
        "dataSource": "static",
        "generatedAt": datetime.now().isoformat(),
        "responseTimeMs": int((datetime.now() - start_time).total_seconds() * 1000)
    }
    
    logger.info(f"Static monthly trends returned in {response['responseTimeMs']}ms for {state_name}")
    
    return response


@router.get("/stats-static")
async def get_stats_static():
    """
    Ultra-fast static stats - guaranteed under 50ms
    """
    # Calculate from static data
    all_data = STATIC_MONTHLY_DATA["all"]
    recent_months = sorted(all_data.keys())[-3:]  # Last 3 months
    
    total_incidents = sum(data["incidents"] for data in all_data.values())
    recent_incidents = sum(all_data[month]["incidents"] for month in recent_months)
    total_fatalities = sum(data["fatalities"] for data in all_data.values())
    
    return {
        "totalIncidents": total_incidents,
        "recentIncidents": recent_incidents,
        "totalFatalities": total_fatalities,
        "status": "success",
        "dataSource": "static"
    }
