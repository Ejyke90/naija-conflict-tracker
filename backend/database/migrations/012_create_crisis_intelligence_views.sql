-- Multi-Dimensional Crisis Intelligence Dashboard Views
-- Optimized for Neon PostgreSQL performance

-- 1. Create indexes for optimal query performance
CREATE INDEX IF NOT EXISTS idx_conflict_events_state_date ON conflict_events(state, event_date DESC);
CREATE INDEX IF NOT EXISTS idx_conflict_events_event_type ON conflict_events(event_type);
CREATE INDEX IF NOT EXISTS idx_conflict_events_conflict_type ON conflict_events(conflict_type);
CREATE INDEX IF NOT EXISTS idx_conflict_events_actor1 ON conflict_events(actor1);
CREATE INDEX IF NOT EXISTS idx_conflict_events_crisis_metrics ON conflict_events(state, event_type, event_date);

-- 2. Materialized View: Monthly Crisis Aggregates
CREATE MATERIALIZED VIEW IF NOT EXISTS crisis_monthly_summary AS
SELECT 
    to_char(event_date, 'YYYY-MM') as month,
    state,
    event_type,
    conflict_type,
    COUNT(*) as incidents,
    SUM(fatalities) as total_fatalities,
    SUM(displaced_persons) as total_displaced,
    SUM(injuries) as total_injuries,
    SUM(properties_destroyed) as total_properties_destroyed,
    -- Crisis Index Score: weighted calculation
    -- Fatalities weight: 3 points, Displaced persons weight: 1 point, Injuries weight: 0.5 points
    (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) as crisis_index_score,
    -- Risk level classification
    CASE 
        WHEN (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) >= 100 THEN 'CRITICAL'
        WHEN (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) >= 50 THEN 'HIGH'
        WHEN (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) >= 20 THEN 'MEDIUM'
        ELSE 'LOW'
    END as risk_level
FROM conflict_events 
WHERE event_date IS NOT NULL
GROUP BY to_char(event_date, 'YYYY-MM'), state, event_type, conflict_type;

-- Create unique index for materialized view refresh
CREATE UNIQUE INDEX IF NOT EXISTS idx_crisis_monthly_summary_unique 
ON crisis_monthly_summary (month, state, event_type, conflict_type);

-- 3. Materialized View: State-Level Crisis Hotspots
CREATE MATERIALIZED VIEW IF NOT EXISTS crisis_state_hotspots AS
SELECT 
    state,
    COUNT(*) as total_incidents,
    SUM(fatalities) as total_fatalities,
    SUM(displaced_persons) as total_displaced,
    SUM(injuries) as total_injuries,
    -- Crisis Index Score for state
    (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) as crisis_index_score,
    -- Most affected month
    to_char(event_date, 'YYYY-MM') as peak_month,
    COUNT(DISTINCT event_type) as crisis_types_count,
    COUNT(DISTINCT actor1) as unique_actors_count,
    -- Risk level classification
    CASE 
        WHEN (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) >= 500 THEN 'CRITICAL'
        WHEN (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) >= 200 THEN 'HIGH'
        WHEN (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) >= 50 THEN 'MEDIUM'
        ELSE 'LOW'
    END as risk_level,
    -- Recent activity (last 30 days)
    COUNT(*) FILTER (WHERE event_date >= CURRENT_DATE - INTERVAL '30 days') as recent_incidents,
    SUM(fatalities) FILTER (WHERE event_date >= CURRENT_DATE - INTERVAL '30 days') as recent_fatalities
FROM conflict_events 
WHERE state IS NOT NULL AND event_date IS NOT NULL
GROUP BY state, to_char(event_date, 'YYYY-MM')
ORDER BY crisis_index_score DESC;

-- Create index for state hotspots
CREATE INDEX IF NOT EXISTS idx_crisis_state_hotspots_score 
ON crisis_state_hotspots (crisis_index_score DESC);

-- 4. Materialized View: Actor Analysis
CREATE MATERIALIZED VIEW IF NOT EXISTS crisis_actor_analysis AS
SELECT 
    actor1 as actor,
    actor1_type as actor_type,
    event_type,
    conflict_type,
    COUNT(*) as incidents,
    SUM(fatalities) as total_fatalities,
    SUM(displaced_persons) as total_displaced,
    SUM(injuries) as total_injuries,
    COUNT(DISTINCT state) as states_affected,
    MIN(event_date) as first_incident,
    MAX(event_date) as last_incident,
    -- Actor threat level
    (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) as threat_score,
    -- Risk classification
    CASE 
        WHEN (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) >= 200 THEN 'CRITICAL'
        WHEN (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) >= 100 THEN 'HIGH'
        WHEN (SUM(fatalities) * 3 + SUM(displaced_persons) * 1 + SUM(injuries) * 0.5) >= 50 THEN 'MEDIUM'
        ELSE 'LOW'
    END as threat_level
FROM conflict_events 
WHERE actor1 IS NOT NULL AND event_date IS NOT NULL
GROUP BY actor1, actor1_type, event_type, conflict_type
ORDER BY threat_score DESC;

-- Create index for actor analysis
CREATE INDEX IF NOT EXISTS idx_crisis_actor_analysis_threat 
ON crisis_actor_analysis (threat_score DESC);

-- 5. Materialized View: Crisis Type Distribution
CREATE MATERIALIZED VIEW IF NOT EXISTS crisis_type_distribution AS
SELECT 
    event_type,
    conflict_type,
    COUNT(*) as total_incidents,
    SUM(fatalities) as total_fatalities,
    SUM(displaced_persons) as total_displaced,
    SUM(injuries) as total_injuries,
    COUNT(DISTINCT state) as states_affected,
    COUNT(DISTINCT actor1) as unique_actors,
    -- Monthly trend (last 6 months vs previous 6 months)
    COUNT(*) FILTER (WHERE event_date >= CURRENT_DATE - INTERVAL '6 months') as recent_incidents,
    COUNT(*) FILTER (WHERE event_date >= CURRENT_DATE - INTERVAL '12 months' AND event_date < CURRENT_DATE - INTERVAL '6 months') as previous_incidents,
    -- Trend calculation
    CASE 
        WHEN COUNT(*) FILTER (WHERE event_date >= CURRENT_DATE - INTERVAL '12 months' AND event_date < CURRENT_DATE - INTERVAL '6 months') = 0 THEN 'NEW'
        WHEN (COUNT(*) FILTER (WHERE event_date >= CURRENT_DATE - INTERVAL '6 months') * 1.0 / 
              COUNT(*) FILTER (WHERE event_date >= CURRENT_DATE - INTERVAL '12 months' AND event_date < CURRENT_DATE - INTERVAL '6 months')) > 1.2 THEN 'INCREASING'
        WHEN (COUNT(*) FILTER (WHERE event_date >= CURRENT_DATE - INTERVAL '6 months') * 1.0 / 
              COUNT(*) FILTER (WHERE event_date >= CURRENT_DATE - INTERVAL '12 months' AND event_date < CURRENT_DATE - INTERVAL '6 months')) < 0.8 THEN 'DECREASING'
        ELSE 'STABLE'
    END as trend_direction
FROM conflict_events 
WHERE event_type IS NOT NULL AND conflict_type IS NOT NULL AND event_date IS NOT NULL
GROUP BY event_type, conflict_type
ORDER BY total_incidents DESC;

-- Create index for crisis type distribution
CREATE INDEX IF NOT EXISTS idx_crisis_type_distribution_incidents 
ON crisis_type_distribution (total_incidents DESC);

-- 6. Function to refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_crisis_intelligence_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY crisis_monthly_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY crisis_state_hotspots;
    REFRESH MATERIALIZED VIEW CONCURRENTLY crisis_actor_analysis;
    REFRESH MATERIALIZED VIEW CONCURRENTLY crisis_type_distribution;
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT SELECT ON crisis_monthly_summary TO neondb_owner;
GRANT SELECT ON crisis_state_hotspots TO neondb_owner;
GRANT SELECT ON crisis_actor_analysis TO neondb_owner;
GRANT SELECT ON crisis_type_distribution TO neondb_owner;
