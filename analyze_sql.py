#!/usr/bin/env python3
"""
Analyze SQL file structure to understand all tables and data
"""

import re

def analyze_sql_file():
    """Analyze the SQL file structure"""
    
    print("ANALYZING SQL FILE STRUCTURE")
    print("=" * 50)
    
    # Read the SQL file
    with open('u503102722_conflictdb (1).sql', 'r') as f:
        content = f.read()
    
    # Find all CREATE TABLE statements
    create_table_pattern = r'CREATE TABLE `([^`]+)`'
    tables = re.findall(create_table_pattern, content)
    
    print('Tables found in SQL file:')
    for i, table in enumerate(tables, 1):
        print(f'   {i}. {table}')
    
    print(f'\nTotal tables: {len(tables)}')
    
    # Find all INSERT INTO statements
    insert_pattern = r'INSERT INTO `([^`]+)`'
    insert_tables = list(set(re.findall(insert_pattern, content)))
    
    print(f'\nTables with INSERT statements:')
    for i, table in enumerate(insert_tables, 1):
        print(f'   {i}. {table}')
    
    print(f'\nTotal tables with data: {len(insert_tables)}')
    
    # Get sample data for each table
    print(f'\nSample INSERT statements by table:')
    for table in insert_tables:
        # Find first INSERT statement for this table
        table_insert_pattern = f'INSERT INTO `{table}`.*?VALUES.*?;'
        match = re.search(table_insert_pattern, content, re.DOTALL | re.MULTILINE)
        if match:
            insert_stmt = match.group(0)
            # Count records in this INSERT
            record_pattern = r'\([^)]+\),'
            records = re.findall(record_pattern, insert_stmt)
            print(f'   {table}: {len(records)} records')
    
    return tables, insert_tables

if __name__ == "__main__":
    analyze_sql_file()
