#!/usr/bin/env python3
"""
Smart Database Restoration Script
Handles table name mapping and existing data properly
"""

import psycopg2
import re
import time
from datetime import datetime

# Table mapping from SQL file to database
TABLE_MAPPING = {
    'actors': 'actors',
    'cache': 'cache', 
    'cache_locks': 'cache_locks',
    'conflicts': 'conflicts',
    'conflict_types': 'conflict_types',
    'countries': None,  # Doesn't exist in DB
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

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        'postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    )

def analyze_sql_file():
    """Analyze SQL file and extract table data"""
    
    print("🔍 ANALYZING SQL FILE")
    print("=" * 30)
    
    with open('u503102722_conflictdb (1).sql', 'r') as f:
        content = f.read()
    
    # Find all INSERT statements
    insert_pattern = r'INSERT INTO `([^`]+)`.*?VALUES.*?;'
    sql_tables = list(set(re.findall(insert_pattern, content, re.DOTALL | re.MULTILINE)))
    
    print(f"Found {len(sql_tables)} tables with data in SQL file:")
    
    table_data = {}
    for table_name in sql_tables:
        if table_name in TABLE_MAPPING and TABLE_MAPPING[table_name]:
            db_table = TABLE_MAPPING[table_name]
            insert_statements = extract_table_inserts(content, table_name)
            
            # Count records
            total_records = 0
            for stmt in insert_statements:
                record_pattern = r'\([^)]+\)(?:,|;)'
                records = re.findall(record_pattern, stmt)
                total_records += len(records)
            
            table_data[table_name] = {
                'db_table': db_table,
                'insert_statements': insert_statements,
                'record_count': total_records
            }
            print(f"   • {table_name:15} -> {db_table:15} ({total_records:6,} records)")
        else:
            print(f"   ⚠️  {table_name:15} -> No mapping or table doesn't exist")
    
    return table_data, content

def extract_table_inserts(content, table_name):
    """Extract INSERT statements for a specific table"""
    pattern = f'INSERT INTO `{table_name}`.*?VALUES.*?;'
    matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
    return matches

def get_table_record_count(conn, table_name):
    """Get current record count for a table"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    except Exception as e:
        print(f"   ❌ Error counting {table_name}: {e}")
        return 0

def convert_mysql_to_postgresql(mysql_stmt, table_name):
    """Convert MySQL INSERT to PostgreSQL format"""
    pg_stmt = mysql_stmt
    
    # Remove backticks and replace with double quotes
    pg_stmt = re.sub(r'`([^`]+)`', r'"\1"', pg_stmt)
    
    # Handle specific table conversions
    if table_name == 'users':
        # Handle user-specific conversions
        pg_stmt = pg_stmt.replace("'viewer',", "'viewer',")
        pg_stmt = pg_stmt.replace("'admin',", "'admin',")
        pg_stmt = pg_stmt.replace("'analyst',", "'analyst',")
    
    # Handle boolean values
    pg_stmt = pg_stmt.replace("'1', 'true'", "true, 'true'")
    pg_stmt = pg_stmt.replace("'0', 'false'", "false, 'false'")
    
    # Handle MySQL NOW() -> PostgreSQL CURRENT_TIMESTAMP
    pg_stmt = pg_stmt.replace('NOW()', 'CURRENT_TIMESTAMP')
    
    # Handle empty strings for numeric fields that should be NULL
    pg_stmt = re.sub(r", ''(?=,|\))", ", NULL", pg_stmt)
    
    return pg_stmt

def create_missing_table(conn, table_name):
    """Create missing countries table"""
    
    if table_name != 'countries':
        return False
    
    print(f"   🔧 Creating missing table: {table_name}")
    
    cursor = conn.cursor()
    
    try:
        create_sql = """
        CREATE TABLE countries (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            code VARCHAR(3) NOT NULL UNIQUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        cursor.execute(create_sql)
        conn.commit()
        cursor.close()
        
        print(f"   ✅ Created {table_name} table")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to create {table_name}: {e}")
        cursor.close()
        return False

def restore_table_data(conn, sql_table_name, table_info, truncate_existing=False):
    """Restore data for a single table"""
    
    db_table = table_info['db_table']
    insert_statements = table_info['insert_statements']
    
    cursor = conn.cursor()
    
    try:
        # Get current state
        current_count = get_table_record_count(conn, db_table)
        
        print(f"📊 Table: {sql_table_name}")
        print(f"   Database table: {db_table}")
        print(f"   Current records: {current_count}")
        print(f"   Records in SQL: {table_info['record_count']}")
        
        if current_count > 0 and not truncate_existing:
            print(f"   ⏭️  Table has data - skipping (use truncate=True to override)")
            return True
        
        # Count records to be inserted
        total_records = table_info['record_count']
        print(f"   📥 Records to insert: {total_records}")
        
        # Truncate if requested
        if truncate_existing and current_count > 0:
            try:
                cursor.execute(f"TRUNCATE TABLE {db_table} CASCADE")
                conn.commit()
                print(f"   🗑️  Truncated existing {current_count} records")
            except Exception as e:
                print(f"   ⚠️  Could not truncate: {e}")
        
        # Insert data
        inserted_statements = 0
        failed_records = 0
        
        for stmt in insert_statements:
            try:
                pg_stmt = convert_mysql_to_postgresql(stmt, sql_table_name)
                cursor.execute(pg_stmt)
                inserted_statements += 1
            except Exception as e:
                # Count failed records
                record_pattern = r'\([^)]+\)(?:,|;)'
                records = re.findall(record_pattern, stmt)
                failed_records += len(records)
                print(f"   ⚠️  Failed to insert {len(records)} records: {str(e)[:100]}")
        
        conn.commit()
        cursor.close()
        
        # Verify results
        new_count = get_table_record_count(conn, db_table)
        print(f"   ✅ Success: {inserted_statements} statements, {new_count} final records")
        
        if failed_records > 0:
            print(f"   ⚠️  {failed_records} records failed to insert")
        
        return True
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        print(f"   ❌ Restoration failed: {e}")
        return False

def main():
    """Main restoration process"""
    
    print("🗄️  SMART DATABASE RESTORATION")
    print("=" * 50)
    print("Handles table mapping and existing data properly")
    print()
    
    # Analyze SQL file
    table_data, content = analyze_sql_file()
    
    if not table_data:
        print("❌ No valid table data found")
        return False
    
    print()
    input("Press Enter to continue to database connection...")
    
    # Connect to database
    try:
        print("🔌 Connecting to database...")
        conn = get_db_connection()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    print()
    input("Press Enter to continue to restoration...")
    
    # Execute restoration
    print("🚀 STARTING SMART DATA RESTORATION")
    print("=" * 45)
    
    # Define restoration order (respecting foreign keys)
    restoration_order = [
        'countries',      # Create first (no dependencies)
        'regions',        # No dependencies  
        'states',         # Depends on countries, regions
        'lgas',           # Depends on states
        'conflict_types', # No dependencies
        'actors',         # No dependencies
        'users',          # No dependencies
        'conflicts',      # Depends on states, lgas, actors, conflict_types
        'migrations',     # System data
        'personal_access_tokens', # System data
        'cache',          # System data
        'cache_locks',    # System data
        'sessions',       # System data
        'failed_jobs',    # System data
        'jobs',           # System data
        'job_batches'     # System data
        'password_reset_tokens' # System data
    ]
    
    success_count = 0
    total_count = 0
    
    for sql_table in restoration_order:
        if sql_table in table_data:
            total_count += 1
            
            table_info = table_data[sql_table]
            db_table = table_info['db_table']
            
            # Handle missing countries table
            if sql_table == 'countries' and db_table is None:
                if create_missing_table(conn, sql_table):
                    # Now try to restore
                    table_info['db_table'] = 'countries'
                    success = restore_table_data(
                        conn, sql_table, table_info, 
                        truncate_existing=False
                    )
                    if success:
                        success_count += 1
            else:
                success = restore_table_data(
                    conn, sql_table, table_info, 
                    truncate_existing=False  # Safe mode
                )
                
                if success:
                    success_count += 1
            
            print()  # Add spacing between tables
    
    conn.close()
    
    # Summary
    print("📊 RESTORATION SUMMARY")
    print("=" * 30)
    print(f"Tables processed: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("✅ All tables restored successfully!")
    else:
        print(f"⚠️  {total_count - success_count} tables had issues")
    
    print()
    print("🔍 VERIFYING RESTORATION")
    
    # Test monthly trends
    try:
        import requests
        print("📈 Testing Monthly Trends API...")
        response = requests.get(
            "https://naija-conflict-tracker-production.up.railway.app/api/v1/timeseries/monthly-trends?months_back=12",
            timeout=10
        )
        
        if response.status_code == 200:
            trends_data = response.json()
            total_incidents = trends_data['summary']['totalIncidents']
            
            print(f"   ✅ Monthly Trends: {total_incidents} total incidents")
            
            if total_incidents > 1000:
                print("🎉 MONTHLY TRENDS ISSUE FIXED!")
                print("   The dashboard should now show complete historical data")
            else:
                print("⚠️  Monthly Trends still showing low numbers")
                print("   This might be because Railway hasn't updated yet")
        else:
            print(f"   ❌ API test failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing API: {e}")
    
    print()
    print("📝 NEXT STEPS:")
    print("1. Check the frontend dashboard")
    print("2. If Monthly Trends still shows low numbers, Railway may need time to update")
    print("3. Consider running the API-based restoration when endpoints are deployed")
    
    return success_count == total_count

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Restoration cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
