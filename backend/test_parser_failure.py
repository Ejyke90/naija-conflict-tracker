#!/usr/bin/env python3
"""
Simple test to demonstrate current parser failure
"""

import re

def test_current_parser():
    """Test the current parser approach"""
    sql_file = '/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql'
    
    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Current parser approach - only finds first INSERT
    conflicts_insert_match = re.search(
        r'INSERT INTO `conflicts`.*?VALUES\s*(.+?);', 
        content, 
        re.DOTALL | re.IGNORECASE
    )
    
    if conflicts_insert_match:
        values_str = conflicts_insert_match.group(1)
        print(f"Current parser approach:")
        print(f"- Found 1 INSERT statement")
        print(f"- Values string length: {len(values_str)} characters")
        
        # Count records in first INSERT only
        record_count = values_str.count('(') - values_str.count('),(') - 1  # Rough estimate
        print(f"- Estimated records in first INSERT: ~{record_count}")
    else:
        print("No INSERT statement found (this would be a different issue)")
    
    # Show what we're missing
    all_inserts = re.findall(r'INSERT INTO `conflicts`.*?VALUES\s*(.+?);', content, re.DOTALL | re.IGNORECASE)
    print(f"\nActual file contains:")
    print(f"- Total INSERT statements: {len(all_inserts)}")
    
    # Count total records across all INSERTs
    total_records = 0
    for i, values in enumerate(all_inserts):
        # Rough count of records in this INSERT
        record_count = values.count('(') - values.count('),(') - 1
        if record_count < 0:
            record_count = values.count('),(') + 1  # Alternative counting
        total_records += record_count
        print(f"- INSERT {i+1}: ~{record_count} records")
    
    print(f"- Total estimated records: ~{total_records}")
    
    # Look for kidnapping data specifically
    kidnapping_matches = content.count('kidnapped_')
    print(f"- Total kidnapping field mentions: {kidnapping_matches}")

if __name__ == "__main__":
    test_current_parser()
