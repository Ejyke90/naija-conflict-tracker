#!/usr/bin/env python3
"""
Force Restoration Script - Overwrites existing data when needed
"""

import psycopg2
import re
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        'postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    )

def analyze_data_gaps():
    """Analyze what data is missing compared to SQL file"""
    
    print("🔍 ANALYZING DATA GAPS")
    print("=" * 30)
    
    # SQL file data counts
    sql_counts = {
        'conflicts': 5106,
        'lgas': 946,
        'states': 40,
        'users': 224,
        'actors': 27,
        'conflict_types': 14,
        'regions': 6
    }
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Comparing SQL file vs Database:")
    print()
    
    gaps = []
    
    for table, sql_count in sql_counts.items():
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            db_count = cursor.fetchone()[0]
            
            if db_count < sql_count:
                missing = sql_count - db_count
                gaps.append((table, db_count, sql_count, missing))
                
                status = "❌" if missing > 100 else "⚠️"
                print(f"{status} {table:15}: {db_count:6,} in DB, {sql_count:6,} in SQL (missing {missing})")
            else:
                print(f"✅ {table:15}: {db_count:6,} in DB, {sql_count:6,} in SQL")
                
        except Exception as e:
            print(f"❌ {table:15}: ERROR - {e}")
    
    cursor.close()
    conn.close()
    
    return gaps

def force_restore_conflicts():
    """Force restore conflicts table with all data"""
    
    print("🚀 FORCE RESTORING CONFLICTS TABLE")
    print("=" * 40)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Read SQL file
        with open('u503102722_conflictdb (1).sql', 'r') as f:
            content = f.read()
        
        # Extract conflicts INSERT statements
        insert_pattern = r'INSERT INTO `conflicts`.*?VALUES.*?;'
        insert_statements = re.findall(insert_pattern, content, re.DOTALL | re.MULTILINE)
        
        print(f"Found {len(insert_statements)} INSERT statements for conflicts")
        
        # Count records
        total_records = 0
        for stmt in insert_statements:
            record_pattern = r'\([^)]+\)(?:,|;)'
            records = re.findall(record_pattern, stmt)
            total_records += len(records)
        
        print(f"Total records to insert: {total_records}")
        
        # Get current count
        cursor.execute("SELECT COUNT(*) FROM conflicts")
        current_count = cursor.fetchone()[0]
        print(f"Current records: {current_count}")
        
        # Truncate table
        print("🗑️  Truncating conflicts table...")
        cursor.execute("TRUNCATE TABLE conflicts CASCADE")
        conn.commit()
        
        # Insert data
        inserted = 0
        failed = 0
        
        for i, stmt in enumerate(insert_statements):
            try:
                # Convert to PostgreSQL
                pg_stmt = stmt.replace('`', '"')
                pg_stmt = pg_stmt.replace("'1', 'true'", "true, 'true'")
                pg_stmt = pg_stmt.replace("'0', 'false'", "false, 'false'")
                pg_stmt = pg_stmt.replace('NOW()', 'CURRENT_TIMESTAMP')
                pg_stmt = re.sub(r", ''(?=,|\))", ", NULL", pg_stmt)
                
                cursor.execute(pg_stmt)
                inserted += 1
                
                if (i + 1) % 100 == 0:
                    print(f"   Progress: {i + 1}/{len(insert_statements)} statements processed")
                
            except Exception as e:
                record_pattern = r'\([^)]+\)(?:,|;)'
                records = re.findall(record_pattern, stmt)
                failed += len(records)
                print(f"   ⚠️  Failed batch {i + 1}: {len(records)} records")
        
        conn.commit()
        cursor.close()
        
        # Verify
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM conflicts")
        new_count = cursor.fetchone()[0]
        cursor.close()
        
        print(f"✅ Force restoration completed!")
        print(f"   Inserted: {inserted} statements")
        print(f"   Failed: {failed} records")
        print(f"   Final count: {new_count} records")
        
        return new_count == total_records
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        print(f"❌ Force restoration failed: {e}")
        return False

def main():
    """Main force restoration"""
    
    print("🗄️  FORCE DATA RESTORATION")
    print("=" * 40)
    print("This will overwrite existing data with SQL file data")
    print()
    
    # Analyze gaps
    gaps = analyze_data_gaps()
    
    if not gaps:
        print("✅ No data gaps found!")
        return True
    
    print()
    print("📊 Tables with missing data:")
    for table, db_count, sql_count, missing in gaps:
        print(f"   • {table}: missing {missing} records")
    
    print()
    response = input("Force restore conflicts table? (y/n): ").lower().strip()
    
    if response == 'y':
        success = force_restore_conflicts()
        
        if success:
            print()
            print("🔍 VERIFYING FIX")
            print("=" * 20)
            
            # Test API
            try:
                import requests
                print("📈 Testing Monthly Trends API...")
                response = requests.get(
                    "https://naija-conflict-tracker-production.up.railway.app/api/v1/timeseries/monthly-trends?months_back=12",
                    timeout=10
                )
                
                if response.status_code == 200:
                    trends = response.json()
                    total = trends['summary']['totalIncidents']
                    
                    print(f"   ✅ Monthly Trends: {total} incidents")
                    
                    if total > 1000:
                        print("🎉 MONTHLY TRENDS FIXED!")
                        print("   The dashboard should now show complete data")
                    else:
                        print("⚠️  Still showing low numbers - Railway may need to restart")
                else:
                    print(f"   ❌ API test failed: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error testing API: {e}")
        
        return success
    else:
        print("👋 Force restoration cancelled")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Force restoration cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
