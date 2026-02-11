#!/usr/bin/env python3
"""
Debug token expiration and session issues
"""
import requests
import json
import time

def test_token_expiration():
    """Test token expiration behavior"""
    print("Testing token expiration...")
    
    try:
        # Login to get token
        login_data = {
            "email": "info@thenextier.com", 
            "password": "test12345"
        }
        
        login_response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print(f"✅ Got token: {token[:50]}...")
            
            # Test immediate use
            headers = {"Authorization": f"Bearer {token}"}
            response1 = requests.get("http://localhost:8000/api/v1/conflicts/pending?limit=5", headers=headers)
            print(f"📊 Immediate request: {response1.status_code}")
            
            # Test after a short delay
            time.sleep(2)
            response2 = requests.get("http://localhost:8000/api/v1/conflicts/pending?limit=20", headers=headers)
            print(f"📊 Delayed request: {response2.status_code}")
            
            if response2.status_code == 401:
                print("❌ Token failing after delay - possible session issue")
                print(f"Response: {response2.text}")
            else:
                print("✅ Token working correctly")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running locally")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_auth_me_endpoint():
    """Test the /auth/me endpoint to check token validity"""
    print("\nTesting /auth/me endpoint...")
    
    try:
        # Login
        login_data = {"email": "info@thenextier.com", "password": "test12345"}
        login_response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test /auth/me
            me_response = requests.get("http://localhost:8000/api/v1/auth/me", headers=headers)
            print(f"📊 /auth/me status: {me_response.status_code}")
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"✅ User authenticated: {user_data.get('email')}")
                print(f"📋 Role: {user_data.get('role')}")
            else:
                print(f"❌ /auth/me failed: {me_response.text}")
                
            # Now test /pending with same token
            pending_response = requests.get("http://localhost:8000/api/v1/conflicts/pending?limit=20", headers=headers)
            print(f"📊 /pending status: {pending_response.status_code}")
            
            if pending_response.status_code == 401:
                print("❌ /pending failing while /auth/me works - endpoint-specific issue")
            else:
                print("✅ Both endpoints working")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔧 DEBUGGING TOKEN EXPIRATION ISSUES")
    print("=" * 60)
    
    test_token_expiration()
    test_auth_me_endpoint()
    
    print("\n" + "=" * 60)
    print("📋 POSSIBLE CAUSES:")
    print("1. Frontend token caching issues")
    print("2. Token not being sent in headers correctly")
    print("3. Endpoint-specific authentication problems")
    print("4. Session management issues")
