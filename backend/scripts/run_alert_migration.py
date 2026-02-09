#!/usr/bin/env python3
"""
Run alert tables migration (004) on production database
"""
import os
import sys
from sqlalchemy import create_engine, text

# Get DATABASE_URL from environment
database_url = os.getenv('NEON_URL') or os.getenv('DATABASE_URL')
if not database_url:
    print("Error: NEON_URL or DATABASE_URL environment variable not set")
    sys.exit(1)

print(f"Connecting to database...")
engine = create_engine(database_url)

# Check current migration version
with engine.connect() as conn:
    # Check if alert_events table exists
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'alert_events'
        );
    """))
    alert_table_exists = result.scalar()
    
    if alert_table_exists:
        print("✅ alert_events table already exists!")
        sys.exit(0)
    
    print("\nCreating alert_events table...")
    
    # Create alert_events table (from migration 004)
    conn.execute(text("""
        CREATE TABLE alert_events (
            id SERIAL PRIMARY KEY,
            conflict_event_id INTEGER,
            alert_type VARCHAR(20) NOT NULL,
            risk_score FLOAT NOT NULL,
            priority INTEGER NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
            location_state VARCHAR(100),
            location_lga VARCHAR(100),
            conflict_category VARCHAR(100),
            title TEXT NOT NULL,
            summary TEXT,
            dedup_key VARCHAR(32),
            acknowledged_at TIMESTAMP,
            acknowledged_by_user_id UUID REFERENCES users(id),
            acknowledgment_notes TEXT,
            resolved_at TIMESTAMP,
            resolved_by_user_id UUID REFERENCES users(id),
            resolution_notes TEXT,
            resolution_actions JSONB,
            notified_channels JSONB,
            notification_sent_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
    """))
    conn.commit()
    print("✅ alert_events table created")
    
    # Create indexes
    print("Creating indexes...")
    indexes = [
        "CREATE INDEX ix_alert_events_status ON alert_events(status);",
        "CREATE INDEX ix_alert_events_created_at ON alert_events(created_at);",
        "CREATE INDEX ix_alert_events_risk_score ON alert_events(risk_score);",
        "CREATE INDEX ix_alert_events_alert_type ON alert_events(alert_type);",
        "CREATE INDEX ix_alert_events_dedup_key ON alert_events(dedup_key);",
        "CREATE INDEX ix_alert_events_location_state ON alert_events(location_state);"
    ]
    
    for idx_sql in indexes:
        conn.execute(text(idx_sql))
    conn.commit()
    print("✅ Indexes created")

print("\n✅ Migration complete! alert_events table created.")
