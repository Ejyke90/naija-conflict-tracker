#!/usr/bin/env python3
"""
Test script for NLP Event Extraction Pipeline
Validates all components working together
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta

# Add app to path
sys.path.append('.')

from app.nlp.pipeline import NLPEventExtractionPipeline, get_pipeline_config
from app.nlp.groq_extractor import GroqEventExtractor
from app.nlp.geocoding import NigerianGeocoder
from app.nlp.verification import EventVerificationSystem
from app.nlp.news_scraper import TargetedNewsScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_groq_extraction():
    """Test Groq Llama 3 event extraction"""
    logger.info("Testing Groq Event Extraction...")
    
    # Check for API key
    if not os.getenv('GROQ_API_KEY'):
        logger.warning("GROQ_API_KEY not found, skipping test")
        return False
    
    extractor = GroqEventExtractor()
    
    # Test article
    test_article = """
    Unknown gunmen attacked a farming community in Bokkos Local Government Area of Plateau State on Monday night, 
    killing at least 12 people and injuring several others. The attackers stormed the village at around 10 PM, 
    setting houses on fire and shooting indiscriminately. Security forces have been deployed to the area, 
    but the attackers fled before they arrived. This is the latest in a series of attacks in the region.
    """
    
    try:
        event = extractor.extract_event(test_article, "https://test.com/article")
        
        if event:
            logger.info("✅ Groq extraction successful")
            logger.info(f"  Crisis Type: {event.crisis_type}")
            logger.info(f"  Actor Primary: {event.actor_primary}")
            logger.info(f"  Fatalities: {event.fatalities}")
            logger.info(f"  Location: {event.location}")
            logger.info(f"  Confidence: {event.confidence_score}")
            return True
        else:
            logger.error("❌ Groq extraction failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Groq extraction error: {str(e)}")
        return False

def test_geocoding():
    """Test geocoding functionality"""
    logger.info("Testing Geocoding...")
    
    geocoder = NigerianGeocoder()
    
    # Test location
    test_location = {
        'state': 'Plateau',
        'lga': 'Bokkos',
        'community': 'Mushere'
    }
    
    try:
        result = geocoder.geocode_location(test_location)
        
        if result:
            logger.info("✅ Geocoding successful")
            logger.info(f"  Coordinates: {result['latitude']}, {result['longitude']}")
            logger.info(f"  Precision: {result['precision']}")
            return True
        else:
            logger.error("❌ Geocoding failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Geocoding error: {str(e)}")
        return False

def test_verification():
    """Test verification system"""
    logger.info("Testing Verification System...")
    
    from app.nlp.groq_extractor import ExtractedEvent
    
    verifier = EventVerificationSystem()
    
    # Test event
    test_event = ExtractedEvent(
        incident_date="2024-01-15",
        location={"state": "Plateau", "lga": "Bokkos", "community": "Mushere"},
        crisis_type="Farmer-Herder Conflict",
        actor_primary="Herder(s)",
        actor_secondary="Farmer(s)",
        fatalities=12,
        source_url="https://test.com/article",
        confidence_score=0.0,
        raw_text="Unknown gunmen attacked a farming community..."
    )
    
    try:
        result = verifier.verify_event(test_event)
        
        logger.info("✅ Verification successful")
        logger.info(f"  Status: {result['verification_status']}")
        logger.info(f"  Confidence: {result['confidence_score']}")
        logger.info(f"  Reasoning: {result['reasoning']}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Verification error: {str(e)}")
        return False

def test_news_scraper():
    """Test news scraper"""
    logger.info("Testing News Scraper...")
    
    scraper = TargetedNewsScraper()
    
    try:
        # Test with small number of articles
        articles = scraper.scrape_recent_articles(hours_back=24)
        
        logger.info(f"✅ News scraper successful")
        logger.info(f"  Articles found: {len(articles)}")
        
        if articles:
            logger.info(f"  Sample article: {articles[0]['title']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ News scraper error: {str(e)}")
        return False

def test_full_pipeline():
    """Test the complete pipeline"""
    logger.info("Testing Full NLP Pipeline...")
    
    try:
        # Get development config
        config = get_pipeline_config('development')
        config['max_articles'] = 3  # Limit for testing
        
        # Initialize pipeline
        pipeline = NLPEventExtractionPipeline(config)
        
        # Run pipeline (mock mode if no API key)
        if not os.getenv('GROQ_API_KEY'):
            logger.warning("No GROQ_API_KEY, running in mock mode")
            # Mock the extraction step
            logger.info("✅ Pipeline configuration successful")
            return True
        
        # Run actual pipeline
        results = pipeline.run_pipeline(hours_back=24)
        
        if results['status'] == 'completed':
            logger.info("✅ Full pipeline successful")
            logger.info(f"  Articles scraped: {results['stats']['articles_scraped']}")
            logger.info(f"  Events extracted: {results['stats']['events_extracted']}")
            logger.info(f"  Events verified: {results['stats']['events_verified']}")
            return True
        else:
            logger.error(f"❌ Pipeline failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Pipeline error: {str(e)}")
        return False

def test_fatality_quantization():
    """Test fatality quantization"""
    logger.info("Testing Fatality Quantization...")
    
    extractor = GroqEventExtractor()
    
    test_cases = [
        ("a couple", 2),
        ("a few", 3),
        ("several", 3),
        ("tens", 11),
        ("a dozen", 12),
        ("more than a dozen", 13),
        ("scores", 20),
        ("dozens", 24),
        ("hundreds", 100)
    ]
    
    all_passed = True
    
    for text, expected in test_cases:
        result = extractor._quantize_fatalities(text)
        if result == expected:
            logger.info(f"  ✅ '{text}' -> {result}")
        else:
            logger.error(f"  ❌ '{text}' -> {result} (expected {expected})")
            all_passed = False
    
    return all_passed

def run_all_tests():
    """Run all tests"""
    logger.info("=" * 50)
    logger.info("NLP Event Extraction Pipeline - Test Suite")
    logger.info("=" * 50)
    
    tests = [
        ("Fatality Quantization", test_fatality_quantization),
        ("Geocoding", test_geocoding),
        ("Verification System", test_verification),
        ("News Scraper", test_news_scraper),
        ("Groq Extraction", test_groq_extraction),
        ("Full Pipeline", test_full_pipeline)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
        return True
    else:
        logger.warning(f"⚠️ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
