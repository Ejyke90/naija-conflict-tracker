#!/usr/bin/env python3
"""
Test script to check database connectivity and data existence
"""
import os
import sys
sys.path.append('/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/backend')

from sqlalchemy import text
from app.db.database import engine, SessionLocal

def test_database_connection():
    """Test basic database connectivity"""
    print("Testing database connection...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            print(f"✅ Database connection successful: {result}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_table_counts():
    """Check record counts in relevant tables"""
    print("\nChecking table record counts...")
    
    try:
        db = SessionLocal()
        
        # Check conflict_events table
        try:
            result = db.execute(text("SELECT COUNT(*) FROM conflict_events")).scalar()
            print(f"📊 conflict_events table: {result} records")
        except Exception as e:
            print(f"❌ conflict_events table error: {e}")
        
        # Check conflicts table  
        try:
            result = db.execute(text("SELECT COUNT(*) FROM conflicts")).scalar()
            print(f"📊 conflicts table: {result} records")
        except Exception as e:
            print(f"❌ conflicts table error: {e}")
        
        # Check for any other conflict-related tables
        try:
            result = db.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%conflict%'
            """)).fetchall()
            print(f"📋 Conflict-related tables: {[row[0] for row in result]}")
        except Exception as e:
            print(f"❌ Table listing error: {e}")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Session error: {e}")

def check_conflict_events_schema():
    """Check the schema of conflict_events table"""
    print("\nChecking conflict_events table schema...")
    
    try:
        db = SessionLocal()
        
        # Get column information
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'conflict_events' 
            ORDER BY ordinal_position
        """)).fetchall()
        
        print("📋 conflict_events columns:")
        for row in result:
            print(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")
            
        # Check for recent data
        result = db.execute(text("""
            SELECT COUNT(*) as total, 
                   COUNT(CASE WHEN verified = true THEN 1 END) as verified,
                   MAX(event_date) as last_event_date
            FROM conflict_events
        """)).fetchone()
        
        if result:
            print(f"\n📈 conflict_events summary:")
            print(f"  - Total records: {result[0]}")
            print(f"  - Verified records: {result[1]}")
            print(f"  - Last event date: {result[2]}")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Schema check error: {e}")

def test_monitoring_query():
    """Test the actual query used in monitoring.py"""
    print("\nTesting monitoring.py query...")
    
    try:
        db = SessionLocal()
        
        # Test the query from /recent-events endpoint
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
            WHERE event_date >= NOW() - INTERVAL '24 hours'
            ORDER BY event_date DESC
            LIMIT 100
        """)
        
        result = db.execute(query).fetchall()
        print(f"📊 Recent events query returned {len(result)} records")
        
        if result:
            print("📋 Sample record:")
            sample = result[0]
            print(f"  - ID: {sample[0]}")
            print(f"  - Type: {sample[1]}")
            print(f"  - Fatalities: {sample[2]}")
            print(f"  - Date: {sample[3]}")
            print(f"  - State: {sample[4]}")
            print(f"  - Location: {sample[5]}")
            print(f"  - Verified: {sample[6]}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Monitoring query error: {e}")

if __name__ == "__main__":
    print("🔍 Nigeria Conflict Tracker - Database Diagnostic Tool")
    print("=" * 60)
    
    if test_database_connection():
        check_table_counts()
        check_conflict_events_schema()
        test_monitoring_query()
    else:
        print("❌ Cannot proceed - database connection failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Diagnostic complete")
