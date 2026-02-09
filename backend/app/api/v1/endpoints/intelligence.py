"""
Conflict Intelligence Endpoints - Archetypes, Triggers, and Risk Analysis
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.db.database import get_db
from app.core.cache import get_redis_client, cache_key, CACHE_TTL
from app.models.conflict import Conflict
from app.models.reference import State
import json

router = APIRouter()


# Conflict Archetype Mappings (based on description keywords)
ARCHETYPE_KEYWORDS = {
    "Farmer-Herder": ["farmer", "herder", "cattle", "grazing", "farmland", "pastoralist"],
    "Banditry": ["bandit", "kidnap", "abduct", "ransom", "highway", "armed robbery"],
    "Terrorism": ["boko haram", "iswap", "terrorist", "insurgent", "suicide", "ied"],
    "Communal Clash": ["communal", "ethnic", "tribal", "village clash", "inter-communal"],
    "Resource Conflict": ["mining", "oil", "land dispute", "boundary", "resource"],
    "Political Violence": ["election", "political", "party", "campaign", "polling"],
    "Cultism": ["cult", "gang", "rival group"],
    "Security Operations": ["military", "police", "operation", "raid", "security force"],
}

# High-Risk Infrastructure Proximity Thresholds (km)
RISK_PROXIMITY_KM = {
    "oil_wells": 50,
    "mines": 30,
    "borders": 100,
    "markets": 20,
}


@router.get("/archetypes")
async def get_conflict_archetypes(
    months_back: int = Query(12, ge=1, le=60),
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Classify conflicts by archetype based on description analysis
    Returns distribution and trends for each conflict type
    
    CACHED: 1 hour (archetypes change slowly)
    """
    cache = await get_redis_client()
    cache_key_str = f"intelligence:archetypes:{months_back}:{state or 'all'}"
    
    # Try cache first
    cached = await cache.get(cache_key_str)
    if cached:
        return json.loads(cached)
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months_back * 30)
    
    # Build base query
    query = db.query(Conflict).filter(
        Conflict.incidence_date >= start_date,
        Conflict.incidence_date <= end_date
    )
    
    if state:
        state_obj = db.query(State).filter(State.name == state).first()
        if state_obj:
            query = query.filter(Conflict.state_id == state_obj.id)
    
    conflicts = query.all()
    
    # Classify by archetype
    archetype_stats = {name: {"count": 0, "fatalities": 0, "incidents": []} 
                      for name in ARCHETYPE_KEYWORDS.keys()}
    archetype_stats["Unclassified"] = {"count": 0, "fatalities": 0, "incidents": []}
    
    for conflict in conflicts:
        description = (conflict.description or "").lower()
        classified = False
        
        for archetype, keywords in ARCHETYPE_KEYWORDS.items():
            if any(kw in description for kw in keywords):
                archetype_stats[archetype]["count"] += 1
                total_fatalities = sum([
                    conflict.civilian_death_male or 0,
                    conflict.civilian_death_female or 0,
                    conflict.civilian_death_unknown or 0,
                    conflict.security_death_male or 0,
                    conflict.security_death_female or 0,
                    conflict.security_death_unknown or 0,
                ])
                archetype_stats[archetype]["fatalities"] += total_fatalities
                archetype_stats[archetype]["incidents"].append({
                    "date": conflict.incidence_date.isoformat(),
                    "state": conflict.state.name if conflict.state else "Unknown",
                    "fatalities": total_fatalities
                })
                classified = True
                break  # Only classify to first matching archetype
        
        if not classified:
            archetype_stats["Unclassified"]["count"] += 1
    
    # Calculate trends (monthly)
    result = {
        "summary": {
            name: {
                "total_incidents": stats["count"],
                "total_fatalities": stats["fatalities"],
                "avg_fatalities_per_incident": round(stats["fatalities"] / stats["count"], 2) if stats["count"] > 0 else 0,
                "percentage": round((stats["count"] / len(conflicts)) * 100, 1) if conflicts else 0
            }
            for name, stats in archetype_stats.items()
            if stats["count"] > 0
        },
        "timeRange": f"{start_date.date()} to {end_date.date()}",
        "totalConflicts": len(conflicts),
        "generatedAt": datetime.now().isoformat()
    }
    
    # Cache for 1 hour
    await cache.setex(cache_key_str, CACHE_TTL["intelligence"], json.dumps(result))
    
    return result


@router.get("/triggers")
async def get_conflict_triggers(
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Identify conflict triggers and risk factors
    - Seasonal patterns (dry season = herder migration)
    - Infrastructure proximity (oil wells, mines)
    - Temporal patterns (market days, elections)
    
    CACHED: 2 hours (triggers are relatively stable)
    """
    cache = await get_redis_client()
    cache_key_str = f"intelligence:triggers:{state or 'all'}"
    
    cached = await cache.get(cache_key_str)
    if cached:
        return json.loads(cached)
    
    # Query conflicts from last 36 months for pattern analysis
    end_date = datetime.now()
    start_date = end_date - timedelta(days=36 * 30)
    
    query = db.query(Conflict).filter(
        Conflict.incidence_date >= start_date,
        Conflict.incidence_date <= end_date
    )
    
    if state:
        state_obj = db.query(State).filter(State.name == state).first()
        if state_obj:
            query = query.filter(Conflict.state_id == state_obj.id)
    
    conflicts = query.all()
    
    # Analyze seasonal patterns
    seasonal_risk = {
        "Dry Season (Nov-Mar)": 0,
        "Rainy Season (Apr-Oct)": 0
    }
    
    month_distribution = [0] * 12
    
    for conflict in conflicts:
        month = conflict.incidence_date.month
        month_distribution[month - 1] += 1
        
        # Nov-Mar = Dry season (herder migration south)
        if month in [11, 12, 1, 2, 3]:
            seasonal_risk["Dry Season (Nov-Mar)"] += 1
        else:
            seasonal_risk["Rainy Season (Apr-Oct)"] += 1
    
    # Identify high-risk months (>20% above average)
    avg_monthly = sum(month_distribution) / 12
    high_risk_months = [
        {
            "month": datetime(2000, i+1, 1).strftime("%B"),
            "incidents": month_distribution[i],
            "risk_level": "High" if month_distribution[i] > avg_monthly * 1.2 else "Normal"
        }
        for i in range(12)
        if month_distribution[i] > 0
    ]
    
    # Infrastructure risk indicators (would need geospatial data)
    # For now, return states with known resource conflicts
    resource_states = ["Rivers", "Delta", "Bayelsa", "Zamfara", "Niger"]  # Oil/Mining states
    
    result = {
        "seasonal_patterns": {
            "dry_season_conflicts": seasonal_risk["Dry Season (Nov-Mar)"],
            "rainy_season_conflicts": seasonal_risk["Rainy Season (Apr-Oct)"],
            "primary_trigger": "Dry Season (Nov-Mar)" if seasonal_risk["Dry Season (Nov-Mar)"] > seasonal_risk["Rainy Season (Apr-Oct)"] else "Rainy Season (Apr-Oct)",
            "insight": "Dry season sees increased farmer-herder conflicts due to cattle migration southward" if seasonal_risk["Dry Season (Nov-Mar)"] > seasonal_risk["Rainy Season (Apr-Oct)"] else "Rainy season conflicts often linked to displacement and flooding"
        },
        "high_risk_months": sorted(high_risk_months, key=lambda x: x["incidents"], reverse=True)[:6],
        "resource_conflict_zones": {
            "oil_states": ["Rivers", "Delta", "Bayelsa", "Akwa Ibom"],
            "mining_states": ["Zamfara", "Niger", "Plateau", "Taraba"],
            "border_states": ["Borno", "Yobe", "Adamawa", "Sokoto", "Kebbi"]
        },
        "trigger_recommendations": [
            {
                "trigger": "Dry Season Migration",
                "action": "Increase monitoring of herder routes Nov-Mar",
                "risk_level": "High"
            },
            {
                "trigger": "Resource Infrastructure",
                "action": "Enhanced security at oil/mining sites",
                "risk_level": "Medium"
            },
            {
                "trigger": "Election Cycles",
                "action": "Monitor political violence during campaign periods",
                "risk_level": "Medium"
            }
        ],
        "generatedAt": datetime.now().isoformat()
    }
    
    # Cache for 2 hours
    await cache.setex(cache_key_str, CACHE_TTL["intelligence"], json.dumps(result))
    
    return result


@router.get("/hotspots")
async def get_conflict_hotspots(
    days_back: int = Query(30, ge=7, le=180),
    min_incidents: int = Query(3, ge=1),
    db: Session = Depends(get_db)
):
    """
    Identify current conflict hotspots with recent activity surges
    Returns states/LGAs with abnormal conflict rates
    
    CACHED: 30 minutes (hotspots change frequently)
    """
    cache = await get_redis_client()
    cache_key_str = f"intelligence:hotspots:{days_back}:{min_incidents}"
    
    cached = await cache.get(cache_key_str)
    if cached:
        return json.loads(cached)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    # Get recent conflicts grouped by state
    hotspot_query = db.query(
        State.name,
        func.count(Conflict.id).label('incident_count'),
        func.sum(
            Conflict.civilian_death_male +
            Conflict.civilian_death_female +
            Conflict.civilian_death_unknown +
            Conflict.security_death_male +
            Conflict.security_death_female +
            Conflict.security_death_unknown
        ).label('total_fatalities')
    ).join(State, Conflict.state_id == State.id).filter(
        Conflict.incidence_date >= start_date
    ).group_by(State.name).having(
        func.count(Conflict.id) >= min_incidents
    ).order_by(func.count(Conflict.id).desc()).all()
    
    hotspots = [
        {
            "state": hs.name,
            "incidents": hs.incident_count,
            "fatalities": int(hs.total_fatalities or 0),
            "incidents_per_day": round(hs.incident_count / days_back, 2),
            "severity": "Critical" if hs.incident_count > 10 else "High" if hs.incident_count > 5 else "Moderate"
        }
        for hs in hotspot_query
    ]
    
    result = {
        "hotspots": hotspots,
        "period": f"Last {days_back} days",
        "totalHotspots": len(hotspots),
        "criticalZones": len([h for h in hotspots if h["severity"] == "Critical"]),
        "generatedAt": datetime.now().isoformat()
    }
    
    # Cache for 30 minutes
    await cache.setex(cache_key_str, 1800, json.dumps(result))
    
    return result


@router.get("/risk-score/{state_name}")
async def get_state_risk_score(
    state_name: str,
    db: Session = Depends(get_db)
):
    """
    Calculate comprehensive risk score for a state
    Based on: recent incidents, trend, seasonality, archetypes
    
    Returns score 0-100 (100 = highest risk)
    
    CACHED: 1 hour
    """
    cache = await get_redis_client()
    cache_key_str = f"intelligence:risk_score:{state_name}"
    
    cached = await cache.get(cache_key_str)
    if cached:
        return json.loads(cached)
    
    state_obj = db.query(State).filter(State.name == state_name).first()
    if not state_obj:
        raise HTTPException(status_code=404, detail="State not found")
    
    # Last 30 days vs previous 30 days
    now = datetime.now()
    recent_start = now - timedelta(days=30)
    previous_start = now - timedelta(days=60)
    
    recent_count = db.query(func.count(Conflict.id)).filter(
        Conflict.state_id == state_obj.id,
        Conflict.incidence_date >= recent_start
    ).scalar()
    
    previous_count = db.query(func.count(Conflict.id)).filter(
        Conflict.state_id == state_obj.id,
        Conflict.incidence_date >= previous_start,
        Conflict.incidence_date < recent_start
    ).scalar()
    
    # Calculate trend
    trend = "Increasing" if recent_count > previous_count else "Stable" if recent_count == previous_count else "Decreasing"
    trend_score = 30 if recent_count > previous_count * 1.2 else 15 if recent_count > previous_count else 0
    
    # Base score from recent incidents
    incident_score = min(recent_count * 2, 40)
    
    # Fatality severity
    recent_fatalities = db.query(
        func.sum(
            Conflict.civilian_death_male +
            Conflict.civilian_death_female +
            Conflict.civilian_death_unknown +
            Conflict.security_death_male +
            Conflict.security_death_female +
            Conflict.security_death_unknown
        )
    ).filter(
        Conflict.state_id == state_obj.id,
        Conflict.incidence_date >= recent_start
    ).scalar() or 0
    
    fatality_score = min(int(recent_fatalities), 30)
    
    # Total risk score
    total_score = min(incident_score + trend_score + fatality_score, 100)
    
    # Risk level
    if total_score >= 70:
        risk_level = "Critical"
        color = "#DC2626"
    elif total_score >= 50:
        risk_level = "High"
        color = "#F59E0B"
    elif total_score >= 30:
        risk_level = "Moderate"
        color = "#3B82F6"
    else:
        risk_level = "Low"
        color = "#10B981"
    
    result = {
        "state": state_name,
        "riskScore": total_score,
        "riskLevel": risk_level,
        "color": color,
        "components": {
            "incidentScore": incident_score,
            "trendScore": trend_score,
            "fatalityScore": fatality_score
        },
        "metrics": {
            "recentIncidents": recent_count,
            "previousIncidents": previous_count,
            "recentFatalities": int(recent_fatalities),
            "trend": trend
        },
        "recommendation": f"{'Immediate intervention required' if risk_level == 'Critical' else 'Enhanced monitoring recommended' if risk_level == 'High' else 'Continue routine monitoring'}",
        "generatedAt": datetime.now().isoformat()
    }
    
    # Cache for 1 hour
    await cache.setex(cache_key_str, CACHE_TTL["intelligence"], json.dumps(result))
    
    return result
