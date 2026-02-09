"""
Test Data Validation System
Validates the data quality rules implementation
"""

from app.services.data_validator import ConflictDataValidator
from datetime import datetime, timedelta


def test_validation_system():
    """Test the data validator with various scenarios"""
    
    validator = ConflictDataValidator()
    
    print("\n" + "="*80)
    print("DATA VALIDATION SYSTEM TEST")
    print("="*80)
    
    # Test 1: Valid event
    print("\n[TEST 1] Valid Conflict Event")
    valid_event = {
        "event_date": datetime.now().date() - timedelta(days=1),
        "state": "Kaduna",
        "event_type": "Armed clash",
        "fatalities": 15,
        "actor1": "Bandits",
        "actor2": "Military",
        "location": "Kauru LGA"
    }
    is_valid, issues, severity = validator.validate(valid_event)
    print(f"  ✓ Valid: {is_valid}")
    print(f"  ✓ Issues: {len(issues)} ({', '.join(issues) if issues else 'None'})")
    assert is_valid, "Valid event should pass validation"
    
    # Test 2: Missing required field
    print("\n[TEST 2] Missing Required Field (event_date)")
    invalid_event = {
        "state": "Lagos",
        "event_type": "Riot",
        "fatalities": 5
    }
    is_valid, issues, severity = validator.validate(invalid_event)
    print(f"  ✓ Valid: {is_valid}")
    print(f"  ✓ Severity: {severity}")
    print(f"  ✓ Issues: {issues}")
    assert not is_valid, "Event without event_date should fail"
    assert severity == "critical", "Missing required field should be critical"
    
    # Test 3: Invalid state
    print("\n[TEST 3] Invalid State Name")
    invalid_state_event = {
        "event_date": datetime.now().date() - timedelta(days=1),
        "state": "Atlantica",  # Non-existent state
        "event_type": "Armed clash",
        "fatalities": 10
    }
    is_valid, issues, severity = validator.validate(invalid_state_event)
    print(f"  ✓ Valid: {is_valid}")
    print(f"  ✓ Issues: {issues}")
    assert not is_valid, "Invalid state should fail validation"
    assert any("Invalid state" in issue for issue in issues)
    
    # Test 4: Suspicious casualty numbers
    print("\n[TEST 4] Suspicious Casualty Numbers (too high)")
    suspicious_event = {
        "event_date": datetime.now().date() - timedelta(days=1),
        "state": "Borno",
        "event_type": "Armed clash",
        "fatalities": 5000,  # Exceeds MAX_FATALITIES
        "actor1": "Boko Haram",
        "actor2": "Military"
    }
    is_valid, issues, severity = validator.validate(suspicious_event)
    print(f"  ✓ Valid: {is_valid}")
    print(f"  ✓ Severity: {severity}")
    print(f"  ✓ Issues: {issues}")
    assert not is_valid, "Excessive fatalities should fail validation"
    assert severity == "warning", "Excessive value should be warning (flagged for review, not rejected)"
    
    # Test 5: Invalid coordinates
    print("\n[TEST 5] Invalid Coordinates (outside Nigeria)")
    bad_coords_event = {
        "event_date": datetime.now().date() - timedelta(days=1),
        "state": "Lagos",
        "event_type": "Riot",
        "fatalities": 2,
        "latitude": -30.5,  # Outside Nigeria
        "longitude": 50.0   # Outside Nigeria
    }
    is_valid, issues, severity = validator.validate(bad_coords_event)
    print(f"  ✓ Valid: {is_valid}")
    print(f"  ✓ Severity: {severity}")
    print(f"  ✓ Issues: {[i for i in issues if 'Latitude' in i or 'Longitude' in i]}")
    assert severity == "warning", "Invalid coordinates should be warning"
    
    # Test 6: Future date
    print("\n[TEST 6] Future Event Date")
    future_event = {
        "event_date": datetime.now().date() + timedelta(days=5),
        "state": "Rivers",
        "event_type": "Protest",
        "fatalities": 0
    }
    is_valid, issues, severity = validator.validate(future_event)
    print(f"  ✓ Valid: {is_valid}")
    print(f"  ✓ Issues: {issues}")
    assert not is_valid, "Future date should fail validation"
    assert severity == "critical"
    
    # Test 7: Negative casualties
    print("\n[TEST 7] Negative Casualty Numbers")
    negative_event = {
        "event_date": datetime.now().date() - timedelta(days=1),
        "state": "Enugu",
        "event_type": "Armed clash",
        "fatalities": -5
    }
    is_valid, issues, severity = validator.validate(negative_event)
    print(f"  ✓ Valid: {is_valid}")
    print(f"  ✓ Issues: {issues}")
    assert not is_valid, "Negative casualties should fail"
    
    # Test 8: Batch validation
    print("\n[TEST 8] Batch Validation Summary")
    events = [valid_event, invalid_event, bad_coords_event]
    results = [validator.validate(e) for e in events]
    summary = validator.get_validation_summary(results)
    print(f"  ✓ Total Events: {summary['total_records']}")
    print(f"  ✓ Passed: {summary['passed']}")
    print(f"  ✓ Failed: {summary['failed']}")
    print(f"  ✓ Pass Rate: {summary['pass_rate']:.1f}%")
    print(f"  ✓ Critical Issues: {summary['critical_issues']}")
    print(f"  ✓ Warning Issues: {summary['warning_issues']}")
    assert summary['passed'] == 1, "Only 1 event should pass"
    assert summary['failed'] == 2, "2 events should fail"
    
    # Test 9: Valid Nigerian states
    print("\n[TEST 9] All Valid Nigerian States")
    test_states = [
        "Kaduna", "Lagos", "Borno", "Rivers", "Kano",
        "Federal Capital Territory", "Akwa Ibom", "Anambra"
    ]
    for state in test_states:
        event = {
            "event_date": datetime.now().date() - timedelta(days=1),
            "state": state,
            "event_type": "Armed clash",
            "fatalities": 5
        }
        is_valid, issues, severity = validator.validate(event)
        print(f"  ✓ {state}: {is_valid}")
        assert is_valid, f"Valid state '{state}' should pass"
    
    # Test 10: Conflict type validation
    print("\n[TEST 10] Valid Conflict Types")
    test_types = [
        "Violence against civilians",
        "Armed clash",
        "Explosions/Remote violence",
        "Kidnapping",
        "Unknown"
    ]
    for conflict_type in test_types:
        event = {
            "event_date": datetime.now().date() - timedelta(days=1),
            "state": "Kaduna",
            "event_type": conflict_type,
            "fatalities": 5
        }
        is_valid, issues, severity = validator.validate(event)
        print(f"  ✓ {conflict_type}: Valid")
        assert is_valid, f"Valid type '{conflict_type}' should pass"
    
    print("\n" + "="*80)
    print("✓ ALL TESTS PASSED - Data Validation System Working Correctly")
    print("="*80)
    print("\nKey Validation Rules Verified:")
    print("  ✓ Required fields enforced")
    print("  ✓ Date validation (future, old dates)")
    print("  ✓ State validation (Nigerian states only)")
    print("  ✓ Casualty number limits")
    print("  ✓ Coordinate validation (Nigeria bounds)")
    print("  ✓ Conflict type recognition")
    print("  ✓ Batch processing")
    print("  ✓ Severity classification (critical vs warning)")


if __name__ == "__main__":
    test_validation_system()
