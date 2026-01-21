"""
Conflict Index API Endpoint
Calculates and returns conflict severity metrics for Nigerian states
Based on 4 indicators: Deadliness, Civilian Danger, Geographic Diffusion, Armed Groups
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, text
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.database import get_db

router = APIRouter(prefix="/conflict-index", tags=["conflict-index"])

# Note: Using raw SQL queries since the model schema doesn't match imported data


def calculate_deadliness_score(state: str, db: Session, months: int = 12) -> float:
    """
    Calculate deadliness score (0-100)
    Formula: (Total fatalities × 0.6) + (Avg fatalities per event × 0.4)
    """
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    
    # Get total fatalities and event count
    result = db.execute(text("""
        SELECT 
            COALESCE(SUM(fatalities), 0) as total_fatalities,
            COUNT(*) as total_events
        FROM conflicts
        WHERE state = :state
        AND event_date >= :cutoff_date
    """), {'state': state, 'cutoff_date': cutoff_date}).first()
    
    total_fatalities = result.total_fatalities or 0
    total_events = result.total_events or 1
    avg_fatalities = total_fatalities / total_events if total_events > 0 else 0
    
    # Normalize to 0-100 scale
    fatality_score = min(100, (total_fatalities / 15) * 100)  # 1500+ fatalities = 100
    avg_score = min(100, (avg_fatalities / 5) * 100)  # 5+ avg fatalities = 100
    
    return (fatality_score * 0.6) + (avg_score * 0.4)


def calculate_civilian_danger(state: str, db: Session, months: int = 12) -> float:
    """
    Calculate civilian danger percentage (0-100)
    Percentage of civilian casualties vs total casualties
    """
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    
    result = db.execute(text("""
        SELECT 
            COUNT(*) as total_events,
            COALESCE(SUM(civilian_casualties), 0) as civilian_casualties,
            COALESCE(SUM(fatalities), 0) as total_fatalities
        FROM conflicts
        WHERE state = :state
        AND event_date >= :cutoff_date
    """), {'state': state, 'cutoff_date': cutoff_date}).first()
    
    total_events = result.total_events or 1
    civilian_casualties = result.civilian_casualties or 0
    total_fatalities = result.total_fatalities or 1
    
    # Calculate percentage of civilian casualties
    if total_fatalities > 0:
        return (civilian_casualties / total_fatalities) * 100
    return 0


def calculate_geographic_diffusion(state: str, db: Session, months: int = 12) -> float:
    """
    Calculate geographic diffusion percentage (0-100)
    Percentage of LGAs in the state that have experienced conflict
    """
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    
    # Count distinct LGAs with conflict events
    result = db.execute(text("""
        SELECT COUNT(DISTINCT lga) as affected_lgas
        FROM conflicts
        WHERE state = :state
        AND event_date >= :cutoff_date
        AND lga IS NOT NULL
        AND lga != ''
    """), {'state': state, 'cutoff_date': cutoff_date}).scalar()
    
    affected_lgas = result or 0
    
    # LGA counts per state
    state_lga_counts = {
        'Kano': 44, 'Lagos': 20, 'Kaduna': 23, 'Katsina': 34, 'Oyo': 33,
        'Rivers': 23, 'Bauchi': 20, 'Jigawa': 27, 'Benue': 23, 'Anambra': 21,
        'Borno': 27, 'Delta': 25, 'Imo': 27, 'Niger': 25, 'Akwa Ibom': 31,
        'Ogun': 20, 'Sokoto': 23, 'Ondo': 18, 'Osun': 30, 'Kogi': 21,
        'Zamfara': 14, 'Enugu': 17, 'Kebbi': 21, 'Edo': 18, 'Plateau': 17,
        'Adamawa': 21, 'Nasarawa': 13, 'Cross River': 18, 'Abia': 17,
        'Ekiti': 16, 'Kwara': 16, 'Gombe': 11, 'Yobe': 17, 'Taraba': 16,
        'Ebonyi': 13, 'Bayelsa': 8, 'FCT': 6, 'Fct': 6
    }
    
    total_lgas = state_lga_counts.get(state, 20)
    return (affected_lgas / total_lgas) * 100 if total_lgas > 0 else 0
    
    total_lgas = state_lga_counts.get(state, 20)  # Default to 20 if state not found
    
    return (affected_lgas / total_lgas) * 100 if total_lgas > 0 else 0


def calculate_armed_groups_count(state: str, db: Session, months: int = 12) -> int:
    """
    Count distinct armed groups active in the state
    """
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    
    result = db.execute(text("""
        SELECT COUNT(DISTINCT actor1) as armed_groups
        FROM conflicts
        WHERE state = :state
        AND event_date >= :cutoff_date
        AND actor1 IS NOT NULL
        AND actor1 != ''
    """), {'state': state, 'cutoff_date': cutoff_date}).scalar()
    
    return result or 0


def calculate_composite_score(deadliness: float, civilian_danger: float, 
                              geo_diffusion: float, armed_groups: int) -> float:
    """
    Calculate overall composite score (0-100)
    Equal weighting: 25% each indicator
    """
    # Normalize armed groups to 0-100 (25+ groups = 100)
    armed_groups_score = min(100, (armed_groups / 25) * 100)
    
    return (deadliness * 0.25) + (civilian_danger * 0.25) + \
           (geo_diffusion * 0.25) + (armed_groups_score * 0.25)


def get_severity_level(composite_score: float) -> str:
    """Classify severity based on composite score"""
    if composite_score >= 80:
        return 'extreme'
    elif composite_score >= 60:
        return 'high'
    elif composite_score >= 40:
        return 'turbulent'
    else:
        return 'moderate'


def calculate_trend(state: str, db: Session) -> str:
    """
    Calculate trend (up/down/stable) by comparing last 3 months vs previous 3
    """
    now = datetime.now()
    recent_cutoff = now - timedelta(days=90)
    previous_cutoff = now - timedelta(days=180)
    
    # Recent 3 months
    recent_count = db.execute(text("""
        SELECT COUNT(*) FROM conflicts
        WHERE state = :state
        AND event_date >= :recent_cutoff
    """), {'state': state, 'recent_cutoff': recent_cutoff}).scalar() or 0
    
    # Previous 3 months (before recent)
    previous_count = db.execute(text("""
        SELECT COUNT(*) FROM conflicts
        WHERE state = :state
        AND event_date >= :previous_cutoff
        AND event_date < :recent_cutoff
    """), {'state': state, 'previous_cutoff': previous_cutoff, 'recent_cutoff': recent_cutoff}).scalar() or 0
    
    if previous_count == 0:
        return 'stable'
    
    change_percent = ((recent_count - previous_count) / previous_count) * 100
    
    if change_percent > 10:
        return 'up'
    elif change_percent < -10:
        return 'down'
    else:
        return 'stable'


@router.get("/")
async def get_conflict_index(
    time_range: str = Query("12months", regex="^(6months|12months|24months|all)$"),
    db: Session = Depends(get_db)
):
    """
    Get conflict index rankings for all Nigerian states
    
    Returns:
        List of states with conflict metrics and rankings
    """
    # Convert time range to months
    months_map = {
        "6months": 6,
        "12months": 12,
        "24months": 24,
        "all": 120  # 10 years
    }
    months = months_map.get(time_range, 12)
    
    # Get all states with conflict data
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    states_result = db.execute(text("""
        SELECT DISTINCT state
        FROM conflicts
        WHERE state IS NOT NULL
        AND state != ''
        AND event_date >= :cutoff_date
        ORDER BY state
    """), {'cutoff_date': cutoff_date}).fetchall()
    
    state_data = []
    
    for (state,) in states_result:
        if not state:
            continue
            
        # Calculate all indicators
        deadliness = calculate_deadliness_score(state, db, months)
        civilian_danger = calculate_civilian_danger(state, db, months)
        geo_diffusion = calculate_geographic_diffusion(state, db, months)
        armed_groups = calculate_armed_groups_count(state, db, months)
        
        # Get total events and fatalities
        stats = db.execute(text("""
            SELECT 
                COUNT(*) as total_events,
                COALESCE(SUM(fatalities), 0) as total_fatalities
            FROM conflicts
            WHERE state = :state
            AND event_date >= :cutoff_date
        """), {'state': state, 'cutoff_date': cutoff_date}).first()
        
        total_events = stats.total_events or 0
        total_fatalities = stats.total_fatalities or 0
        
        # Calculate composite score and severity
        composite_score = calculate_composite_score(
            deadliness, civilian_danger, geo_diffusion, armed_groups
        )
        severity = get_severity_level(composite_score)
        trend = calculate_trend(state, db)
        
        state_data.append({
            'state': state,
            'deadliness': round(deadliness, 1),
            'civilianDanger': round(civilian_danger, 1),
            'geographicDiffusion': round(geo_diffusion, 1),
            'armedGroups': armed_groups,
            'totalEvents': total_events,
            'fatalities': total_fatalities,
            'compositeScore': round(composite_score, 1),
            'severity': severity,
            'trend': trend
        })
    
    # Sort by composite score (descending) and assign ranks
    state_data.sort(key=lambda x: x['compositeScore'], reverse=True)
    for i, data in enumerate(state_data, 1):
        data['rank'] = i
    
    return {
        'states': state_data,
        'totalStates': len(state_data),
        'timeRange': time_range,
        'generatedAt': datetime.now().isoformat()
    }


@router.get("/summary")
async def get_conflict_index_summary(
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for the conflict index
    """
    cutoff_date = datetime.now() - timedelta(days=365)
    
    # Get all summary stats in a single query for efficiency
    summary = db.execute(text("""
        SELECT 
            COUNT(*) as total_events,
            COALESCE(SUM(fatalities), 0) as total_fatalities,
            COUNT(DISTINCT state) as states_affected,
            COUNT(DISTINCT CASE WHEN actor1 IS NOT NULL AND actor1 != '' THEN actor1 END) as armed_groups
        FROM conflicts
        WHERE event_date >= :cutoff_date
    """), {'cutoff_date': cutoff_date}).first()
    
    return {
        'totalEvents': summary.total_events or 0,
        'fatalities': int(summary.total_fatalities or 0),
        'statesAffected': summary.states_affected or 0,
        'armedGroups': summary.armed_groups or 0,
        'timeRange': '12months'
    }
