#!/usr/bin/env python3
"""
Simple Conflict Data Extractor
Extract only conflict records from the MySQL dump
"""

import re

def main():
    """Extract conflict records more carefully"""
    
    # Read the SQL file
    with open('/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql', 'r') as f:
        content = f.read()
    
    # Find the conflicts section
    conflicts_start = content.find('-- Dumping data for table `conflicts`')
    if conflicts_start == -1:
        print("Conflicts table not found")
        return
    
    # Find the next table after conflicts to know where conflicts end
    conflicts_section = content[conflicts_start:]
    next_table_start = conflicts_section.find('-- Dumping data for table', 1)  # Find next table
    
    if next_table_start != -1:
        conflicts_section = conflicts_section[:next_table_start]
    
    # Extract VALUES section
    values_match = re.search(r'VALUES\s*(.*?);', conflicts_section, re.DOTALL)
    if not values_match:
        print("VALUES section not found")
        return
    
    values_content = values_match.group(1)
    
    # Split into individual records (handling multi-line records)
    records = []
    current_record = ''
    paren_count = 0
    
    for char in values_content:
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
        
        current_record += char
        
        if paren_count == 0 and current_record.strip():
            records.append(current_record.strip())
            current_record = ''
    
    # Filter out non-conflict records (look for date pattern in second field)
    conflict_records = []
    date_pattern = r'\(\d+, \'(\d{4}-\d{2}-\d{2})\', \d+, \d+, \d+, \d+,'
    
    for record in records:
        if re.match(date_pattern, record):
            conflict_records.append(record)
    
    print(f"Found {len(conflict_records)} conflict records")
    
    # Count by state (simple extraction)
    state_counts = {}
    for record in conflict_records[:100]:  # Sample first 100 for speed
        # Extract state_id (6th field)
        parts = record.split(',')
        if len(parts) > 5:
            try:
                state_id = int(parts[5].strip())
                state_map = {
                    1: 'Adamawa', 2: 'Bauchi', 3: 'Borno', 4: 'Gombe', 5: 'Taraba', 6: 'Yobe',
                    7: 'Benue', 8: 'Kogi', 9: 'Kwara', 10: 'Nasarawa', 11: 'Niger', 12: 'Plateau', 13: 'FCT',
                    14: 'Jigawa', 15: 'Kaduna', 16: 'Kano', 17: 'Katsina', 18: 'Kebbi', 19: 'Sokoto', 20: 'Zamfara',
                    21: 'Abia', 22: 'Rivers', 23: 'Bayelsa', 24: 'Delta', 25: 'Edo', 26: 'Anambra', 27: 'Enugu',
                    28: 'Ebonyi', 29: 'Cross River', 30: 'Akwa Ibom', 31: 'Imo', 32: 'Oyo', 33: 'Ondo', 34: 'Osun',
                    35: 'Ekiti', 36: 'Lagos', 37: 'Ogun'
                }
                state_name = state_map.get(state_id, f'Unknown_{state_id}')
                state_counts[state_name] = state_counts.get(state_name, 0) + 1
            except:
                pass
    
    print("Sample state counts (first 100 records):")
    for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {state}: {count}")
    
    # Write raw records to file for manual processing
    output_file = '/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/backend/raw_conflict_records.txt'
    with open(output_file, 'w') as f:
        f.write(f"# Conflict Records Extracted from MySQL Dump\n")
        f.write(f"# Total records: {len(conflict_records)}\n")
        f.write(f"# Format: (id, date, type_id, country_id, region_id, state_id, lga_id, community, ...)\n\n")
        
        for i, record in enumerate(conflict_records):
            f.write(f"# Record {i+1}\n")
            f.write(record + "\n\n")
    
    print(f"\nRaw records written to: {output_file}")
    print("You can now process these records manually or with a simpler parser.")

if __name__ == "__main__":
    main()
