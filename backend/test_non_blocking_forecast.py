#!/usr/bin/env python3
"""
Test script to verify the non-blocking forecast endpoint works correctly
"""

import asyncio
import aiohttp
import time
from datetime import datetime

async def test_non_blocking_forecast():
    """Test that the forecast endpoint doesn't block and returns responses"""
    
    base_url = "http://localhost:8000"  # Change if your backend runs elsewhere
    
    print("Testing Non-Blocking Forecast Endpoint")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Single forecast request
        print("\n1. Testing single forecast request...")
        start_time = time.time()
        
        try:
            url = f"{base_url}/api/v1/forecasts/advanced/Nigeria?location_type=national&model=prophet&weeks_ahead=4"
            
            async with session.get(url, timeout=300) as response:  # 5 minute timeout
                if response.status == 200:
                    data = await response.json()
                    elapsed = time.time() - start_time
                    
                    print(f"✅ Success in {elapsed:.2f}s")
                    print(f"   Location: {data.get('location')}")
                    print(f"   Model: {data.get('model')}")
                    print(f"   Forecast points: {len(data.get('forecast', []))}")
                    print(f"   Cached: {data.get('cached', False)}")
                    print(f"   Computation time: {data.get('computation_time', 0)}s")
                    
                else:
                    print(f"❌ Failed with status {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    
        except asyncio.TimeoutError:
            print(f"❌ Timeout after 300s - endpoint is still blocking!")
        except aiohttp.ClientError as e:
            print(f"❌ Connection error: {e}")
        
        # Test 2: Multiple concurrent requests
        print("\n2. Testing concurrent requests...")
        start_time = time.time()
        
        urls = [
            f"{base_url}/api/v1/forecasts/advanced/Nigeria?location_type=national&model=prophet&weeks_ahead=4",
            f"{base_url}/api/v1/analytics/stats",  # Should be fast
        ]
        
        try:
            tasks = []
            for url in urls:
                task = asyncio.create_task(session.get(url, timeout=300))
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed = time.time() - start_time
            
            print(f"✅ Concurrent requests completed in {elapsed:.2f}s")
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    print(f"   Request {i+1}: ❌ Error - {response}")
                else:
                    if response.status == 200:
                        data = await response.json()
                        endpoint_type = "forecast" if "forecast" in str(response.url) else "stats"
                        print(f"   Request {i+1} ({endpoint_type}): ✅ Success")
                    else:
                        print(f"   Request {i+1}: ❌ Status {response.status}")
                        
        except Exception as e:
            print(f"❌ Concurrent test failed: {e}")
        
        # Test 3: Status endpoint
        print("\n3. Testing forecast status endpoint...")
        
        try:
            url = f"{base_url}/api/v1/forecasts/advanced/Nigeria/status?location_type=national&model=prophet&weeks_ahead=4"
            
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Status endpoint working")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Estimated time: {data.get('estimated_time_seconds')}s")
                else:
                    print(f"❌ Status endpoint failed: {response.status}")
                    
        except Exception as e:
            print(f"❌ Status endpoint error: {e}")

async def test_request_timeout_behavior():
    """Test how the endpoint handles timeouts and client disconnections"""
    
    print("\n3. Testing timeout behavior...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Create a session with very short timeout to simulate client timeout
        timeout = aiohttp.ClientTimeout(total=5)  # 5 second timeout
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            start_time = time.time()
            
            url = f"{base_url}/api/v1/forecasts/advanced/Nigeria?location_type=national&model=ensemble&weeks_ahead=8"
            
            print(f"   Making request with 5s timeout (ensemble model takes longer)...")
            
            async with session.get(url) as response:
                print(f"   Unexpected success: {response.status}")
                
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"✅ Correctly timed out after {elapsed:.2f}s (client protection working)")
    except Exception as e:
        print(f"   Error: {e}")

async def main():
    """Run all tests"""
    print("Non-Blocking Forecast Endpoint Test Suite")
    print("=" * 60)
    
    await test_non_blocking_forecast()
    await test_request_timeout_behavior()
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("- If forecast requests complete quickly (<30s), non-blocking is working")
    print("- If concurrent requests complete together, event loop isn't blocked")
    print("- If timeouts work correctly, client protection is active")
    print("\nNext steps:")
    print("- Start backend: python3 -m uvicorn app.main:app --reload")
    print("- Monitor logs for 'Starting async forecast' messages")
    print("- Check for thread pool usage in logs")

if __name__ == "__main__":
    asyncio.run(main())
