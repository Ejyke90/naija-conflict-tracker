"""
Dashboard API endpoints for frontend data consumption
Transforms NLP pipeline results into UI-ready format
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func

# Add database imports
from app.db.database import get_db
from app.models.conflict import Conflict as ConflictModel

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

def load_latest_pipeline_results() -> Dict[str, Any]:
    """Load the most recent pipeline results"""
    try:
        # Look for pipeline results in data directory
        data_dir = Path(__file__).parent.parent.parent / "data"
        
        # Check for latest results file
        results_files = list(data_dir.glob("**/events_*.json"))
        if not results_files:
            # Fallback to pipeline_results.json
            pipeline_results = Path(__file__).parent.parent.parent / "pipeline_results.json"
            if pipeline_results.exists():
                with open(pipeline_results, 'r') as f:
                    return json.load(f)
            return {"events": [], "stats": {}}
        
        # Get the most recent file
        latest_file = max(results_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            return json.load(f)
            
    except Exception as e:
        print(f"Error loading pipeline results: {str(e)}")
        return {"events": [], "stats": {}}

def transform_event_for_ui(event: Dict[str, Any]) -> Dict[str, Any]:
    """Transform pipeline event to UI format"""
    return {
        "id": event.get("event_id", hash(str(event))),
        "date": event.get("incident_date", datetime.now().strftime("%Y-%m-%d")),
        "location": f"{event.get('location', {}).get('state', 'Unknown')} State",
        "type": event.get("crisis_type", "Unknown").title(),
        "casualties": event.get("fatalities", 0) + event.get("injuries", 0),
        "fatalities": event.get("fatalities", 0),
        "injuries": event.get("injuries", 0),
        "status": "verified" if event.get("verification_status") == "auto_publish" else "reported",
        "confidence_score": event.get("confidence_score", 0.0),
        "source_url": event.get("source_url", ""),
        "raw_location": event.get("location", {}),
        "actor_primary": event.get("actor_primary", "Unknown"),
        "actor_secondary": event.get("actor_secondary")
    }

@router.get("/stats")
async def get_dashboard_stats(days: int = Query(30, description="Number of days to look back"), db: Session = Depends(get_db)):
    """Get dashboard statistics from database"""
    try:
        # Query database for statistics
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Total incidents
        total_incidents = db.query(ConflictModel).filter(
            ConflictModel.event_date >= cutoff_date
        ).count()
        
        # Total casualties
        casualty_sums = db.query(
            func.sum(ConflictModel.fatalities_male + ConflictModel.fatalities_female + ConflictModel.fatalities_unknown).label('fatalities'),
            func.sum(ConflictModel.injured_male + ConflictModel.injured_female + ConflictModel.injured_unknown).label('injuries')
        ).filter(ConflictModel.event_date >= cutoff_date).first()
        
        total_fatalities = casualty_sums.fatalities or 0
        total_injuries = casualty_sums.injuries or 0
        total_casualties = total_fatalities + total_injuries
        
        # States affected
        states_count = db.query(
            func.count(func.distinct(ConflictModel.state))
        ).filter(ConflictModel.event_date >= cutoff_date).scalar()
        
        # Crisis types
        crisis_types = db.query(
            ConflictModel.archetype,
            func.count(ConflictModel.id).label('count')
        ).filter(ConflictModel.event_date >= cutoff_date).group_by(
            ConflictModel.archetype
        ).all()
        
        crisis_types_dict = {ct.archetype: ct.count for ct in crisis_types}
        
        # State breakdown
        state_breakdown = db.query(
            ConflictModel.state,
            func.count(ConflictModel.id).label('incidents')
        ).filter(ConflictModel.event_date >= cutoff_date).group_by(
            ConflictModel.state
        ).all()
        
        state_breakdown_dict = {sb.state: sb.incidents for sb in state_breakdown}
        
        # Active hotspots (states with 3+ incidents)
        active_hotspots = len([s for s in state_breakdown if s.incidents >= 3])
        
        return {
            "total_incidents": total_incidents,
            "total_fatalities": total_fatalities,
            "total_injuries": total_injuries,
            "total_casualties": total_casualties,
            "states_affected": states_count or 0,
            "active_hotspots": active_hotspots,
            "crisis_types": crisis_types_dict,
            "state_breakdown": state_breakdown_dict,
            "period_days": days,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

@router.get("/recent-incidents")
async def get_recent_incidents(
    limit: int = Query(10, description="Number of incidents to return"),
    days: int = Query(7, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """Get recent incidents for the dashboard"""
    try:
        # Query database for recent incidents
        cutoff_date = datetime.now() - timedelta(days=days)
        
        incidents = db.query(ConflictModel).filter(
            ConflictModel.event_date >= cutoff_date
        ).order_by(ConflictModel.event_date.desc()).limit(limit).all()
        
        # Transform for UI
        ui_incidents = []
        for incident in incidents:
            ui_incidents.append({
                "id": str(incident.id),
                "date": incident.event_date.strftime("%Y-%m-%d"),
                "location": f"{incident.state}, {incident.lga or ''}",
                "type": incident.archetype or "Unknown",
                "casualties": (incident.fatalities_male or 0) + (incident.fatalities_female or 0) + (incident.fatalities_unknown or 0),
                "fatalities": (incident.fatalities_male or 0) + (incident.fatalities_female or 0) + (incident.fatalities_unknown or 0),
                "injuries": (incident.injured_male or 0) + (incident.injured_female or 0) + (incident.injured_unknown or 0),
                "perpetrator": incident.perpetrator_group or "Unknown",
                "description": incident.description or ""
            })
        
        total_available = db.query(ConflictModel).filter(
            ConflictModel.event_date >= cutoff_date
        ).count()
        
        return {
            "incidents": ui_incidents,
            "total_available": total_available,
            "showing": len(ui_incidents),
            "period_days": days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching incidents: {str(e)}")

@router.get("/incidents/by-state/{state}")
async def get_incidents_by_state(
    state: str,
    limit: int = Query(20, description="Number of incidents to return"),
    days: int = Query(30, description="Number of days to look back")
):
    """Get incidents for a specific state"""
    try:
        # Load pipeline results
        results = load_latest_pipeline_results()
        events = results.get("events", [])
        
        # Filter by state and date
        cutoff_date = datetime.now() - timedelta(days=days)
        state_events = []
        
        for event in events:
            try:
                event_date = datetime.strptime(event.get("incident_date", ""), "%Y-%m-%d")
                event_state = event.get("location", {}).get("state", "").lower()
                
                if event_date >= cutoff_date and event_state == state.lower():
                    state_events.append(event)
            except (ValueError, TypeError):
                continue
        
        # Sort by date (most recent first)
        state_events.sort(
            key=lambda x: x.get("incident_date", ""), 
            reverse=True
        )
        
        # Transform for UI and limit results
        ui_events = [
            transform_event_for_ui(event) 
            for event in state_events[:limit]
        ]
        
        return {
            "state": state.title(),
            "incidents": ui_events,
            "total_available": len(state_events),
            "showing": len(ui_events),
            "period_days": days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching state incidents: {str(e)}")

@router.get("/pipeline-status")
async def get_pipeline_status():
    """Get the status of the latest NLP pipeline run"""
    try:
        # Check for pipeline results file
        pipeline_results = Path(__file__).parent.parent.parent / "pipeline_results.json"
        
        if not pipeline_results.exists():
            return {
                "status": "no_data",
                "message": "No pipeline results available",
                "last_run": None
            }
        
        with open(pipeline_results, 'r') as f:
            results = json.load(f)
        
        return {
            "status": results.get("status", "unknown"),
            "last_run": results.get("timestamp"),
            "stats": results.get("stats", {}),
            "duration": results.get("duration_seconds", 0),
            "success_rate": results.get("success_rate", 0),
            "auto_publish_rate": results.get("auto_publish_rate", 0)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading pipeline status: {str(e)}",
            "last_run": None
        }

@router.get("/health")
async def health_check():
    """Simple health check without database"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "dashboard-api"
    }

@router.get("/health/db")
async def health_check_db(db: Session = Depends(get_db)):
    """Health check with database verification"""
    try:
        # Check database connection
        db_count = db.query(ConflictModel).count()
        print(f"Database count: {db_count}")
        return {
            "status": "healthy", 
            "database": "connected",
            "conflicts_count": db_count,
            "timestamp": datetime.now().isoformat(),
            "service": "dashboard-api"
        }
    except Exception as e:
        print(f"Database error: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "service": "dashboard-api"
        }
