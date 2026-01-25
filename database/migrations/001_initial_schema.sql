-- Nextier Nigeria Conflict Tracker - Supabase Schema
-- Migration: 001_initial_schema
-- Created: 2026-01-25

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Core Events Table
CREATE TABLE IF NOT EXISTS conflict_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_date DATE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    
    -- Location
    state VARCHAR(50) NOT NULL,
    lga VARCHAR(100),
    location VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Event Classification
    event_type VARCHAR(100) NOT NULL, -- e.g., "Armed Conflict", "Communal Clash"
    event_category VARCHAR(100),
    conflict_type VARCHAR(100),
    
    -- Actors
    actor1 VARCHAR(255),
    actor2 VARCHAR(255),
    actor1_type VARCHAR(100),
    actor2_type VARCHAR(100),
    
    -- Impact
    fatalities INTEGER DEFAULT 0,
    injuries INTEGER DEFAULT 0,
    properties_destroyed INTEGER DEFAULT 0,
    displaced_persons INTEGER DEFAULT 0,
    
    -- Metadata
    source TEXT,
    notes TEXT,
    verified BOOLEAN DEFAULT false,
    confidence_level VARCHAR(20), -- 'High', 'Medium', 'Low'
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_coordinates CHECK (
        (latitude BETWEEN -90 AND 90 OR latitude IS NULL) AND
        (longitude BETWEEN -180 AND 180 OR longitude IS NULL)
    ),
    CONSTRAINT valid_fatalities CHECK (fatalities >= 0),
    CONSTRAINT valid_injuries CHECK (injuries >= 0),
    CONSTRAINT valid_year CHECK (year BETWEEN 1990 AND 2100)
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_events_date ON conflict_events(event_date DESC);
CREATE INDEX IF NOT EXISTS idx_events_state ON conflict_events(state);
CREATE INDEX IF NOT EXISTS idx_events_type ON conflict_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_location ON conflict_events(state, lga);
CREATE INDEX IF NOT EXISTS idx_events_year_month ON conflict_events(year, month);
CREATE INDEX IF NOT EXISTS idx_events_coordinates ON conflict_events(latitude, longitude) WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- Spatial index for geographic queries (if PostGIS is enabled)
-- CREATE INDEX IF NOT EXISTS idx_events_geom ON conflict_events USING GIST (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326));

-- States Reference Table
CREATE TABLE IF NOT EXISTS states (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    region VARCHAR(50), -- 'North-East', 'North-West', 'North-Central', 'South-East', 'South-West', 'South-South'
    capital VARCHAR(100),
    population INTEGER,
    area_km2 DECIMAL(10, 2),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- LGAs Reference Table
CREATE TABLE IF NOT EXISTS lgas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    state_name VARCHAR(50) NOT NULL,
    population INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(name, state_name)
);

-- Add foreign key after states table is created
ALTER TABLE lgas ADD CONSTRAINT fk_lgas_state 
    FOREIGN KEY (state_name) REFERENCES states(name) ON DELETE CASCADE;

-- Materialized View for Dashboard Aggregations
CREATE MATERIALIZED VIEW IF NOT EXISTS dashboard_statistics AS
SELECT 
    COUNT(*) as total_events,
    SUM(fatalities) as total_fatalities,
    SUM(injuries) as total_injuries,
    SUM(displaced_persons) as total_displaced,
    COUNT(DISTINCT state) as affected_states,
    MAX(event_date) as last_update,
    date_trunc('month', event_date) as month,
    state,
    event_type,
    SUM(fatalities) as monthly_fatalities,
    SUM(injuries) as monthly_injuries,
    COUNT(*) as monthly_events
FROM conflict_events
GROUP BY date_trunc('month', event_date), state, event_type;

CREATE INDEX IF NOT EXISTS idx_dashboard_stats_month ON dashboard_statistics(month);
CREATE INDEX IF NOT EXISTS idx_dashboard_stats_state ON dashboard_statistics(state);

-- Function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_dashboard_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_statistics;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_conflict_events_updated_at
    BEFORE UPDATE ON conflict_events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert Nigerian states data
INSERT INTO states (name, region, capital, latitude, longitude) VALUES
    ('Abia', 'South-East', 'Umuahia', 5.5325, 7.4810),
    ('Adamawa', 'North-East', 'Yola', 9.3265, 12.3984),
    ('Akwa Ibom', 'South-South', 'Uyo', 5.0078, 7.8537),
    ('Anambra', 'South-East', 'Awka', 6.2209, 6.9370),
    ('Bauchi', 'North-East', 'Bauchi', 10.3158, 9.8442),
    ('Bayelsa', 'South-South', 'Yenagoa', 4.9267, 6.2676),
    ('Benue', 'North-Central', 'Makurdi', 7.7439, 8.5378),
    ('Borno', 'North-East', 'Maiduguri', 11.8311, 13.1511),
    ('Cross River', 'South-South', 'Calabar', 4.9609, 8.3417),
    ('Delta', 'South-South', 'Asaba', 5.5364, 5.7500),
    ('Ebonyi', 'South-East', 'Abakaliki', 6.3250, 8.1137),
    ('Edo', 'South-South', 'Benin City', 6.3350, 5.6037),
    ('Ekiti', 'South-West', 'Ado-Ekiti', 7.7190, 5.3110),
    ('Enugu', 'South-East', 'Enugu', 6.5244, 7.5105),
    ('FCT', 'North-Central', 'Abuja', 9.0765, 7.3986),
    ('Gombe', 'North-East', 'Gombe', 10.2904, 11.1679),
    ('Imo', 'South-East', 'Owerri', 5.4834, 7.0333),
    ('Jigawa', 'North-West', 'Dutse', 12.2230, 9.3486),
    ('Kaduna', 'North-West', 'Kaduna', 10.5222, 7.4383),
    ('Kano', 'North-West', 'Kano', 12.0022, 8.5920),
    ('Katsina', 'North-West', 'Katsina', 12.9908, 7.6006),
    ('Kebbi', 'North-West', 'Birnin Kebbi', 12.4539, 4.1975),
    ('Kogi', 'North-Central', 'Lokoja', 7.7333, 6.7333),
    ('Kwara', 'North-Central', 'Ilorin', 8.4966, 4.5424),
    ('Lagos', 'South-West', 'Ikeja', 6.5244, 3.3792),
    ('Nasarawa', 'North-Central', 'Lafia', 8.5333, 8.3333),
    ('Niger', 'North-Central', 'Minna', 9.6139, 6.5569),
    ('Ogun', 'South-West', 'Abeokuta', 7.1475, 3.3619),
    ('Ondo', 'South-West', 'Akure', 7.2571, 5.2058),
    ('Osun', 'South-West', 'Osogbo', 7.7667, 4.5667),
    ('Oyo', 'South-West', 'Ibadan', 7.3775, 3.9470),
    ('Plateau', 'North-Central', 'Jos', 9.8965, 8.8583),
    ('Rivers', 'South-South', 'Port Harcourt', 4.8156, 7.0498),
    ('Sokoto', 'North-West', 'Sokoto', 13.0622, 5.2339),
    ('Taraba', 'North-East', 'Jalingo', 8.8833, 11.3500),
    ('Yobe', 'North-East', 'Damaturu', 11.7490, 11.9608),
    ('Zamfara', 'North-West', 'Gusau', 12.1628, 6.6599)
ON CONFLICT (name) DO NOTHING;

-- Grant permissions (adjust for your needs)
-- Enable Row Level Security
ALTER TABLE conflict_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE states ENABLE ROW LEVEL SECURITY;
ALTER TABLE lgas ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access (adjust as needed)
CREATE POLICY "Enable read access for all users" ON conflict_events
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for states" ON states
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for lgas" ON lgas
    FOR SELECT USING (true);

-- Create policies for authenticated writes (for future admin panel)
CREATE POLICY "Enable insert for authenticated users only" ON conflict_events
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Enable update for authenticated users only" ON conflict_events
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Enable delete for authenticated users only" ON conflict_events
    FOR DELETE USING (auth.role() = 'authenticated');
