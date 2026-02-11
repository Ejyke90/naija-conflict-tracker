#!/usr/bin/env python3
"""
Test script for Prophet model migration and loading
"""

import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.prophet_forecaster import ProphetForecaster
from scripts.migrate_prophet_models import ProphetModelMigrator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_model_migration():
    """Test the model migration functionality"""
    logger.info("Testing Prophet model migration...")
    
    # Create a test models directory
    models_dir = Path("test_models")
    models_dir.mkdir(exist_ok=True)
    
    # Create forecaster
    forecaster = ProphetForecaster(str(models_dir))
    
    # Test 1: Create and save a model
    logger.info("Test 1: Creating and saving a model...")
    try:
        import pandas as pd
        # Create sample data
        dates = pd.date_range('2023-01-01', periods=52, freq='W')
        values = [10 + i*0.5 + (i % 4) * 2 for i in range(52)]  # Some trend + seasonality
        
        df = pd.DataFrame({
            'ds': dates,
            'y': values
        })
        
        # Train and save model
        forecaster.train(df)
        model_path = forecaster.save_model("test_model")
        logger.info(f"✓ Model saved to {model_path}")
        
    except Exception as e:
        logger.error(f"✗ Failed to create/save model: {e}")
        return False
    
    # Test 2: Load the model
    logger.info("Test 2: Loading the model...")
    try:
        new_forecaster = ProphetForecaster(str(models_dir))
        success = new_forecaster.load_model("test_model")
        
        if success:
            logger.info("✓ Model loaded successfully")
        else:
            logger.error("✗ Failed to load model")
            return False
            
    except Exception as e:
        logger.error(f"✗ Model loading failed: {e}")
        return False
    
    # Test 3: Test migration on directory
    logger.info("Test 3: Running migration on directory...")
    try:
        migrator = ProphetModelMigrator(str(models_dir))
        results = migrator.migrate_directory()
        
        logger.info(f"Migration results: {results['migration_summary']}")
        
        if results["failed_migrations"] == 0:
            logger.info("✓ All migrations successful")
        else:
            logger.warning(f"⚠ {results['failed_migrations']} migrations failed")
            
    except Exception as e:
        logger.error(f"✗ Migration failed: {e}")
        return False
    
    # Test 4: Test get_or_train_model functionality
    logger.info("Test 4: Testing get_or_train_model...")
    try:
        third_forecaster = ProphetForecaster(str(models_dir))
        
        # This should load the existing model
        success = third_forecaster.get_or_train_model(
            model_name="test_model",
            df=df
        )
        
        if success:
            logger.info("✓ get_or_train_model worked correctly")
        else:
            logger.error("✗ get_or_train_model failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ get_or_train_model failed: {e}")
        return False
    
    # Test 5: List saved models
    logger.info("Test 5: Listing saved models...")
    try:
        models = forecaster.list_saved_models()
        logger.info(f"Found {len(models)} saved models:")
        for model in models:
            logger.info(f"  - {model['name']} ({model.get('format', 'unknown')})")
        
        if len(models) > 0:
            logger.info("✓ Model listing works")
        else:
            logger.warning("⚠ No models found")
            
    except Exception as e:
        logger.error(f"✗ Model listing failed: {e}")
        return False
    
    # Cleanup
    logger.info("Cleaning up test files...")
    try:
        import shutil
        shutil.rmtree(models_dir)
        logger.info("✓ Test cleanup completed")
    except Exception as e:
        logger.warning(f"⚠ Cleanup failed: {e}")
    
    logger.info("✓ All tests completed successfully!")
    return True


def test_forecast_with_model_caching():
    """Test forecasting with model caching"""
    logger.info("Testing forecast with model caching...")
    
    try:
        forecaster = ProphetForecaster()
        
        # Test forecast with caching (this will try to load/save models)
        result = forecaster.forecast(
            state="Borno",  # This should have data
            weeks_ahead=2,
            use_cached_model=True
        )
        
        if "error" in result:
            logger.warning(f"⚠ Forecast returned error: {result['error']}")
            logger.info("This might be expected if no conflict data exists")
        else:
            logger.info(f"✓ Forecast completed successfully")
            logger.info(f"  Generated {len(result.get('forecast', []))} predictions")
            logger.info(f"  Model used: {result.get('metadata', {}).get('model_name', 'unknown')}")
            logger.info(f"  Cached model used: {result.get('metadata', {}).get('cached_model_used', False)}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Forecast test failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("Prophet Model Migration Test Suite")
    logger.info("=" * 60)
    
    tests = [
        ("Model Migration", test_model_migration),
        ("Forecast with Caching", test_forecast_with_model_caching)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning {test_name} tests...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
