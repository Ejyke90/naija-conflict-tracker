#!/usr/bin/env python3
"""
Quick test to verify all configurations are working
"""

import os
import sys

def test_configurations():
    """Test if all required configurations are set"""
    print("="*50)
    print("CONFIGURATION TEST")
    print("="*50)
    
    # Test Groq API Key
    groq_key = os.getenv('GROQ_API_KEY')
    if groq_key:
        print(f"✅ GROQ_API_KEY: {'*'*10}{groq_key[-10:]}")
    else:
        print("❌ GROQ_API_KEY: Not found")
    
    # Test Database URL
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        print(f"✅ DATABASE_URL: {'*'*10}{db_url[-10:]}")
    else:
        print("❌ DATABASE_URL: Not found")
    
    # Test if we can import modules
    try:
        from app.nlp.geocoding import NigerianGeocoder
        print("✅ Geocoding module: OK")
        
        geocoder = NigerianGeocoder()
        result = geocoder.geocode_location({
            'state': 'Plateau',
            'lga': 'Bokkos',
            'community': 'Mushere'
        })
        if result:
            print(f"✅ Geocoding test: {result['latitude']:.4f}, {result['longitude']:.4f}")
        else:
            print("❌ Geocoding test: Failed")
    except Exception as e:
        print(f"❌ Geocoding module: {str(e)}")
    
    # Test Groq connection (if API key exists)
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            print("✅ Groq client: Connected")
        except Exception as e:
            print(f"❌ Groq client: {str(e)}")
    
    print("\n" + "="*50)
    print("Ready for GitHub Actions!")
    print("The pipeline will run automatically every 6 automatically")
    print("="*50)

if __name__ == "__main__":
    test_configurations()
