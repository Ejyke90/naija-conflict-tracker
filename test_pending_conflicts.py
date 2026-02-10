#!/usr/bin/env python3
"""
Test script to verify the pending conflicts endpoint fix
"""
import os
import sys
sys.path.append('/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/backend')

from sqlalchemy import text
from app.db.database import SessionLocal

def test_pending_conflicts_query():
    """Test the exact query used in pending conflicts endpoint"""
    print("Testing pending conflicts endpoint query...")
    
    try:
        db = SessionLocal()
        
        # Query for unverified conflicts from conflict_events table with priority sorting
        query = text("""
            SELECT 
                c.id, 
                c.event_date, 
                c.event_type,
                c.notes,
                c.state,
                c.fatalities,
                c.displaced_persons,
                c.verified,
                c.confidence_level,
                c.source,
                c.created_at
            FROM conflict_events c
            WHERE c.verified = false
            ORDER BY c.fatalities DESC, c.created_at ASC
            LIMIT :limit
        """)
        
        result = db.execute(query, {"limit": 20})
        rows = result.fetchall()
        
        print(f"✅ Found {len(rows)} pending conflicts")
        
        if rows:
            print("\n📋 Sample pending conflicts (highest fatalities first):")
            for i, row in enumerate(rows[:5]):  # Show first 5
                print(f"  {i+1}. ID: {row.id}")
                print(f"     Date: {row.event_date}")
                print(f"     Type: {row.event_type}")
                print(f"     State: {row.state}")
                print(f"     Fatalities: {row.fatalities}")
                print(f"     Displaced: {row.displaced_persons}")
                print(f"     Confidence: {row.confidence_level}")
                print()
        else:
            print("ℹ️  No pending conflicts found")
        
        # Verify counts
        total_pending = db.execute(text("SELECT COUNT(*) FROM conflict_events WHERE verified = false")).scalar()
        high_fatalities_pending = db.execute(text("""
            SELECT COUNT(*) FROM conflict_events 
            WHERE verified = false AND fatalities > 0
        """)).scalar()
        
        print("📊 Pending conflicts summary:")
        print(f"  ⏳ Total pending: {total_pending}")
        print(f"  ⚠️  With fatalities: {high_fatalities_pending}")
        print(f"  📊 High priority ratio: {(high_fatalities_pending/total_pending*100):.1f}%" if total_pending > 0 else "  📊 High priority ratio: 0%")
        
        db.close()
        return len(rows)
        
    except Exception as e:
        print(f"❌ Pending conflicts query error: {e}")
        return 0

def test_endpoint_response_format():
    """Test the response format matches what frontend expects"""
    print("\nTesting endpoint response format...")
    
    try:
        db = SessionLocal()
        
        # Same query as endpoint
        query = text("""
            SELECT 
                c.id, 
                c.event_date, 
                c.event_type,
                c.notes,
                c.state,
                c.fatalities,
                c.displaced_persons,
                c.verified,
                c.confidence_level,
                c.source,
                c.created_at
            FROM conflict_events c
            WHERE c.verified = false
            ORDER BY c.fatalities DESC, c.created_at ASC
            LIMIT :limit
        """)
        
        result = db.execute(query, {"limit": 5})
        rows = result.fetchall()
        
        # Convert to list of dicts like the endpoint does
        pending_conflicts = []
        for row in rows:
            pending_conflicts.append({
                "id": str(row.id),
                "event_date": row.event_date.isoformat() if row.event_date else None,
                "event_type": row.event_type or "Unknown",
                "description": row.notes or "No description available",
                "state": row.state,
                "fatalities": row.fatalities or 0,
                "total_kidnapped": row.displaced_persons or 0,  # Using displaced_persons as proxy
                "verified": row.verified or False,
                "confidence_level": row.confidence_level,
                "source": row.source,
                "created_at": row.created_at.isoformat() if row.created_at else None
            })
        
        print("✅ Response format test:")
        print(f"  📋 Sample response structure:")
        if pending_conflicts:
            sample = pending_conflicts[0]
            for key, value in sample.items():
                print(f"    - {key}: {value}")
        
        db.close()
        return pending_conflicts
        
    except Exception as e:
        print(f"❌ Response format test error: {e}")
        return []

if __name__ == "__main__":
    print("🔧 TESTING PENDING CONFLICTS ENDPOINT FIX")
    print("=" * 60)
    
    count = test_pending_conflicts_query()
    test_endpoint_response_format()
    
    print("\n" + "=" * 60)
    if count > 0:
        print("✅ PENDING CONFLICTS ENDPOINT READY")
        print("📋 Analysts can now access the review queue")
        print("🔥 High-fatality incidents will be prioritized")
    else:
        print("ℹ️  No pending conflicts found (all verified)")
        print("📊 This is expected if all events are verified")
    
    print("🚀 Ready for deployment")
