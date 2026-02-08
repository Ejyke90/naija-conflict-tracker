#!/usr/bin/env python3
"""
Data Migration Script: conflict_events → conflicts (new schema)

This script migrates data from the old conflict_events table to the new
normalized schema with actors, conflict_types, regions, states, lgas, and conflicts tables.

Usage:
    python migrate_conflict_events_to_new_schema.py [--db-url DATABASE_URL] [--batch-size 100] [--dry-run]

Requirements:
    - Old schema: conflict_events table exists
    - New schema: neondb_postgres_schema.sql already executed
    - Reference tables populated: actors, conflict_types, regions, states, lgas
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import Dict, Optional, Tuple
import re

from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ConflictMigration:
    """Handles migration from conflict_events to new conflicts schema"""
    
    def __init__(self, database_url: str, batch_size: int = 100, dry_run: bool = False):
        self.database_url = database_url
        self.batch_size = batch_size
        self.dry_run = dry_run
        
        # Create engine and session
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,
            echo=False
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Cache for lookups (avoid repeated queries)
        self.actor_cache: Dict[str, int] = {}
        self.conflict_type_cache: Dict[str, int] = {}
        self.state_cache: Dict[str, int] = {}
        self.lga_cache: Dict[str, int] = {}
        self.region_cache: Dict[str, int] = {}
        
        # Statistics
        self.stats = {
            'total_old_records': 0,
            'migrated': 0,
            'skipped': 0,
            'errors': 0,
            'unmapped_states': set(),
            'unmapped_lgas': set(),
            'unmapped_actors': set(),
            'unmapped_conflict_types': set()
        }
    
    def load_reference_data(self, session: Session):
        """Load reference tables into memory for fast lookups"""
        logger.info("Loading reference data into cache...")
        
        # Load actors
        result = session.execute(text("SELECT id, LOWER(title) FROM actors"))
        for actor_id, title in result:
            self.actor_cache[title.lower()] = actor_id
        logger.info(f"  Loaded {len(self.actor_cache)} actors")
        
        # Load conflict types
        result = session.execute(text("SELECT id, LOWER(title) FROM conflict_types"))
        for type_id, title in result:
            self.conflict_type_cache[title.lower()] = type_id
        logger.info(f"  Loaded {len(self.conflict_type_cache)} conflict types")
        
        # Load states
        result = session.execute(text("SELECT id, LOWER(name), region_id FROM states"))
        for state_id, name, region_id in result:
            self.state_cache[name.lower()] = state_id
        logger.info(f"  Loaded {len(self.state_cache)} states")
        
        # Load LGAs
        result = session.execute(text("SELECT id, LOWER(name), state_id FROM lgas"))
        for lga_id, name, state_id in result:
            # Store with state context for disambiguation
            key = f"{name.lower()}_{state_id}"
            self.lga_cache[key] = lga_id
        logger.info(f"  Loaded {len(self.lga_cache)} LGAs")
        
        # Load regions
        result = session.execute(text("SELECT id, LOWER(name) FROM regions"))
        for region_id, name in result:
            self.region_cache[name.lower()] = region_id
        logger.info(f"  Loaded {len(self.region_cache)} regions")
    
    def normalize_text(self, text: Optional[str]) -> Optional[str]:
        """Normalize text for matching (lowercase, strip, remove extra spaces)"""
        if not text:
            return None
        return re.sub(r'\s+', ' ', text.strip().lower())
    
    def map_actor(self, actor_text: Optional[str]) -> Optional[int]:
        """Map actor text to actor ID"""
        if not actor_text:
            return None
        
        normalized = self.normalize_text(actor_text)
        
        # Direct match
        if normalized in self.actor_cache:
            return self.actor_cache[normalized]
        
        # Try fuzzy matching for common variations
        fuzzy_mappings = {
            'farmer': 'farmer(s)',
            'farmers': 'farmer(s)',
            'herder': 'herder(s)',
            'herders': 'herder(s)',
            'herdsmen': 'herder(s)',
            'fulani herdsmen': 'herder(s)',
            'bandits': 'bandits',
            'bandit': 'bandits',
            'gunmen': 'gunmen',
            'gunman': 'gunmen',
            'unknown gunmen': 'gunmen',
            'boko haram': 'boko haram',
            'iswap': 'iswap',
            'ipob': 'ipob/esn',
            'esn': 'ipob/esn',
            'security forces': 'security forces',
            'police': 'security forces',
            'army': 'security forces',
            'military': 'security forces',
            'soldiers': 'security forces',
            'civilian': 'civilian(s)',
            'civilians': 'civilian(s)',
            'cultists': 'cultists',
            'cult': 'cultists',
            'kidnappers': 'kidnappers',
            'kidnapper': 'kidnappers',
            'armed robbers': 'armed robber(s)',
            'robbers': 'armed robber(s)',
            'mob': 'mob',
            'protesters': 'protesters',
            'hoodlums': 'hoodlums',
        }
        
        if normalized in fuzzy_mappings:
            mapped = fuzzy_mappings[normalized]
            if mapped in self.actor_cache:
                return self.actor_cache[mapped]
        
        # Default to "N/A" if no match found
        self.stats['unmapped_actors'].add(actor_text)
        return self.actor_cache.get('n/a')
    
    def map_conflict_type(self, event_type: Optional[str], conflict_type: Optional[str]) -> Optional[int]:
        """Map event_type or conflict_type text to conflict_type ID"""
        # Try both fields
        for text in [conflict_type, event_type]:
            if not text:
                continue
            
            normalized = self.normalize_text(text)
            
            # Direct match
            if normalized in self.conflict_type_cache:
                return self.conflict_type_cache[normalized]
            
            # Fuzzy matching
            fuzzy_mappings = {
                'terrorism': 'terrorism',
                'terrorist': 'terrorism',
                'boko haram': 'terrorism',
                'iswap': 'terrorism',
                'banditry': 'banditry',
                'bandits': 'banditry',
                'farmer-herder': 'farmer-herder',
                'farmers-herders': 'farmer-herder',
                'herder-farmer': 'farmer-herder',
                'communal': 'communal',
                'communal clash': 'communal',
                'ethnic': 'communal',
                'kidnapping': 'kidnapping',
                'abduction': 'kidnapping',
                'cultism': 'cultism',
                'cult clash': 'cultism',
                'armed clash': 'armed clash',
                'gunfight': 'armed clash',
                'extrajudicial killing': 'extrajudicial killing',
                'police brutality': 'extrajudicial killing',
                'general': 'general',
                'other': 'general',
                'gang violence': 'gang violence',
                'maritime piracy': 'maritime piracy',
                'piracy': 'maritime piracy',
                'oil theft': 'oil theft',
                'pipeline': 'oil theft',
                'vigilante': 'vigilante',
            }
            
            if normalized in fuzzy_mappings:
                mapped = fuzzy_mappings[normalized]
                if mapped in self.conflict_type_cache:
                    return self.conflict_type_cache[mapped]
        
        # Default to "General" if no match
        self.stats['unmapped_conflict_types'].add(f"{event_type}/{conflict_type}")
        return self.conflict_type_cache.get('general')
    
    def map_state(self, state_text: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
        """Map state text to state_id and region_id"""
        if not state_text:
            return None, None
        
        normalized = self.normalize_text(state_text)
        
        # Direct match
        if normalized in self.state_cache:
            state_id = self.state_cache[normalized]
            # Get region_id from states table
            return state_id, self.get_region_for_state(state_id)
        
        # Try fuzzy matching for common variations
        fuzzy_mappings = {
            'federal capital territory': 'fct',
            'abuja': 'fct',
            'nasarawa': 'nasarawa',
            'niger': 'niger',
        }
        
        if normalized in fuzzy_mappings:
            mapped = fuzzy_mappings[normalized]
            if mapped in self.state_cache:
                state_id = self.state_cache[mapped]
                return state_id, self.get_region_for_state(state_id)
        
        self.stats['unmapped_states'].add(state_text)
        return None, None
    
    def get_region_for_state(self, state_id: int) -> Optional[int]:
        """Get region_id for a given state_id"""
        with self.SessionLocal() as session:
            result = session.execute(
                text("SELECT region_id FROM states WHERE id = :state_id"),
                {"state_id": state_id}
            ).fetchone()
            return result[0] if result else None
    
    def map_lga(self, lga_text: Optional[str], state_id: Optional[int]) -> Optional[int]:
        """Map LGA text to lga_id (using state context)"""
        if not lga_text or not state_id:
            return None
        
        normalized = self.normalize_text(lga_text)
        
        # Try with state context first
        key = f"{normalized}_{state_id}"
        if key in self.lga_cache:
            return self.lga_cache[key]
        
        # Try without state context (may match wrong LGA!)
        for cached_key, lga_id in self.lga_cache.items():
            if cached_key.startswith(f"{normalized}_"):
                logger.warning(f"LGA '{lga_text}' matched without state context")
                return lga_id
        
        self.stats['unmapped_lgas'].add(f"{lga_text} ({state_id})")
        return None
    
    def split_casualties(self, fatalities: int, injuries: int) -> Dict[str, int]:
        """
        Split casualties into gender-disaggregated fields.
        Since old schema doesn't have gender breakdown, we mark all as 'unknown'.
        """
        return {
            'civilian_death_male': 0,
            'civilian_death_female': 0,
            'civilian_death_unknown': fatalities,  # All go to 'unknown' gender
            'security_death_male': 0,
            'security_death_female': 0,
            'security_death_unknown': 0,  # We don't track security vs civilian in old schema
            'injured_male': 0,
            'injured_female': 0,
            'injured_unknown': injuries,
            'kidnapped_male': 0,
            'kidnapped_female': 0,
            'kidnapped_unknown': 0,
        }
    
    def migrate_record(self, session: Session, old_record: Dict) -> bool:
        """Migrate a single conflict_events record to new conflicts table"""
        try:
            # Map foreign keys
            state_id, region_id = self.map_state(old_record.get('state'))
            lga_id = self.map_lga(old_record.get('lga'), state_id)
            conflict_type_id = self.map_conflict_type(
                old_record.get('event_type'),
                old_record.get('conflict_type')
            )
            actor_1 = self.map_actor(old_record.get('actor1'))
            actor_2 = self.map_actor(old_record.get('actor2'))
            actor_3 = None  # Old schema doesn't have actor3
            
            # Split casualties
            casualties = self.split_casualties(
                old_record.get('fatalities', 0) or 0,
                old_record.get('injuries', 0) or 0
            )
            
            # Build INSERT query
            insert_sql = text("""
                INSERT INTO conflicts (
                    incidence_date,
                    conflict_type_id,
                    country_id,
                    region_id,
                    state_id,
                    lga_id,
                    community,
                    civilian_death_male,
                    civilian_death_female,
                    civilian_death_unknown,
                    security_death_male,
                    security_death_female,
                    security_death_unknown,
                    injured_male,
                    injured_female,
                    injured_unknown,
                    kidnapped_male,
                    kidnapped_female,
                    kidnapped_unknown,
                    displaced_persons,
                    displaced_male,
                    displaced_female,
                    actor_1,
                    actor_2,
                    actor_3,
                    description,
                    action,
                    confirmation_verification,
                    verification_level,
                    source_url,
                    source_metadata,
                    data_source,
                    created_at,
                    updated_at
                ) VALUES (
                    :incidence_date,
                    :conflict_type_id,
                    1, -- Nigeria
                    :region_id,
                    :state_id,
                    :lga_id,
                    :community,
                    :civilian_death_male,
                    :civilian_death_female,
                    :civilian_death_unknown,
                    :security_death_male,
                    :security_death_female,
                    :security_death_unknown,
                    :injured_male,
                    :injured_female,
                    :injured_unknown,
                    :kidnapped_male,
                    :kidnapped_female,
                    :kidnapped_unknown,
                    :displaced_persons,
                    :displaced_male,
                    :displaced_female,
                    :actor_1,
                    :actor_2,
                    :actor_3,
                    :description,
                    :action,
                    :confirmation_verification,
                    :verification_level,
                    :source_url,
                    :source_metadata,
                    :data_source,
                    :created_at,
                    :updated_at
                )
            """)
            
            # Prepare data
            data = {
                'incidence_date': old_record.get('event_date'),
                'conflict_type_id': conflict_type_id,
                'region_id': region_id,
                'state_id': state_id,
                'lga_id': lga_id,
                'community': old_record.get('location'),
                **casualties,
                'displaced_persons': 'Yes' if (old_record.get('displaced_persons', 0) or 0) > 0 else 'No',
                'displaced_male': 0,
                'displaced_female': old_record.get('displaced_persons', 0) or 0,
                'actor_1': actor_1,
                'actor_2': actor_2,
                'actor_3': actor_3,
                'description': old_record.get('notes'),
                'action': old_record.get('event_category'),
                'confirmation_verification': 'Verified' if old_record.get('verified') else 'Unverified',
                'verification_level': old_record.get('confidence_level'),
                'source_url': old_record.get('source'),
                'source_metadata': f"Migrated from conflict_events (ID: {old_record.get('id')})",
                'data_source': 'Legacy Migration',
                'created_at': old_record.get('created_at', datetime.utcnow()),
                'updated_at': datetime.utcnow()
            }
            
            if not self.dry_run:
                session.execute(insert_sql, data)
            
            self.stats['migrated'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error migrating record {old_record.get('id')}: {e}")
            self.stats['errors'] += 1
            return False
    
    def run(self):
        """Execute the migration"""
        logger.info("=" * 80)
        logger.info("Starting migration: conflict_events → conflicts")
        logger.info(f"Database: {self.database_url.split('@')[1] if '@' in self.database_url else 'local'}")
        logger.info(f"Batch size: {self.batch_size}")
        logger.info(f"Dry run: {self.dry_run}")
        logger.info("=" * 80)
        
        try:
            with self.SessionLocal() as session:
                # Check if tables exist
                logger.info("Checking table existence...")
                old_table_exists = session.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'conflict_events')"
                )).scalar()
                new_table_exists = session.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'conflicts')"
                )).scalar()
                
                if not old_table_exists:
                    logger.error("❌ Old table 'conflict_events' not found!")
                    return False
                
                if not new_table_exists:
                    logger.error("❌ New table 'conflicts' not found! Run neondb_postgres_schema.sql first.")
                    return False
                
                logger.info("✅ Both tables exist")
                
                # Load reference data
                self.load_reference_data(session)
                
                # Count old records
                count_result = session.execute(text("SELECT COUNT(*) FROM conflict_events"))
                self.stats['total_old_records'] = count_result.scalar()
                logger.info(f"\nTotal records to migrate: {self.stats['total_old_records']}")
                
                # Fetch old records in batches
                offset = 0
                while True:
                    logger.info(f"\nProcessing batch: {offset} - {offset + self.batch_size}")
                    
                    # Fetch batch
                    batch_sql = text(f"""
                        SELECT * FROM conflict_events
                        ORDER BY event_date
                        LIMIT :limit OFFSET :offset
                    """)
                    
                    result = session.execute(batch_sql, {
                        'limit': self.batch_size,
                        'offset': offset
                    })
                    
                    records = [dict(row._mapping) for row in result]
                    
                    if not records:
                        break
                    
                    # Migrate each record
                    for record in records:
                        self.migrate_record(session, record)
                    
                    # Commit batch
                    if not self.dry_run:
                        session.commit()
                        logger.info(f"  ✅ Committed {len(records)} records")
                    else:
                        logger.info(f"  🔍 DRY RUN: Would migrate {len(records)} records")
                    
                    offset += self.batch_size
                    
                    # Progress update
                    progress = (self.stats['migrated'] / self.stats['total_old_records']) * 100
                    logger.info(f"  Progress: {progress:.1f}% ({self.stats['migrated']}/{self.stats['total_old_records']})")
                
                # Final statistics
                logger.info("\n" + "=" * 80)
                logger.info("MIGRATION COMPLETE")
                logger.info("=" * 80)
                logger.info(f"Total old records: {self.stats['total_old_records']}")
                logger.info(f"Successfully migrated: {self.stats['migrated']}")
                logger.info(f"Skipped: {self.stats['skipped']}")
                logger.info(f"Errors: {self.stats['errors']}")
                
                if self.stats['unmapped_states']:
                    logger.warning(f"\n⚠️  Unmapped states ({len(self.stats['unmapped_states'])}):")
                    for state in sorted(self.stats['unmapped_states']):
                        logger.warning(f"  - {state}")
                
                if self.stats['unmapped_lgas']:
                    logger.warning(f"\n⚠️  Unmapped LGAs ({len(self.stats['unmapped_lgas'])}):")
                    for lga in sorted(list(self.stats['unmapped_lgas'])[:10]):  # First 10
                        logger.warning(f"  - {lga}")
                    if len(self.stats['unmapped_lgas']) > 10:
                        logger.warning(f"  ... and {len(self.stats['unmapped_lgas']) - 10} more")
                
                if self.stats['unmapped_actors']:
                    logger.warning(f"\n⚠️  Unmapped actors ({len(self.stats['unmapped_actors'])}):")
                    for actor in sorted(list(self.stats['unmapped_actors'])[:10]):
                        logger.warning(f"  - {actor}")
                    if len(self.stats['unmapped_actors']) > 10:
                        logger.warning(f"  ... and {len(self.stats['unmapped_actors']) - 10} more")
                
                logger.info("\n✅ Migration completed successfully!" if self.stats['errors'] == 0 else "\n⚠️  Migration completed with errors")
                return self.stats['errors'] == 0
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Database error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    parser = argparse.ArgumentParser(description='Migrate conflict_events to new conflicts schema')
    parser.add_argument(
        '--db-url',
        type=str,
        help='Database URL (defaults to NEON_DATABASE_URL env var)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Number of records to process per batch (default: 100)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without committing changes (for testing)'
    )
    
    args = parser.parse_args()
    
    # Get database URL
    import os
    database_url = args.db_url or os.getenv('NEON_DATABASE_URL') or os.getenv('DATABASE_URL')
    
    if not database_url:
        logger.error("❌ No database URL provided. Use --db-url or set DATABASE_URL env var.")
        sys.exit(1)
    
    # Run migration
    migrator = ConflictMigration(
        database_url=database_url,
        batch_size=args.batch_size,
        dry_run=args.dry_run
    )
    
    success = migrator.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
