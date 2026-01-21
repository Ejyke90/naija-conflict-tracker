#!/usr/bin/env python3
"""Test dashboard summary query locally"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.models.conflict import Conflict

# Database URL
DATABASE_URL = "postgresql://postgres:bxrZnlNamzLLMoFsTrUBHmbegNVIGBEX@shuttle.proxy.rlwy.net:38253/railway"

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Date ranges
    now = datetime.now().date()
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)
    
    print(f"📅 Date ranges:")
    print(f"  Now: {now}")
    print(f"  30 days ago: {thirty_days_ago}")
    print(f"  60 days ago: {sixty_days_ago}")
    
    # Current period incidents
    print(f"\n🔍 Querying current period incidents...")
    current_period_incidents = db.query(Conflict).filter(
        Conflict.event_date >= thirty_days_ago
    ).count()
    print(f"✅ Current period incidents: {current_period_incidents}")
    
    # Current period fatalities
    print(f"\n🔍 Querying current period fatalities...")
    current_period_fatalities = db.query(
        func.sum(Conflict.fatalities)
    ).filter(
        Conflict.event_date >= thirty_days_ago
    ).scalar() or 0
    print(f"✅ Current period fatalities: {current_period_fatalities}")
    
    # Previous period
    print(f"\n🔍 Querying previous period...")
    previous_period_incidents = db.query(Conflict).filter(
        Conflict.event_date >= sixty_days_ago,
        Conflict.event_date < thirty_days_ago
    ).count()
    print(f"✅ Previous period incidents: {previous_period_incidents}")
    
    previous_period_fatalities = db.query(
        func.sum(Conflict.fatalities)
    ).filter(
        Conflict.event_date >= sixty_days_ago,
        Conflict.event_date < thirty_days_ago
    ).scalar() or 0
    print(f"✅ Previous period fatalities: {previous_period_fatalities}")
    
    # Hotspots
    print(f"\n🔍 Querying hotspots...")
    hotspot_count = db.query(
        Conflict.state,
        Conflict.lga
    ).filter(
        Conflict.event_date >= thirty_days_ago
    ).group_by(
        Conflict.state, Conflict.lga
    ).having(
        func.count(Conflict.id) >= 5
    ).count()
    print(f"✅ Active hotspots: {hotspot_count}")
    
    # States affected
    print(f"\n🔍 Querying states affected...")
    states_affected = db.query(Conflict.state).filter(
        Conflict.event_date >= thirty_days_ago
    ).distinct().count()
    print(f"✅ States affected: {states_affected}")
    
    print(f"\n✅ All queries successful!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
