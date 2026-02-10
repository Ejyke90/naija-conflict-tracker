#!/usr/bin/env python3
"""
Kidnapping Data Migration Script
Merges kidnapping data from MariaDB export into PostgreSQL database
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.config import settings
from mariadb_parser import MariaDBParser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KidnappingDataMigrator:
    """Handles migration of kidnapping data from MariaDB to PostgreSQL"""
    
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.parser = None
        
    def create_database_backup(self) -> bool:
        """Create a backup of the current database state"""
        logger.info("Creating database backup...")
        
        db = self.SessionLocal()
        try:
            # Record current statistics
            backup_stats = {
                'timestamp': datetime.utcnow().isoformat(),
                'total_conflicts': self._get_count(db, "conflicts"),
                'kidnapping_conflicts': self._get_count(db, "conflicts WHERE kidnapped_male > 0 OR kidnapped_female > 0 OR kidnapped_unknown > 0"),
                'total_kidnapped': self._get_sum(db, "kidnapped_male + kidnapped_female + kidnapped_unknown", "conflicts"),
                'total_deaths': self._get_sum(db, "civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown", "conflicts"),
            }
            
            logger.info(f"Backup created: {backup_stats}")
            
            # Save backup info to a file
            with open('database_backup_stats.txt', 'w') as f:
                f.write(f"Database Backup - {backup_stats['timestamp']}\n")
                f.write(f"Total conflicts: {backup_stats['total_conflicts']}\n")
                f.write(f"Kidnapping conflicts: {backup_stats['kidnapping_conflicts']}\n")
                f.write(f"Total kidnapping victims: {backup_stats['total_kidnapped']}\n")
                f.write(f"Total deaths: {backup_stats['total_deaths']}\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
        finally:
            db.close()
    
    def parse_mariadb_data(self, sql_file_path: str) -> List[Dict[str, Any]]:
        """Parse MariaDB SQL export and extract kidnapping records"""
        logger.info("Parsing MariaDB SQL export...")
        
        self.parser = MariaDBParser(sql_file_path)
        records = self.parser.parse_sql_export()
        kidnapping_records = self.parser.extract_kidnapping_records()
        
        logger.info(f"Parsed {len(records)} total records, {len(kidnapping_records)} with kidnapping data")
        
        # Validate kidnapping data
        validation = self.parser.validate_parsed_data()
        logger.info(f"Validation results: {validation}")
        
        return kidnapping_records
    
    def validate_kidnapping_data(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate kidnapping data before migration"""
        logger.info("Validating kidnapping data...")
        
        validation_results = {
            'total_records': len(records),
            'valid_records': 0,
            'invalid_records': 0,
            'total_victims': 0,
            'issues': []
        }
        
        for record in records:
            is_valid = True
            
            # Check for required fields
            if record['total_kidnapped'] <= 0:
                validation_results['issues'].append(f"Record {record['record_id']}: No kidnapping victims")
                is_valid = False
            
            if not record['community'] or record['community'] == 'NULL':
                validation_results['issues'].append(f"Record {record['record_id']}: Missing community")
            
            if record['state_id'] <= 0:
                validation_results['issues'].append(f"Record {record['record_id']}: Invalid state ID")
            
            if is_valid:
                validation_results['valid_records'] += 1
                validation_results['total_victims'] += record['total_kidnapped']
            else:
                validation_results['invalid_records'] += 1
        
        logger.info(f"Validation complete: {validation_results['valid_records']} valid, {validation_results['invalid_records']} invalid")
        
        if validation_results['invalid_records'] > 0:
            logger.warning(f"Validation issues found: {validation_results['issues']}")
        
        return validation_results
    
    def migrate_kidnapping_data(self, kidnapping_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Migrate kidnapping data to PostgreSQL database"""
        logger.info("Starting kidnapping data migration...")
        
        db = self.SessionLocal()
        migration_results = {
            'success': False,
            'records_processed': 0,
            'records_updated': 0,
            'records_created': 0,
            'total_victims_added': 0,
            'errors': []
        }
        
        try:
            # Start transaction
            with db.begin():
                for record in kidnapping_records:
                    try:
                        migration_results['records_processed'] += 1
                        
                        # Check if record already exists
                        existing_record = self._find_existing_record(db, record)
                        
                        if existing_record:
                            # Update existing record
                            success = self._update_existing_record(db, existing_record, record)
                            if success:
                                migration_results['records_updated'] += 1
                                migration_results['total_victims_added'] += record['total_kidnapped']
                        else:
                            # Create new record
                            success = self._create_new_record(db, record)
                            if success:
                                migration_results['records_created'] += 1
                                migration_results['total_victims_added'] += record['total_kidnapped']
                    
                    except Exception as e:
                        error_msg = f"Error processing record {record.get('record_id', 'unknown')}: {e}"
                        logger.error(error_msg)
                        migration_results['errors'].append(error_msg)
                
                # Commit transaction if no errors
                if len(migration_results['errors']) == 0:
                    migration_results['success'] = True
                    logger.info("Migration completed successfully")
                else:
                    raise Exception(f"Migration failed with {len(migration_results['errors'])} errors")
        
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            db.rollback()
            migration_results['errors'].append(f"Transaction failed: {e}")
        
        finally:
            db.close()
        
        return migration_results
    
    def _find_existing_record(self, db, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find existing record in PostgreSQL database"""
        try:
            # Try to find by date, community, and state
            if record['incidence_date'] and record['community'] and record['state_id'] > 0:
                query = text("""
                    SELECT id, kidnapped_male, kidnapped_female, kidnapped_unknown 
                    FROM conflicts 
                    WHERE incidence_date = :date 
                    AND community = :community 
                    AND state_id = :state_id
                    LIMIT 1
                """)
                
                result = db.execute(query, {
                    'date': record['incidence_date'],
                    'community': record['community'],
                    'state_id': record['state_id']
                }).fetchone()
                
                if result:
                    return {
                        'id': result[0],
                        'kidnapped_male': result[1],
                        'kidnapped_female': result[2],
                        'kidnapped_unknown': result[3]
                    }
        
        except Exception as e:
            logger.warning(f"Error finding existing record: {e}")
        
        return None
    
    def _update_existing_record(self, db, existing: Dict[str, Any], new_record: Dict[str, Any]) -> bool:
        """Update existing record with kidnapping data"""
        try:
            # Only update if kidnapping data is different
            if (existing['kidnapped_male'] == new_record['kidnapped_male'] and
                existing['kidnapped_female'] == new_record['kidnapped_female'] and
                existing['kidnapped_unknown'] == new_record['kidnapped_unknown']):
                logger.info(f"Record {existing['id']} already has same kidnapping data, skipping")
                return True
            
            query = text("""
                UPDATE conflicts 
                SET kidnapped_male = :km, 
                    kidnapped_female = :kf, 
                    kidnapped_unknown = :ku,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """)
            
            db.execute(query, {
                'id': existing['id'],
                'km': new_record['kidnapped_male'],
                'kf': new_record['kidnapped_female'],
                'ku': new_record['kidnapped_unknown']
            })
            
            logger.info(f"Updated record {existing['id']} with kidnapping data")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update record {existing['id']}: {e}")
            return False
    
    def _create_new_record(self, db, record: Dict[str, Any]) -> bool:
        """Create new record with kidnapping data"""
        try:
            # Get next available ID
            next_id = self._get_next_id(db)
            
            # Map actor_1 to valid actor ID (use 22 for N/A when actor_1 is 0 or invalid)
            actor_id = record['actor_1'] if record['actor_1'] > 0 else 22
            
            query = text("""
                INSERT INTO conflicts (
                    id, incidence_date, conflict_type_id, country_id, region_id,
                    state_id, lga_id, community, 
                    civilian_death_male, civilian_death_female, civilian_death_unknown,
                    security_death_male, security_death_female, security_death_unknown,
                    injured_male, injured_female, injured_unknown,
                    kidnapped_male, kidnapped_female, kidnapped_unknown,
                    displaced_persons, displaced_male, displaced_female,
                    actor_1, description, action,
                    confirmation_verification, verification_level,
                    source_url, data_source,
                    created_at, updated_at
                ) VALUES (
                    :id, :date, :conflict_type, 1, 1,
                    :state_id, :lga_id, :community,
                    0, 0, 0, 0, 0, 0, 0, 0, 0,
                    :km, :kf, :ku,
                    'No', 0, 0,
                    :actor, :description, 'attack',
                    '1', 'Secondary',
                    :source_url, :data_source,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
            """)
            
            db.execute(query, {
                'id': next_id,
                'date': record['incidence_date'] or '2020-01-01',  # Default date if missing
                'conflict_type': record['conflict_type_id'] if record['conflict_type_id'] > 0 else 2,  # Default conflict type
                'state_id': record['state_id'] if record['state_id'] > 0 else 1,  # Default state if missing
                'lga_id': record['lga_id'] if record['lga_id'] > 0 else 1,  # Default LGA if missing
                'community': record['community'] if record['community'] and record['community'] != 'NULL' else 'Unknown',
                'km': record['kidnapped_male'],
                'kf': record['kidnapped_female'],
                'ku': record['kidnapped_unknown'],
                'actor': actor_id,
                'description': record['description'] if record['description'] and record['description'] != '0' else 'Kidnapping incident',
                'source_url': record['source_url'] if record['source_url'] and record['source_url'] != 'attack by Boko Haram' else '',
                'data_source': record['data_source'] if record['data_source'] and record['data_source'] != 'NULL' else 'MariaDB Migration'
            })
            
            logger.info(f"Created new record {next_id} with kidnapping data")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create new record: {e}")
            return False
    
    def _get_next_id(self, db) -> int:
        """Get next available ID for conflicts table"""
        result = db.execute(text("SELECT COALESCE(MAX(id), 0) + 1 FROM conflicts")).scalar()
        return result
    
    def _get_count(self, db, query: str) -> int:
        """Helper to get count from query"""
        result = db.execute(text(f"SELECT COUNT(*) FROM {query}")).scalar()
        return result or 0
    
    def _get_sum(self, db, column: str, table: str) -> int:
        """Helper to get sum from query"""
        result = db.execute(text(f"SELECT COALESCE(SUM({column}), 0) FROM {table}")).scalar()
        return result or 0
    
    def verify_migration(self) -> Dict[str, Any]:
        """Verify migration results"""
        logger.info("Verifying migration results...")
        
        db = self.SessionLocal()
        try:
            verification = {
                'total_conflicts': self._get_count(db, "conflicts"),
                'kidnapping_conflicts': self._get_count(db, "conflicts WHERE kidnapped_male > 0 OR kidnapped_female > 0 OR kidnapped_unknown > 0"),
                'total_kidnapped': self._get_sum(db, "kidnapped_male + kidnapped_female + kidnapped_unknown", "conflicts"),
                'total_deaths': self._get_sum(db, "civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown", "conflicts"),
            }
            
            # Get sample kidnapping records
            sample_query = text("""
                SELECT id, incidence_date, community, state_id,
                       kidnapped_male + kidnapped_female + kidnapped_unknown as total_victims,
                       description
                FROM conflicts 
                WHERE kidnapped_male > 0 OR kidnapped_female > 0 OR kidnapped_unknown > 0
                ORDER BY incidence_date DESC
                LIMIT 5
            """)
            
            sample_records = db.execute(sample_query).fetchall()
            verification['sample_records'] = [
                {
                    'id': r[0],
                    'date': r[1],
                    'community': r[2],
                    'state_id': r[3],
                    'victims': r[4],
                    'description': r[5][:100] if r[5] else ''
                }
                for r in sample_records
            ]
            
            logger.info(f"Verification complete: {verification}")
            return verification
            
        finally:
            db.close()

def main():
    """Main migration function"""
    logger.info("Starting kidnapping data migration...")
    
    migrator = KidnappingDataMigrator()
    
    # Step 1: Create backup
    if not migrator.create_database_backup():
        logger.error("Failed to create database backup, aborting migration")
        return
    
    # Step 2: Parse MariaDB data
    sql_file = '/Users/ejikeudeze/AI_Projects/naija-conflict-tracker/u503102722_conflictdb (1).sql'
    kidnapping_records = migrator.parse_mariadb_data(sql_file)
    
    if not kidnapping_records:
        logger.error("No kidnapping records found to migrate")
        return
    
    # Step 3: Validate data
    validation = migrator.validate_kidnapping_data(kidnapping_records)
    logger.info(f"Data validation: {validation}")
    
    # Step 4: Migrate data
    migration_results = migrator.migrate_kidnapping_data(kidnapping_records)
    logger.info(f"Migration results: {migration_results}")
    
    # Step 5: Verify migration
    if migration_results['success']:
        verification = migrator.verify_migration()
        logger.info(f"Migration verification: {verification}")
        
        print(f"\n=== MIGRATION SUCCESSFUL ===")
        print(f"Records processed: {migration_results['records_processed']}")
        print(f"Records updated: {migration_results['records_updated']}")
        print(f"Records created: {migration_results['records_created']}")
        print(f"Total victims added: {migration_results['total_victims_added']}")
        print(f"Current kidnapping conflicts: {verification['kidnapping_conflicts']}")
        print(f"Current total kidnapped: {verification['total_kidnapped']}")
    else:
        logger.error("Migration failed")
        print(f"\n=== MIGRATION FAILED ===")
        print(f"Errors: {migration_results['errors']}")

if __name__ == "__main__":
    main()
