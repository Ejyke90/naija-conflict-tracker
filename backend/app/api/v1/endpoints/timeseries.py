"""
Time-Series Analytics & Forecasting Endpoint
Handles monthly trends, anomaly detection, and basic forecasting
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import json

from app.db.database import get_db
from app.utils.timeout import with_timeout
from app.core.cache import get_redis_client
from app.core.config import settings

router = APIRouter()


@router.get("/state-summary")
async def get_state_summary(
    months_back: int = Query(6, ge=3, le=24, description="Months of historical data"),
    limit: int = Query(10, ge=5, le=37, description="Number of top states to return"),
    db: Session = Depends(get_db)
):
    """
    Get aggregated conflict statistics for all states with trend analysis
    
    Returns top N states by incident count with:
    - Total incidents and fatalities
    - Trend direction (increasing, stable, decreasing)
    - Trend percentage change
    - Risk level classification
    - Number of affected LGAs
    """
    from app.models.conflict import Conflict
    from app.models.reference import State, LGA
    
    cutoff_date = datetime.now() - timedelta(days=months_back * 30)
    prev_cutoff_date = cutoff_date - timedelta(days=months_back * 30)
    
    query = text("""
        WITH current_period AS (
            SELECT 
                s.name as state,
                COUNT(c.id) as incidents,
                COALESCE(SUM(
                    c.civilian_death_male + c.civilian_death_female + c.civilian_death_unknown +
                    c.security_death_male + c.security_death_female + c.security_death_unknown
                ), 0) as fatalities,
                COALESCE(SUM(
                    c.injured_male + c.injured_female + c.injured_unknown
                ), 0) as injuries,
                COALESCE(SUM(
                    c.kidnapped_male + c.kidnapped_female + c.kidnapped_unknown
                ), 0) as kidnapped,
                COUNT(DISTINCT c.lga_id) as affected_lgas
            FROM conflicts c
            JOIN states s ON c.state_id = s.id
            WHERE c.incidence_date >= :cutoff_date
            GROUP BY s.name
        ),
        previous_period AS (
            SELECT 
                s.name as state,
                COUNT(c.id) as prev_incidents
            FROM conflicts c
            JOIN states s ON c.state_id = s.id
            WHERE c.incidence_date >= :prev_cutoff_date
            AND c.incidence_date < :cutoff_date
            GROUP BY s.name
        )
        SELECT 
            c.state,
            c.incidents,
            c.fatalities,
            c.injuries,
            c.kidnapped,
            c.affected_lgas,
            COALESCE(p.prev_incidents, 0) as prev_incidents,
            CASE 
                WHEN c.incidents > COALESCE(p.prev_incidents, 0) * 1.1 THEN 'increasing'
                WHEN c.incidents < COALESCE(p.prev_incidents, 0) * 0.9 THEN 'decreasing'
                ELSE 'stable'
            END as trend,
            CASE
                WHEN c.incidents >= 50 OR c.fatalities >= 100 THEN 'critical'
                WHEN c.incidents >= 30 OR c.fatalities >= 50 THEN 'high'
                WHEN c.incidents >= 15 OR c.fatalities >= 20 THEN 'medium'
                ELSE 'low'
            END as risk_level
        FROM current_period c
        LEFT JOIN previous_period p ON c.state = p.state
        ORDER BY c.incidents DESC
        LIMIT :limit
    """)
    
    result = db.execute(query, {
        'cutoff_date': cutoff_date,
        'prev_cutoff_date': prev_cutoff_date,
        'limit': limit
    }).fetchall()
    
    if not result:
        return []
    
    return [
        {
            "state": row.state,
            "incidents": row.incidents,
            "fatalities": int(row.fatalities),
            "injuries": int(row.injuries),
            "kidnapped": int(row.kidnapped),
            "affectedLGAs": row.affected_lgas,
            "previousIncidents": row.prev_incidents,
            "trend": row.trend,
            "trendPercent": round(
                ((row.incidents - row.prev_incidents) / row.prev_incidents * 100) 
                if row.prev_incidents > 0 else 0,
                1
            ),
            "riskLevel": row.risk_level
        }
        for row in result
    ]


def calculate_moving_average(values: List[float], window: int = 3) -> List[float]:
    """Calculate simple moving average"""
    if len(values) < window:
        return values
    
    ma = []
    for i in range(len(values)):
        if i < window - 1:
            ma.append(values[i])
        else:
            window_vals = values[i - window + 1:i + 1]
            ma.append(sum(window_vals) / window)
    return ma


def detect_anomalies(values: List[float], threshold: float = 2.0) -> List[int]:
    """Detect anomalies using standard deviation method"""
    if len(values) < 3:
        return []
    
    mean = statistics.mean(values)
    stdev = statistics.stdev(values)
    
    anomalies = []
    for i, val in enumerate(values):
        z_score = abs((val - mean) / stdev) if stdev > 0 else 0
        if z_score > threshold:
            anomalies.append(i)
    
    return anomalies


def simple_forecast(values: List[float], periods: int = 3) -> List[float]:
    """Simple linear regression forecast"""
    if len(values) < 3:
        return [values[-1]] * periods if values else [0] * periods
    
    # Use last 6 months for trend
    recent = values[-6:] if len(values) >= 6 else values
    n = len(recent)
    
    # Calculate linear trend
    x_vals = list(range(n))
    x_mean = sum(x_vals) / n
    y_mean = sum(recent) / n
    
    numerator = sum((x_vals[i] - x_mean) * (recent[i] - y_mean) for i in range(n))
    denominator = sum((x - x_mean) ** 2 for x in x_vals)
    
    if denominator == 0:
        slope = 0
    else:
        slope = numerator / denominator
    
    intercept = y_mean - slope * x_mean
    
    # Generate forecast
    forecast = []
    for i in range(1, periods + 1):
        pred = intercept + slope * (n + i - 1)
        forecast.append(max(0, pred))  # Don't predict negative values
    
    return forecast


@router.get("/monthly-trends")
@with_timeout(seconds=30)
async def get_monthly_trends(
    state: Optional[str] = Query(None, description="Filter by specific state"),
    months_back: int = Query(60, ge=6, le=120, description="Number of months to analyze"),
    include_forecast: bool = Query(True, description="Include 3-month forecast"),
    db: Session = Depends(get_db)
):
    """
    Get monthly conflict trends with optional forecasting
    
    Returns:
        - Monthly aggregated data (incidents, fatalities)
        - Moving average trend line
        - Anomaly detection (unusual spikes)
        - 3-month forecast (if enabled)
    """
    
    # Use all available data for better coverage (up to 5 years)
    cutoff_date = datetime.now() - timedelta(days=min(months_back * 30, 5 * 365))
    
    # Build query
    if state:
        query = text("""
            SELECT 
                DATE_TRUNC('month', incidence_date) as month,
                COUNT(*) as incidents,
                COALESCE(SUM(
                    civilian_death_male + civilian_death_female + civilian_death_unknown +
                    security_death_male + security_death_female + security_death_unknown
                ), 0) as fatalities,
                COALESCE(SUM(
                    civilian_death_male + civilian_death_female + civilian_death_unknown
                ), 0) as civilian_casualties,
                COUNT(DISTINCT lga_id) as affected_lgas
            FROM conflicts
            WHERE incidence_date >= :cutoff_date
            AND state_id = (SELECT id FROM states WHERE name = :state)
            GROUP BY DATE_TRUNC('month', incidence_date)
            ORDER BY month
        """)
        result = db.execute(query, {'cutoff_date': cutoff_date, 'state': state}).fetchall()
    else:
        query = text("""
            SELECT 
                DATE_TRUNC('month', incidence_date) as month,
                COUNT(*) as incidents,
                COALESCE(SUM(
                    civilian_death_male + civilian_death_female + civilian_death_unknown +
                    security_death_male + security_death_female + security_death_unknown
                ), 0) as fatalities,
                COALESCE(SUM(
                    civilian_death_male + civilian_death_female + civilian_death_unknown
                ), 0) as civilian_casualties,
                COUNT(DISTINCT state_id) as affected_states
            FROM conflicts
            WHERE incidence_date >= :cutoff_date
            GROUP BY DATE_TRUNC('month', incidence_date)
            ORDER BY month
        """)
        result = db.execute(query, {'cutoff_date': cutoff_date}).fetchall()
    
    if not result:
        # Return empty seasonal data instead of error
        return {
            "state": state or "All States",
            "seasonalPattern": [],
            "analysis": {
                "highRiskMonths": [],
                "avgIncidentsPerMonth": 0,
                "message": "No data available for this period"
            }
        }
    
    # Extract time series data
    months = []
    incidents = []
    fatalities = []
    civilian_casualties = []
    geographic_spread = []
    
    for row in result:
        months.append(row.month.strftime('%Y-%m'))
        incidents.append(row.incidents)
        fatalities.append(int(row.fatalities))
        civilian_casualties.append(int(row.civilian_casualties))
        geographic_spread.append(row.affected_lgas if state else row.affected_states)
    
    # Calculate moving averages
    incidents_ma = calculate_moving_average(incidents, window=3)
    fatalities_ma = calculate_moving_average(fatalities, window=3)
    
    # Detect anomalies (spikes)
    incident_anomalies = detect_anomalies(incidents, threshold=2.0)
    fatality_anomalies = detect_anomalies(fatalities, threshold=2.0)
    
    # Build response
    response = {
        "timeRange": {
            "start": months[0],
            "end": months[-1],
            "totalMonths": len(months)
        },
        "state": state or "All States",
        "data": [
            {
                "month": months[i],
                "incidents": incidents[i],
                "fatalities": fatalities[i],
                "civilianCasualties": civilian_casualties[i],
                "geographicSpread": geographic_spread[i],
                "incidentsTrend": round(incidents_ma[i], 1),
                "fatalitiesTrend": round(fatalities_ma[i], 1),
                "isAnomalousIncidents": i in incident_anomalies,
                "isAnomalousFatalities": i in fatality_anomalies
            }
            for i in range(len(months))
        ],
        "summary": {
            "avgIncidentsPerMonth": round(statistics.mean(incidents), 1),
            "avgFatalitiesPerMonth": round(statistics.mean(fatalities), 1),
            "totalIncidents": sum(incidents),
            "totalFatalities": sum(fatalities),
            "peakMonth": months[incidents.index(max(incidents))],
            "peakIncidents": max(incidents),
            "anomalyCount": len(incident_anomalies),
            "trendDirection": "increasing" if incidents[-1] > incidents_ma[-1] else "decreasing"
        }
    }
    
    # Add forecast if requested
    if include_forecast:
        incident_forecast = simple_forecast(incidents, periods=3)
        fatality_forecast = simple_forecast(fatalities, periods=3)
        
        # Generate future month labels
        last_month = datetime.strptime(months[-1], '%Y-%m')
        forecast_months = []
        for i in range(1, 4):
            future_month = last_month + timedelta(days=30 * i)
            forecast_months.append(future_month.strftime('%Y-%m'))
        
        response["forecast"] = {
            "method": "Linear Trend",
            "periods": 3,
            "data": [
                {
                    "month": forecast_months[i],
                    "predictedIncidents": round(incident_forecast[i], 1),
                    "predictedFatalities": round(fatality_forecast[i], 1),
                    "confidence": "Low" if i == 2 else "Medium"  # Further out = less confident
                }
                for i in range(3)
            ],
            "note": "Forecast uses simple linear regression on recent 6-month trend"
        }
    
    # Cache disabled for now - fix cache logic in future iteration
    # if cache:
    #     await cache.setex(cache_key, CACHE_TTL["timeseries"], json.dumps(response))
    
    return response


@router.get("/trend-comparison")
@with_timeout(seconds=15)
async def compare_state_trends(
    states: str = Query(..., description="Comma-separated list of states (max 5)"),
    months_back: int = Query(12, ge=6, le=36),
    db: Session = Depends(get_db)
):
    """
    Compare monthly trends across multiple states
    
    Example: ?states=Borno,Zamfara,Kaduna
    
    CACHED: 12 hours
    """
    
    state_list = [s.strip() for s in states.split(',')][:5]  # Max 5 states
    
    if not state_list:
        raise HTTPException(status_code=400, detail="No states provided")
    
    # Try cache first
    cache = await get_redis_client()
    cache_key = f"timeseries:trend_comparison:{':'.join(sorted(state_list))}:{months_back}"
    
    if cache:
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)
    
    cutoff_date = datetime.now() - timedelta(days=months_back * 30)
    
    # Query data for each state
    state_trends = {}
    
    for state in state_list:
        try:
            # Try normalized schema first  
            query = text("""
                SELECT 
                    DATE_TRUNC('month', incidence_date) as month,
                    COUNT(*) as incidents,
                    COALESCE(SUM(
                        civilian_death_male + civilian_death_female + civilian_death_unknown +
                        security_death_male + security_death_female + security_death_unknown
                    ), 0) as fatalities
                FROM conflicts
                WHERE incidence_date >= :cutoff_date
                AND state_id = (SELECT id FROM states WHERE name = :state)
                GROUP BY DATE_TRUNC('month', incidence_date)
                ORDER BY month
            """)
            result = db.execute(query, {'cutoff_date': cutoff_date, 'state': state}).fetchall()
        except Exception:
            # Fallback to legacy schema
            query = text("""
                SELECT 
                    DATE(event_date - (DAY(event_date) - 1) * INTERVAL '1 day') as month,
                    COUNT(*) as incidents,
                    COALESCE(SUM(fatalities), 0) as fatalities
                FROM conflict_events
                WHERE event_date >= :cutoff_date
                AND LOWER(state) = LOWER(:state)
                GROUP BY DATE(event_date - (DAY(event_date) - 1) * INTERVAL '1 day')
                ORDER BY month
            """)
            try:
                result = db.execute(query, {'cutoff_date': cutoff_date, 'state': state}).fetchall()
            except Exception:
                # SQLite doesn't support DATE_TRUNC or DATE math, use native SQLite
                query = text("""
                    SELECT 
                        strftime('%Y-%m', event_date) as month,
                        COUNT(*) as incidents,
                        COALESCE(SUM(fatalities), 0) as fatalities
                    FROM conflict_events
                    WHERE event_date >= :cutoff_date
                    AND LOWER(state) = LOWER(:state)
                    GROUP BY strftime('%Y-%m', event_date)
                    ORDER BY month
                """)
                result = db.execute(query, {'cutoff_date': cutoff_date.strftime('%Y-%m-%d'), 'state': state}).fetchall()
        
        if result:
            state_trends[state] = {
                "months": [row.month.strftime('%Y-%m') for row in result],
                "incidents": [row.incidents for row in result],
                "fatalities": [int(row.fatalities) for row in result],
                "total": sum(row.incidents for row in result),
                "avgPerMonth": round(statistics.mean([row.incidents for row in result]), 1)
            }
    
    if not state_trends:
        # Return empty comparison instead of error
        return {
            "comparison": {state: {"months": [], "incidents": [], "fatalities": [], "total": 0, "avgPerMonth": 0} for state in state_list},
            "timeRange": f"{months_back} months",
            "generatedAt": datetime.now().isoformat(),
            "message": "No data available for selected states"
        }
    
    response = {
        "comparison": state_trends,
        "timeRange": f"{months_back} months",
        "generatedAt": datetime.now().isoformat()
    }
    
    # Cache for 12 hours
    if cache:
        await cache.set(cache_key, json.dumps(response), ex=43200)
    
    return response


@router.get("/seasonal-analysis")
@with_timeout(seconds=15)
async def analyze_seasonal_patterns(
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Detect seasonal patterns in conflict data
    Groups by month of year to identify high-risk periods
    
    CACHED: 24 hours (seasonal patterns don't change frequently)
    """
    
    # Try cache first
    cache = await get_redis_client()
    cache_key = f"timeseries:seasonal_analysis:{state or 'all'}"
    
    if cache:
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)
    
    if state:
        query = text("""
            SELECT 
                EXTRACT(MONTH FROM incidence_date) as month_num,
                TO_CHAR(incidence_date, 'Month') as month_name,
                COUNT(*) as incidents,
                COALESCE(SUM(
                    civilian_death_male + civilian_death_female + civilian_death_unknown +
                    security_death_male + security_death_female + security_death_unknown
                ), 0) as fatalities,
                COALESCE(AVG(
                    civilian_death_male + civilian_death_female + civilian_death_unknown +
                    security_death_male + security_death_female + security_death_unknown
                ), 0) as avg_fatalities_per_incident
            FROM conflicts
            WHERE state_id = (SELECT id FROM states WHERE name = :state)
            AND incidence_date IS NOT NULL
            GROUP BY EXTRACT(MONTH FROM incidence_date), TO_CHAR(incidence_date, 'Month')
            ORDER BY month_num
        """)
        result = db.execute(query, {'state': state}).fetchall()
    else:
        query = text("""
            SELECT 
                EXTRACT(MONTH FROM incidence_date) as month_num,
                TO_CHAR(incidence_date, 'Month') as month_name,
                COUNT(*) as incidents,
                COALESCE(SUM(
                    civilian_death_male + civilian_death_female + civilian_death_unknown +
                    security_death_male + security_death_female + security_death_unknown
                ), 0) as fatalities,
                COALESCE(AVG(
                    civilian_death_male + civilian_death_female + civilian_death_unknown +
                    security_death_male + security_death_female + security_death_unknown
                ), 0) as avg_fatalities_per_incident
            FROM conflicts
            WHERE incidence_date IS NOT NULL
            GROUP BY EXTRACT(MONTH FROM incidence_date), TO_CHAR(incidence_date, 'Month')
            ORDER BY month_num
        """)
        result = db.execute(query).fetchall()
    
    if not result:
        # Return graceful empty response instead of 404 error
        return {
            "state": state or "All States",
            "seasonalPattern": [],
            "analysis": {
                "highRiskMonths": [],
                "avgIncidentsPerMonth": 0,
                "message": "No data available for this period"
            },
            "status": "ok",
            "cached": False
        }
    
    seasonal_data = [
        {
            "month": (row.month_name or "").strip(),
            "monthNumber": int(row.month_num) if row.month_num is not None else 0,
            "totalIncidents": row.incidents or 0,
            "totalFatalities": int(row.fatalities) if row.fatalities is not None else 0,
            "avgFatalitiesPerIncident": round(float(row.avg_fatalities_per_incident), 2) if row.avg_fatalities_per_incident is not None else 0,
            "riskLevel": "High" if row.incidents > statistics.mean([r.incidents for r in result]) else "Normal"
        }
        for row in result
    ]
    
    # Identify high-risk months
    incidents_by_month = [d["totalIncidents"] for d in seasonal_data]
    mean_incidents = statistics.mean(incidents_by_month)
    high_risk_months = [d["month"] for d in seasonal_data if d["totalIncidents"] > mean_incidents * 1.2]
    
    response = {
        "state": state or "All States",
        "seasonalPattern": seasonal_data,
        "analysis": {
            "highRiskMonths": high_risk_months,
            "avgIncidentsPerMonth": round(mean_incidents, 1),
            "peakMonth": max(seasonal_data, key=lambda x: x["totalIncidents"])["month"],
            "lowestMonth": min(seasonal_data, key=lambda x: x["totalIncidents"])["month"]
        }
    }
    
    # Cache for 24 hours
    if cache:
        await cache.set(cache_key, json.dumps(response), ex=86400)
    
    return response
