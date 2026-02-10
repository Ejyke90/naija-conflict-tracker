#!/usr/bin/env python3
"""
Test script to verify monthly trends caching is working
Run this to test the performance improvements
"""

import asyncio
import time
import requests
import json
from typing import Dict, Any

# Configuration
BACKEND_URL = "https://naija-conflict-tracker-production.up.railway.app"
ENDPOINT = "/api/v1/timeseries/monthly-trends"

async def test_monthly_trends_performance():
    """Test monthly trends endpoint performance and caching"""
    
    print("🧪 Testing Monthly Trends Performance")
    print("=" * 50)
    
    # Test parameters
    test_params = {
        "months_back": 12,
        "include_forecast": True
    }
    
    # First request - should be cache miss (slower)
    print("📊 First request (cache miss)...")
    start_time = time.time()
    
    try:
        response1 = requests.get(
            f"{BACKEND_URL}{ENDPOINT}",
            params=test_params,
            timeout=30
        )
        first_request_time = time.time() - start_time
        
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"✅ First request: {first_request_time:.2f}s")
            print(f"📈 Data points returned: {len(data1.get('data', []))}")
        else:
            print(f"❌ First request failed: {response1.status_code}")
            print(f"Response: {response1.text}")
            return
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return
    
    # Second request - should be cache hit (much faster)
    print("\n⚡ Second request (cache hit)...")
    start_time = time.time()
    
    try:
        response2 = requests.get(
            f"{BACKEND_URL}{ENDPOINT}",
            params=test_params,
            timeout=30
        )
        second_request_time = time.time() - start_time
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ Second request: {second_request_time:.2f}s")
            
            # Verify data consistency
            if data1 == data2:
                print("✅ Data consistency verified")
            else:
                print("⚠️  Data inconsistency detected")
                
            # Calculate performance improvement
            if first_request_time > 0:
                improvement = ((first_request_time - second_request_time) / first_request_time) * 100
                print(f"🚀 Performance improvement: {improvement:.1f}%")
                
                if second_request_time < 0.5:  # Less than 500ms
                    print("✅ Excellent performance! Caching is working well.")
                elif second_request_time < 2.0:  # Less than 2s
                    print("✅ Good performance improvement")
                else:
                    print("⚠️  Cache may not be working optimally")
            else:
                print("⚠️  Could not calculate performance improvement")
                
        else:
            print(f"❌ Second request failed: {response2.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return
    
    # Test with different parameters (should be separate cache key)
    print("\n🔄 Testing different parameters (separate cache key)...")
    start_time = time.time()
    
    try:
        response3 = requests.get(
            f"{BACKEND_URL}{ENDPOINT}",
            params={"months_back": 6, "include_forecast": False},
            timeout=30
        )
        third_request_time = time.time() - start_time
        
        if response3.status_code == 200:
            print(f"✅ Different params request: {third_request_time:.2f}s")
        else:
            print(f"❌ Different params request failed: {response3.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print(f"   • First request (cache miss): {first_request_time:.2f}s")
    print(f"   • Second request (cache hit): {second_request_time:.2f}s")
    print(f"   • Performance improvement: {improvement:.1f}%")
    
    if second_request_time < first_request_time * 0.1:
        print("   ✅ Caching is working excellently!")
    elif second_request_time < first_request_time * 0.5:
        print("   ✅ Caching is working well")
    else:
        print("   ⚠️  Caching may need optimization")

if __name__ == "__main__":
    asyncio.run(test_monthly_trends_performance())
