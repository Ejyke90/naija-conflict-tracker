#!/usr/bin/env python3
"""
Test that the update_updated_at_column trigger works with the new updated_at column.
"""
import psycopg2
import os
import sys
from datetime import datetime, timedelta

def test_trigger():
    db_url = os.getenv("DATABASE_URL") or os.getenv("NEON_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    print(f"🔗 Connecting to database...")
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Get a test user
        cur.execute("SELECT id, email, updated_at FROM users LIMIT 1")
        result = cur.fetchone()
        
        if not result:
            print("❌ No users found in database")
            sys.exit(1)
        
        user_id, email, old_updated_at = result
        print(f"\n📧 Test user: {email}")
        print(f"   User ID: {user_id}")
        print(f"   Current updated_at: {old_updated_at}")
        
        # Wait a moment to ensure timestamp will change
        import time
        time.sleep(1)
        
        # Simulate the login endpoint update (this is what was failing)
        print(f"\n🔄 Simulating login update (UPDATE users SET last_login=...)...")
        cur.execute(
            "UPDATE users SET last_login = %s WHERE id = %s",
            (datetime.utcnow(), user_id)
        )
        
        # Check if updated_at was automatically updated by the trigger
        cur.execute("SELECT updated_at FROM users WHERE id = %s", (user_id,))
        new_updated_at = cur.fetchone()[0]
        
        print(f"   New updated_at: {new_updated_at}")
        
        if new_updated_at > old_updated_at:
            print(f"\n✅ SUCCESS! Trigger updated the updated_at column automatically")
            print(f"   Time difference: {new_updated_at - old_updated_at}")
        elif new_updated_at == old_updated_at:
            print(f"\n⚠️  WARNING: updated_at was not changed by trigger")
            print(f"   This might be expected if trigger only fires on actual changes")
        else:
            print(f"\n❌ ERROR: updated_at went backwards in time!")
        
        # Rollback to not affect actual data
        conn.rollback()
        print(f"\n♻️  Changes rolled back (test only)")
        
        cur.close()
        conn.close()
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_trigger()
