#!/usr/bin/env python3
"""
NLP Event Extraction Engine Demo
Shows the system capabilities without requiring API keys
"""

import sys
import json
from datetime import datetime

# Add app to path
sys.path.append('.')

from app.nlp.geocoding import NigerianGeocoder
from app.nlp.verification import EventVerificationSystem
from app.nlp.groq_extractor import ExtractedEvent

def demo_fatality_quantization():
    """Demonstrate fatality quantization"""
    print("\n" + "="*50)
    print("FATALITY QUANTIZATION DEMO")
    print("="*50)
    
    from app.nlp.groq_extractor import GroqEventExtractor
    extractor = GroqEventExtractor()
    
    test_cases = [
        "a couple people were killed",
        "a few fatalities reported", 
        "several people died",
        "tens of casualties",
        "a dozen victims",
        "more than a dozen killed",
        "dozens injured",
        "scores of people affected",
        "hundreds displaced"
    ]
    
    print("Vague Term → Quantified Number")
    print("-" * 40)
    
    for text in test_cases:
        # Extract the vague term
        vague_terms = ['a couple', 'a few', 'several', 'tens', 'a dozen', 'more than a dozen', 'dozens', 'scores', 'hundreds']
        for term in vague_terms:
            if term in text.lower():
                number = extractor._quantize_fatalities(term)
                print(f"{term:20s} → {number:3d}")
                break

def demo_geocoding():
    """Demonstrate geocoding capabilities"""
    print("\n" + "="*50)
    print("GEOCODING DEMO")
    print("="*50)
    
    geocoder = NigerianGeocoder()
    
    test_locations = [
        {"state": "Plateau", "lga": "Bokkos", "community": "Mushere"},
        {"state": "Lagos", "lga": "Ikeja", "community": "Oba Akran"},
        {"state": "Rivers", "lga": "Port Harcourt", "community": "Diobu"},
        {"state": "Borno", "lga": "Maiduguri", "community": "Customs"},
        {"state": "Kano", "lga": "Kano", "community": "Fagge"}
    ]
    
    print("Location → Coordinates (Precision)")
    print("-" * 50)
    
    for location in test_locations:
        result = geocoder.geocode_location(location)
        if result:
            print(f"{location['state']}, {location['lga']}, {location['community']}")
            print(f"  → ({result['latitude']:.4f}, {result['longitude']:.4f}) [{result['precision']}]")
        else:
            print(f"{location} → Not found")

def demo_verification():
    """Demonstrate verification system"""
    print("\n" + "="*50)
    print("VERIFICATION SYSTEM DEMO")
    print("="*50)
    
    verifier = EventVerificationSystem()
    
    # Sample events with different quality levels
    sample_events = [
        {
            "title": "High Quality Event",
            "event": ExtractedEvent(
                incident_date="2024-01-15",
                location={"state": "Plateau", "lga": "Bokkos", "community": "Mushere"},
                crisis_type="Farmer-Herder Conflict",
                actor_primary="Herder(s)",
                actor_secondary="Farmer(s)",
                fatalities=12,
                source_url="https://punchng.com/article1",
                confidence_score=0.0,
                raw_text="Unknown gunmen attacked a farming community in Bokkos Local Government Area of Plateau State on Monday night, killing at least 12 people and injuring several others. The attackers stormed the village at around 10 PM, setting houses on fire and shooting indiscriminately. Police spokesperson DSP John James confirmed the incident and said security forces have been deployed to the area."
            )
        },
        {
            "title": "Medium Quality Event",
            "event": ExtractedEvent(
                incident_date="2024-01-14",
                location={"state": "Unknown", "lga": "Unknown", "community": "Unknown"},
                crisis_type="Gunmen Attacks",
                actor_primary="Gunmen",
                actor_secondary=None,
                fatalities=3,
                source_url="https://vanguardngr.com/article2",
                confidence_score=0.0,
                raw_text="Gunmen attacked some people in the north. Several were killed according to reports."
            )
        }
    ]
    
    for sample in sample_events:
        print(f"\n{sample['title']}:")
        print("-" * 30)
        
        result = verifier.verify_event(sample['event'])
        
        print(f"Status: {result['verification_status']}")
        print(f"Confidence: {result['confidence_score']:.2f}")
        print(f"Reasoning: {result['reasoning']}")
        print(f"Recommendations:")
        for rec in result['recommendations']:
            print(f"  • {rec}")

def demo_archetype_mapping():
    """Demonstrate crisis and actor archetype mapping"""
    print("\n" + "="*50)
    print("ARCHETYPE MAPPING DEMO")
    print("="*50)
    
    from app.nlp.groq_extractor import GroqEventExtractor
    extractor = GroqEventExtractor()
    
    print("\nCrisis Archetypes:")
    print("-" * 20)
    for crisis, keywords in extractor.crisis_archetypes.items():
        print(f"{crisis:25s}: {', '.join(keywords[:3])}...")
    
    print("\nActor Archetypes:")
    print("-" * 20)
    for actor, keywords in extractor.actor_archetypes.items():
        print(f"{actor:25s}: {', '.join(keywords[:3])}...")

def demo_confidence_scoring():
    """Demonstrate confidence scoring components"""
    print("\n" + "="*50)
    print("CONFIDENCE SCORING DEMO")
    print("="*50)
    
    verifier = EventVerificationSystem()
    
    print("\nSource Quality Weights:")
    print("-" * 25)
    for source, weight in verifier.source_weights.items():
        print(f"{source:20s}: {weight:.2f}")
    
    print("\nCrisis Reliability Weights:")
    print("-" * 30)
    for crisis, weight in verifier.crisis_reliability.items():
        print(f"{crisis:25s}: {weight:.2f}")
    
    print("\nActor Reliability Weights:")
    print("-" * 30)
    for actor, weight in verifier.actor_reliability.items():
        print(f"{actor:25s}: {weight:.2f}")

def demo_pipeline_workflow():
    """Show the complete pipeline workflow"""
    print("\n" + "="*50)
    print("PIPELINE WORKFLOW DEMO")
    print("="*50)
    
    workflow = """
    NLP Event Extraction Pipeline Workflow:
    
    1. SCRAPING (Every 6 hours)
       ├─ Target 5 high-quality Nigerian news sources
       ├─ Filter for conflict-related articles
       ├─ Extract full article content
       └─ Remove duplicates
    
    2. EXTRACTION (Groq Llama 3)
       ├─ Send article text to Groq API
       ├─ Force JSON output with structured schema
       ├─ Map to crisis/actor archetypes
       ├─ Quantify fatalities from vague terms
       └─ Calculate initial confidence
    
    3. GEOCODING
       ├─ Parse location (State, LGA, Community)
       ├─ Match against 774 LGAs database
       ├─ Lookup village coordinates
       └─ Assign precision level
    
    4. VERIFICATION
       ├─ Calculate comprehensive confidence score
       ├─ Apply source quality weights
       ├─ Validate location and date
       └─ Determine publication status
    
    5. OUTPUT
       ├─ Auto-publish if confidence ≥ 0.85
       ├─ Flag for review if confidence 0.70-0.84
       └─ Reject if confidence < 0.70
    
    6. STORAGE
       ├─ Save structured JSON events
       ├─ Store in PostGIS database
       └─ Update dashboard in real-time
    """
    
    print(workflow)

def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("NLP EVENT EXTRACTION ENGINE - DEMONSTRATION")
    print("="*60)
    print("\nThis demo showcases the ACLED-level professional")
    print("conflict event extraction system for Nigeria.")
    print("\nFeatures:")
    print("• Groq Llama 3 for high-speed, low-cost inference")
    print("• Structured JSON output matching Nextier schema")
    print("• 774 LGAs + villages geocoding database")
    print("• Confidence scoring with auto-publish threshold")
    print("• GitHub Actions 6-hour scheduled execution")
    
    # Run all demos
    demo_archetype_mapping()
    demo_fatality_quantization()
    demo_geocoding()
    demo_verification()
    demo_confidence_scoring()
    demo_pipeline_workflow()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nTo use the system:")
    print("1. Set GROQ_API_KEY environment variable")
    print("2. Run: python app/nlp/pipeline.py")
    print("3. Or deploy via GitHub Actions cron job")
    print("\nThe system will automatically:")
    print("• Scrape Nigerian news every 6 hours")
    print("• Extract conflict events using Groq")
    print("• Geocode locations precisely")
    print("• Verify and publish high-confidence events")
    print("• Store in database for visualization")

if __name__ == "__main__":
    main()
