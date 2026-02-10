#!/usr/bin/env python3
"""
Simple and Effective Data Restoration
Drops and recreates tables, then imports all data from SQL file
"""

import psycopg2
import re
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        'postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    )

def create_countries_table(conn):
    """Create the missing countries table"""
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE countries (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                code VARCHAR(3) NOT NULL UNIQUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        conn.commit()
        cursor.close()
        print("✅ Created countries table")
        return True
    except Exception as e:
        print(f"❌ Failed to create countries table: {e}")
        return False

def check_conflict_events_duplicate(conn):
    """Check if conflict_events is duplicate data"""
    
    cursor = conn.cursor()
    
    try:
        # Get sample from conflict_events
        cursor.execute("SELECT * FROM conflict_events LIMIT 5")
        ce_sample = cursor.fetchall()
        
        # Get sample from conflicts
        cursor.execute("SELECT id, incidence_date, description FROM conflicts LIMIT 5")
        conflicts_sample = cursor.fetchall()
        
        cursor.close()
        
        print("🔍 DUPLICATE DATA ANALYSIS")
        print("=" * 30)
        print("conflict_events sample:")
        for row in ce_sample:
            print(f"   ID: {row[0]}, Date: {row[1]}, Desc: {row[2][:50]}...")
        
        print()
        print("conflicts sample:")
        for row in conflicts_sample:
            print(f"   ID: {row[0]}, Date: {row[1]}, Desc: {row[2][:50]}...")
        
        # Check if they're the same data
        if ce_sample and conflicts_sample:
            ce_dates = [row[1] for row in ce_sample]
            conflicts_dates = [row[1] for row in conflicts_sample]
            
            overlap = len(set(ce_dates) & set(conflicts_dates))
            print()
            print(f"Date overlap: {overlap} out of 5 records")
            
            if overlap >= 3:
                print("⚠️  conflict_events appears to be duplicate data")
                return True
            else:
                print("✅ conflict_events appears to be different data")
                return False
        else:
            print("⚠️  Could not compare - one table is empty")
            return False
            
    except Exception as e:
        print(f"❌ Error checking duplicates: {e}")
        return False

def drop_and_recreate_table(conn, table_name):
    """Drop and recreate a table"""
    
    cursor = conn.cursor()
    
    try:
        print(f"🗑️  Dropping table: {table_name}")
        cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        
        # Get table structure from SQL file
        with open('u503102722_conflictdb (1).sql', 'r') as f:
            content = f.read()
        
        # Find CREATE TABLE statement
        create_pattern = f'CREATE TABLE `{table_name}`.*?;'
        create_match = re.search(create_pattern, content, re.DOTALL | re.MULTILINE)
        
        if create_match:
            create_sql = create_match.group(0)
            # Convert MySQL to PostgreSQL
            pg_sql = create_sql.replace('`', '"').replace('INT(11)', 'INTEGER').replace('INT(4)', 'INTEGER')
            pg_sql = pg_sql.replace('AUTO_INCREMENT', 'SERIAL').replace('PRIMARY KEY', 'PRIMARY KEY')
            
            print(f"   📝 Recreating table: {table_name}")
            cursor.execute(pg_sql)
            conn.commit()
            cursor.close()
            return True
        else:
            print(f"❌ No CREATE TABLE statement found for {table_name}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to recreate {table_name}: {e}")
        cursor.close()
        return False

def import_table_data(conn, table_name):
    """Import data for a specific table"""
    
    cursor = conn.cursor()
    
    try:
        with open('u503102722_conflictdb (1).sql', 'r') as f:
            content = f.read()
        
        # Find INSERT statements
        insert_pattern = f'INSERT INTO `{table_name}`.*?VALUES.*?;'
        insert_statements = re.findall(insert_pattern, content, re.DOTALL | re.MULTILINE)
        
        if not insert_statements:
            print(f"⚠️  No INSERT statements found for {table_name}")
            return True
        
        print(f"📥 Importing {len(insert_statements)} INSERT statements for {table_name}")
        
        total_inserted = 0
        total_failed = 0
        
        for i, stmt in enumerate(insert_statements):
            try:
                # Convert MySQL to PostgreSQL
                pg_stmt = stmt.replace('`', '"')
                
                # Handle boolean values
                pg_stmt = pg_stmt.replace("'1', 'true'", "true")
                pg_stmt = pg_stmt.replace("'0', 'false'", "false")
                
                # Handle timestamps
                pg_stmt = pg_stmt.replace('NOW()', 'CURRENT_TIMESTAMP')
                pg_stmt = pg_stmt.replace("'2026-01-25 11:22:35'", "'2026-01-25 11:22:35'")
                
                # Handle empty strings for numeric fields
                pg_stmt = re.sub(r", ''(?=,|\))", ", NULL", pg_stmt)
                
                # Handle specific field conversions
                if table_name == 'users':
                    pg_stmt = pg_stmt.replace("'viewer',", "'viewer'")
                    pg_stmt = pg_stmt.replace("'admin',", "'admin'")
                    pg_stmt = pg_stmt.replace("'analyst',", "'analyst'")
                
                cursor.execute(pg_stmt)
                total_inserted += 1
                
                if (i + 1) % 10 == 0:
                    print(f"   Progress: {i + 1}/{len(insert_statements)}")
                
            except Exception as e:
                # Count failed records
                record_pattern = r'\([^)]+\)(?:,|;)'
                records = re.findall(record_pattern, stmt)
                total_failed += len(records)
                print(f"   ⚠️  Failed statement {i + 1}: {len(records)} records")
        
        conn.commit()
        cursor.close()
        
        # Verify results
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        final_count = cursor.fetchone()[0]
        cursor.close()
        
        print(f"   ✅ Imported: {total_inserted} statements")
        print(f"   ⚠️  Failed: {total_failed} records")
        print(f"   📊 Final count: {final_count} records")
        
        return total_failed == 0
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        print(f"❌ Import failed for {table_name}: {e}")
        return False

def main():
    """Main restoration process"""
    
    print("🗄️  SIMPLE & EFFECTIVE DATA RESTORATION")
    print("=" * 50)
    print()
    
    # Check for duplicate data first
    conn = get_db_connection()
    is_duplicate = check_conflict_events_duplicate(conn)
    
    print()
    response = input("Continue with restoration? (y/n): ").lower().strip()
    
    if response != 'y':
        print("👋 Restoration cancelled")
        return
    
    print()
    print("🚀 STARTING RESTORATION")
    print("=" * 30)
    
    # Create missing countries table
    if create_countries_table(conn):
        # Import countries data
        import_table_data(conn, 'countries')
    
    # Tables to restore (drop and recreate)
    tables_to_restore = [
        'conflicts',  # Main data
        'states',      # Reference data
        'lgas',        # Geographic data
        'users',       # User data
        'actors',      # Actor data
        'conflict_types', # Conflict categories
        'regions',     # Regional data
    ]
    
    success_count = 0
    
    for table_name in tables_to_restore:
        print()
        print(f"🔄 Processing table: {table_name}")
        
        # Drop and recreate
        if drop_and_recreate_table(conn, table_name):
            # Import data
            if import_table_data(conn, table_name):
                success_count += 1
            else:
                print(f"   ❌ Data import failed for {table_name}")
        else:
            print(f"   ❌ Table recreation failed for {table_name}")
    
    conn.close()
    
    print()
    print("📊 RESTORATION SUMMARY")
    print("=" * 30)
    print(f"Tables processed: {success_count}/{len(tables_to_restore)}")
    
    if success_count == len(tables_to_restore):
        print("✅ All tables restored successfully!")
        
        # Test the fix
        print()
        print("🔍 TESTING MONTHLY TRENDS FIX")
        print("=" * 30)
        
        try:
            import requests
            response = requests.get(
                "https://naija-conflict-tracker-production.up.railway.app/api/v1/timeseries/monthly-trends?months_back=12",
                timeout=15
            )
            
            if response.status_code == 200:
                trends = response.json()
                total = trends['summary']['totalIncidents']
                
                print(f"   ✅ Monthly Trends API: {total} total incidents")
                
                if total > 1000:
                    print("🎉 MONTHLY TRENDS ISSUE FIXED!")
                    print("   The dashboard should now show complete data")
                    print("   Expected: ~5,106 incidents instead of {total}")
                else:
                    print(f"⚠️  Still showing {total} incidents")
                    print("   Railway backend may need time to update")
            else:
                print(f"   ❌ API test failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing API: {e}")
    else:
        print(f"⚠️  {len(tables_to_restore) - success_count} tables had issues")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Restoration cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
