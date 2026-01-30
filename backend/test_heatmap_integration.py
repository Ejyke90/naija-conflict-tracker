#!/usr/bin/env python
"""
Test script for heatmap endpoint integration
Tests both conflicts and spatial endpoints
"""

import requests
import json
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "http://localhost:8000"
API_V1 = f"{BACKEND_URL}/api/v1"

def test_conflicts_heatmap():
    """Test /conflicts/heatmap/data endpoint"""
    print("\n" + "="*60)
    print("Testing /api/v1/conflicts/heatmap/data")
    print("="*60)
    
    try:
        response = requests.get(
            f"{API_V1}/conflicts/heatmap/data",
            params={"days_back": 30}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Points returned: {len(data.get('points', []))}")
            print(f"✅ Bounds: {data.get('bounds')}")
            
            if data['points']:
                print(f"✅ Sample point: {data['points'][0]}")
                print(f"   Format: [latitude, longitude, intensity]")
            
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_spatial_heatmap():
    """Test /spatial/heatmap/data endpoint"""
    print("\n" + "="*60)
    print("Testing /api/v1/spatial/heatmap/data")
    print("="*60)
    
    try:
        response = requests.get(
            f"{API_V1}/spatial/heatmap/data",
            params={"days_back": 30}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Total locations: {data.get('total_locations')}")
            print(f"✅ Points returned: {len(data.get('points', []))}")
            print(f"✅ Details returned: {len(data.get('details', []))}")
            
            if data['details']:
                detail = data['details'][0]
                print(f"✅ Sample detail:")
                print(f"   Location: {detail.get('location')}")
                print(f"   State: {detail.get('state')}")
                print(f"   Incidents: {detail.get('incident_count')}")
                print(f"   Fatalities: {detail.get('total_fatalities')}")
                print(f"   Intensity: {detail.get('intensity')}")
            
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_geojson_export():
    """Test converting heatmap data to GeoJSON"""
    print("\n" + "="*60)
    print("Testing GeoJSON Export Format")
    print("="*60)
    
    try:
        response = requests.get(
            f"{API_V1}/conflicts/heatmap/data",
            params={"days_back": 30}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch heatmap data: {response.status_code}")
            return False
        
        data = response.json()
        points = data.get('points', [])
        
        if not points:
            print("⚠️  No points to export")
            return True
        
        # Convert to GeoJSON
        features = []
        for point in points:
            lat, lng, intensity = point
            features.append({
                "type": "Feature",
                "properties": {"intensity": intensity},
                "geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]  # GeoJSON uses [lng, lat]
                }
            })
        
        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Validate GeoJSON
        json.dumps(geojson)  # Will throw if invalid
        
        print(f"✅ GeoJSON valid")
        print(f"✅ Features: {len(geojson['features'])}")
        print(f"✅ Sample feature:")
        print(f"   {json.dumps(geojson['features'][0], indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_intensity_values():
    """Test intensity value ranges"""
    print("\n" + "="*60)
    print("Testing Intensity Value Ranges")
    print("="*60)
    
    try:
        response = requests.get(
            f"{API_V1}/conflicts/heatmap/data",
            params={"days_back": 30}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch heatmap data")
            return False
        
        data = response.json()
        points = data.get('points', [])
        
        if not points:
            print("⚠️  No points to analyze")
            return True
        
        intensities = [p[2] for p in points]
        min_intensity = min(intensities)
        max_intensity = max(intensities)
        avg_intensity = sum(intensities) / len(intensities)
        
        print(f"✅ Intensity Statistics:")
        print(f"   Min: {min_intensity:.2f}")
        print(f"   Max: {max_intensity:.2f}")
        print(f"   Avg: {avg_intensity:.2f}")
        print(f"   Count: {len(intensities)}")
        
        # Check if values are in reasonable range (0-10 for Leaflet.heat)
        if max_intensity <= 10:
            print(f"✅ All intensities <= 10 (valid for Leaflet.heat)")
        else:
            print(f"⚠️  Some intensities > 10 (may need normalization)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("HEATMAP ENDPOINT TEST SUITE")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.utcnow().isoformat()}")
    print("="*60)
    
    results = {
        "Conflicts Heatmap": test_conflicts_heatmap(),
        "Spatial Heatmap": test_spatial_heatmap(),
        "GeoJSON Export": test_geojson_export(),
        "Intensity Values": test_intensity_values(),
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
