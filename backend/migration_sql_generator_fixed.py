#!/usr/bin/env python3
"""
Generate SQL INSERT statements for the complete migration (fixed)
"""

import os
import sys
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def generate_migration_sql():
    """Generate SQL file with all INSERT statements"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"=== GENERATING MIGRATION SQL (FIXED) ===")
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
        output_file = f"complete_migration_fixed_{timestamp}.sql"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"-- Complete Kidnapping Data Migration (FIXED)\n")
            f.write(f"-- Generated: {timestamp}\n")
            f.write(f"-- Total records: {len(records)}\n")
            f.write(f"-- Kidnapping records: {len(kidnapping_records)}\n")
            f.write(f"-- Total victims: {sum(r['total_kidnapped'] for r in kidnapping_records)}\n\n")
            
            f.write(f"-- Clear existing data\n")
            f.write(f"TRUNCATE TABLE public.conflicts;\n\n")
            
            f.write(f"-- Insert all records\n")
            f.write(f"INSERT INTO public.conflicts (\n")
            f.write(f"    incidence_date, conflict_type_id, state_id, lga_id, community,\n")
            f.write(f"    civilian_death_male, civilian_death_female, civilian_death_unknown,\n")
            f.write(f"    security_death_male, security_death_female, security_death_unknown,\n")
            f.write(f"    injured_male, injured_female, injured_unknown,\n")
            f.write(f"    kidnapped_male, kidnapped_female, kidnapped_unknown,\n")
            f.write(f"    displaced_persons, actor_1, description, source_url, data_source,\n")
            f.write(f"    created_at, updated_at\n")
            f.write(f") VALUES\n")
            
            for i, record in enumerate(records):
                # Escape and format values
                values = []
                
                # Handle date
                date_val = record['incidence_date']
                if date_val:
                    values.append(f"'{date_val}'")
                else:
                    values.append('NULL')
                
                # Handle integers - ensure no empty strings
                for field in ['conflict_type_id', 'state_id', 'lga_id', 'civilian_death_male', 
                             'civilian_death_female', 'civilian_death_unknown', 'security_death_male',
                             'security_death_female', 'security_death_unknown', 'injured_male',
                             'injured_female', 'injured_unknown', 'kidnapped_male', 'kidnapped_female',
                             'kidnapped_unknown', 'actor_1']:
                    int_val = record[field]
                    if int_val is None or int_val == '':
                        values.append('0')
                    else:
                        values.append(str(int_val))
                
                # Handle text fields (escape single quotes, use NULL for empty)
                for field in ['community', 'displaced_persons', 'description', 'source_url', 'data_source']:
                    text_val = str(record[field]).strip()
                    if text_val and text_val != '' and text_val != '0':
                        # Escape single quotes
                        escaped_val = text_val.replace("'", "''")
                        values.append(f"'{escaped_val}'")
                    else:
                        values.append("NULL")
                
                # Add timestamps
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
    sql_file = generate_migration_sql()
    
    if sql_file:
        print(f"\n🎉 Ready to execute migration!")
        print(f"📋 File: {sql_file}")
        print(f"🚀 Run: psql 'postgresql://...' < {sql_file}")
    else:
        print(f"❌ SQL generation failed")
