"""
ETL Service for migrating conflict_events to normalized conflicts schema

This service handles the migration of data from the legacy conflict_events table
to the new normalized conflicts table with proper foreign key relationships.
"""

from datetime import datetime
from typing import Generator, Optional, Dict, Tuple
import logging
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class SchemaMigrationService:
    """
    Service for migrating conflict data from legacy schema to normalized schema.
    
    The migration is idempotent - can be run multiple times without creating duplicates.
    It maps text fields from conflict_events to foreign keys in the new conflicts table.
    """

    def __init__(self, db_session: Session):
        """
        Initialize migration service with database session.
        
        Args:
            db_session: SQLAlchemy sync session for database operations
        """
        self.db = db_session
        self.batch_size = 1000
        self.total_processed = 0
        self.total_failed = 0
        self.failed_rows: list[Dict] = []

    def get_migration_status(self) -> Dict:
        """
        Get current migration status.
        
        Returns:
            Dict with migration counts and statistics
        """
        # Count total conflict_events
        result = self.db.execute(text("SELECT COUNT(*) FROM conflict_events"))
        total_events = result.scalar() or 0

        # Count migrated conflicts
        result = self.db.execute(text("SELECT COUNT(*) FROM conflicts"))
        migrated_count = result.scalar() or 0

        return {
            "total_events": total_events,
            "migrated_count": migrated_count,
            "remaining": total_events - migrated_count,
            "status": "completed" if (total_events == migrated_count and total_events > 0) else "pending",
            "percentage": (migrated_count / total_events * 100) if total_events > 0 else 0,
        }

    def migrate_conflict_events_to_conflicts(
        self,
        batch_size: Optional[int] = None,
        dry_run: bool = False
    ) -> Generator[Dict, None, None]:
        """
        Migrate conflict_events to conflicts table with proper foreign keys.
        
        This generator yields progress updates as it processes batches.
        The migration is idempotent - if a record with matching event_date,
        state_id, and conflict_type_id exists, it skips that record.
        
        Args:
            batch_size: Number of records to process per batch (default: 1000)
            dry_run: If True, don't actually write to database (just validate)
            
        Yields:
            Dict with migration progress: {status, processed, failed, total, message}
        """
        # Initialize these at method level to prevent UnboundLocalError in except handler
        total_processed = 0
        total_failed = 0
        
        if batch_size:
            self.batch_size = batch_size

        try:
            # Get total count of conflict_events not yet migrated
            query = text("""
                SELECT COUNT(*) FROM conflict_events ce
                WHERE NOT EXISTS (
                    SELECT 1 FROM conflicts c
                    WHERE c.incidence_date = ce.event_date
                    AND c.state_id = (SELECT id FROM states WHERE LOWER(name) = LOWER(ce.state))
                )
            """)
            result = self.db.execute(query)
            total_remaining = result.scalar() or 0

            if total_remaining == 0:
                yield {
                    "status": "completed",
                    "message": "All conflict_events have been migrated",
                    "processed": 0,
                    "failed": 0,
                    "total": 0,
                }
                return

            offset = 0

            while offset < total_remaining:
                # Fetch batch of unmigrated events
                batch_query = text("""
                    SELECT ce.id, ce.event_date, ce.state, ce.lga, 
                           ce.conflict_type, ce.actor1, ce.actor2,
                           ce.fatalities, ce.injuries, ce.displaced_persons,
                           ce.properties_destroyed, ce.location, ce.latitude, ce.longitude,
                           ce.source, ce.notes, ce.verified, ce.event_type,
                           ce.actor1_type, ce.actor2_type, ce.confidence_level
                    FROM conflict_events ce
                    WHERE NOT EXISTS (
                        SELECT 1 FROM conflicts c
                        WHERE c.incidence_date = ce.event_date
                        AND c.state_id = (SELECT id FROM states WHERE LOWER(name) = LOWER(ce.state))
                    )
                    ORDER BY ce.event_date ASC
                    LIMIT :batch_size OFFSET :offset
                """)
                
                result = self.db.execute(
                    batch_query,
                    {"batch_size": self.batch_size, "offset": offset}
                )
                rows = result.fetchall()

                if not rows:
                    break

                # Process each row in batch
                batch_processed = 0
                batch_failed = 0

                for row in rows:
                    try:
                        # Resolve foreign keys
                        state_id = self._resolve_state_id(row.state)
                        lga_id = self._resolve_lga_id(row.lga, state_id) if row.lga else None
                        conflict_type_id = self._resolve_conflict_type_id(row.conflict_type)
                        actor_1_id = self._resolve_actor_id(row.actor1) if row.actor1 else None
                        actor_2_id = self._resolve_actor_id(row.actor2) if row.actor2 else None

                        if state_id is None:
                            total_failed += 1
                            batch_failed += 1
                            self.failed_rows.append({
                                "event_id": str(row.id),
                                "reason": f"State not found: {row.state}",
                            })
                            continue

                        # Build INSERT query for conflicts table
                        insert_query = text("""
                            INSERT INTO conflicts (
                                incidence_date, state_id, lga_id, conflict_type_id,
                                actor_1, actor_2,
                                civilian_death_unknown, injured_unknown,
                                displaced_persons, properties_destroyed,
                                community, latitude, longitude,
                                source_url, description, data_source,
                                verification_level, created_at, updated_at
                            ) VALUES (
                                :incidence_date, :state_id, :lga_id, :conflict_type_id,
                                :actor_1, :actor_2,
                                :fatalities, :injuries,
                                :displaced_persons, :properties_destroyed,
                                :location, :latitude, :longitude,
                                :source, :description, :data_source,
                                :verification_level, :created_at, :updated_at
                            )
                            ON CONFLICT DO NOTHING
                        """)

                        if not dry_run:
                            self.db.execute(
                                insert_query,
                                {
                                    "incidence_date": row.event_date,
                                    "state_id": state_id,
                                    "lga_id": lga_id,
                                    "conflict_type_id": conflict_type_id,
                                    "actor_1": actor_1_id,
                                    "actor_2": actor_2_id,
                                    "fatalities": row.fatalities or 0,
                                    "injuries": row.injuries or 0,
                                    "displaced_persons": str(row.displaced_persons) if row.displaced_persons else None,
                                    "properties_destroyed": row.properties_destroyed or 0,
                                    "location": row.location,
                                    "latitude": row.latitude,
                                    "longitude": row.longitude,
                                    "source": row.source,
                                    "description": row.notes,
                                    "data_source": row.event_type,
                                    "verification_level": row.confidence_level,
                                    "created_at": datetime.utcnow(),
                                    "updated_at": datetime.utcnow(),
                                }
                            )

                        total_processed += 1
                        batch_processed += 1

                    except Exception as e:
                        total_failed += 1
                        batch_failed += 1
                        self.failed_rows.append({
                            "event_id": str(row.id),
                            "reason": str(e),
                        })
                        logger.error(f"Failed to migrate event {row.id}: {e}")

                # Commit batch
                if not dry_run:
                    self.db.commit()

                offset += self.batch_size

                # Yield progress
                yield {
                    "status": "migrating",
                    "processed": total_processed,
                    "failed": total_failed,
                    "total": total_remaining,
                    "batch_processed": batch_processed,
                    "batch_failed": batch_failed,
                    "percentage": (total_processed / total_remaining * 100) if total_remaining > 0 else 0,
                    "message": f"Processed {batch_processed} records, failed {batch_failed}",
                }

            # Final status
            yield {
                "status": "completed",
                "processed": total_processed,
                "failed": total_failed,
                "total": total_remaining,
                "percentage": 100.0,
                "message": f"Migration complete: {total_processed} migrated, {total_failed} failed",
                "failed_records": self.failed_rows if self.failed_rows else None,
            }

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            yield {
                "status": "error",
                "message": str(e),
                "processed": total_processed,
                "failed": total_failed,
            }

    def verify_migration(self) -> Dict:
        """
        Verify migration completed successfully.
        
        Returns:
            Dict with verification results
        """
        # Compare row counts
        result = self.db.execute(text("SELECT COUNT(*) FROM conflict_events"))
        events_count = result.scalar() or 0

        result = self.db.execute(text("SELECT COUNT(*) FROM conflicts"))
        conflicts_count = result.scalar() or 0

        # Check for null state_ids (indicates failed foreign key resolution)
        result = self.db.execute(
            text("SELECT COUNT(*) FROM conflicts WHERE state_id IS NULL")
        )
        null_state_ids = result.scalar() or 0

        return {
            "total_source_events": events_count,
            "total_migrated": conflicts_count,
            "match": events_count == conflicts_count,
            "null_foreign_keys": null_state_ids,
            "status": "verified" if events_count == conflicts_count and null_state_ids == 0 else "failed",
            "message": (
                "Migration verified successfully"
                if events_count == conflicts_count and null_state_ids == 0
                else f"Verification failed: {events_count} events, {conflicts_count} conflicts, {null_state_ids} null state_ids"
            ),
        }

    # Private helper methods for foreign key resolution

    def _resolve_state_id(self, state_name: str) -> Optional[int]:
        """
        Resolve state name to state_id from states table.
        
        Args:
            state_name: Name of the state
            
        Returns:
            state_id or None if not found
        """
        if not state_name:
            return None

        query = text("""
            SELECT id FROM states 
            WHERE LOWER(name) = LOWER(:state_name)
            LIMIT 1
        """)
        result = self.db.execute(query, {"state_name": state_name.strip()})
        row = result.fetchone()
        return row[0] if row else None

    def _resolve_lga_id(self, lga_name: str, state_id: int) -> Optional[int]:
        """
        Resolve LGA name to lga_id from lgas table.
        
        Args:
            lga_name: Name of the LGA
            state_id: ID of the state (for lga/state matching)
            
        Returns:
            lga_id or None if not found
        """
        if not lga_name or not state_id:
            return None

        query = text("""
            SELECT id FROM lgas 
            WHERE state_id = :state_id 
            AND LOWER(name) = LOWER(:lga_name)
            LIMIT 1
        """)
        result = self.db.execute(
            query,
            {"state_id": state_id, "lga_name": lga_name.strip()}
        )
        row = result.fetchone()
        return row[0] if row else None

    def _resolve_conflict_type_id(self, conflict_type_name: str) -> Optional[int]:
        """
        Resolve conflict type name to conflict_type_id.
        Creates a new record if type doesn't exist.
        
        Args:
            conflict_type_name: Name of the conflict type
            
        Returns:
            conflict_type_id
        """
        if not conflict_type_name:
            return None

        # Try to find existing
        query = text("""
            SELECT id FROM conflict_types
            WHERE LOWER(title) = LOWER(:type_name)
            LIMIT 1
        """)
        result = self.db.execute(query, {"type_name": conflict_type_name.strip()})
        row = result.fetchone()
        
        if row:
            return row[0]

        # Create new if doesn't exist
        insert_query = text("""
            INSERT INTO conflict_types (title, created_at, updated_at)
            VALUES (:title, :created_at, :updated_at)
            RETURNING id
        """)
        result = self.db.execute(
            insert_query,
            {
                "title": conflict_type_name.strip(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )
        row = result.fetchone()
        return row[0] if row else None

    def _resolve_actor_id(self, actor_name: str) -> Optional[int]:
        """
        Resolve actor name to actor_id.
        Creates a new record if actor doesn't exist.
        
        Args:
            actor_name: Name of the actor
            
        Returns:
            actor_id
        """
        if not actor_name:
            return None

        # Try to find existing
        query = text("""
            SELECT id FROM actors
            WHERE LOWER(title) = LOWER(:actor_name)
            LIMIT 1
        """)
        result = self.db.execute(query, {"actor_name": actor_name.strip()})
        row = result.fetchone()
        
        if row:
            return row[0]

        # Create new if doesn't exist
        insert_query = text("""
            INSERT INTO actors (title, created_at, updated_at)
            VALUES (:title, :created_at, :updated_at)
            RETURNING id
        """)
        result = self.db.execute(
            insert_query,
            {
                "title": actor_name.strip(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )
        row = result.fetchone()
        return row[0] if row else None
