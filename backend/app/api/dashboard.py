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
from app.models.conflict import ConflictEvent as ConflictModel

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
            func.sum(ConflictModel.fatalities).label('fatalities'),
            func.sum(ConflictModel.injuries).label('injuries')
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
            ConflictModel.event_type,
            func.count(ConflictModel.id).label('count')
        ).filter(ConflictModel.event_date >= cutoff_date).group_by(
            ConflictModel.event_type
        ).all()
        
        crisis_types_dict = {ct.conflict_type: ct.count for ct in crisis_types}
        
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
                "type": incident.conflict_type or "Unknown",
                "casualties": (incident.fatalities or 0) + (incident.injured or 0),
                "fatalities": (incident.fatalities or 0),
                "injuries": (incident.injured or 0),
                "perpetrator": incident.actor1 or "Unknown",
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

@router.get("/report/analysis")
async def get_conflict_analysis_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    state: Optional[str] = Query(None, description="Filter by state"),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive conflict analysis report with charts data
    For REPORT_GENERATOR_AGENT and DATAVIZ_AGENT
    """
    try:
        import traceback
        # Date range handling
        if not end_date:
            end_dt = datetime.now()
        else:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        if not start_date:
            start_dt = end_dt - timedelta(days=90)  # Default 90 days
        else:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        
        # Base query
        query = db.query(ConflictModel).filter(
            ConflictModel.event_date >= start_dt,
            ConflictModel.event_date <= end_dt
        )
        
        # State filter
        if state:
            query = query.filter(ConflictModel.state == state)
        
        incidents = query.all()
        total_incidents = len(incidents)
        
        # Calculate fatalities
        total_fatalities = sum(
            (i.fatalities or 0)
            for i in incidents
        )
        
        # Calculate injuries
        total_injuries = sum(
            (i.injured or 0)
            for i in incidents
        )
        
        # States affected
        states_affected = len(set(i.state for i in incidents if i.state))
        
        # Active hotspots (states with 5+ incidents)
        state_counts = {}
        for incident in incidents:
            if incident.state:
                state_counts[incident.state] = state_counts.get(incident.state, 0) + 1
        
        active_hotspots = len([s for s, count in state_counts.items() if count >= 5])
        
        # Regional distribution
        regional_data = {}
        for incident in incidents:
            if incident.state:
                fatalities = (incident.fatalities or 0)
                if incident.state not in regional_data:
                    regional_data[incident.state] = {
                        "incidents": 0,
                        "fatalities": 0,
                        "risk_level": "Low"
                    }
                regional_data[incident.state]["incidents"] += 1
                regional_data[incident.state]["fatalities"] += fatalities
        
        # Assign risk levels
        for state, data in regional_data.items():
            if data["incidents"] >= 20 or data["fatalities"] >= 100:
                data["risk_level"] = "Critical"
            elif data["incidents"] >= 10 or data["fatalities"] >= 50:
                data["risk_level"] = "High"
            elif data["incidents"] >= 5 or data["fatalities"] >= 20:
                data["risk_level"] = "Medium"
            else:
                data["risk_level"] = "Low"
        
        # Temporal trends (monthly aggregation)
        monthly_trends = {}
        for incident in incidents:
            if incident.event_date is None: continue
            
            try:
                month_key = incident.event_date.strftime("%Y-%m")
            except AttributeError:
                # Handle case where event_date might not be a datetime object
                print(f"Warning: Invalid date format for incident {incident.id}: {incident.event_date}")
                continue
                
            if month_key not in monthly_trends:
                monthly_trends[month_key] = {
                    "incidents": 0,
                    "fatalities": 0
                }
            monthly_trends[month_key]["incidents"] += 1
            monthly_trends[month_key]["fatalities"] += (incident.fatalities or 0)
        
        # Conflict types breakdown
        archetype_breakdown = {}
        for incident in incidents:
            archetype = incident.conflict_type or "Unknown"
            if archetype not in archetype_breakdown:
                archetype_breakdown[archetype] = {
                    "count": 0,
                    "fatalities": 0
                }
            archetype_breakdown[archetype]["count"] += 1
            archetype_breakdown[archetype]["fatalities"] += (incident.fatalities or 0)
        
        # Top affected states
        top_states = sorted(
            regional_data.items(),
            key=lambda x: x[1]["incidents"],
            reverse=True
        )[:10]
        
        # Perpetrator groups
        perpetrator_stats = {}
        for incident in incidents:
            perp = incident.actor1 or "Unknown"
            if perp not in perpetrator_stats:
                perpetrator_stats[perp] = 0
            perpetrator_stats[perp] += 1
        
        return {
            "summary": {
                "total_incidents": total_incidents,
                "total_fatalities": total_fatalities,
                "total_injuries": total_injuries,
                "states_affected": states_affected,
                "active_hotspots": active_hotspots,
                "period": {
                    "start": start_dt.strftime("%Y-%m-%d"),
                    "end": end_dt.strftime("%Y-%m-%d")
                }
            },
            "regional_distribution": [
                {
                    "region": state,
                    "incidents": data["incidents"],
                    "fatalities": data["fatalities"],
                    "risk_level": data["risk_level"]
                }
                for state, data in sorted(
                    regional_data.items(),
                    key=lambda x: x[1]["incidents"],
                    reverse=True
                )
            ],
            "temporal_trends": [
                {
                    "month": month,
                    "incidents": data["incidents"],
                    "fatalities": data["fatalities"]
                }
                for month, data in sorted(monthly_trends.items())
            ],
            "conflict_types": [
                {
                    "type": archetype,
                    "count": data["count"],
                    "fatalities": data["fatalities"]
                }
                for archetype, data in sorted(
                    archetype_breakdown.items(),
                    key=lambda x: x[1]["count"],
                    reverse=True
                )
            ],
            "top_perpetrators": [
                {
                    "group": group,
                    "incidents": count
                }
                for group, count in sorted(
                    perpetrator_stats.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            ],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
