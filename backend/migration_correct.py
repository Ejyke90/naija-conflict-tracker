#!/usr/bin/env python3
"""
Final migration with EXACT column order from database schema
"""

import os
import sys
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def generate_correct_migration():
    """Generate SQL file with EXACT database column order"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"=== GENERATING CORRECT MIGRATION ===")
    print(f"Timestamp: {timestamp}")
    
    try:
        # Import the fixed parser
        from mariadb_parser import MariaDBParser
        
        # Parse the complete dataset
        print(f"📊 Parsing complete dataset...")
        sql_file = '/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql'
        
        parser = MariaDBParser(sql_file)
        records = parser.parse_sql_export()
        kidnapping_records = parser.extract_kidnapping_records()
        
        print(f"✅ Parsed {len(records)} total records")
        print(f"✅ Found {len(kidnapping_records)} kidnapping records")
        
        # Generate SQL file
        output_file = f"correct_migration_{timestamp}.sql"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"-- CORRECT Kidnapping Data Migration\n")
            f.write(f"-- Generated: {timestamp}\n")
            f.write(f"-- Total records: {len(records)}\n")
            f.write(f"-- Kidnapping records: {len(kidnapping_records)}\n")
            f.write(f"-- Total victims: {sum(r['total_kidnapped'] for r in kidnapping_records)}\n\n")
            
            f.write(f"-- Clear existing data\n")
            f.write(f"TRUNCATE TABLE public.conflicts;\n\n")
            
            f.write(f"-- Insert all records with EXACT column order\n")
            f.write(f"INSERT INTO public.conflicts (\n")
            f.write(f"    incidence_date, conflict_type_id, country_id, region_id,\n")
            f.write(f"    state_id, lga_id, community,\n")
            f.write(f"    civilian_death_male, civilian_death_female, civilian_death_unknown,\n")
            f.write(f"    security_death_male, security_death_female, security_death_unknown,\n")
            f.write(f"    injured_male, injured_female, injured_unknown,\n")
            f.write(f"    kidnapped_male, kidnapped_female, kidnapped_unknown,\n")
            f.write(f"    displaced_persons, displaced_male, displaced_female,\n")
            f.write(f"    actor_1, actor_2, actor_3,\n")
            f.write(f"    description, action, highway_roads_water,\n")
            f.write(f"    confirmation_verification, verification_level,\n")
            f.write(f"    source_url, source_contact_details, source_contact_pictures,\n")
            f.write(f"    source_metadata, data_source, reporter_id,\n")
            f.write(f"    created_at, updated_at\n")
            f.write(f") VALUES\n")
            
            for i, record in enumerate(records):
                # Format values in EXACT database column order
                values = []
                
                # 1. incidence_date (skip id - auto-generated)
                date_val = record['incidence_date']
                if date_val:
                    values.append(f"'{date_val}'")
                else:
                    values.append('NULL')
                
                # 2-7. conflict_type_id, country_id, region_id, state_id, lga_id
                for field in ['conflict_type_id', 'country_id', 'region_id', 'state_id', 'lga_id']:
                    int_val = record.get(field, 0)
                    values.append(str(int_val) if int_val else '0')
                
                # 8. community
                community_val = str(record['community']).strip()
                if community_val and community_val != '' and community_val != '0':
                    escaped_val = community_val.replace("'", "''")
                    values.append(f"'{escaped_val}'")
                else:
                    values.append("NULL")
                
                # 9-17. death and injury counts
                for field in ['civilian_death_male', 'civilian_death_female', 'civilian_death_unknown',
                             'security_death_male', 'security_death_female', 'security_death_unknown',
                             'injured_male', 'injured_female', 'injured_unknown']:
                    int_val = record.get(field, 0)
                    values.append(str(int_val) if int_val else '0')
                
                # 18-20. kidnapping counts
                for field in ['kidnapped_male', 'kidnapped_female', 'kidnapped_unknown']:
                    int_val = record.get(field, 0)
                    values.append(str(int_val) if int_val else '0')
                
                # 21. displaced_persons
                displaced_val = str(record['displaced_persons']).strip()
                if displaced_val.lower() in ['yes', 'no']:
                    values.append(f"'{displaced_val}'")
                else:
                    values.append("'No'")
                
                # 22-23. displaced counts
                for field in ['displaced_male', 'displaced_female']:
                    int_val = 0  # Default to 0 as not in source data
                    values.append(str(int_val))
                
                # 24-26. actors
                for field in ['actor_1', 'actor_2', 'actor_3']:
                    int_val = record.get(field, 0)
                    if field == 'actor_2' or field == 'actor_3':
                        int_val = 0  # Default to 0 for actor_2, actor_3
                    values.append(str(int_val) if int_val else '0')
                
                # 27-35. text fields
                for field in ['description', 'action', 'highway_roads_water', 
                             'confirmation_verification', 'verification_level',
                             'source_url', 'source_contact_details', 'source_contact_pictures',
                             'source_metadata']:
                    text_val = str(record.get(field, '')).strip()
                    if text_val and text_val != '' and text_val != '0':
                        escaped_val = text_val.replace("'", "''")
                        values.append(f"'{escaped_val}'")
                    else:
                        values.append("NULL")
                
                # 36. data_source
                data_source_val = str(record['data_source']).strip()
                if data_source_val and data_source_val != '' and data_source_val != '0':
                    escaped_val = data_source_val.replace("'", "''")
                    values.append(f"'{escaped_val}'")
                else:
                    values.append("NULL")
                
                # 37. reporter_id
                values.append('1')  # Default to 1
                
                # 38-39. timestamps
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                values.append(f"'{now}'")
                values.append(f"'{now}'")
                
                # Write the VALUES line
                f.write(f"    ({', '.join(values)})")
                
                # Add comma except for last record
                if i < len(records) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
            
            f.write(f"\n-- Verification query\n")
            f.write(f"SELECT \n")
            f.write(f"    COUNT(*) as total_records,\n")
            f.write(f"    COUNT(*) FILTER (WHERE kidnapped_male > 0 OR kidnapped_female > 0 OR kidnapped_unknown > 0) as kidnapping_records,\n")
            f.write(f"    SUM(kidnapped_male + kidnapped_female + kidnapped_unknown) as total_victims\n")
            f.write(f"FROM public.conflicts;\n")
        
        print(f"✅ SQL file generated: {output_file}")
        print(f"📊 Ready to execute with: psql <your_connection_string> < {output_file}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error generating SQL: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    sql_file = generate_correct_migration()
    
    if sql_file:
        print(f"\n🎉 Ready to execute CORRECT migration!")
        print(f"📋 File: {sql_file}")
        print(f"🚀 Run: psql 'postgresql://...' < {sql_file}")
    else:
        print(f"❌ SQL generation failed")
