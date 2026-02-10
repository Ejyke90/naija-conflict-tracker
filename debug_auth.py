#!/usr/bin/env python3
"""
Debug authentication issues for the pending conflicts endpoint
"""
import os
import sys
sys.path.append('/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/backend')

from sqlalchemy import text
from app.db.database import SessionLocal
from app.models.auth import User

def check_user_status():
    """Check the status of the info@thenextier.com user"""
    print("Checking user authentication status...")
    
    try:
        db = SessionLocal()
        
        # Find the user
        user = db.execute(text("""
            SELECT id, email, role, is_active, created_at, updated_at 
            FROM users 
            WHERE email = :email
        """), {"email": "info@thenextier.com"}).fetchone()
        
        if user:
            print(f"✅ User found:")
            print(f"  - ID: {user.id}")
            print(f"  - Email: {user.email}")
            print(f"  - Role: {user.role}")
            print(f"  - Active: {user.is_active}")
            print(f"  - Created: {user.created_at}")
            print(f"  - Updated: {user.updated_at}")
            
            if not user.is_active:
                print("❌ ISSUE: User is not active!")
                print("🔧 FIX: Update user.is_active = True")
                
                # Fix the user status
                db.execute(text("""
                    UPDATE users 
                    SET is_active = true, updated_at = NOW() 
                    WHERE email = :email
                """), {"email": "info@thenextier.com"})
                db.commit()
                print("✅ User activated successfully!")
            else:
                print("✅ User is active - this is not the issue")
        else:
            print("❌ User not found in database")
            print("🔧 Creating user...")
            
            # Create the user
            db.execute(text("""
                INSERT INTO users (email, role, is_active, created_at, updated_at)
                VALUES (:email, 'admin', true, NOW(), NOW())
                ON CONFLICT (email) DO UPDATE SET
                    role = 'admin', is_active = true, updated_at = NOW()
            """), {"email": "info@thenextier.com"})
            db.commit()
            print("✅ User created and activated!")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error checking user: {e}")

def test_endpoint_with_debug():
    """Test the endpoint with debug information"""
    print("\nTesting endpoint with debug...")
    
    try:
        # Test the exact query used in the endpoint
        db = SessionLocal()
        
        # This is the query that should work
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
        
        print(f"✅ Database query works: {len(rows)} results")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database query error: {e}")

if __name__ == "__main__":
    print("🔧 DEBUGGING AUTHENTICATION ISSUES")
    print("=" * 60)
    
    check_user_status()
    test_endpoint_with_debug()
    
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS:")
    print("1. Try logging in again with the activated user")
    print("2. Test the /api/v1/conflicts/pending endpoint")
    print("3. If still 401, check token format and expiration")
