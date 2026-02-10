#!/usr/bin/env python3
"""
Create conflicts table if it doesn't exist
"""

import os
import sys

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def create_conflicts_table():
    """Create conflicts table with proper schema"""
    try:
        from sqlalchemy import create_engine, text
        from core.config import settings
        
        # Create database connection
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'conflicts'
                )
            """))
            
            table_exists = result.scalar()
            
            if table_exists:
                print("✅ conflicts table already exists")
                return True
            
            # Create the table
            print("🔨 Creating conflicts table...")
            
            create_sql = text("""
                CREATE TABLE conflicts (
                    id SERIAL PRIMARY KEY,
                    incidence_date DATE,
                    conflict_type_id INTEGER,
                    country_id INTEGER DEFAULT 1,
                    region_id INTEGER DEFAULT 1,
                    state_id INTEGER,
                    lga_id INTEGER,
                    community TEXT,
                    civilian_death_male INTEGER DEFAULT 0,
                    civilian_death_female INTEGER DEFAULT 0,
                    civilian_death_unknown INTEGER DEFAULT 0,
                    security_death_male INTEGER DEFAULT 0,
                    security_death_female INTEGER DEFAULT 0,
                    security_death_unknown INTEGER DEFAULT 0,
                    injured_male INTEGER DEFAULT 0,
                    injured_female INTEGER DEFAULT 0,
                    injured_unknown INTEGER DEFAULT 0,
                    kidnapped_male INTEGER DEFAULT 0,
                    kidnapped_female INTEGER DEFAULT 0,
                    kidnapped_unknown INTEGER DEFAULT 0,
                    displaced_persons TEXT,
                    displaced_male INTEGER DEFAULT 0,
                    displaced_female INTEGER DEFAULT 0,
                    actor_1 INTEGER,
                    actor_2 INTEGER DEFAULT 0,
                    actor_3 INTEGER DEFAULT 0,
                    description TEXT,
                    action TEXT,
                    highway_roads_water TEXT,
                    confirmation_verification TEXT,
                    verification_level TEXT,
                    source_url TEXT,
                    source_contact_details TEXT,
                    source_contact_pictures TEXT,
                    source_metadata TEXT,
                    data_source TEXT,
                    reporter_id INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL
                );
                
                CREATE INDEX idx_conflicts_incidence_date ON conflicts(incidence_date);
                CREATE INDEX idx_conflicts_state_id ON conflicts(state_id);
                CREATE INDEX idx_conflicts_kidnapped ON conflicts(
                    CASE WHEN kidnapped_male > 0 OR kidnapped_female > 0 OR kidnapped_unknown > 0 
                    THEN 1 ELSE 0 END
                );
            """)
            
            conn.execute(create_sql)
            conn.commit()
            
            print("✅ conflicts table created successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

if __name__ == "__main__":
    success = create_conflicts_table()
    
    if success:
        print("🎉 Table ready for migration")
    else:
        print("❌ Table creation failed")
