#!/usr/bin/env python3
"""
Create alert_read_status table
"""
import os
import sys
from sqlalchemy import create_engine, text

# Get DATABASE_URL from environment
database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("Error: DATABASE_URL environment variable not set")
    sys.exit(1)

print(f"Connecting to database...")
engine = create_engine(database_url)

with engine.connect() as conn:
    # Check if table exists
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'alert_read_status'
        );
    """))
    table_exists = result.scalar()
    
    if table_exists:
        print("✅ alert_read_status table already exists!")
        sys.exit(0)
    
    print("Creating alert_read_status table...")
    
    # Create table
    conn.execute(text("""
        CREATE TABLE alert_read_status (
            id SERIAL PRIMARY KEY,
            alert_id INTEGER NOT NULL REFERENCES alert_events(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            read_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
    """))
    conn.commit()
    print("✅ alert_read_status table created")
    
    # Create indexes
    print("Creating indexes...")
    indexes = [
        "CREATE INDEX ix_alert_read_status_alert_id ON alert_read_status(alert_id);",
        "CREATE INDEX ix_alert_read_status_user_id ON alert_read_status(user_id);",
        "CREATE UNIQUE INDEX ix_alert_read_status_unique ON alert_read_status(alert_id, user_id);"
    ]
    
    for idx_sql in indexes:
        conn.execute(text(idx_sql))
    conn.commit()
    print("✅ Indexes created")
    
print("\n✅ Migration complete! alert_read_status table created.")
