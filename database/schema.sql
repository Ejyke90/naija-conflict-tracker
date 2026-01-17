-- Nigeria Conflict Tracker Database Schema
-- PostgreSQL with PostGIS extension

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- =============================================
-- CORE TABLES
-- =============================================

-- Conflicts/Events Table
CREATE TABLE IF NOT EXISTS conflicts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_date TIMESTAMP NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    archetype VARCHAR(100),
    
    -- Location (hierarchical)
    state VARCHAR(50) NOT NULL,
    lga VARCHAR(100),
    community VARCHAR(200),
    location_detail TEXT,
    coordinates GEOGRAPHY(POINT, 4326),
    
    -- Casualties (gender-disaggregated)
    fatalities_male INTEGER DEFAULT 0,
    fatalities_female INTEGER DEFAULT 0,
    fatalities_unknown INTEGER DEFAULT 0,
    injured_male INTEGER DEFAULT 0,
    injured_female INTEGER DEFAULT 0,
    injured_unknown INTEGER DEFAULT 0,
    kidnapped_male INTEGER DEFAULT 0,
    kidnapped_female INTEGER DEFAULT 0,
    kidnapped_unknown INTEGER DEFAULT 0,
    displaced INTEGER DEFAULT 0,
    
    -- Actors
    perpetrator_group VARCHAR(200),
    target_group VARCHAR(200),
    
    -- Data provenance
    source_type VARCHAR(50),
    source_url TEXT,
    source_reliability INTEGER CHECK (source_reliability BETWEEN 1 AND 5),
    confidence_score FLOAT CHECK (confidence_score BETWEEN 0 AND 1),
    
    -- Metadata
    description TEXT,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Convert to TimescaleDB hypertable for time-series optimization
SELECT create_hypertable('conflicts', 'event_date');

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_conflicts_state ON conflicts(state);
CREATE INDEX IF NOT EXISTS idx_conflicts_lga ON conflicts(lga);
CREATE INDEX IF NOT EXISTS idx_conflicts_type ON conflicts(event_type);
CREATE INDEX IF NOT EXISTS idx_conflicts_date ON conflicts(event_date DESC);
CREATE INDEX IF NOT EXISTS idx_conflicts_location ON conflicts USING GIST(coordinates);
CREATE INDEX IF NOT EXISTS idx_conflicts_archetype ON conflicts(archetype);
CREATE INDEX IF NOT EXISTS idx_conflicts_perpetrator ON conflicts(perpetrator_group);

-- =============================================
-- SUPPORTING TABLES
-- =============================================

-- Geographic Boundaries (for mapping)
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    type VARCHAR(20) NOT NULL, -- state, lga, community
    name VARCHAR(200) NOT NULL,
    parent_id INTEGER REFERENCES locations(id),
    boundary GEOGRAPHY(MULTIPOLYGON, 4326),
    population INTEGER,
    poverty_rate FLOAT,
    unemployment_rate FLOAT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(type, name)
);

-- Create indexes for locations
CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(type);
CREATE INDEX IF NOT EXISTS idx_locations_parent ON locations(parent_id);
CREATE INDEX IF NOT EXISTS idx_location_boundary ON locations USING GIST(boundary);

-- Conflict Actors/Groups
CREATE TABLE IF NOT EXISTS actors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    type VARCHAR(50), -- armed_group, military, police, militia, bandits
    ideology VARCHAR(100),
    active_since DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Poverty Indicators (for correlation analysis)
CREATE TABLE IF NOT EXISTS poverty_indicators (
    id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(id),
    year INTEGER NOT NULL,
    poverty_rate FLOAT,
    unemployment_rate FLOAT,
    gdp_per_capita FLOAT,
    education_index FLOAT,
    source VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(location_id, year)
);

-- Social Media Chatter
CREATE TABLE IF NOT EXISTS social_chatter (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50), -- twitter, facebook
    post_id VARCHAR(200) UNIQUE,
    content TEXT,
    author VARCHAR(200),
    location VARCHAR(200),
    coordinates GEOGRAPHY(POINT, 4326),
    sentiment FLOAT, -- -1 (negative) to 1 (positive)
    relevance_score FLOAT,
    keywords TEXT[],
    posted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('social_chatter', 'posted_at');

-- Forecasts
CREATE TABLE IF NOT EXISTS forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    forecast_date TIMESTAMP NOT NULL,
    target_date TIMESTAMP NOT NULL,
    location_type VARCHAR(20), -- state, lga
    location_name VARCHAR(200),
    
    -- Predictions
    risk_score FLOAT CHECK (risk_score BETWEEN 0 AND 1),
    risk_level VARCHAR(20), -- low, medium, high, very_high
    predicted_incidents INTEGER,
    predicted_casualties INTEGER,
    
    -- Model metadata
    model_version VARCHAR(50),
    confidence_interval JSONB, -- {lower: 0.3, upper: 0.7}
    contributing_factors JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- News Articles (for full-text search)
CREATE TABLE IF NOT EXISTS news_articles (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    url TEXT UNIQUE,
    source VARCHAR(200),
    published_at TIMESTAMP,
    extracted_locations TEXT[],
    linked_conflict_id UUID REFERENCES conflicts(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================
-- VIEWS FOR COMMON QUERIES
-- =============================================

-- Hot Zones (High conflict areas)
CREATE OR REPLACE VIEW hot_zones AS
SELECT 
    state,
    lga,
    COUNT(*) as incident_count,
    SUM(fatalities_male + fatalities_female + fatalities_unknown) as total_fatalities,
    SUM(kidnapped_male + kidnapped_female + kidnapped_unknown) as total_kidnapped,
    AVG(confidence_score) as avg_confidence,
    MAX(event_date) as latest_incident
FROM conflicts
WHERE event_date >= NOW() - INTERVAL '6 months'
GROUP BY state, lga
HAVING COUNT(*) >= 5
ORDER BY incident_count DESC;

-- Monthly Trends
CREATE OR REPLACE VIEW monthly_trends AS
SELECT 
    DATE_TRUNC('month', event_date) as month,
    state,
    event_type,
    COUNT(*) as incidents,
    SUM(fatalities_male + fatalities_female + fatalities_unknown) as fatalities,
    SUM(injured_male + injured_female + injured_unknown) as injured,
    SUM(kidnapped_male + kidnapped_female + kidnapped_unknown) as kidnapped
FROM conflicts
GROUP BY month, state, event_type
ORDER BY month DESC;

-- Gender Impact Analysis
CREATE OR REPLACE VIEW gender_impact AS
SELECT 
    state,
    SUM(fatalities_male) as male_fatalities,
    SUM(fatalities_female) as female_fatalities,
    SUM(fatalities_unknown) as unknown_fatalities,
    SUM(kidnapped_male) as male_kidnapped,
    SUM(kidnapped_female) as female_kidnapped,
    SUM(kidnapped_unknown) as unknown_kidnapped,
    SUM(injured_male) as male_injured,
    SUM(injured_female) as female_injured,
    SUM(injured_unknown) as unknown_injured
FROM conflicts
WHERE event_date >= NOW() - INTERVAL '1 year'
GROUP BY state
ORDER BY male_fatalities DESC;

-- Actor Statistics
CREATE OR REPLACE VIEW actor_statistics AS
SELECT 
    perpetrator_group,
    COUNT(*) as incident_count,
    SUM(fatalities_male + fatalities_female + fatalities_unknown) as total_fatalities,
    SUM(kidnapped_male + kidnapped_female + kidnapped_unknown) as total_kidnapped,
    STRING_AGG(DISTINCT state, ', ') as affected_states,
    MIN(event_date) as first_incident,
    MAX(event_date) as latest_incident
FROM conflicts
WHERE perpetrator_group IS NOT NULL
GROUP BY perpetrator_group
ORDER BY incident_count DESC;

-- =============================================
-- SAMPLE DATA (for development)
-- =============================================

-- Insert Nigerian States
INSERT INTO locations (type, name, population) VALUES 
('state', 'Abia', 2845380),
('state', 'Adamawa', 3178950),
('state', 'Akwa Ibom', 5452137),
('state', 'Anambra', 4182132),
('state', 'Bauchi', 6537314),
('state', 'Bayelsa', 1704915),
('state', 'Benue', 5774638),
('state', 'Borno', 5709656),
('state', 'Cross River', 3737969),
('state', 'Delta', 4417069),
('state', 'Ebonyi', 2810434),
('state', 'Edo', 3233366),
('state', 'Ekiti', 3247234),
('state', 'Enugu', 3916209),
('state', 'FCT', 1405301),
('state', 'Gombe', 3256528),
('state', 'Imo', 5408201),
('state', 'Jigawa', 5297496),
('state', 'Kaduna', 9058905),
('state', 'Kano', 13137664),
('state', 'Katsina', 8598588),
('state', 'Kebbi', 4093388),
('state', 'Kogi', 4473990),
('state', 'Kwara', 2365353),
('state', 'Lagos', 12456787),
('state', 'Nasarawa', 2512340),
('state', 'Niger', 5986952),
('state', 'Ogun', 5217708),
('state', 'Ondo', 4651781),
('state', 'Osun', 4234136),
('state', 'Oyo', 7933915),
('state', 'Plateau', 4338392),
('state', 'Rivers', 6537274),
('state', 'Sokoto', 6904606),
('state', 'Taraba', 3700392),
('state', 'Yobe', 3236330),
('state', 'Zamfara', 9278646)
ON CONFLICT (type, name) DO NOTHING;

-- Insert sample actors
INSERT INTO actors (name, type) VALUES 
('Bandits', 'armed_group'),
('Boko Haram', 'armed_group'),
('ISWAP', 'armed_group'),
('Fulani Herdsmen', 'militia'),
('Security Forces', 'military'),
('Unknown Gunmen', 'armed_group'),
('Cultists', 'militia')
ON CONFLICT (name) DO NOTHING;

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_conflicts_updated_at BEFORE UPDATE ON conflicts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_locations_updated_at BEFORE UPDATE ON locations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
