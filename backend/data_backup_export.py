#!/usr/bin/env python3
"""
Data backup using existing migration infrastructure
Creates CSV exports of critical tables before migration
"""

import os
import sys
import csv
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def create_data_backup():
    """Create CSV backup of critical data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"=== Creating Data Backup (CSV Export) ===")
    print(f"Timestamp: {timestamp}")
    
    try:
        # Import database components
        from sqlalchemy import create_engine, text
        from core.config import settings
        
        # Create database connection
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Backup conflicts table (current data)
            print("📥 Exporting conflicts table...")
            conflicts_file = f"backup_conflicts_{timestamp}.csv"
            
            result = conn.execute(text("SELECT COUNT(*) FROM conflicts"))
            total_conflicts = result.scalar()
            print(f"   Total conflicts: {total_conflicts}")
            
            if total_conflicts > 0:
                result = conn.execute(text("""
                    SELECT id, incidence_date, conflict_type_id, state_id, lga_id, community,
                           civilian_death_male, civilian_death_female, civilian_death_unknown,
                           security_death_male, security_death_female, security_death_unknown,
                           injured_male, injured_female, injured_unknown,
                           kidnapped_male, kidnapped_female, kidnapped_unknown,
                           description, created_at
                    FROM conflicts 
                    ORDER BY id
                """))
                
                with open(conflicts_file, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    # Write header
                    writer.writerow(['id', 'incidence_date', 'conflict_type_id', 'state_id', 'lga_id', 'community',
                                   'civilian_death_male', 'civilian_death_female', 'civilian_death_unknown',
                                   'security_death_male', 'security_death_female', 'security_death_unknown',
                                   'injured_male', 'injured_female', 'injured_unknown',
                                   'kidnapped_male', 'kidnapped_female', 'kidnapped_unknown',
                                   'description', 'created_at'])
                    
                    # Write data
                    for row in result:
                        writer.writerow(row)
                
                print(f"   ✅ Conflicts exported: {conflicts_file}")
            else:
                print("   ℹ️  No conflicts data to export")
                conflicts_file = None
            
            # Backup kidnapping-specific statistics
            print("📊 Exporting kidnapping statistics...")
            kidnapping_stats_file = f"backup_kidnapping_stats_{timestamp}.csv"
            
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(*) FILTER (WHERE kidnapped_male > 0 OR kidnapped_female > 0 OR kidnapped_unknown > 0) as kidnapping_records,
                    SUM(kidnapped_male) as total_male,
                    SUM(kidnapped_female) as total_female,
                    SUM(kidnapped_unknown) as total_unknown,
                    SUM(kidnapped_male + kidnapped_female + kidnapped_unknown) as total_victims,
                    MIN(incidence_date) as earliest_date,
                    MAX(incidence_date) as latest_date
                FROM conflicts
            """))
            
            stats = result.fetchone()
            
            with open(kidnapping_stats_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['metric', 'value'])
                writer.writerow(['total_records', stats[0]])
                writer.writerow(['kidnapping_records', stats[1]])
                writer.writerow(['total_male_victims', stats[2]])
                writer.writerow(['total_female_victims', stats[3]])
                writer.writerow(['total_unknown_victims', stats[4]])
                writer.writerow(['total_all_victims', stats[5]])
                writer.writerow(['earliest_date', stats[6]])
                writer.writerow(['latest_date', stats[7]])
            
            print(f"   ✅ Kidnapping stats exported: {kidnapping_stats_file}")
            
            # Create summary report
            summary_file = f"backup_summary_{timestamp}.txt"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"=== DATA BACKUP SUMMARY ===\n")
                f.write(f"Created: {timestamp}\n")
                f.write(f"Total conflicts: {stats[0]}\n")
                f.write(f"Kidnapping records: {stats[1]}\n")
                f.write(f"Total victims: {stats[5]}\n")
                f.write(f"Date range: {stats[6]} to {stats[7]}\n")
                f.write(f"\nFiles created:\n")
                if conflicts_file:
                    f.write(f"- {conflicts_file}\n")
                f.write(f"- {kidnapping_stats_file}\n")
                f.write(f"- {summary_file}\n")
                f.write(f"\nTo restore: Import CSV files back to database\n")
            
            print(f"   ✅ Summary created: {summary_file}")
            
            print(f"\n✅ BACKUP SUCCESSFUL")
            print(f"📁 Files created with timestamp: {timestamp}")
            print(f"🔄 Restore by importing CSV files")
            
            return True
            
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

if __name__ == "__main__":
    success = create_data_backup()
    
    if not success:
        print(f"\n❌ BACKUP FAILED")
        print(f"🚨 DO NOT PROCEED WITH MIGRATION")
        sys.exit(1)
