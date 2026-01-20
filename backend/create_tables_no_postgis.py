#!/usr/bin/env python3
"""Create database tables without PostGIS for Railway"""

import os
from sqlalchemy import create_engine, text

# Database URL
DATABASE_URL = "postgresql://postgres:bxrZnlNamzLLMoFsTrUBHmbegNVIGBEX@shuttle.proxy.rlwy.net:38253/railway"

# Create engine
engine = create_engine(DATABASE_URL)

# SQL to create tables without PostGIS
create_conflicts_sql = """
CREATE TABLE IF NOT EXISTS conflicts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_date TIMESTAMP NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    archetype VARCHAR(100),
    description TEXT,
    state VARCHAR(50) NOT NULL,
    lga VARCHAR(100),
    community VARCHAR(200),
    location_detail TEXT,
    latitude FLOAT,
    longitude FLOAT,
    fatalities_male INTEGER DEFAULT 0,
    fatalities_female INTEGER DEFAULT 0,
    fatalities_unknown INTEGER DEFAULT 0,
    injured_male INTEGER DEFAULT 0,
    injured_female INTEGER DEFAULT 0,
    injured_unknown INTEGER DEFAULT 0,
    kidnapped_male INTEGER DEFAULT 0,
    kidnapped_female INTEGER DEFAULT 0,
    kidnapped_unknown INTEGER DEFAULT 0,
    displaced INTEGER DEFAULT 0,
    perpetrator_group VARCHAR(200),
    target_group VARCHAR(200),
    source_type VARCHAR(50),
    source_url TEXT,
    source_reliability INTEGER,
    confidence_score FLOAT,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conflicts_event_date ON conflicts(event_date);
CREATE INDEX IF NOT EXISTS idx_conflicts_state ON conflicts(state);
CREATE INDEX IF NOT EXISTS idx_conflicts_event_type ON conflicts(event_type);
CREATE INDEX IF NOT EXISTS idx_conflicts_archetype ON conflicts(archetype);
CREATE INDEX IF NOT EXISTS idx_conflicts_perpetrator ON conflicts(perpetrator_group);
"""

create_locations_sql = """
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    type VARCHAR(20) NOT NULL,
    name VARCHAR(200) NOT NULL,
    parent_id INTEGER REFERENCES locations(id),
    population INTEGER,
    poverty_rate FLOAT,
    unemployment_rate FLOAT,
    extra_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(type);
CREATE INDEX IF NOT EXISTS idx_locations_parent ON locations(parent_id);
"""

try:
    with engine.connect() as conn:
        # Create conflicts table
        print("Creating conflicts table...")
        conn.execute(text(create_conflicts_sql))
        print("✅ Conflicts table created")
        
        # Create locations table
        print("Creating locations table...")
        conn.execute(text(create_locations_sql))
        print("✅ Locations table created")
        
        conn.commit()
        
    print("\n🎉 All tables created successfully!")
    
except Exception as e:
    print(f"❌ Error creating tables: {e}")
