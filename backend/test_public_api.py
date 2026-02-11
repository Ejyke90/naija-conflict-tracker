#!/usr/bin/env python3
"""
Test script to verify public API endpoints are working without authentication
"""

import requests
import json
from datetime import datetime

def test_public_endpoints():
    """Test public endpoints that frontend LivePulse component needs"""
    
    # Test endpoints (adjust URL based on your backend deployment)
    base_urls = [
        "http://localhost:8000",
        "https://naija-conflict-tracker-production.up.railway.app",
        "http://127.0.0.1:8000"
    ]
    
    endpoints = [
        "/api/v1/analytics/stats",
        "/api/v1/forecasts/advanced/Nigeria?location_type=state&model=ensemble&weeks_ahead=4"
    ]
    
    results = {}
    
    for base_url in base_urls:
        print(f"\nTesting base URL: {base_url}")
        results[base_url] = {}
        
        for endpoint in endpoints:
            url = base_url + endpoint
            try:
                print(f"  Testing: {url}")
                response = requests.get(url, timeout=10)
                
                results[base_url][endpoint] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "content_type": response.headers.get("content-type", ""),
                    "response_size": len(response.content)
                }
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        results[base_url][endpoint]["data_keys"] = list(data.keys()) if isinstance(data, dict) else "non_dict_response"
                        print(f"    ✓ Success - Keys: {results[base_url][endpoint]['data_keys']}")
                    except json.JSONDecodeError:
                        results[base_url][endpoint]["json_error"] = True
                        print(f"    ⚠ Success but invalid JSON")
                else:
                    print(f"    ✗ Failed: {response.status_code}")
                    try:
                        error_data = response.json()
                        results[base_url][endpoint]["error"] = error_data
                        print(f"    Error: {error_data}")
                    except:
                        print(f"    Raw response: {response.text[:200]}...")
                        
            except requests.exceptions.ConnectionError:
                results[base_url][endpoint] = {
                    "success": False,
                    "error": "Connection refused"
                }
                print(f"    ✗ Connection refused")
            except requests.exceptions.Timeout:
                results[base_url][endpoint] = {
                    "success": False,
                    "error": "Timeout"
                }
                print(f"    ✗ Timeout")
            except Exception as e:
                results[base_url][endpoint] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"    ✗ Error: {e}")
    
    return results

def analyze_results(results):
    """Analyze test results and provide recommendations"""
    
    print("\n" + "="*60)
    print("ANALYSIS AND RECOMMENDATIONS")
    print("="*60)
    
    working_endpoints = []
    failing_endpoints = []
    
    for base_url, endpoints in results.items():
        for endpoint, result in endpoints.items():
            if result.get("success", False):
                working_endpoints.append((base_url, endpoint))
            else:
                failing_endpoints.append((base_url, endpoint, result.get("error", "Unknown error")))
    
    print(f"\n✅ Working endpoints: {len(working_endpoints)}")
    for base_url, endpoint in working_endpoints:
        print(f"  {base_url}{endpoint}")
    
    print(f"\n❌ Failing endpoints: {len(failing_endpoints)}")
    for base_url, endpoint, error in failing_endpoints:
        print(f"  {base_url}{endpoint} - {error}")
    
    # Recommendations
    print(f"\n🔧 Recommendations:")
    
    if len(working_endpoints) == 0:
        print("  1. Backend server is not running or not accessible")
        print("  2. Start the backend server:")
        print("     cd backend && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("  3. Check if Railway deployment is working")
        
    elif len(working_endpoints) < len(working_endpoints) + len(failing_endpoints):
        print("  1. Some endpoints are working, others have issues")
        print("  2. Check authentication requirements for failing endpoints")
        print("  3. Verify CORS configuration")
        
    else:
        print("  1. All endpoints are working!")
        print("  2. If frontend still shows errors, check:")
        print("     - Frontend is making requests to correct URL")
        print("     - No network/CORS issues")
        print("     - Browser console for JavaScript errors")

def main():
    print("Testing Public API Endpoints for LivePulse Component")
    print("=" * 60)
    
    results = test_public_endpoints()
    analyze_results(results)
    
    # Save results for debugging
    with open("api_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: api_test_results.json")

if __name__ == "__main__":
    main()
