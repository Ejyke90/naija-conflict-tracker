#!/usr/bin/env python3
"""Test Railway database connection and data"""

import os
from sqlalchemy import create_engine, text

# Database URL
DATABASE_URL = "postgresql://postgres:bxrZnlNamzLLMoFsTrUBHmbegNVIGBEX@shuttle.proxy.rlwy.net:38253/railway"

# Create engine
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Check if conflicts table exists
        result = conn.execute(text("SELECT COUNT(*) FROM conflicts")).scalar()
        print(f"✅ Conflicts in database: {result}")
        
        # Check table structure
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'conflicts'
            ORDER BY ordinal_position
        """)).fetchall()
        
        print("\n📋 Conflicts table structure:")
        for col in result:
            print(f"  - {col[0]}: {col[1]}")
            
        # Sample data
        result = conn.execute(text("""
            SELECT state, event_type, perpetrator_group, event_date 
            FROM conflicts 
            LIMIT 5
        """)).fetchall()
        
        print("\n📊 Sample data:")
        for row in result:
            print(f"  - {row[0]}: {row[1]} by {row[2]} on {row[3]}")
            
except Exception as e:
    print(f"❌ Error: {e}")
