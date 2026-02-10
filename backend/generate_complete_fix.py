#!/usr/bin/env python3
"""
Generate the complete SQL fix script for all date mappings.
"""

import os
import re

def extract_original_dates(sql_file_path):
    """Extract ID-date pairs from original MariaDB SQL dump."""
    print(f"Extracting dates from {sql_file_path}")
    
    id_date_map = {}
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find INSERT statements for conflicts table
    insert_pattern = r'\((\d+),\s*\'(\d{4}-\d{2}-\d{2})\''
    matches = re.findall(insert_pattern, content)
    
    for match in matches:
        old_id = int(match[0])
        date = match[1]
        id_date_map[old_id] = date
    
    print(f"Extracted {len(id_date_map)} ID-date pairs from original data")
    return id_date_map

def generate_complete_fix_script(original_map, offset=19885):
    """Generate complete SQL fix script."""
    script_lines = [
        "-- Fix incidence_date with REAL data from original MariaDB dump",
        "-- This script maps original IDs to current PostgreSQL IDs using offset",
        f"-- Offset pattern: original_id + {offset} = current_id",
        "-- Generated automatically by generate_complete_fix.py",
        "",
        "BEGIN;",
        ""
    ]
    
    updates_count = 0
    
    # Group by date to reduce script size
    date_groups = {}
    for old_id, date in original_map.items():
        if date not in date_groups:
            date_groups[date] = []
        date_groups[date].append(old_id)
    
    for date, old_ids in sorted(date_groups.items()):
        # Create UPDATE statements for each date group
        id_list = []
        for old_id in old_ids:
            new_id = old_id + offset
            id_list.append(str(new_id))
        
        # Split into batches of 100 to avoid SQL statement length limits
        for i in range(0, len(id_list), 100):
            batch_ids = id_list[i:i+100]
            ids_str = ", ".join(batch_ids)
            script_lines.append(f"UPDATE conflicts SET incidence_date = '{date}' WHERE id IN ({ids_str}) AND incidence_date = created_at::date;")
            updates_count += len(batch_ids)
    
    script_lines.extend([
        "",
        f"-- Total updates: {updates_count}",
        "COMMIT;",
        "",
        "-- Verify the fix",
        "SELECT incidence_date, COUNT(*) FROM conflicts GROUP BY incidence_date ORDER BY COUNT(*) DESC LIMIT 10;",
        "",
        "-- Check date range after fix",
        "SELECT MIN(incidence_date), MAX(incidence_date), COUNT(*) FROM conflicts WHERE incidence_date != created_at::date;"
    ])
    
    script_content = "\n".join(script_lines)
    
    # Write script to file
    with open('backend/fix_dates_complete.sql', 'w') as f:
        f.write(script_content)
    
    print(f"Generated complete fix script with {updates_count} updates")
    print("Script saved to: backend/fix_dates_complete.sql")
    
    return updates_count

def main():
    """Main execution function."""
    print("Generating complete date fix script...")
    
    # Extract original dates
    sql_file = "u503102722_conflictdb (1).sql"
    if not os.path.exists(sql_file):
        print(f"Original SQL file not found: {sql_file}")
        return
    
    original_map = extract_original_dates(sql_file)
    
    # Generate complete fix script
    updates_count = generate_complete_fix_script(original_map)
    
    print(f"Successfully generated complete fix script with {updates_count} date corrections")
    print("Execute with: psql $DATABASE_URL < backend/fix_dates_complete.sql")

if __name__ == "__main__":
    main()
