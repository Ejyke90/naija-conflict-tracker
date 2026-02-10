#!/usr/bin/env python3
"""
Comprehensive Data Analysis and Migration Workflow
Analyzes MariaDB export vs PostgreSQL current state
"""

import os
import re
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.config import settings

class DataAnalysisWorkflow:
    def __init__(self):
        self.maria_db_file = '/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql'
        self.postgres_engine = create_engine(settings.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.postgres_engine)
        
    def parse_maria_db_export(self):
        """Parse MariaDB SQL export file"""
        print("=== PARSING MARIA DB EXPORT ===")
        
        with open(self.maria_db_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find the conflicts INSERT statement
        conflicts_insert_match = re.search(
            r'INSERT INTO `conflicts`.*?VALUES\s*(.+?);', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        
        if not conflicts_insert_match:
            print("❌ No conflicts INSERT statement found")
            return []
        
        values_str = conflicts_insert_match.group(1)
        
        # Parse individual records more carefully
        records = []
        current_record = ''
        paren_count = 0
        in_quotes = False
        quote_char = None
        
        for char in values_str:
            if char in ("'", '"') and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif char == '(' and not in_quotes:
                paren_count += 1
                current_record += char
            elif char == ')' and not in_quotes:
                paren_count -= 1
                current_record += char
                if paren_count == 0:
                    records.append(current_record.strip())
                    current_record = ''
            else:
                current_record += char
        
        print(f"Found {len(records)} raw records")
        
        # Parse each record
        parsed_records = []
        for i, record in enumerate(records):
            try:
                # Remove outer parentheses
                if record.startswith('(') and record.endswith(')'):
                    record = record[1:-1]
                
                # Parse values handling quoted strings
                values = []
                current_val = ''
                in_val_quotes = False
                val_quote_char = None
                
                for char in record:
                    if char in ("'", '"') and not in_val_quotes:
                        in_val_quotes = True
                        val_quote_char = char
                    elif char == val_quote_char and in_val_quotes:
                        in_val_quotes = False
                        val_quote_char = None
                    elif char == ',' and not in_val_quotes:
                        values.append(current_val.strip())
                        current_val = ''
                    else:
                        current_val += char
                
                if current_val.strip():
                    values.append(current_val.strip())
                
                if len(values) >= 24:  # Minimum expected columns
                    parsed_records.append({
                        'raw_index': i,
                        'values': values
                    })
                    
            except Exception as e:
                print(f"Error parsing record {i}: {e}")
                continue
        
        print(f"Successfully parsed {len(parsed_records)} records")
        return parsed_records
    
    def analyze_maria_db_data(self, records):
        """Analyze MariaDB data for kidnapping and death information"""
        print("\n=== ANALYZING MARIA DB DATA ===")
        
        kidnapping_records = []
        death_records = []
        all_records = []
        
        for record in records:
            values = record['values']
            
            try:
                # Extract key fields (adjust indices based on actual schema)
                record_id = values[0].strip().strip("'")
                date_val = values[1].strip().strip("'")
                conflict_type_id = values[2].strip()
                state_id = values[5].strip()
                lga_id = values[6].strip()
                community = values[7].strip().strip("'")
                
                # Death data (indices 9, 10, 11)
                death_male = self.safe_int(values[9].strip())
                death_female = self.safe_int(values[10].strip())
                death_unknown = self.safe_int(values[11].strip())
                total_deaths = death_male + death_female + death_unknown
                
                # Kidnapping data (indices 18, 19, 20)
                kidnapped_male = self.safe_int(values[18].strip())
                kidnapped_female = self.safe_int(values[19].strip())
                kidnapped_unknown = self.safe_int(values[20].strip())
                total_kidnapped = kidnapped_male + kidnapped_female + kidnapped_unknown
                
                # Other fields
                actor_1 = values[21].strip()
                description = values[23].strip().strip("'") if len(values) > 23 else ''
                source_url = values[27].strip().strip("'") if len(values) > 27 else ''
                data_source = values[30].strip().strip("'") if len(values) > 30 else ''
                
                record_data = {
                    'id': record_id,
                    'date': date_val,
                    'conflict_type_id': conflict_type_id,
                    'state_id': state_id,
                    'lga_id': lga_id,
                    'community': community,
                    'death_male': death_male,
                    'death_female': death_female,
                    'death_unknown': death_unknown,
                    'total_deaths': total_deaths,
                    'kidnapped_male': kidnapped_male,
                    'kidnapped_female': kidnapped_female,
                    'kidnapped_unknown': kidnapped_unknown,
                    'total_kidnapped': total_kidnapped,
                    'actor_1': actor_1,
                    'description': description,
                    'source_url': source_url,
                    'data_source': data_source
                }
                
                all_records.append(record_data)
                
                if total_kidnapped > 0:
                    kidnapping_records.append(record_data)
                
                if total_deaths > 0:
                    death_records.append(record_data)
                    
            except Exception as e:
                print(f"Error analyzing record {record['raw_index']}: {e}")
                continue
        
        print(f"Total records analyzed: {len(all_records)}")
        print(f"Records with kidnapping data: {len(kidnapping_records)}")
        print(f"Records with death data: {len(death_records)}")
        
        if kidnapping_records:
            total_kidnapped = sum(r['total_kidnapped'] for r in kidnapping_records)
            print(f"Total kidnapping victims: {total_kidnapped}")
        
        if death_records:
            total_deaths = sum(r['total_deaths'] for r in death_records)
            print(f"Total death victims: {total_deaths}")
        
        return all_records, kidnapping_records, death_records
    
    def safe_int(self, value):
        """Safely convert to int, handling NULL and other values"""
        value = value.strip().strip("'")
        if value == 'NULL' or value == '' or not value.isdigit():
            return 0
        return int(value)
    
    def analyze_postgres_current_state(self):
        """Analyze current PostgreSQL database state"""
        print("\n=== ANALYZING CURRENT POSTGRESQL DB ===")
        
        db = self.SessionLocal()
        
        try:
            # Basic counts
            result = db.execute(text("SELECT COUNT(*) FROM conflicts"))
            total_conflicts = result.scalar()
            
            result = db.execute(text("""
                SELECT COUNT(*) FROM conflicts 
                WHERE kidnapped_male > 0 OR kidnapped_female > 0 OR kidnapped_unknown > 0
            """))
            kidnapping_conflicts = result.scalar()
            
            result = db.execute(text("""
                SELECT SUM(kidnapped_male + kidnapped_female + kidnapped_unknown) FROM conflicts
            """))
            total_kidnapped = result.scalar() or 0
            
            result = db.execute(text("""
                SELECT COUNT(*) FROM conflicts 
                WHERE civilian_death_male > 0 OR civilian_death_female > 0 OR civilian_death_unknown > 0
            """))
            death_conflicts = result.scalar()
            
            result = db.execute(text("""
                SELECT SUM(civilian_death_male + civilian_death_female + civilian_death_unknown) FROM conflicts
            """))
            total_deaths = result.scalar() or 0
            
            result = db.execute(text("SELECT MIN(incidence_date), MAX(incidence_date) FROM conflicts"))
            date_range = result.fetchone()
            
            print(f"Total conflicts: {total_conflicts}")
            print(f"Conflicts with kidnapping data: {kidnapping_conflicts}")
            print(f"Total kidnapping victims: {total_kidnapped}")
            print(f"Conflicts with death data: {death_conflicts}")
            print(f"Total deaths: {total_deaths}")
            print(f"Date range: {date_range[0]} to {date_range[1]}")
            
            return {
                'total_conflicts': total_conflicts,
                'kidnapping_conflicts': kidnapping_conflicts,
                'total_kidnapped': total_kidnapped,
                'death_conflicts': death_conflicts,
                'total_deaths': total_deaths,
                'date_range': date_range
            }
            
        finally:
            db.close()
    
    def compare_data_sources(self, maria_data, postgres_stats):
        """Compare MariaDB export with current PostgreSQL state"""
        print("\n=== DATA COMPARISON ANALYSIS ===")
        
        maria_all, maria_kidnapping, maria_deaths = maria_data
        
        print("MARIA DB EXPORT:")
        print(f"  Total records: {len(maria_all)}")
        print(f"  Kidnapping records: {len(maria_kidnapping)}")
        print(f"  Death records: {len(maria_deaths)}")
        
        if maria_kidnapping:
            maria_total_kidnapped = sum(r['total_kidnapped'] for r in maria_kidnapping)
            print(f"  Total kidnapping victims: {maria_total_kidnapped}")
        
        if maria_deaths:
            maria_total_deaths = sum(r['total_deaths'] for r in maria_deaths)
            print(f"  Total death victims: {maria_total_deaths}")
        
        print("\nCURRENT POSTGRESQL:")
        print(f"  Total conflicts: {postgres_stats['total_conflicts']}")
        print(f"  Kidnapping conflicts: {postgres_stats['kidnapping_conflicts']}")
        print(f"  Total kidnapping victims: {postgres_stats['total_kidnapped']}")
        print(f"  Death conflicts: {postgres_stats['death_conflicts']}")
        print(f"  Total deaths: {postgres_stats['total_deaths']}")
        
        print("\n=== KEY FINDINGS ===")
        
        # Kidnapping data gap
        if len(maria_kidnapping) > 0 and postgres_stats['kidnapping_conflicts'] == 0:
            print("❌ CRITICAL: All kidnapping data is missing from PostgreSQL!")
            print(f"   MariaDB has {len(maria_kidnapping)} kidnapping records")
            print(f"   PostgreSQL has {postgres_stats['kidnapping_conflicts']} kidnapping records")
        
        # Death data comparison
        if maria_deaths:
            maria_total_deaths = sum(r['total_deaths'] for r in maria_deaths)
            if maria_total_deaths != postgres_stats['total_deaths']:
                print(f"⚠️  Death data mismatch: MariaDB ({maria_total_deaths}) vs PostgreSQL ({postgres_stats['total_deaths']})")
        
        return {
            'kidnapping_data_missing': len(maria_kidnapping) > 0 and postgres_stats['kidnapping_conflicts'] == 0,
            'maria_kidnapping_records': len(maria_kidnapping),
            'postgres_kidnapping_records': postgres_stats['kidnapping_conflicts'],
            'maria_total_kidnapped': sum(r['total_kidnapped'] for r in maria_kidnapping) if maria_kidnapping else 0,
            'postgres_total_kidnapped': postgres_stats['total_kidnapped']
        }
    
    def generate_migration_plan(self, comparison_results, kidnapping_records):
        """Generate specific migration recommendations"""
        print("\n=== MIGRATION PLAN ===")
        
        if comparison_results['kidnapping_data_missing']:
            print("🔄 IMMEDIATE ACTION REQUIRED:")
            print(f"1. Migrate {comparison_results['maria_kidnapping_records']} kidnapping records")
            print(f"2. Add {comparison_results['maria_total_kidnapped']} kidnapping victims to database")
            print("3. This will resolve the 'No data' issue in kidnapping dashboard")
            
            print("\nSample records to migrate:")
            for i, record in enumerate(kidnapping_records[:5], 1):
                print(f"  {i}. {record['date']} - {record['community']} - {record['total_kidnapped']} victims")
                print(f"     Actor: {record['actor_1']}, Description: {record['description'][:80]}...")
            
            return {
                'action_required': True,
                'records_to_migrate': len(kidnapping_records),
                'total_victims_to_add': comparison_results['maria_total_kidnapped'],
                'priority': 'HIGH'
            }
        else:
            print("✅ No immediate migration required")
            return {
                'action_required': False,
                'priority': 'LOW'
            }
    
    def run_complete_analysis(self):
        """Run the complete data analysis workflow"""
        print("🔍 STARTING COMPREHENSIVE DATA ANALYSIS WORKFLOW")
        print("=" * 60)
        
        # Step 1: Parse MariaDB export
        maria_records = self.parse_maria_db_export()
        
        # Step 2: Analyze MariaDB data
        maria_all, maria_kidnapping, maria_deaths = self.analyze_maria_db_data(maria_records)
        
        # Step 3: Analyze PostgreSQL current state
        postgres_stats = self.analyze_postgres_current_state()
        
        # Step 4: Compare data sources
        comparison_results = self.compare_data_sources((maria_all, maria_kidnapping, maria_deaths), postgres_stats)
        
        # Step 5: Generate migration plan
        migration_plan = self.generate_migration_plan(comparison_results, maria_kidnapping)
        
        print("\n" + "=" * 60)
        print("📊 ANALYSIS COMPLETE")
        
        return {
            'maria_records': len(maria_all),
            'maria_kidnapping': len(maria_kidnapping),
            'postgres_kidnapping': postgres_stats['kidnapping_conflicts'],
            'migration_required': migration_plan['action_required'],
            'records_to_migrate': migration_plan.get('records_to_migrate', 0),
            'victims_to_add': migration_plan.get('total_victims_to_add', 0)
        }

if __name__ == "__main__":
    import sys
    workflow = DataAnalysisWorkflow()
    results = workflow.run_complete_analysis()
    
    print(f"\n🎯 SUMMARY:")
    print(f"   MariaDB records: {results['maria_records']}")
    print(f"   MariaDB kidnapping records: {results['maria_kidnapping']}")
    print(f"   PostgreSQL kidnapping records: {results['postgres_kidnapping']}")
    print(f"   Migration required: {results['migration_required']}")
    if results['migration_required']:
        print(f"   Records to migrate: {results['records_to_migrate']}")
        print(f"   Victims to add: {results['victims_to_add']}")
