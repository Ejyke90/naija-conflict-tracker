"""
Test Advanced Forecasting Models
Run this script to validate Prophet, ARIMA, and Ensemble forecasters
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml import ProphetForecaster, ARIMAForecaster, EnsembleForecaster, ModelEvaluator
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_prophet_forecaster():
    """Test Prophet forecasting"""
    logger.info("\n" + "="*60)
    logger.info("TESTING PROPHET FORECASTER")
    logger.info("="*60)
    
    try:
        forecaster = ProphetForecaster()
        
        # Test with Borno state (highest conflict activity)
        result = forecaster.forecast(
            state="Borno",
            weeks_ahead=4
        )
        
        if "error" in result:
            logger.error(f"Prophet Error: {result['error']}")
            return False
        
        logger.info(f"\n✅ Prophet Forecast for Borno State:")
        logger.info(f"   Training data: {result['metadata']['training_data_points']} weeks")
        logger.info(f"   Training period: {result['metadata']['training_period']['start']} to {result['metadata']['training_period']['end']}")
        logger.info(f"   Trend: {result['metadata']['trend_direction']}")
        
        logger.info(f"\n   Predictions:")
        for pred in result['forecast'][:2]:  # Show first 2 weeks
            logger.info(f"   - {pred['date']}: {pred['predicted_incidents']} incidents "
                       f"(CI: {pred['lower_bound']}-{pred['upper_bound']})")
        
        if result['metadata'].get('significant_changepoints'):
            logger.info(f"\n   Significant trend changes detected:")
            for cp in result['metadata']['significant_changepoints']:
                logger.info(f"   - {cp['date']}: {cp['direction']} (magnitude: {cp['magnitude']:.2f})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Prophet test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_arima_forecaster():
    """Test ARIMA forecasting"""
    logger.info("\n" + "="*60)
    logger.info("TESTING ARIMA FORECASTER")
    logger.info("="*60)
    
    try:
        forecaster = ARIMAForecaster()
        
        # Test with Kaduna state
        result = forecaster.forecast(
            state="Kaduna",
            weeks_ahead=4
        )
        
        if "error" in result:
            logger.error(f"ARIMA Error: {result['error']}")
            return False
        
        logger.info(f"\n✅ ARIMA Forecast for Kaduna State:")
        logger.info(f"   Training data: {result['metadata']['training_data_points']} weeks")
        logger.info(f"   ARIMA order: {result['metadata']['diagnostics']['order']}")
        logger.info(f"   AIC: {result['metadata']['diagnostics']['AIC']}")
        logger.info(f"   BIC: {result['metadata']['diagnostics']['BIC']}")
        
        stationarity = result['metadata']['diagnostics']['stationarity_test']
        if 'p_value' in stationarity and stationarity['p_value'] is not None:
            logger.info(f"   Stationarity: {stationarity['interpretation']} (p={stationarity['p_value']:.4f})")
        
        logger.info(f"\n   Predictions:")
        for pred in result['forecast'][:2]:
            logger.info(f"   - {pred['date']}: {pred['predicted_incidents']} incidents "
                       f"(CI: {pred['lower_bound']}-{pred['upper_bound']})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ARIMA test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ensemble_forecaster():
    """Test Ensemble forecasting"""
    logger.info("\n" + "="*60)
    logger.info("TESTING ENSEMBLE FORECASTER")
    logger.info("="*60)
    
    try:
        forecaster = EnsembleForecaster()
        
        # Test with Plateau state
        result = forecaster.forecast(
            state="Plateau",
            weeks_ahead=4,
            include_individual_models=True
        )
        
        if "error" in result:
            logger.error(f"Ensemble Error: {result['error']}")
            return False
        
        logger.info(f"\n✅ Ensemble Forecast for Plateau State:")
        logger.info(f"   Models used: {', '.join(result['metadata']['component_models'])}")
        logger.info(f"   Weights: {result['metadata']['weights']}")
        logger.info(f"   Success rate: {result['metadata']['models_succeeded']}/{result['metadata']['models_succeeded'] + result['metadata']['models_failed']}")
        
        logger.info(f"\n   Ensemble Predictions:")
        for pred in result['forecast'][:2]:
            logger.info(f"   - {pred['date']}: {pred['predicted_incidents']} incidents "
                       f"(CI: {pred['lower_bound']}-{pred['upper_bound']}, "
                       f"{pred['models_used']} models)")
        
        if 'individual_forecasts' in result:
            logger.info(f"\n   Individual Model Contributions:")
            for model_name in result['individual_forecasts'].keys():
                logger.info(f"   - {model_name}: ✓")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ensemble test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_evaluation():
    """Test model evaluation and backtesting"""
    logger.info("\n" + "="*60)
    logger.info("TESTING MODEL EVALUATION")
    logger.info("="*60)
    
    try:
        evaluator = ModelEvaluator()
        
        # Compare models for a high-conflict state
        result = evaluator.compare_models(
            state="Borno",
            test_size=8  # Use last 8 weeks for testing
        )
        
        if "error" in result:
            logger.error(f"Evaluation Error: {result['error']}")
            return False
        
        logger.info(f"\n✅ Model Comparison for Borno State:")
        logger.info(f"   Test size: {result['metadata']['test_size']} weeks")
        logger.info(f"   Total data points: {result['metadata']['data_points']}")
        logger.info(f"   Best model: {result['best_model']} (MAE: {result['best_mae']})")
        
        logger.info(f"\n   Performance Metrics:")
        for model_name, model_result in result['comparison'].items():
            if "metrics" in model_result:
                metrics = model_result["metrics"]
                logger.info(f"\n   {model_name}:")
                logger.info(f"      MAE: {metrics['MAE']}")
                logger.info(f"      RMSE: {metrics['RMSE']}")
                logger.info(f"      MAPE: {metrics['MAPE']}%")
                logger.info(f"      Coverage: {metrics['Coverage']}%")
                logger.info(f"      Direction Accuracy: {metrics['DirectionAccuracy']}%")
                
                if 'performance_rating' in model_result:
                    rating = model_result['performance_rating']
                    logger.info(f"      Overall Rating: {rating['Overall']}")
            else:
                logger.info(f"\n   {model_name}: Failed - {model_result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Evaluation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    logger.info("\n" + "="*60)
    logger.info("ADVANCED FORECASTING TEST SUITE")
    logger.info("="*60)
    
    results = {
        "Prophet": test_prophet_forecaster(),
        "ARIMA": test_arima_forecaster(),
        "Ensemble": test_ensemble_forecaster(),
        "Evaluation": test_model_evaluation()
    }
    
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    logger.info(f"\nOverall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        logger.info("\n🎉 All tests passed! Advanced forecasting is ready.")
        return 0
    else:
        logger.warning(f"\n⚠️  {total_tests - total_passed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
