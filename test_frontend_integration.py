#!/usr/bin/env python3
"""
Test Frontend Integration for Verification System

This script tests that the frontend can properly connect to the backend API
and that the validation system components are working correctly.
"""

import requests
import json
from datetime import datetime

def test_backend_api():
    """Test backend API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Backend API Integration")
    print("=" * 40)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Backend health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test 2: Validation summary endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/system/validation/summary")
        if response.status_code == 200:
            data = response.json()
            print("✅ Validation summary endpoint working")
            print(f"   Pending items: {data.get('pendingCount', 0)}")
            print(f"   Is urgent: {data.get('isUrgent', False)}")
            print(f"   High priority: {data.get('highPriorityCount', 0)}")
            print(f"   Total verified: {data.get('totalVerified', 0)}")
        else:
            print(f"❌ Validation summary failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Validation summary error: {e}")
        return False
    
    # Test 3: Authentication check for protected endpoints
    try:
        response = requests.get(f"{base_url}/api/v1/conflicts/pending")
        if response.status_code == 401:
            print("✅ Authentication properly required for protected endpoints")
        else:
            print(f"⚠️  Expected 401, got: {response.status_code}")
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False
    
    return True

def test_frontend_server():
    """Test frontend server"""
    frontend_url = "http://localhost:3001"
    
    print("\n🎨 Testing Frontend Server")
    print("=" * 30)
    
    try:
        response = requests.get(frontend_url)
        if response.status_code == 200:
            print("✅ Frontend server running")
            print(f"   URL: {frontend_url}")
        else:
            print(f"❌ Frontend server error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to frontend: {e}")
        return False
    
    return True

def test_api_connectivity():
    """Test that frontend can reach backend API"""
    print("\n🔗 Testing Frontend-to-Backend Connectivity")
    print("=" * 45)
    
    # Simulate frontend API call (same as ValidationQueueCard)
    api_url = "http://localhost:8000/api/v1/system/validation/summary"
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            print("✅ Frontend can reach backend API")
            print(f"   API endpoint: {api_url}")
            print(f"   Response time: {response.elapsed.total_seconds():.2f}s")
            
            # Validate response structure
            required_fields = ['pendingCount', 'isUrgent', 'highPriorityCount', 'totalVerified']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️  Missing response fields: {missing_fields}")
            else:
                print("✅ API response structure is correct")
                
        else:
            print(f"❌ API connectivity failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connectivity error: {e}")
        return False
    
    return True

def main():
    """Run all integration tests"""
    print("🚀 Verification System Integration Tests")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Run tests
    backend_ok = test_backend_api()
    frontend_ok = test_frontend_server()
    connectivity_ok = test_api_connectivity()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 25)
    print(f"Backend API:     {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Frontend Server: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    print(f"API Connectivity: {'✅ PASS' if connectivity_ok else '❌ FAIL'}")
    
    overall_success = backend_ok and frontend_ok and connectivity_ok
    print(f"\nOverall Status:  {'🎉 ALL TESTS PASSED' if overall_success else '⚠️  SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎯 Next Steps:")
        print("   1. Open http://localhost:3001 in your browser")
        print("   2. Navigate to /dashboard/review")
        print("   3. Test the verification workflow")
        print("   4. Check real-time updates (30-second refresh)")
    else:
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure backend server is running on port 8000")
        print("   2. Ensure frontend server is running on port 3001")
        print("   3. Check database connection and validation_summary view")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
