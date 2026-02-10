#!/usr/bin/env python3
"""
Update User Role to Analyst

This script updates an existing user to have analyst role for testing verification system
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def load_database_url():
    """Load database URL from environment variables"""
    load_dotenv()
    
    database_url = (
        os.getenv('DATABASE_URL') or 
        os.getenv('POSTGRES_URL') or
        os.getenv('POSTGRESQL_URL') or
        'postgresql://localhost:5432/conflict_tracker'
    )
    
    return database_url

def update_user_to_analyst():
    """Update existing user to analyst role"""
    print("🔄 Updating User Role to Analyst")
    print("=" * 35)
    
    try:
        # Connect to database
        database_url = load_database_url()
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Update the test user to analyst role
            update_sql = text("""
                UPDATE users 
                SET role = 'analyst', updated_at = NOW()
                WHERE email = 'analyst.test@conflicttracker.com'
                RETURNING id, email, role
            """)
            
            result = conn.execute(update_sql)
            updated_user = result.fetchone()
            
            if updated_user:
                print("✅ User role updated successfully")
                print(f"   ID: {updated_user.id}")
                print(f"   Email: {updated_user.email}")
                print(f"   New Role: {updated_user.role}")
                
                conn.commit()
                return True
            else:
                print("❌ User not found")
                return False
                
    except Exception as e:
        print(f"❌ Error updating user role: {e}")
        return False

def test_updated_user():
    """Test the updated user can access verification endpoints"""
    print("\n🧪 Testing Updated User Access")
    print("=" * 30)
    
    import requests
    
    # Login to get token
    login_data = {
        "email": "analyst.test@conflicttracker.com",
        "password": "AnalystPassword123!"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
        
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get('access_token')
            user_role = auth_data.get('user', {}).get('role')
            
            print(f"✅ Login successful")
            print(f"   Role: {user_role}")
            
            # Test access to pending conflicts
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get("http://localhost:8000/api/v1/conflicts/pending", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Access to /api/v1/conflicts/pending - SUCCESS")
                print(f"   Found {len(data)} pending conflicts")
                return True
            else:
                print(f"❌ Access failed: {response.status_code}")
                print(f"   Response: {response.json()}")
                return False
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Update User Role for Verification Testing")
    print("=" * 45)
    
    # Update user role
    if not update_user_to_analyst():
        print("❌ Failed to update user role")
        return False
    
    # Test updated user
    if not test_updated_user():
        print("❌ Updated user test failed")
        return False
    
    print("\n🎉 User Role Update Complete!")
    print("\n📋 Updated User Details:")
    print("   Email: analyst.test@conflicttracker.com")
    print("   Password: AnalystPassword123!")
    print("   Role: analyst ✅")
    
    print("\n🎯 Frontend Testing Instructions:")
    print("   1. Open browser: http://localhost:3001")
    print("   2. Login with analyst.test@conflicttracker.com")
    print("   3. Password: AnalystPassword123!")
    print("   4. Go to: http://localhost:3001/dashboard/review")
    print("   5. The verification system should now work! 🚀")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
