-- Migration script to transform data from old schema to new schema
-- This assumes you have the old 'conflicts' table

-- Insert data from old schema to new schema
INSERT INTO conflict_events (
    event_date,
    year,
    month,
    state,
    lga,
    location,
    event_type,
    conflict_type,
    actor1,
    actor2,
    fatalities,
    injuries,
    displaced_persons,
    source,
    notes,
    created_at
)
SELECT 
    event_date,
    EXTRACT(YEAR FROM event_date)::INTEGER,
    EXTRACT(MONTH FROM event_date)::INTEGER,
    state,
    lga,
    community,
    COALESCE(conflict_type, 'Unknown'),
    conflict_type,
    actor1,
    actor2,
    COALESCE(fatalities, 0),
    COALESCE(injured, 0),
    COALESCE(displaced, 0),
    COALESCE(source, data_source),
    description,
    COALESCE(created_at, NOW())
FROM conflicts
WHERE event_date IS NOT NULL AND state IS NOT NULL
ON CONFLICT (id) DO NOTHING;

-- Refresh materialized view after data import
SELECT refresh_dashboard_stats();
