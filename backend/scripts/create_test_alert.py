#!/usr/bin/env python3
"""
Create a test high-risk alert event
"""
import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime
import hashlib

database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("Error: DATABASE_URL not set")
    sys.exit(1)

print("Connecting to database...")
engine = create_engine(database_url)

with engine.connect() as conn:
    # Create a test alert event
    print("\nCreating test high-risk alert...")
    
    # Generate dedup key
    dedup_string = f"Kaduna_Banditry_{datetime.now().date()}"
    dedup_key = hashlib.md5(dedup_string.encode()).hexdigest()
    
    conn.execute(text("""
        INSERT INTO alert_events (
            conflict_event_id,
            alert_type,
            risk_score,
            priority,
            status,
            location_state,
            location_lga,
            conflict_category,
            title,
            summary,
            dedup_key,
            created_at,
            updated_at
        ) VALUES (
            NULL,
            'HIGH',
            92.5,
            1,
            'ACTIVE',
            'Kaduna',
            'Birnin Gwari',
            'Banditry',
            'High-Risk Bandit Attack in Birnin Gwari',
            'Armed bandits attacked multiple villages in Birnin Gwari LGA. Estimated casualties: 15+. Residents displaced. Urgent intervention needed.',
            :dedup_key,
            NOW(),
            NOW()
        )
        RETURNING id, alert_type, risk_score, title;
    """), {"dedup_key": dedup_key})
    
    result = conn.execute(text("SELECT * FROM alert_events WHERE dedup_key = :key"), {"key": dedup_key})
    alert = result.fetchone()
    
    conn.commit()
    
    print("\n✅ Test alert created successfully!")
    print(f"   Alert ID: {alert[0]}")
    print(f"   Type: {alert[2]}")
    print(f"   Risk Score: {alert[3]}")
    print(f"   Title: {alert[8]}")
    print(f"   Status: {alert[5]}")
    print(f"\n   View in dashboard: http://localhost:3002/dashboard")
    print(f"   API: curl http://localhost:8000/api/v1/alerts/active")
