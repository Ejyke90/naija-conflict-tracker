#!/usr/bin/env python3
"""
Check actual database table names and structure
"""

import psycopg2

def get_database_tables():
    """Get all tables in the database"""
    
    conn = psycopg2.connect('postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
    cursor = conn.cursor()

    print('ACTUAL TABLES IN DATABASE:')
    print('=' * 30)

    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f'{table_name:20}: {count:6,} records')
        except Exception as e:
            print(f'{table_name:20}: ERROR - {e}')

    conn.close()
    return [table[0] for table in tables]

def get_table_structure(table_name):
    """Get column information for a specific table"""
    
    conn = psycopg2.connect('postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
    cursor = conn.cursor()

    print(f'\nSTRUCTURE OF TABLE: {table_name}')
    print('=' * 40)

    cursor.execute(f"""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    
    for col in columns:
        print(f'{col[0]:20}: {col[1]:15} | {"NULL" if col[2] == "YES" else "NOT NULL":8} | {col[3] or "No default"}')

    conn.close()

if __name__ == "__main__":
    tables = get_database_tables()
    
    # Show structure for key tables
    key_tables = ['conflicts', 'states', 'lgas', 'users']
    for table in key_tables:
        if table in tables:
            get_table_structure(table)
