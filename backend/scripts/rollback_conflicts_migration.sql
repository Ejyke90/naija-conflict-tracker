-- Rollback script: restore old conflict_events table and drop new conflicts
-- Use only if migration causes issues in production.

BEGIN;

-- Rename archive back if needed
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'conflict_events_archive_20260208'
    ) THEN
        IF EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'conflict_events'
        ) THEN
            RAISE NOTICE 'Dropping current conflicts_events to restore archive';
            DROP TABLE conflict_events;
        END IF;
        ALTER TABLE conflict_events_archive_20260208 RENAME TO conflict_events;
    END IF;
END $$;

-- Drop new tables (order matters because of FKs)
DROP TABLE IF EXISTS conflicts CASCADE;
DROP TABLE IF EXISTS actors CASCADE;
DROP TABLE IF EXISTS conflict_types CASCADE;
DROP TABLE IF EXISTS lgas CASCADE;
DROP TABLE IF EXISTS states CASCADE;
DROP TABLE IF EXISTS regions CASCADE;
DROP TABLE IF EXISTS countries CASCADE;

COMMIT;
