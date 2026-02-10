-- Complete Conflict Data Backup Script for Neon
-- Run this in Neon SQL Editor to backup all conflict-related tables

-- 1. Check current data in all conflict tables
SELECT 'conflicts' as table_name, COUNT(*) as record_count FROM conflicts
UNION ALL
SELECT 'conflicts_events', COUNT(*) FROM conflict_events
UNION ALL  
SELECT 'conflicts_with_totals', COUNT(*) FROM conflicts_with_totals
UNION ALL
SELECT 'conflict_events_archive_20260208', COUNT(*) FROM conflict_events_archive_20260208
UNION ALL
SELECT 'conflict_types', COUNT(*) FROM conflict_types;

-- 2. Backup main conflicts table
COPY conflicts TO 'conflicts_backup_20260209.csv' WITH CSV HEADER;

-- 3. Backup conflict_events table  
COPY conflict_events TO 'conflict_events_backup_20260209.csv' WITH CSV HEADER;

-- 4. Backup conflicts_with_totals (if it has data)
COPY conflicts_with_totals TO 'conflicts_with_totals_backup_20260209.csv' WITH CSV HEADER;

-- 5. Backup archive table
COPY conflict_events_archive_20260208 TO 'conflict_events_archive_backup_20260209.csv' WITH CSV HEADER;

-- 6. Backup reference data
COPY conflict_types TO 'conflict_types_backup_20260209.csv' WITH CSV HEADER;

-- 7. Check kidnapping data specifically
SELECT 
    'conflicts' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE kidnapped_male > 0 OR kidnapped_female > 0 OR kidnapped_unknown > 0) as kidnapping_records,
    SUM(kidnapped_male) as male_victims,
    SUM(kidnapped_female) as female_victims, 
    SUM(kidnapped_unknown) as unknown_victims,
    SUM(kidnapped_male + kidnapped_female + kidnapped_unknown) as total_victims,
    MIN(incidence_date) as earliest_date,
    MAX(incidence_date) as latest_date
FROM conflicts

UNION ALL

SELECT 
    'conflict_events' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE kidnapped_male > 0 OR kidnapped_female > 0 OR kidnapped_unknown > 0) as kidnapping_records,
    SUM(kidnapped_male) as male_victims,
    SUM(kidnapped_female) as female_victims,
    SUM(kidnapped_unknown) as unknown_victims, 
    SUM(kidnapped_male + kidnapped_female + kidnapped_unknown) as total_victims,
    MIN(event_date) as earliest_date,
    MAX(event_date) as latest_date
FROM conflict_events;
