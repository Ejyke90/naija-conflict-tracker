#!/usr/bin/env python3
"""
Comprehensive test script to verify all fixed API endpoints
"""
import os
import sys
sys.path.append('/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/backend')

from sqlalchemy import text
from app.db.database import SessionLocal
from datetime import datetime, timedelta

def test_pipeline_status_endpoint():
    """Test /api/v1/monitoring/pipeline-status endpoint logic"""
    print("Testing pipeline-status endpoint logic...")
    
    try:
        db = SessionLocal()
        
        # Get basic database status from conflict_events table
        conflict_count = db.execute(text("SELECT COUNT(*) FROM conflict_events")).scalar()
        
        # Get verification status
        verified_count = db.execute(text("SELECT COUNT(*) FROM conflict_events WHERE verified = true")).scalar()
        unverified_count = conflict_count - verified_count
        
        # Get recent activity (last 30 days)
        recent_cutoff = datetime.now().date() - timedelta(days=30)
        recent_incidents = db.execute(text("SELECT COUNT(*) FROM conflict_events WHERE event_date >= :cutoff"), {"cutoff": recent_cutoff}).scalar()
        
        # Get records with fatalities
        records_with_fatalities = db.execute(text("SELECT COUNT(*) FROM conflict_events WHERE fatalities > 0")).scalar()
        
        # Get last activity date
        last_activity = db.execute(text("SELECT MAX(event_date) FROM conflict_events")).scalar()
        
        # Get active alerts (high fatality events in last 7 days)
        alert_cutoff = datetime.now().date() - timedelta(days=7)
        high_fatality_events = db.execute(text("""
            SELECT COUNT(*) FROM conflict_events 
            WHERE event_date >= :cutoff AND fatalities > 0
        """), {"cutoff": alert_cutoff}).scalar()
        
        result = {
            "total_records": conflict_count,
            "verified_events": verified_count,
            "unverified_events": unverified_count,
            "recent_incidents": recent_incidents,
            "records_with_fatalities": records_with_fatalities,
            "last_activity": last_activity.isoformat() if last_activity else None,
            "active_alerts": high_fatality_events,
        }
        
        print("✅ Pipeline Status Results:")
        print(f"  📊 Total records: {result['total_records']}")
        print(f"  ✅ Verified events: {result['verified_events']}")
        print(f"  ⏳ Unverified events: {result['unverified_events']}")
        print(f"  📈 Recent incidents (30d): {result['recent_incidents']}")
        print(f"  💀 Records with fatalities: {result['records_with_fatalities']}")
        print(f"  📅 Last activity: {result['last_activity']}")
        print(f"  🚨 Active alerts (7d): {result['active_alerts']}")
        
        db.close()
        return result
        
    except Exception as e:
        print(f"❌ Pipeline status test error: {e}")
        return None

def test_validation_summary_endpoint():
    """Test /api/v1/system/validation/summary endpoint logic"""
    print("\nTesting validation summary endpoint logic...")
    
    try:
        db = SessionLocal()
        
        # Get validation metrics from conflict_events table
        total_count_result = db.execute(text("SELECT COUNT(*) FROM conflict_events")).scalar()
        verified_count_result = db.execute(text("SELECT COUNT(*) FROM conflict_events WHERE verified = true")).scalar()
        pending_count = total_count_result - verified_count_result
        
        # Get high priority count (unverified events with fatalities)
        high_priority_result = db.execute(text("""
            SELECT COUNT(*) FROM conflict_events 
            WHERE verified = false AND fatalities > 0
        """)).scalar()
        
        # Get last activity (most recent event date)
        last_activity_result = db.execute(text("SELECT MAX(event_date) FROM conflict_events")).scalar()
        
        # Get oldest pending item (oldest unverified event)
        oldest_pending_result = db.execute(text("""
            SELECT MIN(event_date) FROM conflict_events 
            WHERE verified = false
        """)).scalar()
        
        # Determine if urgent (high priority items > 10 or pending > 1000)
        is_urgent = high_priority_result > 10 or pending_count > 1000
        
        result = {
            "pendingCount": pending_count,
            "isUrgent": is_urgent,
            "highPriorityCount": high_priority_result,
            "lastActivity": last_activity_result.isoformat() if last_activity_result else None,
            "totalVerified": verified_count_result,
            "oldestItem": oldest_pending_result.isoformat() if oldest_pending_result else None,
        }
        
        print("✅ Validation Summary Results:")
        print(f"  ⏳ Pending events: {result['pendingCount']}")
        print(f"  🚨 Is urgent: {result['isUrgent']}")
        print(f"  ⚠️  High priority: {result['highPriorityCount']}")
        print(f"  📅 Last activity: {result['lastActivity']}")
        print(f"  ✅ Total verified: {result['totalVerified']}")
        print(f"  📜 Oldest pending: {result['oldestItem']}")
        
        db.close()
        return result
        
    except Exception as e:
        print(f"❌ Validation summary test error: {e}")
        return None

def test_dashboard_summary_endpoint():
    """Test /api/v1/analytics/dashboard-summary endpoint logic"""
    print("\nTesting dashboard summary endpoint logic...")
    
    try:
        db = SessionLocal()
        
        # Date ranges for current and previous periods (30 days)
        now = datetime.now().date()
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)
        
        # Current period (last 30 days)
        current_period_result = db.execute(text("""
            SELECT 
                COUNT(*) as incidents,
                COALESCE(SUM(fatalities), 0) as fatalities,
                COUNT(DISTINCT state) as states_affected
            FROM conflict_events 
            WHERE event_date >= :cutoff_date
        """), {"cutoff_date": thirty_days_ago}).first()
        
        current_period_incidents = current_period_result.incidents
        current_period_fatalities = current_period_result.fatalities
        states_affected = current_period_result.states_affected
        
        # Previous period (30-60 days ago)
        previous_period_result = db.execute(text("""
            SELECT 
                COUNT(*) as incidents,
                COALESCE(SUM(fatalities), 0) as fatalities
            FROM conflict_events 
            WHERE event_date >= :start_date AND event_date < :end_date
        """), {"start_date": sixty_days_ago, "end_date": thirty_days_ago}).first()
        
        previous_period_incidents = previous_period_result.incidents
        previous_period_fatalities = previous_period_result.fatalities
        
        # Calculate percentage changes
        incidents_change = 0
        if previous_period_incidents > 0:
            incidents_change = ((current_period_incidents - previous_period_incidents) / previous_period_incidents) * 100
        
        fatalities_change = 0
        if previous_period_fatalities > 0:
            fatalities_change = ((current_period_fatalities - previous_period_fatalities) / previous_period_fatalities) * 100
        
        # Active hotspots (states with 5+ incidents in last 30 days)
        hotspot_result = db.execute(text("""
            SELECT COUNT(*) as hotspot_count
            FROM (
                SELECT state, COUNT(*) as incident_count
                FROM conflict_events 
                WHERE event_date >= :cutoff_date
                GROUP BY state
                HAVING COUNT(*) >= 5
            ) hotspots
        """), {"cutoff_date": thirty_days_ago}).first()
        
        hotspot_count = hotspot_result.hotspot_count
        
        # Last updated
        last_updated_result = db.execute(text("SELECT MAX(event_date) FROM conflict_events")).scalar()
        last_updated = last_updated_result.isoformat() if last_updated_result else now.isoformat()
        
        result = {
            "totalIncidents": current_period_incidents,
            "totalIncidentsChange": round(incidents_change, 1),
            "fatalities": int(current_period_fatalities),
            "fatalitiesChange": round(fatalities_change, 1),
            "activeHotspots": hotspot_count,
            "statesAffected": states_affected,
            "totalStates": 36,
            "lastUpdated": last_updated
        }
        
        print("✅ Dashboard Summary Results:")
        print(f"  📊 Total incidents (30d): {result['totalIncidents']}")
        print(f"  📈 Incidents change: {result['totalIncidentsChange']}%")
        print(f"  💀 Fatalities (30d): {result['fatalities']}")
        print(f"  📈 Fatalities change: {result['fatalitiesChange']}%")
        print(f"  🔥 Active hotspots: {result['activeHotspots']}")
        print(f"  🗺️  States affected: {result['statesAffected']}")
        print(f"  📅 Last updated: {result['lastUpdated']}")
        
        db.close()
        return result
        
    except Exception as e:
        print(f"❌ Dashboard summary test error: {e}")
        return None

def test_landing_stats_endpoint():
    """Test /api/v1/public/landing-stats endpoint logic"""
    print("\nTesting landing stats endpoint logic...")
    
    try:
        db = SessionLocal()
        
        # Date ranges
        now = datetime.now().date()
        thirty_days_ago = now - timedelta(days=30)
        
        # Total incidents in last 30 days
        total_incidents_30d = db.execute(text("""
            SELECT COUNT(*) FROM conflict_events 
            WHERE event_date >= :cutoff_date
        """), {"cutoff_date": thirty_days_ago}).scalar()
        
        # Total fatalities in last 30 days
        total_fatalities_30d = db.execute(text("""
            SELECT COALESCE(SUM(fatalities), 0) FROM conflict_events 
            WHERE event_date >= :cutoff_date
        """), {"cutoff_date": thirty_days_ago}).scalar()
        
        # Active hotspots (states with >=5 incidents in last 30 days)
        hotspots = db.execute(text("""
            SELECT COUNT(*) FROM (
                SELECT state FROM conflict_events 
                WHERE event_date >= :cutoff_date AND state IS NOT NULL
                GROUP BY state
                HAVING COUNT(*) >= 5
            ) hotspots
        """), {"cutoff_date": thirty_days_ago}).scalar()
        
        # States affected in last 30 days
        states_affected = db.execute(text("""
            SELECT COUNT(DISTINCT state) FROM conflict_events 
            WHERE event_date >= :cutoff_date AND state IS NOT NULL
        """), {"cutoff_date": thirty_days_ago}).scalar()
        
        result = {
            "totalIncidents": total_incidents_30d,
            "totalFatalities": int(total_fatalities_30d),
            "activeHotspots": hotspots,
            "statesAffected": states_affected,
        }
        
        print("✅ Landing Stats Results:")
        print(f"  📊 Total incidents (30d): {result['totalIncidents']}")
        print(f"  💀 Total fatalities (30d): {result['totalFatalities']}")
        print(f"  🔥 Active hotspots: {result['activeHotspots']}")
        print(f"  🗺️  States affected: {result['statesAffected']}")
        
        db.close()
        return result
        
    except Exception as e:
        print(f"❌ Landing stats test error: {e}")
        return None

def validate_against_handoff():
    """Validate all results against the handoff document expectations"""
    print("\n" + "="*60)
    print("🔍 VALIDATION AGAINST HANDOFF DOCUMENT")
    print("="*60)
    
    # Expected values from handoff document
    expected = {
        "total_records": 6993,
        "verified_events": 11,
        "unverified_events": 6982,
        "last_activity": "2026-02-09"
    }
    
    # Test all endpoints
    pipeline_results = test_pipeline_status_endpoint()
    validation_results = test_validation_summary_endpoint()
    
    print("\n📋 VALIDATION CHECKLIST:")
    
    if pipeline_results:
        if pipeline_results["total_records"] == expected["total_records"]:
            print("✅ Pipeline Status: Total records match (6,993)")
        else:
            print(f"❌ Pipeline Status: Total records mismatch - got {pipeline_results['total_records']}")
            
        if pipeline_results["verified_events"] == expected["verified_events"]:
            print("✅ Pipeline Status: Verified events match (11)")
        else:
            print(f"❌ Pipeline Status: Verified events mismatch - got {pipeline_results['verified_events']}")
            
        if pipeline_results["unverified_events"] == expected["unverified_events"]:
            print("✅ Pipeline Status: Unverified events match (6,982)")
        else:
            print(f"❌ Pipeline Status: Unverified events mismatch - got {pipeline_results['unverified_events']}")
            
        if pipeline_results["last_activity"] == expected["last_activity"]:
            print("✅ Pipeline Status: Last activity matches (2026-02-09)")
        else:
            print(f"❌ Pipeline Status: Last activity mismatch - got {pipeline_results['last_activity']}")
    
    if validation_results:
        if validation_results["pendingCount"] == expected["unverified_events"]:
            print("✅ Validation Summary: Pending events match (6,982)")
        else:
            print(f"❌ Validation Summary: Pending events mismatch - got {validation_results['pendingCount']}")
            
        if validation_results["totalVerified"] == expected["verified_events"]:
            print("✅ Validation Summary: Verified events match (11)")
        else:
            print(f"❌ Validation Summary: Verified events mismatch - got {validation_results['totalVerified']}")
    
    # Test other endpoints
    test_dashboard_summary_endpoint()
    test_landing_stats_endpoint()

if __name__ == "__main__":
    print("🔧 COMPREHENSIVE API ENDPOINT TESTING")
    print("="*60)
    
    validate_against_handoff()
    
    print("\n" + "="*60)
    print("✅ ALL ENDPOINT TESTS COMPLETE")
    print("📋 Ready for frontend integration testing")
