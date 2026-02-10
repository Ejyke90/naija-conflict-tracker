#!/usr/bin/env python3
"""
Execute complete kidnapping data migration using the fixed parser
"""

import os
import sys
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def execute_migration():
    """Execute the complete migration with all 1,107 kidnapping records"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"=== EXECUTING COMPLETE KIDNAPPING MIGRATION ===")
    print(f"Timestamp: {timestamp}")
    print(f"Target: All 1,107 kidnapping records with 8,727 victims")
    
    try:
        # Import the fixed parser
        from mariadb_parser import MariaDBParser
        
        # Import database components
        from sqlalchemy import create_engine, text
        from core.config import settings
        
        # Create database connection
        engine = create_engine(settings.DATABASE_URL)
        
        print(f"🔗 Connected to database")
        
        # Step 1: Parse the complete dataset
        print(f"\n📊 Step 1: Parsing complete dataset...")
        sql_file = '/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql'
        
        parser = MariaDBParser(sql_file)
        records = parser.parse_sql_export()
        kidnapping_records = parser.extract_kidnapping_records()
        
        print(f"✅ Parsed {len(records)} total records")
        print(f"✅ Found {len(kidnapping_records)} kidnapping records")
        
        # Step 2: Clear existing conflicts data (for clean migration)
        print(f"\n🧹 Step 2: Clearing existing conflicts data...")
        with engine.connect() as conn:
            # Get current counts before clearing
            result = conn.execute(text("SELECT COUNT(*) FROM conflicts"))
            old_count = result.scalar()
            print(f"   Current records: {old_count}")
            
            # Clear the table
            conn.execute(text("TRUNCATE TABLE conflicts"))
            conn.commit()
            print(f"   ✅ Cleared conflicts table")
        
        # Step 3: Insert all records
        print(f"\n📥 Step 3: Inserting all records...")
        with engine.connect() as conn:
            inserted_count = 0
            kidnapping_inserted = 0
            
            for i, record in enumerate(records):
                try:
                    # Convert record to SQL INSERT
                    sql = text("""
                        INSERT INTO conflicts (
                            id, incidence_date, conflict_type_id, country_id, region_id,
                            state_id, lga_id, community, civilian_death_male, civilian_death_female,
                            civilian_death_unknown, security_death_male, security_death_female,
                            security_death_unknown, injured_male, injured_female, injured_unknown,
                            kidnapped_male, kidnapped_female, kidnapped_unknown, displaced_persons,
                            displaced_male, displaced_female, actor_1, actor_2, actor_3,
                            description, action, highway_roads_water, confirmation_verification,
                            verification_level, source_url, source_contact_details,
                            source_contact_pictures, source_metadata, data_source,
                            reporter_id, created_at, updated_at, deleted_at
                        ) VALUES (
                            :id, :incidence_date, :conflict_type_id, 1, 1,
                            :state_id, :lga_id, :community, :civilian_death_male, :civilian_death_female,
                            :civilian_death_unknown, :security_death_male, :security_death_female,
                            :security_death_unknown, :injured_male, :injured_female, :injured_unknown,
                            :kidnapped_male, :kidnapped_female, :kidnapped_unknown, :displaced_persons,
                            :displaced_male, :displaced_female, :actor_1, :actor_2, :actor_3,
                            :description, :action, :highway_roads_water, :confirmation_verification,
                            :verification_level, :source_url, :source_contact_details,
                            :source_contact_pictures, :source_metadata, :data_source,
                            :reporter_id, :created_at, :updated_at, :deleted_at
                        )
                    """)
                    
                    conn.execute(sql, {
                        'id': record['id'],
                        'incidence_date': record['incidence_date'],
                        'conflict_type_id': record['conflict_type_id'],
                        'state_id': record['state_id'],
                        'lga_id': record['lga_id'],
                        'community': record['community'],
                        'civilian_death_male': record['civilian_death_male'],
                        'civilian_death_female': record['civilian_death_female'],
                        'civilian_death_unknown': record['civilian_death_unknown'],
                        'security_death_male': record['security_death_male'],
                        'security_death_female': record['security_death_female'],
                        'security_death_unknown': record['security_death_unknown'],
                        'injured_male': record['injured_male'],
                        'injured_female': record['injured_female'],
                        'injured_unknown': record['injured_unknown'],
                        'kidnapped_male': record['kidnapped_male'],
                        'kidnapped_female': record['kidnapped_female'],
                        'kidnapped_unknown': record['kidnapped_unknown'],
                        'displaced_persons': record['displaced_persons'],
                        'displaced_male': 0,  # Default values for missing fields
                        'displaced_female': 0,
                        'actor_1': record['actor_1'],
                        'actor_2': 0,
                        'actor_3': 0,
                        'description': record['description'],
                        'action': '',
                        'highway_roads_water': None,
                        'confirmation_verification': '',
                        'verification_level': '',
                        'source_url': record['source_url'],
                        'source_contact_details': '',
                        'source_contact_pictures': '',
                        'source_metadata': '',
                        'data_source': record['data_source'],
                        'reporter_id': 1,
                        'created_at': datetime.now(),
                        'updated_at': datetime.now(),
                        'deleted_at': None
                    })
                    
                    inserted_count += 1
                    if record['total_kidnapped'] > 0:
                        kidnapping_inserted += 1
                    
                    # Progress update every 500 records
                    if inserted_count % 500 == 0:
                        print(f"   Progress: {inserted_count}/{len(records)} records inserted")
                        conn.commit()  # Commit periodically
                
                except Exception as e:
                    print(f"   ⚠️  Error inserting record {i+1}: {e}")
                    continue
            
            # Final commit
            conn.commit()
            print(f"   ✅ Inserted {inserted_count} total records")
            print(f"   ✅ Inserted {kidnapping_inserted} kidnapping records")
        
        # Step 4: Verify migration results
        print(f"\n🔍 Step 4: Verifying migration results...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(*) FILTER (WHERE kidnapped_male > 0 OR kidnapped_female > 0 OR kidnapped_unknown > 0) as kidnapping_records,
                    SUM(kidnapped_male + kidnapped_female + kidnapped_unknown) as total_victims,
                    MIN(incidence_date) as earliest_date,
                    MAX(incidence_date) as latest_date
                FROM conflicts
            """))
            
            stats = result.fetchone()
            
            print(f"📊 Migration Results:")
            print(f"   Total records: {stats[0]}")
            print(f"   Kidnapping records: {stats[1]}")
            print(f"   Total victims: {stats[2]}")
            print(f"   Date range: {stats[3]} to {stats[4]}")
            
            # Compare with expected
            expected_records = len(records)
            expected_kidnapping = len(kidnapping_records)
            expected_victims = sum(r['total_kidnapped'] for r in kidnapping_records)
            
            print(f"\n📈 Comparison:")
            print(f"   Expected records: {expected_records} → Got: {stats[0]} {'✅' if stats[0] == expected_records else '❌'}")
            print(f"   Expected kidnapping: {expected_kidnapping} → Got: {stats[1]} {'✅' if stats[1] == expected_kidnapping else '❌'}")
            print(f"   Expected victims: {expected_victims} → Got: {stats[2]} {'✅' if stats[2] == expected_victims else '❌'}")
            
            # Create migration report
            report_file = f"migration_report_{timestamp}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(f"=== KIDNAPPING MIGRATION REPORT ===\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Status: {'SUCCESS' if stats[0] == expected_records else 'PARTIAL'}\n")
                f.write(f"\nResults:\n")
                f.write(f"Total records: {stats[0]} (expected: {expected_records})\n")
                f.write(f"Kidnapping records: {stats[1]} (expected: {expected_kidnapping})\n")
                f.write(f"Total victims: {stats[2]} (expected: {expected_victims})\n")
                f.write(f"Date range: {stats[3]} to {stats[4]}\n")
                f.write(f"\nImprovement from old data:\n")
                f.write(f"Kidnapping records: 13 → {stats[1]} ({stats[1]/13:.1f}x increase)\n")
                f.write(f"Victims: 78 → {stats[2]} ({stats[2]/78:.1f}x increase)\n")
            
            print(f"\n📄 Report saved: {report_file}")
            
            return stats[0] == expected_records and stats[1] == expected_kidnapping
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚨 WARNING: This will replace all conflicts data in the database")
    print("🚨 Make sure you have a backup (Neon point-in-time restore available)")
    
    response = input("\nProceed with migration? (yes/no): ")
    if response.lower() == 'yes':
        success = execute_migration()
        
        if success:
            print(f"\n🎉 MIGRATION SUCCESSFUL!")
            print(f"📊 Dashboard should now show meaningful kidnapping data")
            print(f"🔄 Test dashboard at: https://naija-conflict-tracker-xpcc.vercel.app")
        else:
            print(f"\n❌ MIGRATION ISSUES DETECTED")
            print(f"🔄 Use Neon point-in-time restore if needed")
    else:
        print("❌ Migration cancelled")
