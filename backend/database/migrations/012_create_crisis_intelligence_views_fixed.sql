-- Multi-Dimensional Crisis Intelligence Dashboard Views - FIXED VERSION
-- Optimized for Neon PostgreSQL performance
-- Works with the actual conflicts table structure

-- 1. Create additional indexes on the conflicts table for optimal query performance
-- Note: Only create indexes that don't already exist
CREATE INDEX IF NOT EXISTS idx_conflicts_crisis_metrics ON conflicts(state_id, incidence_date DESC, verified);
CREATE INDEX IF NOT EXISTS idx_conflicts_actor_analysis ON conflicts(actor_1, incidence_date DESC);
CREATE INDEX IF NOT EXISTS idx_conflicts_displaced_analysis ON conflicts(displaced_persons, incidence_date DESC) WHERE displaced_persons IS NOT NULL;

-- 2. Materialized View: Monthly Crisis Aggregates
CREATE MATERIALIZED VIEW IF NOT EXISTS crisis_monthly_summary AS
SELECT 
    to_char(incidence_date, 'YYYY-MM') as month,
    s.name as state,
    ct.name as conflict_type,
    COUNT(*) as incidents,
    SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) as total_fatalities,
    CASE 
        WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
        ELSE 0
    END as total_displaced,
    SUM(injured_male + injured_female + injured_unknown) as total_injuries,
    -- Crisis Index Score: weighted calculation
    -- Fatalities weight: 3 points, Displaced persons weight: 1 point, Injuries weight: 0.5 points
    (SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) * 3 + 
     CASE 
        WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
        ELSE 0
     END * 1 + 
     SUM(injured_male + injured_female + injured_unknown) * 0.5) as crisis_index_score,
    -- Risk level classification
    CASE 
        WHEN (SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) * 3 + 
             CASE 
                WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
                ELSE 0
             END * 1 + 
             SUM(injured_male + injured_female + injured_unknown) * 0.5) >= 100 THEN 'CRITICAL'
        WHEN (SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) * 3 + 
             CASE 
                WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
                ELSE 0
             END * 1 + 
             SUM(injured_male + injured_female + injured_unknown) * 0.5) >= 50 THEN 'HIGH'
        WHEN (SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) * 3 + 
             CASE 
                WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
                ELSE 0
             END * 1 + 
             SUM(injured_male + injured_female + injured_unknown) * 0.5) >= 20 THEN 'MEDIUM'
        ELSE 'LOW'
    END as risk_level
FROM conflicts c
LEFT JOIN states s ON c.state_id = s.id  
LEFT JOIN conflict_types ct ON c.conflict_type_id = ct.id
WHERE c.incidence_date IS NOT NULL AND c.verified = true
GROUP BY to_char(incidence_date, 'YYYY-MM'), s.name, ct.name;

-- Create unique index for materialized view refresh
CREATE UNIQUE INDEX IF NOT EXISTS idx_crisis_monthly_summary_unique 
ON crisis_monthly_summary (month, state, conflict_type);

-- 3. Materialized View: State-Level Crisis Hotspots
CREATE MATERIALIZED VIEW IF NOT EXISTS crisis_state_hotspots AS
SELECT 
    s.name as state,
    COUNT(*) as total_incidents,
    SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) as total_fatalities,
    CASE 
        WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
        ELSE 0
    END as total_displaced,
    SUM(injured_male + injured_female + injured_unknown) as total_injuries,
    -- Crisis Index Score for state
    (SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) * 3 + 
     CASE 
        WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
        ELSE 0
     END * 1 + 
     SUM(injured_male + injured_female + injured_unknown) * 0.5) as crisis_index_score,
    -- Most affected month
    to_char(incidence_date, 'YYYY-MM') as peak_month,
    COUNT(DISTINCT c.conflict_type_id) as crisis_types_count,
    COUNT(DISTINCT c.actor_1) as unique_actors_count,
    -- Risk level classification
    CASE 
        WHEN (SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) * 3 + 
             CASE 
                WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
                ELSE 0
             END * 1 + 
             SUM(injured_male + injured_female + injured_unknown) * 0.5) >= 500 THEN 'CRITICAL'
        WHEN (SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) * 3 + 
             CASE 
                WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
                ELSE 0
             END * 1 + 
             SUM(injured_male + injured_female + injured_unknown) * 0.5) >= 200 THEN 'HIGH'
        WHEN (SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) * 3 + 
             CASE 
                WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
                ELSE 0
             END * 1 + 
             SUM(injured_male + injured_female + injured_unknown) * 0.5) >= 50 THEN 'MEDIUM'
        ELSE 'LOW'
    END as risk_level,
    -- Recent activity (last 30 days)
    COUNT(*) FILTER (WHERE incidence_date >= CURRENT_DATE - INTERVAL '30 days') as recent_incidents,
    SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) FILTER (WHERE incidence_date >= CURRENT_DATE - INTERVAL '30 days') as recent_fatalities
FROM conflicts c
LEFT JOIN states s ON c.state_id = s.id
WHERE c.state_id IS NOT NULL AND c.incidence_date IS NOT NULL AND c.verified = true
GROUP BY s.name, to_char(incidence_date, 'YYYY-MM')
ORDER BY crisis_index_score DESC;

-- Create index for state hotspots
CREATE INDEX IF NOT EXISTS idx_crisis_state_hotspots_score 
ON crisis_state_hotspots (crisis_index_score DESC);

-- 4. Materialized View: Actor Analysis
CREATE MATERIALIZED VIEW IF NOT EXISTS crisis_actor_analysis AS
SELECT 
    COALESCE(a.name, 'Unknown Actor') as actor,
    COALESCE(a.actor_type, 'Unknown') as actor_type,
    ct.name as conflict_type,
    COUNT(*) as incidents,
    SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) as total_fatalities,
    CASE 
        WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
        ELSE 0
    END as total_displaced,
    SUM(injured_male + injured_female + injured_unknown) as total_injuries,
    COUNT(DISTINCT c.state_id) as states_affected,
    MIN(c.incidence_date) as first_incident,
    MAX(c.incidence_date) as last_incident,
    -- Actor threat level
    (SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) * 3 + 
     CASE 
        WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
        ELSE 0
     END * 1 + 
     SUM(injured_male + injured_female + injured_unknown) * 0.5) as threat_score,
    -- Risk classification
    CASE 
        WHEN (SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) * 3 + 
             CASE 
                WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
                ELSE 0
             END * 1 + 
             SUM(injured_male + injured_female + injured_unknown) * 0.5) >= 200 THEN 'CRITICAL'
        WHEN (SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) * 3 + 
             CASE 
                WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
                ELSE 0
             END * 1 + 
             SUM(injured_male + injured_female + injured_unknown) * 0.5) >= 100 THEN 'HIGH'
        WHEN (SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) * 3 + 
             CASE 
                WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
                ELSE 0
             END * 1 + 
             SUM(injured_male + injured_female + injured_unknown) * 0.5) >= 50 THEN 'MEDIUM'
        ELSE 'LOW'
    END as threat_level
FROM conflicts c
LEFT JOIN states s ON c.state_id = s.id
LEFT JOIN conflict_types ct ON c.conflict_type_id = ct.id
LEFT JOIN actors a ON c.actor_1 = a.id
WHERE c.actor_1 IS NOT NULL AND c.incidence_date IS NOT NULL AND c.verified = true
GROUP BY a.name, a.actor_type, ct.name
ORDER BY threat_score DESC;

-- Create index for actor analysis
CREATE INDEX IF NOT EXISTS idx_crisis_actor_analysis_threat 
ON crisis_actor_analysis (threat_score DESC);

-- 5. Materialized View: Crisis Type Distribution
CREATE MATERIALIZED VIEW IF NOT EXISTS crisis_type_distribution AS
SELECT 
    ct.name as conflict_type,
    ct.name as event_type,
    COUNT(*) as total_incidents,
    SUM(civilian_death_male + civilian_death_female + civilian_death_unknown + security_death_male + security_death_female + security_death_unknown) as total_fatalities,
    CASE 
        WHEN displaced_persons ~ '^[0-9]+$' THEN CAST(displaced_persons AS INTEGER)
        ELSE 0
    END as total_displaced,
    SUM(injured_male + injured_female + injured_unknown) as total_injuries,
    COUNT(DISTINCT c.state_id) as states_affected,
    COUNT(DISTINCT c.actor_1) as unique_actors,
    -- Monthly trend (last 6 months vs previous 6 months)
    COUNT(*) FILTER (WHERE incidence_date >= CURRENT_DATE - INTERVAL '6 months') as recent_incidents,
    COUNT(*) FILTER (WHERE incidence_date >= CURRENT_DATE - INTERVAL '12 months' AND incidence_date < CURRENT_DATE - INTERVAL '6 months') as previous_incidents,
    -- Trend calculation
    CASE 
        WHEN COUNT(*) FILTER (WHERE incidence_date >= CURRENT_DATE - INTERVAL '12 months' AND incidence_date < CURRENT_DATE - INTERVAL '6 months') = 0 THEN 'NEW'
        WHEN (COUNT(*) FILTER (WHERE incidence_date >= CURRENT_DATE - INTERVAL '6 months') * 1.0 / 
              COUNT(*) FILTER (WHERE incidence_date >= CURRENT_DATE - INTERVAL '12 months' AND incidence_date < CURRENT_DATE - INTERVAL '6 months')) > 1.2 THEN 'INCREASING'
        WHEN (COUNT(*) FILTER (WHERE incidence_date >= CURRENT_DATE - INTERVAL '6 months') * 1.0 / 
              COUNT(*) FILTER (WHERE incidence_date >= CURRENT_DATE - INTERVAL '12 months' AND incidence_date < CURRENT_DATE - INTERVAL '6 months')) < 0.8 THEN 'DECREASING'
        ELSE 'STABLE'
    END as trend_direction
FROM conflicts c
LEFT JOIN conflict_types ct ON c.conflict_type_id = ct.id
WHERE ct.name IS NOT NULL AND c.incidence_date IS NOT NULL AND c.verified = true
GROUP BY ct.name
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

-- Initial data load
SELECT refresh_crisis_intelligence_views();
