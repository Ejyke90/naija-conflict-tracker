#!/usr/bin/env python3
"""
Migration script to import kidnapping data from MariaDB export to PostgreSQL
"""

import os
import sys
import re
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.config import settings
from db.database import get_db

def parse_sql_export():
    """Parse the MariaDB SQL export file"""
    sql_file = '/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql'
    
    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Extract INSERT statements for conflicts table
    insert_pattern = r"INSERT INTO `conflicts`.*?VALUES\s*(.*?);"
    matches = re.findall(insert_pattern, content, re.DOTALL)
    
    kidnapping_records = []
    
    for match in matches:
        # Split into individual records
        records = match.split('),(')
        
        for i, record in enumerate(records):
            # Clean up the record
            if i == 0:
                record = record[1:]  # Remove opening parenthesis
            if i == len(records) - 1:
                record = record[:-1]  # Remove closing parenthesis
            
            # Parse the values
            values = []
            current_value = ''
            in_quotes = False
            quote_char = None
            
            for char in record:
                if char in ("'", '"') and not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char and in_quotes:
                    in_quotes = False
                    quote_char = None
                elif char == ',' and not in_quotes:
                    values.append(current_value.strip())
                    current_value = ''
                else:
                    current_value += char
            
            values.append(current_value.strip())  # Add last value
            
            # Check for kidnapping data (positions 18, 19, 20 are kidnapped_male, kidnapped_female, kidnapped_unknown)
            if len(values) >= 21:
                kidnapped_male = values[18] if values[18] != 'NULL' else '0'
                kidnapped_female = values[19] if values[19] != 'NULL' else '0'
                kidnapped_unknown = values[20] if values[20] != 'NULL' else '0'
                
                total_kidnapped = int(kidnapped_male) + int(kidnapped_female) + int(kidnapped_unknown)
                
                if total_kidnapped > 0:
                    kidnapping_records.append({
                        'id': values[0],
                        'incidence_date': values[1],
                        'conflict_type_id': values[2],
                        'state_id': values[5],
                        'lga_id': values[6],
                        'community': values[7].strip("'"),
                        'kidnapped_male': int(kidnapped_male),
                        'kidnapped_female': int(kidnapped_female),
                        'kidnapped_unknown': int(kidnapped_unknown),
                        'description': values[23].strip("'"),
                        'actor_1': values[21],
                        'source_url': values[27].strip("'"),
                        'data_source': values[30].strip("'"),
                        'created_at': values[32],
                        'updated_at': values[33]
                    })
    
    return kidnapping_records

def migrate_kidnapping_data():
    """Migrate kidnapping data to PostgreSQL"""
    
    # Connect to database
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Parse the SQL export
        kidnapping_records = parse_sql_export()
        
        print(f"Found {len(kidnapping_records)} kidnapping records in MariaDB export")
        
        # Show sample records
        for i, record in enumerate(kidnapping_records[:5]):
            total = record['kidnapped_male'] + record['kidnapped_female'] + record['kidnapped_unknown']
            print(f"\nRecord {i+1}:")
            print(f"  ID: {record['id']}")
            print(f"  Date: {record['incidence_date']}")
            print(f"  Community: {record['community']}")
            print(f"  Victims: {total} (M:{record['kidnapped_male']}, F:{record['kidnapped_female']}, U:{record['kidnapped_unknown']})")
            print(f"  Description: {record['description'][:100]}...")
        
        # Check if these records already exist in PostgreSQL
        existing_ids = []
        for record in kidnapping_records:
            result = db.execute(text("SELECT id FROM conflicts WHERE id = :id"), {"id": record['id']})
            if result.fetchone():
                existing_ids.append(record['id'])
        
        print(f"\n{len(existing_ids)} records already exist in PostgreSQL")
        
        # Update existing records with kidnapping data
        updated_count = 0
        for record in kidnapping_records:
            if record['id'] not in existing_ids:
                # Insert new record
                insert_sql = text("""
                    INSERT INTO conflicts (
                        id, incidence_date, conflict_type_id, country_id, region_id,
                        state_id, lga_id, community, civilian_death_male, civilian_death_female,
                        civilian_death_unknown, security_death_male, security_death_female,
                        security_death_unknown, injured_male, injured_female, injured_unknown,
                        kidnapped_male, kidnapped_female, kidnapped_unknown,
                        displaced_persons, displaced_male, displaced_female,
                        actor_1, actor_2, actor_3, description, action,
                        highway_roads_water, confirmation_verification, verification_level,
                        source_url, source_contact_details, source_contact_pictures,
                        source_metadata, data_source, reporter_id, created_at, updated_at
                    ) VALUES (
                        :id, :incidence_date, :conflict_type_id, 1, 1,
                        :state_id, :lga_id, :community, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        :kidnapped_male, :kidnapped_female, :kidnapped_unknown,
                        'No', 0, 0, :actor_1, NULL, NULL, :description, 'attack',
                        NULL, '1', 'Secondary', :source_url, NULL, NULL,
                        NULL, :data_source, NULL, :created_at, :updated_at
                    )
                """)
                
                db.execute(insert_sql, {
                    'id': record['id'],
                    'incidence_date': record['incidence_date'],
                    'conflict_type_id': record['conflict_type_id'],
                    'state_id': record['state_id'],
                    'lga_id': record['lga_id'],
                    'community': record['community'],
                    'kidnapped_male': record['kidnapped_male'],
                    'kidnapped_female': record['kidnapped_female'],
                    'kidnapped_unknown': record['kidnapped_unknown'],
                    'actor_1': record['actor_1'],
                    'description': record['description'],
                    'source_url': record['source_url'],
                    'data_source': record['data_source'],
                    'created_at': record['created_at'],
                    'updated_at': record['updated_at']
                })
                updated_count += 1
            else:
                # Update existing record
                update_sql = text("""
                    UPDATE conflicts 
                    SET kidnapped_male = :kidnapped_male,
                        kidnapped_female = :kidnapped_female,
                        kidnapped_unknown = :kidnapped_unknown
                    WHERE id = :id
                """)
                
                db.execute(update_sql, {
                    'id': record['id'],
                    'kidnapped_male': record['kidnapped_male'],
                    'kidnapped_female': record['kidnapped_female'],
                    'kidnapped_unknown': record['kidnapped_unknown']
                })
                updated_count += 1
        
        db.commit()
        print(f"\n✅ Successfully migrated {updated_count} kidnapping records to PostgreSQL")
        
        # Verify the migration
        result = db.execute(text("SELECT COUNT(*) FROM conflicts WHERE kidnapped_male > 0 OR kidnapped_female > 0 OR kidnapped_unknown > 0"))
        count = result.scalar()
        print(f"✅ Total kidnapping records in PostgreSQL: {count}")
        
        # Show sample data
        result = db.execute(text("""
            SELECT id, incidence_date, community, 
                   kidnapped_male + kidnapped_female + kidnapped_unknown as total_victims,
                   description
            FROM conflicts 
            WHERE kidnapped_male > 0 OR kidnapped_female > 0 OR kidnapped_unknown > 0
            ORDER BY incidence_date DESC
            LIMIT 5
        """))
        records = result.fetchall()
        
        print("\nSample migrated records:")
        for record in records:
            print(f"  ID: {record[0]}, Date: {record[1]}, Community: {record[2]}, Victims: {record[3]}")
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_kidnapping_data()
