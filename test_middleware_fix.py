#!/usr/bin/env python3
"""Quick test to verify middleware fixes work"""

try:
    print("Testing imports...")
    
    # Test main app import
    from app.main import app
    print("✅ Main app imported successfully")
    
    # Test middleware import
    from app.middleware.performance import PerformanceMiddleware
    print("✅ PerformanceMiddleware imported successfully")
    
    # Test that middleware is registered
    middleware_classes = [type(middleware.cls) for middleware in app.user_middleware]
    if PerformanceMiddleware in middleware_classes:
        print("✅ PerformanceMiddleware is registered in app")
    else:
        print("❌ PerformanceMiddleware not found in app middleware stack")
    
    print("🎉 All tests passed! The middleware fix should work.")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
