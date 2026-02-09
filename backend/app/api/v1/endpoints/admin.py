"""
Admin API Endpoints

Provides API endpoints for administrative tasks like schema migrations.
Protected endpoints for internal use only.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, AsyncGenerator
import json
import logging
from datetime import datetime

from app.db.database import get_db
from app.services.schema_migration_service import SchemaMigrationService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/migrate-schema")
async def migrate_schema(
    db: AsyncSession = Depends(get_db),
    batch_size: Optional[int] = Query(1000, ge=100, le=10000),
    dry_run: bool = Query(False),
) -> StreamingResponse:
    """
    Migrate conflict_events to conflicts table with proper foreign keys.
    
    This endpoint starts a schema migration that transforms data from the legacy
    conflict_events table to the new normalized conflicts schema with proper
    foreign key relationships to states, LGAs, conflict types, and actors.
    
    The migration is idempotent - can be safely called multiple times without
    creating duplicate records.
    
    Query Parameters:
    - batch_size: Records to process per batch (100-10000, default: 1000)
    - dry_run: If true, validate but don't write to database (default: false)
    
    Response:
    - Streaming JSON with progress updates for each batch
    - Final status with counts of migrated vs failed records
    
    Example:
    ```
    curl -X POST http://localhost:8000/api/v1/admin/migrate-schema
    
    # With options
    curl -X POST "http://localhost:8000/api/v1/admin/migrate-schema?batch_size=5000&dry_run=false"
    ```
    """
    try:
        service = SchemaMigrationService(db)
        
        # Define streaming response generator
        async def event_generator() -> AsyncGenerator[str, None]:
            try:
                async for progress in service.migrate_conflict_events_to_conflicts(
                    batch_size=batch_size,
                    dry_run=dry_run
                ):
                    # Add timestamp to progress update
                    progress["timestamp"] = datetime.utcnow().isoformat()
                    yield json.dumps(progress) + "\n"
                    
            except Exception as e:
                logger.error(f"Migration error: {e}")
                yield json.dumps({
                    "status": "error",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }) + "\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="application/x-ndjson",
            headers={
                "Content-Disposition": "inline",
                "X-Accel-Buffering": "no",  # Disable buffering for streaming
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to start migration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/migration-status")
async def get_migration_status(db: AsyncSession = Depends(get_db)):
    """
    Get current migration status.
    
    Shows counts of:
    - total_events: Total conflicts in conflict_events table
    - migrated_count: Conflicts successfully migrated to conflicts table
    - remaining: Not yet migrated
    - percentage: Completion percentage
    - status: 'pending', 'in progress', or 'completed'
    
    Response:
    ```json
    {
        "total_events": 10000,
        "migrated_count": 8500,
        "remaining": 1500,
        "percentage": 85.0,
        "status": "pending",
        "timestamp": "2026-02-09T15:30:00"
    }
    ```
    """
    try:
        service = SchemaMigrationService(db)
        status = await service.get_migration_status()
        status["timestamp"] = datetime.utcnow().isoformat()
        return status
        
    except Exception as e:
        logger.error(f"Failed to get migration status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-migration")
async def verify_migration(db: AsyncSession = Depends(get_db)):
    """
    Verify migration completed successfully.
    
    Checks:
    - Row count match between conflict_events and conflicts
    - No null state_ids (indicates unresolved foreign keys)
    
    Response:
    ```json
    {
        "total_source_events": 10000,
        "total_migrated": 10000,
        "match": true,
        "null_foreign_keys": 0,
        "status": "verified",
        "message": "Migration verified successfully",
        "timestamp": "2026-02-09T15:30:00"
    }
    ```
    """
    try:
        service = SchemaMigrationService(db)
        result = await service.verify_migration()
        result["timestamp"] = datetime.utcnow().isoformat()
        return result
        
    except Exception as e:
        logger.error(f"Failed to verify migration: {e}")
        raise HTTPException(status_code=500, detail=str(e))
