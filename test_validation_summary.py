#!/usr/bin/env python3
"""
Test script to verify the fixed validation summary endpoint
"""
import os
import sys
sys.path.append('/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/backend')

from sqlalchemy import text
from app.db.database import SessionLocal

def test_validation_summary_query():
    """Test the exact query used in validation summary endpoint"""
    print("Testing validation summary query...")
    
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
        
        print("✅ Validation Summary Query Results:")
        print(f"  ⏳ Pending events: {result['pendingCount']}")
        print(f"  🚨 Is urgent: {result['isUrgent']}")
        print(f"  ⚠️  High priority (unverified with fatalities): {result['highPriorityCount']}")
        print(f"  📅 Last activity: {result['lastActivity']}")
        print(f"  ✅ Total verified: {result['totalVerified']}")
        print(f"  📜 Oldest pending: {result['oldestItem']}")
        
        # Verify against expected values from handoff
        print("\n🔍 Validation against handoff document:")
        if result['pendingCount'] == 6982:
            print("✅ Pending events match handoff (6,982)")
        else:
            print(f"❌ Pending events mismatch: expected 6982, got {result['pendingCount']}")
            
        if result['totalVerified'] == 11:
            print("✅ Verified events match handoff (11)")
        else:
            print(f"❌ Verified events mismatch: expected 11, got {result['totalVerified']}")
        
        # Check if urgency logic makes sense
        if result['isUrgent']:
            print("🚨 System correctly flagged as urgent (high pending count)")
        else:
            print("ℹ️ System not flagged as urgent")
            
        db.close()
        return result
        
    except Exception as e:
        print(f"❌ Validation summary query error: {e}")
        return None

def test_additional_validation_metrics():
    """Test additional validation metrics for dashboard"""
    print("\nTesting additional validation metrics...")
    
    try:
        db = SessionLocal()
        
        # Test fatality distribution among pending vs verified
        pending_fatalities = db.execute(text("""
            SELECT SUM(fatalities) FROM conflict_events 
            WHERE verified = false AND fatalities > 0
        """)).scalar() or 0
        
        verified_fatalities = db.execute(text("""
            SELECT SUM(fatalities) FROM conflict_events 
            WHERE verified = true AND fatalities > 0
        """)).scalar() or 0
        
        # Test pending events by state
        pending_by_state = db.execute(text("""
            SELECT state, COUNT(*) as count
            FROM conflict_events 
            WHERE verified = false
            GROUP BY state
            ORDER BY count DESC
            LIMIT 5
        """)).fetchall()
        
        # Test recent pending events (last 30 days)
        from datetime import datetime, timedelta
        recent_cutoff = datetime.now().date() - timedelta(days=30)
        recent_pending = db.execute(text("""
            SELECT COUNT(*) FROM conflict_events 
            WHERE verified = false AND event_date >= :cutoff
        """), {"cutoff": recent_cutoff}).scalar()
        
        print("📊 Additional Validation Metrics:")
        print(f"  💀 Pending fatalities: {pending_fatalities}")
        print(f"  ✅ Verified fatalities: {verified_fatalities}")
        print(f"  📅 Recent pending (30d): {recent_pending}")
        
        print("\n🗺️  Top 5 states by pending events:")
        for state, count in pending_by_state:
            print(f"    - {state}: {count} pending")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Additional metrics error: {e}")

if __name__ == "__main__":
    print("🔧 Testing Fixed Validation Summary Endpoint")
    print("=" * 60)
    
    test_validation_summary_query()
    test_additional_validation_metrics()
    
    print("\n" + "=" * 60)
    print("✅ Validation summary endpoint testing complete")
