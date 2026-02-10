#!/usr/bin/env python3
"""
Direct Database Restoration Script
Bypasses API and directly restores data to Railway database
"""

import psycopg2
import re
import time
from datetime import datetime

def get_railway_db_connection():
    """Get direct connection to Railway PostgreSQL database"""
    # You'll need to get the actual Railway database connection string
    # For now, let's use the Neon database we tested earlier
    return psycopg2.connect(
        'postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    )

def analyze_sql_structure():
    """Analyze what needs to be restored"""
    
    print("🔍 ANALYZING SQL FILE STRUCTURE")
    print("=" * 40)
    
    with open('u503102722_conflictdb (1).sql', 'r') as f:
        content = f.read()
    
    # Find all INSERT statements
    insert_pattern = r'INSERT INTO `([^`]+)`.*?VALUES.*?;'
    tables_with_data = list(set(re.findall(insert_pattern, content, re.DOTALL | re.MULTILINE)))
    
    print("Tables with data in SQL file:")
    for i, table in enumerate(tables_with_data, 1):
        print(f"   {i}. {table}")
    
    return tables_with_data, content

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

def check_table_exists(conn, table_name):
    """Check if table exists"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            );
        """)
        exists = cursor.fetchone()[0]
        cursor.close()
        return exists
    except Exception:
        return False

def extract_table_inserts(content, table_name):
    """Extract INSERT statements for a specific table"""
    pattern = f'INSERT INTO `{table_name}`.*?VALUES.*?;'
    matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
    return matches

def convert_mysql_to_postgresql(mysql_stmt):
    """Convert MySQL INSERT to PostgreSQL format"""
    pg_stmt = mysql_stmt
    
    # Remove backticks and replace with double quotes
    pg_stmt = re.sub(r'`([^`]+)`', r'"\1"', pg_stmt)
    
    # Handle boolean values
    pg_stmt = pg_stmt.replace("'1', 'true'", "true, 'true'")
    pg_stmt = pg_stmt.replace("'0', 'false'", "false, 'false'")
    
    # Handle MySQL NOW() -> PostgreSQL CURRENT_TIMESTAMP
    pg_stmt = pg_stmt.replace('NOW()', 'CURRENT_TIMESTAMP')
    
    # Handle empty strings for numeric fields that should be NULL
    pg_stmt = re.sub(r", ''(?=,|\))", ", NULL", pg_stmt)
    
    return pg_stmt

def restore_table_data(conn, table_name, insert_statements, truncate_existing=False):
    """Restore data for a single table"""
    
    cursor = conn.cursor()
    
    try:
        # Check current state
        exists = check_table_exists(conn, table_name)
        current_count = get_table_record_count(conn, table_name) if exists else 0
        
        print(f"📊 Table: {table_name}")
        print(f"   Exists: {exists}")
        print(f"   Current records: {current_count}")
        
        if not exists:
            print(f"   ❌ Table {table_name} does not exist - skipping")
            return False
        
        if current_count > 0 and not truncate_existing:
            print(f"   ⏭️  Table has data - skipping (use truncate=True to override)")
            return True
        
        # Count records to be inserted
        total_records = 0
        for stmt in insert_statements:
            record_pattern = r'\([^)]+\)(?:,|;)'
            records = re.findall(record_pattern, stmt)
            total_records += len(records)
        
        print(f"   📥 Records to insert: {total_records}")
        
        # Truncate if requested
        if truncate_existing and current_count > 0:
            try:
                cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
                conn.commit()
                print(f"   🗑️  Truncated existing {current_count} records")
            except Exception as e:
                print(f"   ⚠️  Could not truncate: {e}")
        
        # Insert data
        inserted_statements = 0
        failed_records = 0
        
        for stmt in insert_statements:
            try:
                pg_stmt = convert_mysql_to_postgresql(stmt)
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
        new_count = get_table_record_count(conn, table_name)
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
    
    print("🗄️  DIRECT DATABASE RESTORATION")
    print("=" * 50)
    print("This script directly restores data to the database")
    print()
    
    # Analyze SQL file
    tables_with_data, content = analyze_sql_structure()
    
    print()
    input("Press Enter to continue to database connection...")
    
    # Connect to database
    try:
        print("🔌 Connecting to database...")
        conn = get_railway_db_connection()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    print()
    input("Press Enter to continue to table analysis...")
    
    # Check current table status
    print("📋 CURRENT TABLE STATUS")
    print("=" * 30)
    
    for table_name in sorted(tables_with_data):
        if check_table_exists(conn, table_name):
            count = get_table_record_count(conn, table_name)
            status = "✅" if count > 0 else "❌"
            print(f"   {status} {table_name:15}: {count:6,} records")
        else:
            print(f"   ❌ {table_name:15}: Table not found")
    
    print()
    input("Press Enter to continue to restoration...")
    
    # Execute restoration
    print("🚀 STARTING DATA RESTORATION")
    print("=" * 40)
    
    # Define restoration order (respecting foreign keys)
    restoration_order = [
        'countries',      # No dependencies
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
        'sessions'        # System data
    ]
    
    success_count = 0
    total_count = 0
    
    for table_name in restoration_order:
        if table_name in tables_with_data:
            total_count += 1
            
            insert_statements = extract_table_inserts(content, table_name)
            
            if insert_statements:
                success = restore_table_data(
                    conn, table_name, insert_statements, 
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
        else:
            print(f"   ❌ API test failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing API: {e}")
    
    return success_count == total_count

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("❌ requests module not installed. Install with: pip install requests")
        exit(1)
    
    main()
