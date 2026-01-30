#!/usr/bin/env python3
"""
Populate production database with demo conflict data to showcase heatmap visualization.
Creates clusters of conflicts with varying fatalities to show green/orange/red intensity bands.
"""

import os
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Import models
from app.models.conflict import ConflictEvent


# Demo locations in Nigeria with high, medium, and low intensity clusters
DEMO_CLUSTERS = {
    "North Central (High Intensity)": {
        "center": (9.0767, 7.3986),  # Kaduna, Nigeria
        "radius": 0.5,
        "incidents": [
            {"name": "Kaduna rural clash", "fatalities": 45, "days_ago": 5},
            {"name": "Kaduna town incident", "fatalities": 38, "days_ago": 8},
            {"name": "Chikun LGA violence", "fatalities": 52, "days_ago": 12},
            {"name": "Igabi community attack", "fatalities": 28, "days_ago": 15},
        ]
    },
    "Northeast (Medium-High Intensity)": {
        "center": (13.1667, 2.1667),  # Maiduguri, Borno
        "radius": 0.7,
        "incidents": [
            {"name": "Maiduguri fringe battle", "fatalities": 35, "days_ago": 3},
            {"name": "Borno rural clash", "fatalities": 20, "days_ago": 7},
            {"name": "Jere community violence", "fatalities": 18, "days_ago": 10},
        ]
    },
    "South South (Medium Intensity)": {
        "center": (4.7957, 7.0022),  # Port Harcourt, Rivers
        "radius": 0.6,
        "incidents": [
            {"name": "Rivers piracy incident", "fatalities": 12, "days_ago": 4},
            {"name": "Port Harcourt gang clash", "fatalities": 8, "days_ago": 9},
        ]
    },
    "Southwest (Low-Medium Intensity)": {
        "center": (6.5244, 3.3792),  # Lagos
        "radius": 0.5,
        "incidents": [
            {"name": "Lagos border dispute", "fatalities": 5, "days_ago": 6},
            {"name": "Oyo community clash", "fatalities": 3, "days_ago": 11},
        ]
    },
}


def populate_demo_data():
    """Populate database with demo conflict data."""
    
    # Create async engine for production database
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:naija123@localhost:5432/naija_conflicts_prod"
    )
    
    engine = create_engine(database_url)
    
    try:
        with Session(engine) as session:
            print("🌍 Populating demo heatmap data...")
            print("=" * 60)
            
            incident_count = 0
            
            for cluster_name, cluster_data in DEMO_CLUSTERS.items():
                center_lat, center_lng = cluster_data["center"]
                radius = cluster_data["radius"]
                
                print(f"\n📍 {cluster_name}")
                print(f"   Center: ({center_lat:.4f}, {center_lng:.4f})")
                
                for idx, incident in enumerate(cluster_data["incidents"]):
                    # Generate slightly offset coordinates within the cluster
                    offset_lat = center_lat + (idx * 0.1 - 0.15) * (radius / 0.5)
                    offset_lng = center_lng + ((idx % 2) * 0.1 - 0.05) * (radius / 0.5)
                    
                    event_date = datetime.utcnow() - timedelta(days=incident["days_ago"])
                    
                    event = ConflictEvent(
                        event_date=event_date.date(),
                        year=event_date.year,
                        month=event_date.month,
                        event_type="Armed Conflict",
                        event_category="Violence",
                        conflict_type="Armed Conflict",
                        state="Demo State",
                        lga="Demo LGA",
                        location=incident["name"],
                        latitude=offset_lat,
                        longitude=offset_lng,
                        actor1="Armed Group",
                        actor2="Community/State",
                        actor1_type="Rebel Group",
                        actor2_type="Civilians",
                        fatalities=incident["fatalities"],
                        injuries=incident["fatalities"] * 2,
                        properties_destroyed=0,
                        displaced_persons=incident["fatalities"] * 10,
                        source="Demo Heatmap Data",
                        notes=f"Demo conflict for heatmap visualization: {incident['name']}",
                        verified=True,
                        confidence_level="High",
                    )
                    
                    session.add(event)
                    incident_count += 1
                    
                    # Calculate intensity (1-10 scale)
                    max_fatalities = 52  # Maximum in our demo set
                    intensity = 1 + (incident["fatalities"] / max_fatalities) * 9
                    color = "🟢" if intensity < 4 else "🟠" if intensity < 7 else "🔴"
                    
                    print(f"   {color} {incident['name']}")
                    print(f"      Location: ({offset_lat:.4f}, {offset_lng:.4f})")
                    print(f"      Fatalities: {incident['fatalities']} | Intensity: {intensity:.1f}/10")
                
            # Commit all incidents
            session.commit()
            
            print("\n" + "=" * 60)
            print(f"✅ Successfully added {incident_count} demo conflicts!")
            print("\n📊 Intensity Breakdown:")
            print("   🟢 Green (Low):    0-3.3 fatalities")
            print("   🟠 Orange (Med):   3.3-6.6 fatalities")
            print("   🔴 Red (High):     6.6-10 fatalities")
            print("\n🗺️  Recommended zoom locations for demo:")
            print("   1. Kaduna (9.08°N, 7.40°E) - See all 3 intensity colors clustered")
            print("   2. Maiduguri (13.17°N, 2.17°E) - High intensity cluster")
            print("   3. Port Harcourt (4.80°N, 7.00°E) - Lower intensity cluster")
            print("\n💡 Pro tip: Click 'Heatmap (On)' button, then zoom in to each location")
            
    except Exception as e:
        print(f"❌ Error populating demo data: {e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    populate_demo_data()
