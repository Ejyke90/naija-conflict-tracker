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

from app.db.database import get_db

router = APIRouter()


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
async def get_monthly_trends(
    state: Optional[str] = Query(None, description="Filter by specific state"),
    months_back: int = Query(24, ge=6, le=60, description="Number of months to analyze"),
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
    
    cutoff_date = datetime.now() - timedelta(days=months_back * 30)
    
    # Build query
    if state:
        query = text("""
            SELECT 
                DATE_TRUNC('month', event_date) as month,
                COUNT(*) as incidents,
                COALESCE(SUM(fatalities), 0) as fatalities,
                COALESCE(SUM(civilian_casualties), 0) as civilian_casualties,
                COUNT(DISTINCT lga) as affected_lgas
            FROM conflicts
            WHERE event_date >= :cutoff_date
            AND state = :state
            GROUP BY DATE_TRUNC('month', event_date)
            ORDER BY month
        """)
        result = db.execute(query, {'cutoff_date': cutoff_date, 'state': state}).fetchall()
    else:
        query = text("""
            SELECT 
                DATE_TRUNC('month', event_date) as month,
                COUNT(*) as incidents,
                COALESCE(SUM(fatalities), 0) as fatalities,
                COALESCE(SUM(civilian_casualties), 0) as civilian_casualties,
                COUNT(DISTINCT state) as affected_states
            FROM conflicts
            WHERE event_date >= :cutoff_date
            GROUP BY DATE_TRUNC('month', event_date)
            ORDER BY month
        """)
        result = db.execute(query, {'cutoff_date': cutoff_date}).fetchall()
    
    if not result:
        raise HTTPException(status_code=404, detail="No data found for specified period")
    
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
    
    return response


@router.get("/trend-comparison")
async def compare_state_trends(
    states: str = Query(..., description="Comma-separated list of states (max 5)"),
    months_back: int = Query(12, ge=6, le=36),
    db: Session = Depends(get_db)
):
    """
    Compare monthly trends across multiple states
    
    Example: ?states=Borno,Zamfara,Kaduna
    """
    
    state_list = [s.strip() for s in states.split(',')][:5]  # Max 5 states
    
    if not state_list:
        raise HTTPException(status_code=400, detail="No states provided")
    
    cutoff_date = datetime.now() - timedelta(days=months_back * 30)
    
    # Query data for each state
    state_trends = {}
    
    for state in state_list:
        query = text("""
            SELECT 
                DATE_TRUNC('month', event_date) as month,
                COUNT(*) as incidents,
                COALESCE(SUM(fatalities), 0) as fatalities
            FROM conflicts
            WHERE event_date >= :cutoff_date
            AND state = :state
            GROUP BY DATE_TRUNC('month', event_date)
            ORDER BY month
        """)
        result = db.execute(query, {'cutoff_date': cutoff_date, 'state': state}).fetchall()
        
        if result:
            state_trends[state] = {
                "months": [row.month.strftime('%Y-%m') for row in result],
                "incidents": [row.incidents for row in result],
                "fatalities": [int(row.fatalities) for row in result],
                "total": sum(row.incidents for row in result),
                "avgPerMonth": round(statistics.mean([row.incidents for row in result]), 1)
            }
    
    if not state_trends:
        raise HTTPException(status_code=404, detail="No data found for specified states")
    
    return {
        "comparison": state_trends,
        "timeRange": f"{months_back} months",
        "generatedAt": datetime.now().isoformat()
    }


@router.get("/seasonal-analysis")
async def analyze_seasonal_patterns(
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Detect seasonal patterns in conflict data
    Groups by month of year to identify high-risk periods
    """
    
    if state:
        query = text("""
            SELECT 
                EXTRACT(MONTH FROM event_date) as month_num,
                TO_CHAR(event_date, 'Month') as month_name,
                COUNT(*) as incidents,
                COALESCE(SUM(fatalities), 0) as fatalities,
                COALESCE(AVG(fatalities), 0) as avg_fatalities_per_incident
            FROM conflicts
            WHERE state = :state
            GROUP BY EXTRACT(MONTH FROM event_date), TO_CHAR(event_date, 'Month')
            ORDER BY month_num
        """)
        result = db.execute(query, {'state': state}).fetchall()
    else:
        query = text("""
            SELECT 
                EXTRACT(MONTH FROM event_date) as month_num,
                TO_CHAR(event_date, 'Month') as month_name,
                COUNT(*) as incidents,
                COALESCE(SUM(fatalities), 0) as fatalities,
                COALESCE(AVG(fatalities), 0) as avg_fatalities_per_incident
            FROM conflicts
            GROUP BY EXTRACT(MONTH FROM event_date), TO_CHAR(event_date, 'Month')
            ORDER BY month_num
        """)
        result = db.execute(query).fetchall()
    
    if not result:
        raise HTTPException(status_code=404, detail="No data found")
    
    seasonal_data = [
        {
            "month": row.month_name.strip(),
            "monthNumber": int(row.month_num),
            "totalIncidents": row.incidents,
            "totalFatalities": int(row.fatalities),
            "avgFatalitiesPerIncident": round(float(row.avg_fatalities_per_incident), 2),
            "riskLevel": "High" if row.incidents > statistics.mean([r.incidents for r in result]) else "Normal"
        }
        for row in result
    ]
    
    # Identify high-risk months
    incidents_by_month = [d["totalIncidents"] for d in seasonal_data]
    mean_incidents = statistics.mean(incidents_by_month)
    high_risk_months = [d["month"] for d in seasonal_data if d["totalIncidents"] > mean_incidents * 1.2]
    
    return {
        "state": state or "All States",
        "seasonalPattern": seasonal_data,
        "analysis": {
            "highRiskMonths": high_risk_months,
            "avgIncidentsPerMonth": round(mean_incidents, 1),
            "peakMonth": max(seasonal_data, key=lambda x: x["totalIncidents"])["month"],
            "lowestMonth": min(seasonal_data, key=lambda x: x["totalIncidents"])["month"]
        }
    }
