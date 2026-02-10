#!/usr/bin/env python3
"""
Create missing locations table and populate with Nigerian states and LGAs
"""
import psycopg2
from sqlalchemy import create_engine, text
from app.core.config import settings

def create_locations_table():
    """Create locations table and populate with Nigerian data"""
    
    database_url = settings.DATABASE_URL
    
    # Nigerian states and their capitals
    NIGERIAN_STATES = {
        'Abia': 'Umuahia', 'Adamawa': 'Yola', 'Akwa Ibom': 'Uyo', 'Anambra': 'Awka',
        'Bauchi': 'Bauchi', 'Bayelsa': 'Yenagoa', 'Benue': 'Makurdi', 'Borno': 'Maiduguri',
        'Cross River': 'Calabar', 'Delta': 'Asaba', 'Ebonyi': 'Abakaliki', 'Edo': 'Benin City',
        'Ekiti': 'Ado Ekiti', 'Enugu': 'Enugu', 'Gombe': 'Gombe', 'Imo': 'Owerri',
        'Jigawa': 'Dutse', 'Kaduna': 'Kaduna', 'Kano': 'Kano', 'Katsina': 'Katsina',
        'Kebbi': 'Birnin Kebbi', 'Kogi': 'Lokoja', 'Kwara': 'Ilorin', 'Lagos': 'Ikeja',
        'Nasarawa': 'Karu', 'Niger': 'Minna', 'Ogun': 'Abeokuta', 'Ondo': 'Akure',
        'Osun': 'Osogbo', 'Oyo': 'Ibadan', 'Plateau': 'Jos', 'Rivers': 'Port Harcourt',
        'Sokoto': 'Sokoto', 'Taraba': 'Jalingo', 'Yobe': 'Damaturu', 'Zamfara': 'Gusau',
        'FCT': 'Abuja'
    }
    
    # Sample LGAs by state
    NIGERIAN_LGAS = {
        'Abia': ['Aba North', 'Aba South', 'Arochukwu', 'Bende', 'Ikwuano', 'Isiala Ngwa North'],
        'Adamawa': ['Demsa', 'Fufure', 'Guyuk', 'Hong', 'Jimeta', 'Maiduguri', 'Mayobelwa'],
        'Akwa Ibom': ['Abak', 'Afilang', 'Etim Ekpo', 'Eket', 'Etinan', 'Ikot Abasi'],
        'Anambra': ['Aguata', 'Anambra East', 'Anambra West', 'Anaocha', 'Awka North'],
        'Borno': ['Abadam', 'Askira Uba', 'Bama', 'Bayo', 'Biu', 'Chibok'],
        'Kaduna': ['Birnin Gwari', 'Chikun', 'Giwa', 'Jaba', 'Jema\'a', 'Kachia'],
        'Kano': ['Ajinkyire', 'Albasu', 'Bagwaji', 'Bebeji', 'Bichi', 'Bunkure'],
        'Lagos': ['Agege', 'Ajeromi-Ifelodun', 'Alimosho', 'Amuwo-Odofin', 'Apapa'],
        'Oyo': ['Afijio', 'Egbeda', 'Ibadan North', 'Ibadan South East', 'Ibarapa Central'],
        'Rivers': ['Abua/Odual', 'Ahoada East', 'Ahoada West', 'Akuku-Toru', 'Andoni'],
    }
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Create locations table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS locations (
                    id SERIAL PRIMARY KEY,
                    type VARCHAR(20) NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    parent_id INTEGER REFERENCES locations(id),
                    boundary GEOGRAPHY(MULTIPOLYGON, 4326),
                    population INTEGER,
                    poverty_rate FLOAT,
                    unemployment_rate FLOAT,
                    extra_data JSONB
                )
            """))
            
            # Create indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_locations_type ON locations(type)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_locations_name ON locations(name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_locations_parent_id ON locations(parent_id)"))
            
            print("✅ Created locations table with indexes")
            
            # Insert Nigerian states
            for state_name in sorted(NIGERIAN_STATES.keys()):
                conn.execute(text("""
                    INSERT INTO locations (type, name) 
                    VALUES (:type, :name)
                    ON CONFLICT DO NOTHING
                """), {'type': 'state', 'name': state_name})
            
            conn.commit()
            print(f"✅ Inserted {len(NIGERIAN_STATES)} states")
            
            # Insert LGAs
            lga_count = 0
            for state_name, lgas in NIGERIAN_LGAS.items():
                # Get state ID
                result = conn.execute(text("""
                    SELECT id FROM locations WHERE type = 'state' AND name = :name
                """), {'name': state_name}).fetchone()
                
                if result:
                    state_id = result[0]
                    for lga_name in lgas:
                        conn.execute(text("""
                            INSERT INTO locations (type, name, parent_id) 
                            VALUES (:type, :name, :parent_id)
                            ON CONFLICT DO NOTHING
                        """), {'type': 'lga', 'name': lga_name, 'parent_id': state_id})
                        lga_count += 1
            
            conn.commit()
            print(f"✅ Inserted {lga_count} LGAs")
            
            # Verify data
            state_count = conn.execute(text("SELECT COUNT(*) FROM locations WHERE type = 'state'")).scalar()
            lga_count = conn.execute(text("SELECT COUNT(*) FROM locations WHERE type = 'lga'")).scalar()
            
            print(f"📊 Final counts: {state_count} states, {lga_count} LGAs")
            print("🎉 Locations table creation completed!")
            
    except Exception as e:
        print(f"❌ Error creating locations table: {e}")
        raise

if __name__ == "__main__":
    create_locations_table()
