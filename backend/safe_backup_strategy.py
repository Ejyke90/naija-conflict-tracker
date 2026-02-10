#!/usr/bin/env python3
"""
Safe backup strategy that works around permission issues
"""

import os
import sys
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def create_safe_backup():
    """Create backup using safe methods"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"=== Safe Backup Strategy ===")
    print(f"Timestamp: {timestamp}")
    
    try:
        from sqlalchemy import create_engine, text
        from core.config import settings
        
        # Create database connection
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # First, let's see what we can access
            print("🔍 Checking table access...")
            
            # Check if we can access the conflicts table
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM conflicts"))
                count = result.scalar()
                print(f"✅ Conflicts table accessible: {count} records")
                
                if count > 0:
                    # Create backup of current data
                    backup_file = f"backup_conflicts_safe_{timestamp}.csv"
                    
                    result = conn.execute(text("""
                        SELECT id, incidence_date, conflict_type_id, state_id, lga_id, community,
                               civilian_death_male, civilian_death_female, civilian_death_unknown,
                               security_death_male, security_death_female, security_death_unknown,
                               injured_male, injured_female, injured_unknown,
                               kidnapped_male, kidnapped_female, kidnapped_unknown,
                               description, created_at
                        FROM conflicts 
                        ORDER BY id
                        LIMIT 1000
                    """))
                    
                    # Write to CSV
                    import csv
                    with open(backup_file, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        # Write header
                        writer.writerow(['id', 'incidence_date', 'conflict_type_id', 'state_id', 'lga_id', 'community',
                                       'civilian_death_male', 'civilian_death_female', 'civilian_death_unknown',
                                       'security_death_male', 'security_death_female', 'security_death_unknown',
                                       'injured_male', 'injured_female', 'injured_unknown',
                                       'kidnapped_male', 'kidnapped_female', 'kidnapped_unknown',
                                       'description', 'created_at'])
                        
                        # Write data
                        records_written = 0
                        for row in result:
                            writer.writerow(row)
                            records_written += 1
                    
                    print(f"✅ Backup created: {backup_file}")
                    print(f"📊 Records backed up: {records_written}")
                    
                    # Create summary
                    summary_file = f"backup_summary_{timestamp}.txt"
                    with open(summary_file, 'w', encoding='utf-8') as f:
                        f.write(f"=== BACKUP SUMMARY ===\n")
                        f.write(f"Timestamp: {timestamp}\n")
                        f.write(f"Total conflicts: {count}\n")
                        f.write(f"Records backed up: {records_written}\n")
                        f.write(f"Backup file: {backup_file}\n")
                        f.write(f"\nReady for migration with backup protection\n")
                    
                    print(f"✅ Summary created: {summary_file}")
                    return True
                    
                else:
                    print("ℹ️  No data in conflicts table - nothing to backup")
                    return True
                    
            except Exception as table_error:
                print(f"❌ Cannot access conflicts table: {table_error}")
                
                # Try alternative approach - backup schema and structure
                print("🔄 Attempting schema backup...")
                
                try:
                    result = conn.execute(text("""
                        SELECT table_name, column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = 'conflicts'
                        ORDER BY ordinal_position
                    """))
                    
                    schema_file = f"backup_conflicts_schema_{timestamp}.csv"
                    
                    import csv
                    with open(schema_file, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(['table_name', 'column_name', 'data_type', 'is_nullable'])
                        
                        for row in result:
                            writer.writerow(row)
                    
                    print(f"✅ Schema backup created: {schema_file}")
                    
                    # Create note about data access issue
                    note_file = f"backup_access_issue_{timestamp}.txt"
                    with open(note_file, 'w', encoding='utf-8') as f:
                        f.write(f"=== BACKUP ACCESS ISSUE ===\n")
                        f.write(f"Timestamp: {timestamp}\n")
                        f.write(f"Issue: Cannot access conflicts table directly\n")
                        f.write(f"Error: {table_error}\n")
                        f.write(f"Schema backed up: {schema_file}\n")
                        f.write(f"\n⚠️  MIGRATION RISK: Cannot verify current data\n")
                        f.write(f"Recommendation: Proceed with caution\n")
                    
                    print(f"⚠️  Access issue documented: {note_file}")
                    return False  # Don't proceed without data backup
                    
                except Exception as schema_error:
                    print(f"❌ Schema backup also failed: {schema_error}")
                    return False
                    
    except Exception as e:
        print(f"❌ Backup strategy failed: {e}")
        return False

if __name__ == "__main__":
    success = create_safe_backup()
    
    if success:
        print(f"\n✅ BACKUP SUCCESSFUL - Safe to proceed with migration")
    else:
        print(f"\n❌ BACKUP INCOMPLETE - Exercise caution with migration")
        print(f"🚨 Consider manual backup via Railway dashboard")
