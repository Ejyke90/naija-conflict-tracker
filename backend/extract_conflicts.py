#!/usr/bin/env python3
"""
Extract conflict data from MySQL dump and convert to PostgreSQL format
"""

import re
import sys
from collections import defaultdict

def extract_conflict_data():
    """Extract conflict records from the MySQL dump"""
    
    # Read the SQL file
    with open('/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql', 'r') as f:
        content = f.read()
    
    # Find the conflicts section
    conflicts_start = content.find('-- Dumping data for table `conflicts`')
    if conflicts_start == -1:
        print("Conflicts table not found")
        return []
    
    conflicts_section = content[conflicts_start:]
    
    # Extract INSERT VALUES for conflicts
    # Pattern to match the conflict records
    pattern = r'\((\d+), \'(\d{4}-\d{2}-\d{2})\', (\d+), \d+, \d+, (\d+), \d+, \'([^\']+)\', (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+), \'([^\']+)\', \'([^\']+)\''
    
    matches = re.findall(pattern, conflicts_section)
    
    print(f"Found {len(matches)} conflict records")
    
    return matches

def convert_to_postgresql(matches):
    """Convert MySQL data to PostgreSQL INSERT statements"""
    
    # State mapping from MySQL ID to name
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
    
    statements = []
    
    for match in matches:
        (record_id, date, conflict_type_id, country_id, region_id, state_id, lga_id, community,
         civilian_death_male, civilian_death_female, civilian_death_unknown,
         security_death_male, security_death_female, security_death_unknown,
         injured_male, injured_female, injured_unknown,
         kidnapped_male, kidnapped_female, kidnapped_unknown,
         displaced_persons, displaced_male, displaced_female,
         actor_1, actor_2, actor_3, description, action) = match
        
        # Convert to proper types
        state_id = int(state_id)
        conflict_type_id = int(conflict_type_id)
        civilian_death_male = int(civilian_death_male) if civilian_death_male != 'NULL' else 0
        civilian_death_female = int(civilian_death_female) if civilian_death_female != 'NULL' else 0
        civilian_death_unknown = int(civilian_death_unknown) if civilian_death_unknown != 'NULL' else 0
        security_death_male = int(security_death_male) if security_death_male != 'NULL' else 0
        security_death_female = int(security_death_female) if security_death_female != 'NULL' else 0
        security_death_unknown = int(security_death_unknown) if security_death_unknown != 'NULL' else 0
        
        # Get state name
        state_name = state_map.get(state_id, f'Unknown_{state_id}')
        
        # Get conflict type
        event_type = conflict_types.get(conflict_type_id, 'Other')
        
        # Calculate total fatalities
        total_fatalities_male = civilian_death_male + security_death_male
        total_fatalities_female = civilian_death_female + security_death_female
        total_fatalities_unknown = civilian_death_unknown + security_death_unknown
        
        # Create INSERT statement
        stmt = f"""INSERT INTO conflicts (
    event_date,
    event_type,
    archetype,
    state,
    community,
    fatalities_male,
    fatalities_female,
    fatalities_unknown,
    injured_male,
    injured_female,
    injured_unknown,
    kidnapped_male,
    kidnapped_female,
    kidnapped_unknown,
    displaced,
    perpetrator_group,
    description,
    source_type,
    confidence_score,
    created_at,
    updated_at
) VALUES (
    '{date}',
    '{event_type}',
    'Unknown Perpetrator',
    '{state_name}',
    '{community.replace("'", "''")}',
    {total_fatalities_male},
    {total_fatalities_female},
    {total_fatalities_unknown},
    {injured_male if injured_male != 'NULL' else 0},
    {injured_female if injured_female != 'NULL' else 0},
    {injured_unknown if injured_unknown != 'NULL' else 0},
    {kidnapped_male if kidnapped_male != 'NULL' else 0},
    {kidnapped_female if kidnapped_female != 'NULL' else 0},
    {kidnapped_unknown if kidnapped_unknown != 'NULL' else 0},
    {displaced_persons if displaced_persons != 'NULL' else 0},
    'Unknown',
    '{description.replace("'", "''")}',
    'News Report',
    0.8,
    '{date} 00:00:00',
    '{date} 00:00:00'
);"""
        
        statements.append(stmt)
    
    return statements

def main():
    """Main extraction process"""
    
    print("Extracting conflict data from MySQL dump...")
    
    # Extract data
    matches = extract_conflict_data()
    
    if not matches:
        print("No conflict data found")
        return
    
    # Count by state
    state_counts = defaultdict(int)
    for match in matches:
        state_id = int(match[4])
        state_map = {
            1: 'Adamawa', 2: 'Bauchi', 3: 'Borno', 4: 'Gombe', 5: 'Taraba', 6: 'Yobe',
            7: 'Benue', 8: 'Kogi', 9: 'Kwara', 10: 'Nasarawa', 11: 'Niger', 12: 'Plateau', 13: 'FCT',
            14: 'Jigawa', 15: 'Kaduna', 16: 'Kano', 17: 'Katsina', 18: 'Kebbi', 19: 'Sokoto', 20: 'Zamfara',
            21: 'Abia', 22: 'Rivers', 23: 'Bayelsa', 24: 'Delta', 25: 'Edo', 26: 'Anambra', 27: 'Enugu',
            28: 'Ebonyi', 29: 'Cross River', 30: 'Akwa Ibom', 31: 'Imo', 32: 'Oyo', 33: 'Ondo', 34: 'Osun',
            35: 'Ekiti', 36: 'Lagos', 37: 'Ogun'
        }
        state_name = state_map.get(state_id, f'Unknown_{state_id}')
        state_counts[state_name] += 1
    
    print("Records by state (top 10):")
    for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {state}: {count}")
    
    # Convert to PostgreSQL
    print("Converting to PostgreSQL format...")
    statements = convert_to_postgresql(matches)
    
    # Write to file
    output_file = '/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/backend/import_all_conflicts.sql'
    
    with open(output_file, 'w') as f:
        f.write("-- Import All Conflict Data from MySQL Dump\n")
        f.write("-- PostgreSQL compatible format\n")
        f.write("-- Total records: " + str(len(statements)) + "\n\n")
        
        f.write("BEGIN;\n\n")
        f.write("-- Disable foreign key checks temporarily\n")
        f.write("SET session_replication_role = replica;\n\n")
        
        # Write all INSERT statements
        for i, stmt in enumerate(statements):
            f.write(f"-- Record {i+1}\n")
            f.write(stmt + "\n\n")
        
        f.write("-- Re-enable foreign key checks\n")
        f.write("SET session_replication_role = DEFAULT;\n\n")
        
        f.write("COMMIT;\n\n")
        
        f.write("-- Verification queries:\n")
        f.write("-- SELECT state, COUNT(*) as incidents FROM conflicts GROUP BY state ORDER BY incidents DESC LIMIT 10;\n")
        f.write("-- SELECT DATE_TRUNC('month', event_date) as month, COUNT(*) as incidents FROM conflicts GROUP BY month ORDER BY month;\n")
        f.write("-- SELECT COUNT(*) as total_records FROM conflicts;\n")
    
    print(f"Generated {len(statements)} INSERT statements")
    print(f"Output written to: {output_file}")

if __name__ == "__main__":
    main()
