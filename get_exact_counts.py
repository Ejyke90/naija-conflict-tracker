#!/usr/bin/env python3
"""
Get exact record counts for all tables in SQL file
"""

import re

def get_exact_counts():
    """Get exact record counts for all tables"""
    
    with open('u503102722_conflictdb (1).sql', 'r') as f:
        content = f.read()

    # Tables with INSERT statements
    insert_tables = ['users', 'migrations', 'states', 'regions', 'conflicts', 'sessions', 'actors', 'conflict_types', 'countries', 'personal_access_tokens', 'cache', 'lgas']

    print('EXACT RECORD COUNTS:')
    print('=' * 30)

    for table in insert_tables:
        # Find all INSERT statements for this table
        insert_pattern = f'INSERT INTO `{table}`.*?VALUES.*?;'
        matches = re.findall(insert_pattern, content, re.DOTALL | re.MULTILINE)
        
        total_records = 0
        for match in matches:
            # Count records in this INSERT (look for complete value tuples ending with ), or );
            record_pattern = r'\([^)]+\)(?:,|;)'
            records = re.findall(record_pattern, match)
            total_records += len(records)
        
        print(f'{table:20}: {total_records:6,} records')

if __name__ == "__main__":
    get_exact_counts()
