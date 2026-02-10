#!/usr/bin/env python3
"""
Complete Conflict Data Import Generator
Extracts all 7,300+ records from MySQL dump and converts to PostgreSQL format
"""

import re
import sys
from datetime import datetime

def extract_all_conflicts():
    """Extract ALL conflict records from the MySQL dump"""
    
    # Read the SQL file
    with open('/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql', 'r') as f:
        content = f.read()
    
    # Find the conflicts section
    conflicts_start = content.find('-- Dumping data for table `conflicts`')
    if conflicts_start == -1:
        print("Conflicts table not found")
        return []
    
    # Extract everything after conflicts start
    conflicts_section = content[conflicts_start:]
    
    # Find the VALUES section
    values_start = conflicts_section.find('VALUES')
    if values_start == -1:
        print("VALUES section not found")
        return []
    
    values_section = conflicts_section[values_start + 6:]  # Skip 'VALUES'
    
    # Split by lines and filter out non-record lines
    lines = values_section.split('\n')
    record_lines = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('(') and line.endswith('),') or line.endswith(');'):
            record_lines.append(line.rstrip(',').rstrip(';'))
    
    print(f"Found {len(record_lines)} conflict record lines")
    return record_lines

def parse_record_line(line):
    """Parse a single record line into components"""
    
    # Remove surrounding parentheses
    line = line.strip('(').strip(')')
    
    # Split by comma, but handle quoted strings properly
    parts = []
    current = ''
    in_quotes = False
    
    for char in line:
        if char == "'" and not in_quotes:
            in_quotes = True
        elif char == "'" and in_quotes:
            in_quotes = False
        elif char == ',' and not in_quotes:
            parts.append(current.strip())
            current = ''
        else:
            current += char
    
    if current:
        parts.append(current.strip())
    
    # Ensure we have enough parts
    while len(parts) < 35:
        parts.append('NULL')
    
    return parts[:35]  # Return first 35 parts (conflict record fields)

def convert_to_postgresql_sql(record_lines):
    """Convert all record lines to PostgreSQL INSERT statements"""
    
    # State mapping
    state_map = {
        1: 'Adamawa', 2: 'Bauchi', 3: 'Borno', 4: 'Gombe', 5: 'Taraba', 6: 'Yobe',
        7: 'Benue', 8: 'Kogi', 9: 'Kwara', 10: 'Nasarawa', 11: 'Niger', 12: 'Plateau', 13: 'FCT',
        14: 'Jigawa', 15: 'Kaduna', 16: 'Kano', 17: 'Katsina', 18: 'Kebbi', 19: 'Sokoto', 20: 'Zamfara',
        21: 'Abia', 22: 'Rivers', 23: 'Bayelsa', 24: 'Delta', 25: 'Edo', 26: 'Anambra', 27: 'Enugu',
        28: 'Ebonyi', 29: 'Cross River', 30: 'Akwa Ibom', 31: 'Imo', 32: 'Oyo', 33: 'Ondo', 34: 'Osun',
        35: 'Ekiti', 36: 'Lagos', 37: 'Ogun'
    }
    
    # Conflict type mapping
    conflict_types = {
        1: 'Armed Conflict', 2: 'Banditry', 3: 'Terrorism', 4: 'Communal Violence',
        5: 'Cult Clash', 6: 'Farmers-Herders Clash', 7: 'Police Action', 8: 'Political Violence'
    }
    
    # Actor mapping
    actor_map = {
        1: 'Armed Robbers', 2: 'Bandits', 3: 'Boko Haram', 4: 'Civilians',
        5: 'Ethnic Groups', 6: 'Farmers', 7: 'Gunmen', 8: 'Herdsmen',
        9: 'Hoodlums'
    }
    
    statements = []
    state_counts = {}
    
    for i, line in enumerate(record_lines):
        try:
            parts = parse_record_line(line)
            
            # Extract fields
            record_id = parts[0]
            date = parts[1].strip("'")
            conflict_type_id = int(parts[2]) if parts[2] != 'NULL' else 1
            country_id = parts[3]
            region_id = parts[4]
            state_id = int(parts[5]) if parts[5] != 'NULL' else 1
            lga_id = parts[6]
            community = parts[7].strip("'").replace("'", "''")
            
            # Casualties
            civilian_death_male = int(parts[8]) if parts[8] != 'NULL' else 0
            civilian_death_female = int(parts[9]) if parts[9] != 'NULL' else 0
            civilian_death_unknown = int(parts[10]) if parts[10] != 'NULL' else 0
            security_death_male = int(parts[11]) if parts[11] != 'NULL' else 0
            security_death_female = int(parts[12]) if parts[12] != 'NULL' else 0
            security_death_unknown = int(parts[13]) if parts[13] != 'NULL' else 0
            
            injured_male = int(parts[14]) if parts[14] != 'NULL' else 0
            injured_female = int(parts[15]) if parts[15] != 'NULL' else 0
            injured_unknown = int(parts[16]) if parts[16] != 'NULL' else 0
            
            kidnapped_male = int(parts[17]) if parts[17] != 'NULL' else 0
            kidnapped_female = int(parts[18]) if parts[18] != 'NULL' else 0
            kidnapped_unknown = int(parts[19]) if parts[19] != 'NULL' else 0
            
            displaced_persons = int(parts[20]) if parts[20] != 'NULL' else 0
            displaced_male = int(parts[21]) if parts[21] != 'NULL' else 0
            displaced_female = int(parts[22]) if parts[22] != 'NULL' else 0
            
            actor_1 = int(parts[23]) if parts[23] != 'NULL' else None
            actor_2 = int(parts[24]) if parts[24] != 'NULL' else None
            actor_3 = int(parts[25]) if parts[25] != 'NULL' else None
            
            description = parts[26].strip("'").replace("'", "''") if parts[26] != 'NULL' else ''
            action = parts[27].strip("'").replace("'", "''") if parts[27] != 'NULL' else ''
            
            verification_level = parts[30].strip("'") if parts[30] != 'NULL' else 'Unknown'
            source_url = parts[31].strip("'").replace("'", "''") if parts[31] != 'NULL' else ''
            data_source = parts[34].strip("'") if parts[34] != 'NULL' else 'Unknown'
            
            # Calculate totals
            total_fatalities_male = civilian_death_male + security_death_male
            total_fatalities_female = civilian_death_female + security_death_female
            total_fatalities_unknown = civilian_death_unknown + security_death_unknown
            total_fatalities = total_fatalities_male + total_fatalities_female + total_fatalities_unknown
            
            # Get mapped values
            state_name = state_map.get(state_id, f'Unknown_{state_id}')
            event_type = conflict_types.get(conflict_type_id, 'Other')
            perpetrator = actor_map.get(actor_1, 'Unknown') if actor_1 else 'Unknown'
            
            # Count by state
            state_counts[state_name] = state_counts.get(state_name, 0) + 1
            
            # Create INSERT statement
            stmt = f"""INSERT INTO conflicts (
    event_date, event_type, archetype, state, community,
    fatalities_male, fatalities_female, fatalities_unknown,
    injured_male, injured_female, injured_unknown,
    kidnapped_male, kidnapped_female, kidnapped_unknown,
    displaced, perpetrator_group, description, source_url,
    source_type, confidence_score, created_at, updated_at
) VALUES (
    '{date}',
    '{event_type}',
    '{perpetrator}',
    '{state_name}',
    '{community}',
    {total_fatalities_male},
    {total_fatalities_female},
    {total_fatalities_unknown},
    {injured_male},
    {injured_female},
    {injured_unknown},
    {kidnapped_male},
    {kidnapped_female},
    {kidnapped_unknown},
    {displaced_persons},
    '{perpetrator}',
    '{description}',
    '{source_url}',
    '{data_source}',
    0.8,
    '{date} 00:00:00',
    '{date} 00:00:00'
);"""
            
            statements.append(stmt)
            
        except Exception as e:
            print(f"Error processing record {i+1}: {e}")
            print(f"Problem line: {line[:100]}...")
            continue
    
    return statements, state_counts

def main():
    """Main generation process"""
    
    print("=== Complete Conflict Data Import Generator ===")
    print("Extracting ALL conflict records from MySQL dump...")
    
    # Extract all records
    record_lines = extract_all_conflicts()
    
    if not record_lines:
        print("No conflict records found!")
        return
    
    print(f"Successfully extracted {len(record_lines)} conflict records")
    
    # Convert to PostgreSQL
    print("Converting to PostgreSQL format...")
    statements, state_counts = convert_to_postgresql_sql(record_lines)
    
    print(f"Generated {len(statements)} PostgreSQL INSERT statements")
    
    # Show state statistics
    print("\n=== Records by State (Top 15) ===")
    for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {state}: {count}")
    
    # Write complete import file
    output_file = '/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/backend/import_all_conflicts_complete.sql'
    
    with open(output_file, 'w') as f:
        f.write("-- Complete Import of All Conflict Data from MySQL Dump\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"-- Total records: {len(statements)}\n")
        f.write("-- Time period: 2020-2025\n")
        f.write("-- PostgreSQL compatible format\n\n")
        
        f.write("BEGIN;\n\n")
        f.write("-- Disable foreign key checks temporarily for faster import\n")
        f.write("SET session_replication_role = replica;\n\n")
        
        # Write all INSERT statements in batches
        batch_size = 100
        for i in range(0, len(statements), batch_size):
            f.write(f"-- Batch {i//batch_size + 1} (Records {i+1}-{min(i+batch_size, len(statements))})\n")
            for j in range(i, min(i + batch_size, len(statements))):
                f.write(statements[j] + "\n")
            f.write("\n")
        
        f.write("-- Re-enable foreign key checks\n")
        f.write("SET session_replication_role = DEFAULT;\n\n")
        
        f.write("COMMIT;\n\n")
        
        f.write("-- Import completed successfully!\n\n")
        
        f.write("-- Verification queries:\n")
        f.write("-- 1. Total records: SELECT COUNT(*) as total_records FROM conflicts;\n")
        f.write("-- 2. By state: SELECT state, COUNT(*) as incidents FROM conflicts GROUP BY state ORDER BY incidents DESC LIMIT 10;\n")
        f.write("-- 3. By month: SELECT DATE_TRUNC('month', event_date) as month, COUNT(*) as incidents FROM conflicts GROUP BY month ORDER BY month;\n")
        f.write("-- 4. Recent data: SELECT * FROM conflicts WHERE event_date >= '2025-01-01' ORDER BY event_date DESC LIMIT 10;\n")
        f.write("-- 5. High conflict states: SELECT state, COUNT(*) as incidents FROM conflicts WHERE event_date >= '2020-01-01' GROUP BY state HAVING COUNT(*) > 100 ORDER BY incidents DESC;\n")
    
    print(f"\nComplete import file generated: {output_file}")
    print(f"File size: ~{len(statements) * 500 / 1024 / 1024:.1f} MB")
    print("\nTo execute the import:")
    print(f"  psql -d your_database -f {output_file}")
    print("\nAfter import, verify with the verification queries in the file.")

if __name__ == "__main__":
    main()
