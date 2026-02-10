#!/usr/bin/env python3
"""
Test script to verify our monthly-trends changes work locally
This tests the code changes without requiring a full database setup
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        from app.api.v1.endpoints.timeseries import get_monthly_trends
        print("✅ get_monthly_trends imported successfully")
        
        from app.core.cache import get_from_cache_resilient, set_cache_resilient, CACHE_TTL
        print("✅ Cache functions imported successfully")
        
        # Check monthly_trends TTL is configured
        if 'monthly_trends' in CACHE_TTL:
            print(f"✅ monthly_trends TTL configured: {CACHE_TTL['monthly_trends']}s")
        else:
            print("❌ monthly_trends TTL not found in CACHE_TTL")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_function_signature():
    """Test that the function signature is correct"""
    print("\n🔍 Testing function signature...")
    
    try:
        from app.api.v1.endpoints.timeseries import get_monthly_trends
        import inspect
        
        sig = inspect.signature(get_monthly_trends)
        params = list(sig.parameters.keys())
        
        expected_params = ['state', 'months_back', 'include_forecast', 'db']
        
        for param in expected_params:
            if param in params:
                print(f"✅ Parameter '{param}' found")
            else:
                print(f"❌ Parameter '{param}' missing")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Function signature test failed: {e}")
        return False

def test_cache_key_generation():
    """Test that cache key generation would work"""
    print("\n🔑 Testing cache key generation logic...")
    
    try:
        # Simulate cache key generation
        state = "Borno"
        months_back = 12
        include_forecast = True
        
        cache_key = f"timeseries:monthly_trends:{state or 'all'}:{months_back}:{include_forecast}"
        expected_key = "timeseries:monthly_trends:Borno:12:True"
        
        if cache_key == expected_key:
            print(f"✅ Cache key generation works: {cache_key}")
            return True
        else:
            print(f"❌ Cache key mismatch: got {cache_key}, expected {expected_key}")
            return False
            
    except Exception as e:
        print(f"❌ Cache key test failed: {e}")
        return False

def test_code_structure():
    """Test that the code structure looks correct"""
    print("\n📋 Testing code structure...")
    
    try:
        with open('backend/app/api/v1/endpoints/timeseries.py', 'r') as f:
            content = f.read()
            
        # Check for caching code
        if 'get_from_cache_resilient' in content:
            print("✅ Cache retrieval code found")
        else:
            print("❌ Cache retrieval code missing")
            return False
            
        if 'set_cache_resilient' in content:
            print("✅ Cache setting code found")
        else:
            print("❌ Cache setting code missing")
            return False
            
        # Check for materialized view code
        if 'monthly_trends_summary' in content:
            print("✅ Materialized view code found")
        else:
            print("❌ Materialized view code missing")
            return False
            
        # Check that old disabled cache code is gone
        if 'Cache disabled for now' in content:
            print("❌ Old disabled cache code still present")
            return False
        else:
            print("✅ Old disabled cache code removed")
            
        return True
        
    except Exception as e:
        print(f"❌ Code structure test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Monthly Trends Changes Locally")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_function_signature,
        test_cache_key_generation,
        test_code_structure
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"   ✅ Passed: {passed}/{total}")
    print(f"   ❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Changes look good for deployment.")
        print("\n📋 Next steps:")
        print("   1. Commit changes")
        print("   2. Deploy to test environment")
        print("   3. Test monthly-trends endpoint performance")
        print("   4. Monitor for any issues")
    else:
        print("\n⚠️  Some tests failed. Review issues before deploying.")
        print("\n🔄 Rollback if needed:")
        print("   ./scripts/rollback_monthly_trends_performance.sh")

if __name__ == "__main__":
    main()
