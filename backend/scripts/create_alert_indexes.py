#!/usr/bin/env python3
"""
Create indexes for alert_read_status table
"""
import os
import sys
from sqlalchemy import create_engine, text

# Get DATABASE_URL from environment
database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("Error: DATABASE_URL environment variable not set")
    sys.exit(1)

print("Connecting to database...")
engine = create_engine(database_url)

with engine.connect() as conn:
    print("Creating indexes for alert_read_status...")
    
    indexes = [
        ("ix_alert_read_status_alert_id", "CREATE INDEX IF NOT EXISTS ix_alert_read_status_alert_id ON alert_read_status(alert_id);"),
        ("ix_alert_read_status_user_id", "CREATE INDEX IF NOT EXISTS ix_alert_read_status_user_id ON alert_read_status(user_id);"),
        ("ix_alert_read_status_unique", "CREATE UNIQUE INDEX IF NOT EXISTS ix_alert_read_status_unique ON alert_read_status(alert_id, user_id);")
    ]
    
    for idx_name, idx_sql in indexes:
        try:
            conn.execute(text(idx_sql))
            conn.commit()
            print(f"✅ {idx_name} created")
        except Exception as e:
            print(f"⚠️  {idx_name}: {str(e)}")
            conn.rollback()
    
print("\n✅ Index creation complete!")
