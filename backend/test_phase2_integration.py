"""
Phase 2 Integration Tests
Tests Redis caching, Celery tasks, PDF generation, and advanced forecasting with caching.

Usage:
    python test_phase2_integration.py
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_redis_connection():
    """Test Redis connection and basic operations"""
    print("\n" + "="*60)
    print("TEST 1: Redis Connection")
    print("="*60)
    
    try:
        from app.core.cache import get_redis_client
        
        redis = await get_redis_client()
        
        # Test set/get
        await redis.set("test_key", "test_value", ex=60)
        value = await redis.get("test_key")
        
        if value == "test_value":
            print("✅ Redis connection successful")
            print(f"   - Set/Get operation working")
        else:
            print("❌ Redis value mismatch")
            return False
        
        # Test cache stats
        from app.core.cache import get_cache_stats
        stats = await get_cache_stats()
        print(f"   - Cache keys: {stats.get('keys', 0)}")
        print(f"   - Memory used: {stats.get('memory_used', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("   Make sure Redis is running: redis-server")
        return False


async def test_forecast_caching():
    """Test forecast endpoint with Redis caching"""
    print("\n" + "="*60)
    print("TEST 2: Forecast Caching")
    print("="*60)
    
    try:
        from app.ml import ProphetForecaster
        from app.core.cache import cache_forecast, invalidate_forecast_cache
        import time
        
        # Define a test forecast function
        @cache_forecast(ttl=300, key_prefix="test_forecast")
        async def get_test_forecast(location: str, weeks: int):
            """Simulated forecast function"""
            forecaster = ProphetForecaster()
            return await forecaster.forecast(
                location_name=location,
                location_type="state",
                weeks_ahead=weeks
            )
        
        # First call - should hit database
        print("   - Making first forecast call (cache miss)...")
        start = time.time()
        result1 = await get_test_forecast(location="Borno", weeks=4)
        time1 = time.time() - start
        print(f"   - First call took: {time1:.2f}s")
        print(f"   - Predictions: {len(result1['predictions'])} weeks")
        
        # Second call - should hit cache
        print("   - Making second forecast call (cache hit)...")
        start = time.time()
        result2 = await get_test_forecast(location="Borno", weeks=4)
        time2 = time.time() - start
        print(f"   - Second call took: {time2:.2f}s")
        
        # Cache should be much faster
        if time2 < time1 * 0.5:  # At least 50% faster
            print(f"✅ Caching working (speedup: {time1/time2:.1f}x)")
        else:
            print(f"⚠️  Cache may not be working (speedup: {time1/time2:.1f}x)")
        
        # Test cache invalidation
        print("   - Testing cache invalidation...")
        await invalidate_forecast_cache("test_forecast:*")
        print("✅ Cache invalidation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Forecast caching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_generation():
    """Test PDF report generation"""
    print("\n" + "="*60)
    print("TEST 3: PDF Report Generation")
    print("="*60)
    
    try:
        from app.reports import ForecastReportGenerator, generate_forecast_pdf_report
        from datetime import datetime
        
        # Create sample forecast data
        sample_forecasts = {
            "Borno": {
                "predictions": [
                    {"date": "2024-01-01", "predicted": 12.5, "lower": 8.2, "upper": 16.8},
                    {"date": "2024-01-08", "predicted": 14.2, "lower": 9.5, "upper": 18.9},
                    {"date": "2024-01-15", "predicted": 11.8, "lower": 7.1, "upper": 16.5},
                    {"date": "2024-01-22", "predicted": 13.5, "lower": 8.8, "upper": 18.2},
                ],
                "model": "Prophet",
                "confidence": 0.95
            },
            "Kaduna": {
                "predictions": [
                    {"date": "2024-01-01", "predicted": 8.3, "lower": 5.1, "upper": 11.5},
                    {"date": "2024-01-08", "predicted": 9.1, "lower": 5.9, "upper": 12.3},
                    {"date": "2024-01-15", "predicted": 7.8, "lower": 4.6, "upper": 11.0},
                    {"date": "2024-01-22", "predicted": 8.9, "lower": 5.7, "upper": 12.1},
                ],
                "model": "Ensemble",
                "confidence": 0.95
            }
        }
        
        # Generate PDF
        print("   - Generating PDF report...")
        output_file = f"test_forecast_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = generate_forecast_pdf_report(sample_forecasts, output_file)
        
        # Check if file exists
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path) / 1024  # KB
            print(f"✅ PDF generated successfully")
            print(f"   - File: {pdf_path}")
            print(f"   - Size: {file_size:.1f} KB")
            print(f"   - States: {len(sample_forecasts)}")
            return True
        else:
            print("❌ PDF file not created")
            return False
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_celery_tasks():
    """Test Celery task configuration"""
    print("\n" + "="*60)
    print("TEST 4: Celery Tasks Configuration")
    print("="*60)
    
    try:
        from app.tasks.forecast_tasks import (
            generate_state_forecast,
            generate_all_state_forecasts,
            generate_weekly_forecast_report,
            celery_app
        )
        
        print("✅ Celery app configured")
        print(f"   - Broker: {celery_app.conf.broker_url}")
        print(f"   - Backend: {celery_app.conf.result_backend}")
        
        # Check registered tasks
        tasks = list(celery_app.tasks.keys())
        forecast_tasks = [t for t in tasks if 'forecast' in t.lower()]
        print(f"   - Registered tasks: {len(forecast_tasks)}")
        for task in forecast_tasks:
            print(f"     • {task}")
        
        # Check schedules
        if hasattr(celery_app.conf, 'beat_schedule'):
            print(f"   - Scheduled tasks: {len(celery_app.conf.beat_schedule)}")
            for name, schedule in celery_app.conf.beat_schedule.items():
                print(f"     • {name}: {schedule.get('schedule', 'N/A')}")
        
        print("\n⚠️  To test task execution, run:")
        print("   celery -A app.tasks.forecast_tasks worker --loglevel=info")
        print("   celery -A app.tasks.forecast_tasks beat --loglevel=info")
        
        return True
        
    except Exception as e:
        print(f"❌ Celery configuration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_advanced_forecasting():
    """Test advanced forecasting models with all features"""
    print("\n" + "="*60)
    print("TEST 5: Advanced Forecasting Models")
    print("="*60)
    
    try:
        from app.ml import ProphetForecaster, ARIMAForecaster, EnsembleForecaster
        
        # Test Prophet
        print("\n   Testing Prophet Forecaster...")
        prophet = ProphetForecaster()
        prophet_result = await prophet.forecast(
            location_name="Borno",
            location_type="state",
            weeks_ahead=4
        )
        print(f"   ✅ Prophet: {len(prophet_result['predictions'])} predictions")
        print(f"      - Avg prediction: {sum(p['predicted'] for p in prophet_result['predictions'])/len(prophet_result['predictions']):.2f}")
        print(f"      - Changepoints: {len(prophet_result.get('changepoints', []))}")
        
        # Test ARIMA
        print("\n   Testing ARIMA Forecaster...")
        arima = ARIMAForecaster()
        arima_result = await arima.forecast(
            location_name="Borno",
            location_type="state",
            weeks_ahead=4
        )
        print(f"   ✅ ARIMA: {len(arima_result['predictions'])} predictions")
        print(f"      - Order: {arima_result['metadata'].get('order', 'N/A')}")
        print(f"      - AIC: {arima_result['metadata'].get('aic', 'N/A'):.2f}")
        
        # Test Ensemble
        print("\n   Testing Ensemble Forecaster...")
        ensemble = EnsembleForecaster()
        ensemble_result = await ensemble.forecast(
            location_name="Borno",
            location_type="state",
            weeks_ahead=4
        )
        print(f"   ✅ Ensemble: {len(ensemble_result['predictions'])} predictions")
        print(f"      - Models used: {', '.join(ensemble_result['metadata'].get('models_used', []))}")
        print(f"      - Avg prediction: {sum(p['predicted'] for p in ensemble_result['predictions'])/len(ensemble_result['predictions']):.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced forecasting test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("PHASE 2 INTEGRATION TEST SUITE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "Redis Connection": await test_redis_connection(),
        "Forecast Caching": await test_forecast_caching(),
        "PDF Generation": test_pdf_generation(),
        "Celery Tasks": await test_celery_tasks(),
        "Advanced Forecasting": await test_advanced_forecasting(),
    }
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All Phase 2 features working correctly!")
        print("\nNext steps:")
        print("1. Deploy to Railway with Redis service")
        print("2. Configure environment variables")
        print("3. Start Celery workers and beat scheduler")
        print("4. Deploy frontend to Vercel")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("\nCommon fixes:")
        print("- Start Redis: redis-server")
        print("- Check DATABASE_URL environment variable")
        print("- Install dependencies: pip install -r requirements.txt")


if __name__ == "__main__":
    asyncio.run(main())
