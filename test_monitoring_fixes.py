#!/usr/bin/env python3
"""
Test script to verify the fixed monitoring endpoints
"""
import os
import sys
sys.path.append('/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/backend')

from sqlalchemy import text
from app.db.database import SessionLocal
from datetime import datetime, timedelta

def test_pipeline_status_query():
    """Test the exact query used in pipeline-status endpoint"""
    print("Testing pipeline-status query...")
    
    try:
        db = SessionLocal()
        
        # Get basic database status from conflict_events table
        conflict_count = db.execute(text("SELECT COUNT(*) FROM conflict_events")).scalar()
        
        # Get verification status
        verified_count = db.execute(text("SELECT COUNT(*) FROM conflict_events WHERE verified = true")).scalar()
        unverified_count = conflict_count - verified_count
        
        # Get recent activity (last 30 days to be more reasonable)
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
        
        print("✅ Pipeline Status Query Results:")
        print(f"  📊 Total records: {result['total_records']}")
        print(f"  ✅ Verified events: {result['verified_events']}")
        print(f"  ⏳ Unverified events: {result['unverified_events']}")
        print(f"  📈 Recent incidents (30d): {result['recent_incidents']}")
        print(f"  💀 Records with fatalities: {result['records_with_fatalities']}")
        print(f"  📅 Last activity: {result['last_activity']}")
        print(f"  🚨 Active alerts (7d): {result['active_alerts']}")
        
        # Verify against expected values from handoff
        print("\n🔍 Validation against handoff document:")
        if result['total_records'] == 6993:
            print("✅ Total records match handoff (6,993)")
        else:
            print(f"❌ Total records mismatch: expected 6993, got {result['total_records']}")
            
        if result['verified_events'] == 11:
            print("✅ Verified events match handoff (11)")
        else:
            print(f"❌ Verified events mismatch: expected 11, got {result['verified_events']}")
            
        if result['unverified_events'] == 6982:
            print("✅ Unverified events match handoff (6,982)")
        else:
            print(f"❌ Unverified events mismatch: expected 6982, got {result['unverified_events']}")
        
        db.close()
        return result
        
    except Exception as e:
        print(f"❌ Pipeline status query error: {e}")
        return None

def test_recent_events_query():
    """Test the exact query used in recent-events endpoint"""
    print("\nTesting recent-events query...")
    
    try:
        db = SessionLocal()
        
        # Test with different timeframes
        for hours in [24, 168, 720]:  # 1 day, 1 week, 1 month
            days_back = max(1, hours // 24)
            cutoff_date = datetime.now().date() - timedelta(days=days_back)
            
            query = text("""
                SELECT 
                    id,
                    event_type,
                    fatalities,
                    event_date,
                    state,
                    location,
                    verified,
                    confidence_level,
                    source,
                    created_at
                FROM conflict_events
                WHERE event_date >= :cutoff_date
                ORDER BY event_date DESC
                LIMIT 100
            """)
            
            results = db.execute(query, {"cutoff_date": cutoff_date}).fetchall()
            
            print(f"📊 Recent events ({hours}h = {days_back}d): {len(results)} records")
            
            if results:
                sample = results[0]
                print(f"  📋 Sample event:")
                print(f"    - ID: {sample.id}")
                print(f"    - Type: {sample.event_type}")
                print(f"    - Fatalities: {sample.fatalities}")
                print(f"    - Date: {sample.event_date}")
                print(f"    - State: {sample.state}")
                print(f"    - Verified: {sample.verified}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Recent events query error: {e}")

def test_data_quality_metrics():
    """Test data quality calculations"""
    print("\nTesting data quality metrics...")
    
    try:
        db = SessionLocal()
        
        # Test various data quality metrics
        total_records = db.execute(text("SELECT COUNT(*) FROM conflict_events")).scalar()
        
        # Verification rate
        verified_count = db.execute(text("SELECT COUNT(*) FROM conflict_events WHERE verified = true")).scalar()
        verification_rate = (verified_count / total_records * 100) if total_records > 0 else 0
        
        # Fatalities ratio
        fatalities_count = db.execute(text("SELECT COUNT(*) FROM conflict_events WHERE fatalities > 0")).scalar()
        fatalities_ratio = (fatalities_count / total_records * 100) if total_records > 0 else 0
        
        # States coverage
        states_count = db.execute(text("SELECT COUNT(DISTINCT state) FROM conflict_events")).scalar()
        
        # Date range
        min_date = db.execute(text("SELECT MIN(event_date) FROM conflict_events")).scalar()
        max_date = db.execute(text("SELECT MAX(event_date) FROM conflict_events")).scalar()
        
        print("📊 Data Quality Results:")
        print(f"  📈 Verification rate: {verification_rate:.1f}%")
        print(f"  💀 Fatalities ratio: {fatalities_ratio:.1f}%")
        print(f"  🗺️  States covered: {states_count}")
        print(f"  📅 Date range: {min_date} to {max_date}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Data quality metrics error: {e}")

if __name__ == "__main__":
    print("🔧 Testing Fixed Monitoring Endpoints")
    print("=" * 60)
    
    test_pipeline_status_query()
    test_recent_events_query()
    test_data_quality_metrics()
    
    print("\n" + "=" * 60)
    print("✅ Monitoring endpoint testing complete")
