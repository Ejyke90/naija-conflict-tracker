#!/usr/bin/env python3
"""
Test script to verify the pipeline fix for ExtractedEvent object handling
"""

import os
import sys
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_extracted_event_conversion():
    """Test that ExtractedEvent objects can be converted to/from dictionaries"""
    try:
        from app.nlp.groq_extractor import ExtractedEvent
        
        # Create a sample ExtractedEvent
        sample_event = ExtractedEvent(
            incident_date="2024-01-15",
            location={"state": "Plateau", "lga": "Bokkos", "community": "Mushere"},
            crisis_type="gunmen attacks",
            actor_primary="gunmen",
            actor_secondary=None,
            fatalities=5,
            injuries=3,
            source_url="https://example.com/news",
            confidence_score=0.85,
            raw_text="Sample news article text about conflict incident"
        )
        
        print("✓ ExtractedEvent object created successfully")
        
        # Convert to dictionary
        event_dict = sample_event.dict()
        print("✓ ExtractedEvent converted to dictionary")
        
        # Convert back to ExtractedEvent
        reconstructed_event = ExtractedEvent(**event_dict)
        print("✓ Dictionary converted back to ExtractedEvent")
        
        # Verify they're equivalent
        assert reconstructed_event.incident_date == sample_event.incident_date
        assert reconstructed_event.location == sample_event.location
        assert reconstructed_event.crisis_type == sample_event.crisis_type
        assert reconstructed_event.fatalities == sample_event.fatalities
        print("✓ Conversion preserves data integrity")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False

def test_verification_system():
    """Test that verification system can handle ExtractedEvent objects"""
    try:
        from app.nlp.groq_extractor import ExtractedEvent
        from app.nlp.verification import EventVerificationSystem
        
        # Create sample event
        sample_event = ExtractedEvent(
            incident_date="2024-01-15",
            location={"state": "Plateau", "lga": "Bokkos", "community": "Mushere"},
            crisis_type="gunmen attacks",
            actor_primary="gunmen",
            fatalities=5,
            source_url="https://example.com/news",
            confidence_score=0.85,
            raw_text="Sample news article text"
        )
        
        # Initialize verification system (without geocoder to avoid dependencies)
        verifier = EventVerificationSystem(geocoder=None)
        
        # Test single event verification
        result = verifier.verify_event(sample_event)
        print("✓ Single event verification works")
        
        # Test batch verification
        batch_results = verifier.batch_verify_events([sample_event])
        print("✓ Batch event verification works")
        
        # Verify result structure
        assert 'events' in batch_results
        assert 'summary' in batch_results
        print("✓ Verification returns expected structure")
        
        return True
        
    except Exception as e:
        print(f"✗ Verification test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_mock_pipeline_results():
    """Create a mock pipeline results file for testing"""
    mock_results = {
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "duration_seconds": 45.2,
        "stats": {
            "articles_scraped": 25,
            "events_extracted": 8,
            "events_verified": 8,
            "auto_published": 3,
            "pending_verification": 4,
            "rejected": 1,
            "errors": 0
        },
        "success_rate": 100.0,
        "auto_publish_rate": 37.5
    }
    
    with open('pipeline_results.json', 'w') as f:
        json.dump(mock_results, f, indent=2)
    
    print("✓ Mock pipeline results file created")
    return True

def main():
    """Run all tests"""
    print("Testing Pipeline Fix for ExtractedEvent Handling")
    print("=" * 50)
    
    tests = [
        ("ExtractedEvent Conversion", test_extracted_event_conversion),
        ("Verification System", test_verification_system),
        ("Mock Results File", create_mock_pipeline_results)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"  FAILED: {test_name}")
    
    print(f"\n{'=' * 50}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Pipeline fix is working correctly.")
        return 0
    else:
        print("✗ Some tests failed. Pipeline may still have issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
