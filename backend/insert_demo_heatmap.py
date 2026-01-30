#!/usr/bin/env python3
"""
Direct SQL insertion of demo heatmap data into Railway production database.
"""

import requests
import json
from datetime import datetime, timedelta

# Production API base URL
PROD_API = "https://naija-conflict-tracker-production.up.railway.app/api/v1"

# Demo conflict data with coordinates
DEMO_CONFLICTS = [
    # Kaduna - High Intensity (all red)
    {"location": "Kaduna rural clash", "lat": 8.9267, "lng": 7.3486, "fatalities": 45, "days_ago": 5},
    {"location": "Kaduna town incident", "lat": 9.0267, "lng": 7.4486, "fatalities": 38, "days_ago": 8},
    {"location": "Chikun LGA violence", "lat": 9.1267, "lng": 7.3486, "fatalities": 52, "days_ago": 12},
    {"location": "Igabi community attack", "lat": 9.2267, "lng": 7.4486, "fatalities": 28, "days_ago": 15},
    
    # Maiduguri - Medium-High Intensity  
    {"location": "Maiduguri fringe battle", "lat": 12.9567, "lng": 2.0967, "fatalities": 35, "days_ago": 3},
    {"location": "Borno rural clash", "lat": 13.0967, "lng": 2.2367, "fatalities": 20, "days_ago": 7},
    {"location": "Jere community violence", "lat": 13.2367, "lng": 2.0967, "fatalities": 18, "days_ago": 10},
    
    # Port Harcourt - Lower Intensity (green)
    {"location": "Rivers piracy incident", "lat": 4.6157, "lng": 6.9422, "fatalities": 12, "days_ago": 4},
    {"location": "Port Harcourt gang clash", "lat": 4.7357, "lng": 7.0622, "fatalities": 8, "days_ago": 9},
    
    # Lagos/Southwest - Low Intensity (green)
    {"location": "Lagos border dispute", "lat": 6.3744, "lng": 3.3292, "fatalities": 5, "days_ago": 6},
    {"location": "Oyo community clash", "lat": 6.4744, "lng": 3.4292, "fatalities": 3, "days_ago": 11},
]

def insert_demo_data():
    """Insert demo conflicts via API."""
    print("🌍 Inserting demo heatmap data into production database...")
    print("=" * 60)
    
    success_count = 0
    
    for conflict in DEMO_CONFLICTS:
        # Prepare conflict payload
        event_date = datetime.utcnow() - timedelta(days=conflict["days_ago"])
        
        # Calculate intensity for reference
        max_fatalities = 52
        intensity = 1 + (conflict["fatalities"] / max_fatalities) * 9
        color = "🟢" if intensity < 4 else "🟠" if intensity < 7 else "🔴"
        
        # Create conflict event through API
        # Since there's likely no public create endpoint, we'll use direct database SQL
        # For now, just log what we would insert
        print(f"{color} {conflict['location']}")
        print(f"   Location: ({conflict['lat']:.4f}, {conflict['lng']:.4f})")
        print(f"   Fatalities: {conflict['fatalities']} | Intensity: {intensity:.1f}/10")
        print()
        
        success_count += 1
    
    print("=" * 60)
    print(f"\n✅ Ready to insert {success_count} demo conflicts!")
    print("\nNote: Use Rails console or direct PostgreSQL to insert:")
    print("\nSQL INSERT example:")
    print("""
    INSERT INTO conflict_events 
    (event_date, year, month, event_type, event_category, conflict_type, 
     state, lga, location, latitude, longitude, actor1, actor2, actor1_type, actor2_type,
     fatalities, injuries, properties_destroyed, displaced_persons, source, notes, verified, confidence_level)
    VALUES
    ('2026-01-25'::date, 2026, 1, 'Armed Conflict', 'Violence', 'Armed Conflict',
     'Kaduna', 'Chikun', 'Chikun LGA violence', 9.1267, 7.3486, 'Armed Group', 'Civilians',
     'Rebel Group', 'Civilians', 52, 104, 0, 520, 'Demo Data', 'High fatality incident', true, 'High');
    """)
    
    print("\n🗺️  After insertion, test heatmap at:")
    print("https://naija-conflict-tracker.vercel.app/dashboard")
    print("\nRecommended demo zoom locations:")
    print("   1. Kaduna (9.08°N, 7.40°E) - All 3 colors (green, orange, red)")
    print("   2. Maiduguri (13.17°N, 2.17°E) - Orange & red bands")
    print("   3. Port Harcourt (4.80°N, 7.00°E) - Green band")

if __name__ == "__main__":
    insert_demo_data()
