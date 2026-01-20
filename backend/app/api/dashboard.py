"""
Dashboard API endpoints for frontend data consumption
Transforms NLP pipeline results into UI-ready format
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

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
async def get_dashboard_stats(days: int = Query(30, description="Number of days to look back")):
    """Get dashboard statistics for the specified time period"""
    try:
        # Load pipeline results
        results = load_latest_pipeline_results()
        events = results.get("events", [])
        
        # Filter events by date range
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_events = []
        
        for event in events:
            try:
                event_date = datetime.strptime(event.get("incident_date", ""), "%Y-%m-%d")
                if event_date >= cutoff_date:
                    recent_events.append(event)
            except (ValueError, TypeError):
                continue
        
        # Calculate statistics
        total_incidents = len(recent_events)
        total_fatalities = sum(event.get("fatalities", 0) for event in recent_events)
        total_injuries = sum(event.get("injuries", 0) for event in recent_events)
        
        # Count unique states
        states_affected = set()
        for event in recent_events:
            state = event.get("location", {}).get("state")
            if state and state != "Unknown":
                states_affected.add(state)
        
        # Calculate hotspots (states with multiple incidents)
        state_incident_counts = {}
        for event in recent_events:
            state = event.get("location", {}).get("state", "Unknown")
            state_incident_counts[state] = state_incident_counts.get(state, 0) + 1
        
        active_hotspots = sum(1 for count in state_incident_counts.values() if count >= 3)
        
        # Crisis type breakdown
        crisis_types = {}
        for event in recent_events:
            crisis_type = event.get("crisis_type", "Unknown")
            crisis_types[crisis_type] = crisis_types.get(crisis_type, 0) + 1
        
        return {
            "total_incidents": total_incidents,
            "total_fatalities": total_fatalities,
            "total_injuries": total_injuries,
            "total_casualties": total_fatalities + total_injuries,
            "states_affected": len(states_affected),
            "active_hotspots": active_hotspots,
            "crisis_types": crisis_types,
            "state_breakdown": state_incident_counts,
            "period_days": days,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")

@router.get("/recent-incidents")
async def get_recent_incidents(
    limit: int = Query(10, description="Number of incidents to return"),
    days: int = Query(7, description="Number of days to look back")
):
    """Get recent incidents for the dashboard"""
    try:
        # Load pipeline results
        results = load_latest_pipeline_results()
        events = results.get("events", [])
        
        # Filter and sort events
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_events = []
        
        for event in events:
            try:
                event_date = datetime.strptime(event.get("incident_date", ""), "%Y-%m-%d")
                if event_date >= cutoff_date:
                    recent_events.append(event)
            except (ValueError, TypeError):
                continue
        
        # Sort by date (most recent first)
        recent_events.sort(
            key=lambda x: x.get("incident_date", ""), 
            reverse=True
        )
        
        # Transform for UI and limit results
        ui_events = [
            transform_event_for_ui(event) 
            for event in recent_events[:limit]
        ]
        
        return {
            "incidents": ui_events,
            "total_available": len(recent_events),
            "showing": len(ui_events),
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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "dashboard-api"
    }
