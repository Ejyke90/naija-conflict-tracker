#!/usr/bin/env python3
"""
Table mapping between SQL file and database
"""

# SQL file tables -> Database tables
TABLE_MAPPING = {
    # Exact matches (no mapping needed)
    'actors': 'actors',
    'cache': 'cache', 
    'cache_locks': 'cache_locks',
    'conflicts': 'conflicts',
    'conflict_types': 'conflict_types',
    'countries': 'countries',  # This doesn't exist in DB yet
    'failed_jobs': 'failed_jobs',
    'jobs': 'jobs',
    'job_batches': 'job_batches',
    'lgas': 'lgas',
    'migrations': 'migrations',
    'password_reset_tokens': 'password_reset_tokens',
    'personal_access_tokens': 'personal_access_tokens',
    'regions': 'regions',
    'sessions': 'sessions',
    'states': 'states',
    'users': 'users'
}

# Tables that exist in database but might need special handling
DB_TABLES = [
    'actors', 'alembic_version', 'alert_events', 'alert_read_status', 'audit_log',
    'cache', 'cache_locks', 'conflict_events', 'conflict_events_archive_20260208',
    'conflict_types', 'conflicts', 'conflicts_with_totals', 'failed_jobs',
    'geography_columns', 'geometry_columns', 'job_batches', 'jobs', 'lgas',
    'migrations', 'password_reset_tokens', 'personal_access_tokens', 'regions',
    'sessions', 'spatial_ref_sys', 'states', 'users'
]

def get_table_mapping():
    """Get the mapping between SQL file and database tables"""
    
    print("TABLE MAPPING ANALYSIS")
    print("=" * 30)
    
    print("SQL File -> Database Table Mapping:")
    for sql_table, db_table in TABLE_MAPPING.items():
        print(f"   {sql_table:20} -> {db_table}")
    
    print()
    print("Tables that exist in database:")
    for table in sorted(DB_TABLES):
        print(f"   • {table}")
    
    return TABLE_MAPPING

def confirm_table_mappings():
    """Ask user to confirm table mappings"""
    
    print("\n🤔 TABLE MAPPING CONFIRMATION")
    print("=" * 40)
    
    print("I found the following mappings between SQL file and database:")
    print()
    
    # Show mappings with current data status
    import psycopg2
    
    conn = psycopg2.connect('postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
    cursor = conn.cursor()
    
    for sql_table, db_table in TABLE_MAPPING.items():
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {db_table}")
            count = cursor.fetchone()[0]
            status = "✅" if count > 0 else "❌"
            print(f"   {status} {sql_table:20} -> {db_table:20} ({count:6,} records)")
        except Exception as e:
            print(f"   ❌ {sql_table:20} -> {db_table:20} (ERROR: {e})")
    
    conn.close()
    
    print()
    print("📝 SPECIAL NOTES:")
    print("• 'countries' table doesn't exist in database - should we create it?")
    print("• 'conflict_events' exists with 6,993 records - is this duplicate data?")
    print("• Most tables have some data already")
    print()
    
    response = input("Do these mappings look correct? (y/n): ").lower().strip()
    
    if response == 'y':
        return True
    else:
        print("Please modify the table mapping in table_mapping.py")
        return False

if __name__ == "__main__":
    get_table_mapping()
    confirm_table_mappings()
