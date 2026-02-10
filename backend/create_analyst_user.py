#!/usr/bin/env python3
"""
Create Test Analyst User for Verification System

This script creates a user with analyst role to test the verification system
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"

def create_analyst_user():
    """Create a user with analyst role"""
    print("👤 Creating Analyst User")
    print("=" * 25)
    
    # Try to delete existing user first (optional)
    try:
        # First try to login to see if user exists
        login_data = {
            "email": "analyst.test@conflicttracker.com",
            "password": "AnalystPassword123!"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            print("ℹ️ Analyst user already exists, using existing user")
            return response.json().get('access_token')
    except:
        pass
    
    # Register new analyst user
    register_data = {
        "email": "analyst.test@conflicttracker.com",
        "password": "AnalystPassword123!",
        "full_name": "Verification Analyst",
        "role": "analyst"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
        
        if response.status_code == 201:
            print("✅ Analyst user registered successfully")
            user_data = response.json()
            print(f"   Email: {user_data.get('email')}")
            print(f"   Role: {user_data.get('role')}")
            print(f"   ID: {user_data.get('id')}")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None
    
    # Login to get token
    print("\n🔑 Logging In Analyst User")
    print("=" * 25)
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        
        if response.status_code == 200:
            auth_data = response.json()
            print("✅ Analyst login successful")
            print(f"   Role: {auth_data.get('user', {}).get('role')}")
            return auth_data.get('access_token')
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_analyst_access(token):
    """Test analyst access to verification endpoints"""
    print(f"\n🛡️ Testing Analyst Access")
    print("=" * 25)
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test pending conflicts
    try:
        response = requests.get(f"{BASE_URL}/api/v1/conflicts/pending", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ GET /api/v1/conflicts/pending - SUCCESS")
            print(f"   Found {len(data)} pending conflicts")
            
            if data:
                first = data[0]
                print(f"   First conflict: ID {first.get('id')}, Deaths: {first.get('total_deaths', 0)}")
                return first.get('id')  # Return conflict ID for testing
            else:
                print("   No pending conflicts found")
                return None
        else:
            print(f"❌ Access failed: {response.status_code}")
            print(f"   Response: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Access error: {e}")
        return None

def main():
    """Main function"""
    print("🚀 Creating Analyst User for Verification Testing")
    print("=" * 50)
    
    # Create analyst user and get token
    token = create_analyst_user()
    
    if not token:
        print("❌ Failed to create analyst user")
        return False
    
    # Test analyst access
    conflict_id = test_analyst_access(token)
    
    print(f"\n🎉 Analyst User Ready!")
    print(f"\n📋 User Details:")
    print(f"   Email: analyst.test@conflicttracker.com")
    print(f"   Password: AnalystPassword123!")
    print(f"   Role: analyst")
    print(f"   Token: {token[:50]}...")
    
    print(f"\n🎯 Frontend Setup Instructions:")
    print(f"   1. Open browser and go to http://localhost:3001")
    print(f"   2. Login with: analyst.test@conflicttracker.com")
    print(f"   3. Password: AnalystPassword123!")
    print(f"   4. Navigate to: http://localhost:3001/dashboard/review")
    print(f"   5. The verification system should now work!")
    
    if conflict_id:
        print(f"\n🧪 Test Data Available:")
        print(f"   Conflict ID for testing: {conflict_id}")
        print(f"   You can verify this conflict in the frontend")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
