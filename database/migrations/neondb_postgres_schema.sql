-- ================================================
-- Nextier Nigeria Violent Conflicts Database
-- PostgreSQL Schema for Neon DB
-- Converted from MariaDB schema (u503102722_conflictdb.sql)
-- Migration Date: February 8, 2026
-- ================================================

-- IMPORTANT: This script creates NEW tables alongside existing ones
-- The old conflict_events table will be archived (not dropped) after migration
-- See: /openspec/changes/migrate-production-database-schema/CLEANUP_STRATEGY.md

-- ================================================
-- PRE-MIGRATION CHECKS
-- ================================================

-- Verify PostgreSQL version (should be 14+)
SELECT version();

-- List existing tables (for comparison before/after)
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check if old conflict_events table exists
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'conflict_events'
    ) THEN
        RAISE NOTICE 'Old conflict_events table found - will be archived after migration';
    ELSE
        RAISE NOTICE 'No existing conflict_events table found';
    END IF;
END $$;

-- ================================================
-- EXTENSIONS
-- ================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

-- Set timezone
SET timezone = 'UTC';

-- ================================================
-- REFERENCE TABLES
-- ================================================

-- --------------------------------------------------------
-- Table: actors
-- Purpose: Armed groups, security forces, civilians, etc.
-- --------------------------------------------------------
CREATE TABLE actors (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_actors_title ON actors(title);

-- Insert actor types
INSERT INTO actors (id, title, created_at, updated_at) VALUES
(1, 'Armed Robber(s)', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(2, 'Bandits', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(3, 'Boko Haram', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(4, 'Civilian(s)', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(5, 'Ethnic Groups', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(6, 'Farmer(s)', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(7, 'Gunmen', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(8, 'Herder(s)', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(9, 'Hoodlums', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(10, 'ISWAP', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(11, 'Informal Security Actors', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(12, 'IPOB/ESN', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(13, 'Jama''atu Ansarul', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(14, 'Kidnappers', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(15, 'Lukarawa', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(16, 'Mahmuda', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(17, 'Maritime Pirates', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(18, 'Mob', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(19, 'Protesters', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(20, 'Religious Groups', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(21, 'Security Forces', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(22, 'N/A', NULL, NULL),
(23, 'Farmers(s)', NULL, NULL),
(24, 'Cultists', NULL, NULL),
(25, 'Militant(s)', NULL, NULL),
(26, 'Hoodlums', NULL, NULL),
(27, 'Neighbours', NULL, NULL),
(28, 'Ritualists', NULL, NULL),
(29, 'Assassins', NULL, NULL),
(30, 'Husband', NULL, NULL),
(31, 'Child', NULL, NULL),
(32, 'Children', NULL, NULL),
(33, 'Group', NULL, NULL);

-- Reset sequence to max ID
SELECT setval('actors_id_seq', (SELECT MAX(id) FROM actors));

-- --------------------------------------------------------
-- Table: conflict_types
-- Purpose: Taxonomy of violence types
-- --------------------------------------------------------
CREATE TABLE conflict_types (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conflict_types_title ON conflict_types(title);

INSERT INTO conflict_types (id, title, created_at, updated_at) VALUES
(1, 'Armed Clash', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(2, 'Banditry', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(3, 'Communal', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(4, 'Cultism', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(5, 'Extrajudicial Killing', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(6, 'Farmer-Herder', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(7, 'Gang Violence', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(8, 'General', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(9, 'Kidnapping', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(10, 'Maritime Piracy', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(11, 'Oil Theft', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(12, 'Terrorism', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(13, 'Vigilante', '2026-01-25 10:22:28', '2026-01-25 10:22:28');

SELECT setval('conflict_types_id_seq', (SELECT MAX(id) FROM conflict_types));

-- --------------------------------------------------------
-- Table: countries
-- Purpose: Country reference (currently only Nigeria)
-- --------------------------------------------------------
CREATE TABLE countries (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO countries (id, name, created_at, updated_at) VALUES
(1, 'Nigeria', '2026-01-25 10:22:28', '2026-01-25 10:22:28');

SELECT setval('countries_id_seq', (SELECT MAX(id) FROM countries));

-- --------------------------------------------------------
-- Table: regions
-- Purpose: Nigeria's 6 geo-political zones
-- --------------------------------------------------------
CREATE TABLE regions (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_regions_name ON regions(name);

INSERT INTO regions (id, name, created_at, updated_at) VALUES
(1, 'North East', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(2, 'North Central', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(3, 'North West', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(4, 'South East', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(5, 'South South', '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(6, 'South West', '2026-01-25 10:22:28', '2026-01-25 10:22:28');

SELECT setval('regions_id_seq', (SELECT MAX(id) FROM regions));

-- --------------------------------------------------------
-- Table: states
-- Purpose: Nigeria's 37 states (36 + FCT)
-- --------------------------------------------------------
CREATE TABLE states (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    region_id BIGINT REFERENCES regions(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_states_name ON states(name);
CREATE INDEX idx_states_region_id ON states(region_id);

INSERT INTO states (id, name, region_id, created_at, updated_at) VALUES
(1, 'Adamawa', 1, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(2, 'Bauchi', 1, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(3, 'Borno', 1, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(4, 'Gombe', 1, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(5, 'Taraba', 1, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(6, 'Yobe', 1, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(7, 'Benue', 2, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(8, 'FCT', 2, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(9, 'Kogi', 2, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(10, 'Kwara', 2, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(11, 'Niger', 2, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(12, 'Nasarawa', 2, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(13, 'Plateau', 2, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(14, 'Jigawa', 3, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(15, 'Kaduna', 3, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(16, 'Kano', 3, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(17, 'Katsina', 3, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(18, 'Kebbi', 3, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(19, 'Sokoto', 3, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(20, 'Zamfara', 3, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(21, 'Abia', 4, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(22, 'Anambra', 4, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(23, 'Ebonyi', 4, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(24, 'Enugu', 4, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(25, 'Imo', 4, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(26, 'Akwa Ibom', 5, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(27, 'Bayelsa', 5, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(28, 'Cross River', 5, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(29, 'Delta', 5, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(30, 'Edo', 5, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(31, 'Rivers', 5, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(32, 'Ekiti', 6, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(33, 'Lagos', 6, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(34, 'Ogun', 6, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(35, 'Ondo', 6, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(36, 'Osun', 6, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(37, 'Oyo', 6, '2026-01-25 10:22:28', '2026-01-25 10:22:28');

SELECT setval('states_id_seq', (SELECT MAX(id) FROM states));

-- --------------------------------------------------------
-- Table: lgas
-- Purpose: Local Government Areas (794 LGAs)
-- NOTE: Full INSERT statements for all 794 LGAs will be added here
-- This is a subset for schema validation
-- --------------------------------------------------------
CREATE TABLE lgas (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    state_id BIGINT REFERENCES states(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_lgas_name ON lgas(name);
CREATE INDEX idx_lgas_state_id ON lgas(state_id);

-- Sample LGAs (first 20 - full list of 794 will be in separate migration file)
INSERT INTO lgas (id, name, state_id, created_at, updated_at) VALUES
(17, 'Shelleng', 1, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(48, 'Damboa', 3, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(44, 'Banki', 3, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(50, 'Foduma Kolowombe', 3, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(52, 'Gamboru Ngala', 3, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(57, 'Konduga', 3, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(65, 'Mafa', 3, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(67, 'Monguno', 3, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(126, 'Gwer East', 7, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(207, 'Rijau', 11, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(213, 'Mangu', 13, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(268, 'Kachia', 15, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(272, 'Kajuru', 15, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(340, 'Kadisau', 17, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(349, 'Kusada', 17, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(775, 'Kankara', 17, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(776, 'Maru', 20, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(470, 'Ikwo', 23, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(494, 'Isu', 25, '2026-01-25 10:22:28', '2026-01-25 10:22:28'),
(781, 'Ika', 26, '2026-01-25 10:22:28', '2026-01-25 10:22:28');

-- NOTE: Full 794 LGA list will be loaded from separate data file

-- ================================================
-- MAIN CONFLICT EVENTS TABLE
-- ================================================

CREATE TABLE conflicts (
    id BIGSERIAL PRIMARY KEY,
    
    -- Date and Classification
    incidence_date DATE NOT NULL,
    conflict_type_id BIGINT REFERENCES conflict_types(id) ON DELETE SET NULL,
    
    -- Location Hierarchy
    country_id BIGINT REFERENCES countries(id) ON DELETE SET NULL,
    region_id BIGINT REFERENCES regions(id) ON DELETE SET NULL,
    state_id BIGINT REFERENCES states(id) ON DELETE SET NULL,
    lga_id BIGINT REFERENCES lgas(id) ON DELETE SET NULL,
    community VARCHAR(255),
    
    -- Casualties: Civilian Deaths (Gender-Disaggregated)
    civilian_death_male INTEGER DEFAULT 0,
    civilian_death_female INTEGER DEFAULT 0,
    civilian_death_unknown INTEGER DEFAULT 0,
    
    -- Casualties: Security Forces Deaths (Gender-Disaggregated)
    security_death_male INTEGER DEFAULT 0,
    security_death_female INTEGER DEFAULT 0,
    security_death_unknown INTEGER DEFAULT 0,
    
    -- Casualties: Injured (Gender-Disaggregated)
    injured_male INTEGER DEFAULT 0,
    injured_female INTEGER DEFAULT 0,
    injured_unknown INTEGER DEFAULT 0,
    
    -- Casualties: Kidnapped (Gender-Disaggregated)
    kidnapped_male INTEGER DEFAULT 0,
    kidnapped_female INTEGER DEFAULT 0,
    kidnapped_unknown INTEGER DEFAULT 0,
    
    -- Displacement
    displaced_persons VARCHAR(10) CHECK (displaced_persons IN ('Yes', 'No')),
    displaced_male INTEGER DEFAULT 0,
    displaced_female INTEGER DEFAULT 0,
    
    -- Actors (up to 3 actors per conflict)
    actor_1 BIGINT REFERENCES actors(id) ON DELETE SET NULL,
    actor_2 BIGINT REFERENCES actors(id) ON DELETE SET NULL,
    actor_3 BIGINT REFERENCES actors(id) ON DELETE SET NULL,
    
    -- Event Details
    description TEXT,
    action TEXT,
    highway_roads_water TEXT,
    
    -- Data Quality and Verification
    confirmation_verification VARCHAR(255),
    verification_level VARCHAR(255),
    source_url TEXT,
    source_contact_details TEXT,
    source_contact_pictures VARCHAR(255),
    source_metadata TEXT,
    data_source VARCHAR(255),
    
    -- Reporter (user who entered this data)
    reporter_id BIGINT, -- Will link to users table
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP -- Soft delete support
);

-- ================================================
-- INDEXES FOR PERFORMANCE
-- ================================================

-- Date-based queries (time-series analysis)
CREATE INDEX idx_conflicts_incidence_date ON conflicts(incidence_date);
CREATE INDEX idx_conflicts_created_at ON conflicts(created_at);

-- Location-based queries
CREATE INDEX idx_conflicts_country_id ON conflicts(country_id);
CREATE INDEX idx_conflicts_region_id ON conflicts(region_id);
CREATE INDEX idx_conflicts_state_id ON conflicts(state_id);
CREATE INDEX idx_conflicts_lga_id ON conflicts(lga_id);
CREATE INDEX idx_conflicts_community ON conflicts(community);

-- Classification queries
CREATE INDEX idx_conflicts_conflict_type_id ON conflicts(conflict_type_id);

-- Actor-based queries
CREATE INDEX idx_conflicts_actor_1 ON conflicts(actor_1);
CREATE INDEX idx_conflicts_actor_2 ON conflicts(actor_2);
CREATE INDEX idx_conflicts_actor_3 ON conflicts(actor_3);

-- Verification queries
CREATE INDEX idx_conflicts_verification_level ON conflicts(verification_level);

-- Soft delete support
CREATE INDEX idx_conflicts_deleted_at ON conflicts(deleted_at);

-- Composite index for common queries (state + date range)
CREATE INDEX idx_conflicts_state_date ON conflicts(state_id, incidence_date);

-- Composite index for actor analysis (actor + date)
CREATE INDEX idx_conflicts_actor1_date ON conflicts(actor_1, incidence_date);

-- ================================================
-- USER MANAGEMENT TABLES (Laravel-compatible)
-- ================================================

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    email_verified_at TIMESTAMP,
    password VARCHAR(255) NOT NULL,
    remember_token VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- --------------------------------------------------------
-- Password reset tokens
-- --------------------------------------------------------
CREATE TABLE password_reset_tokens (
    email VARCHAR(255) PRIMARY KEY,
    token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP
);

CREATE INDEX idx_password_reset_tokens_email ON password_reset_tokens(email);

-- --------------------------------------------------------
-- Personal access tokens (API authentication)
-- --------------------------------------------------------
CREATE TABLE personal_access_tokens (
    id BIGSERIAL PRIMARY KEY,
    tokenable_type VARCHAR(255) NOT NULL,
    tokenable_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    token VARCHAR(64) UNIQUE NOT NULL,
    abilities TEXT,
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_personal_access_tokens_tokenable ON personal_access_tokens(tokenable_type, tokenable_id);
CREATE INDEX idx_personal_access_tokens_token ON personal_access_tokens(token);

-- ================================================
-- LARAVEL SYSTEM TABLES
-- ================================================

-- Cache table
CREATE TABLE cache (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT NOT NULL,
    expiration INTEGER NOT NULL
);

CREATE INDEX idx_cache_expiration ON cache(expiration);

-- Cache locks
CREATE TABLE cache_locks (
    key VARCHAR(255) PRIMARY KEY,
    owner VARCHAR(255) NOT NULL,
    expiration INTEGER NOT NULL
);

-- Failed jobs (queue)
CREATE TABLE failed_jobs (
    id BIGSERIAL PRIMARY KEY,
    uuid VARCHAR(255) UNIQUE NOT NULL,
    connection TEXT NOT NULL,
    queue TEXT NOT NULL,
    payload TEXT NOT NULL,
    exception TEXT NOT NULL,
    failed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_failed_jobs_uuid ON failed_jobs(uuid);

-- Jobs queue
CREATE TABLE jobs (
    id BIGSERIAL PRIMARY KEY,
    queue VARCHAR(255) NOT NULL,
    payload TEXT NOT NULL,
    attempts SMALLINT NOT NULL,
    reserved_at INTEGER,
    available_at INTEGER NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE INDEX idx_jobs_queue ON jobs(queue);

-- Job batches
CREATE TABLE job_batches (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    total_jobs INTEGER NOT NULL,
    pending_jobs INTEGER NOT NULL,
    failed_jobs INTEGER NOT NULL,
    failed_job_ids TEXT NOT NULL,
    options TEXT,
    cancelled_at INTEGER,
    created_at INTEGER NOT NULL,
    finished_at INTEGER
);

-- Migrations tracking
CREATE TABLE migrations (
    id SERIAL PRIMARY KEY,
    migration VARCHAR(255) NOT NULL,
    batch INTEGER NOT NULL
);

-- Sessions (if using database sessions)
CREATE TABLE sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id BIGINT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    payload TEXT NOT NULL,
    last_activity INTEGER NOT NULL
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_last_activity ON sessions(last_activity);

-- ================================================
-- COMPUTED COLUMNS / VIEWS (for convenience)
-- ================================================

-- View: Total deaths per conflict
CREATE OR REPLACE VIEW conflicts_with_totals AS
SELECT 
    c.*,
    (COALESCE(c.civilian_death_male, 0) + 
     COALESCE(c.civilian_death_female, 0) + 
     COALESCE(c.civilian_death_unknown, 0)) AS total_civilian_deaths,
    
    (COALESCE(c.security_death_male, 0) + 
     COALESCE(c.security_death_female, 0) + 
     COALESCE(c.security_death_unknown, 0)) AS total_security_deaths,
    
    (COALESCE(c.injured_male, 0) + 
     COALESCE(c.injured_female, 0) + 
     COALESCE(c.injured_unknown, 0)) AS total_injured,
    
    (COALESCE(c.kidnapped_male, 0) + 
     COALESCE(c.kidnapped_female, 0) + 
     COALESCE(c.kidnapped_unknown, 0)) AS total_kidnapped,
    
    (COALESCE(c.civilian_death_male, 0) + 
     COALESCE(c.civilian_death_female, 0) + 
     COALESCE(c.civilian_death_unknown, 0) +
     COALESCE(c.security_death_male, 0) + 
     COALESCE(c.security_death_female, 0) + 
     COALESCE(c.security_death_unknown, 0)) AS total_deaths
FROM conflicts c;

-- ================================================
-- TRIGGERS (auto-update timestamps)
-- ================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_actors_updated_at BEFORE UPDATE ON actors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conflict_types_updated_at BEFORE UPDATE ON conflict_types
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_countries_updated_at BEFORE UPDATE ON countries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_regions_updated_at BEFORE UPDATE ON regions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_states_updated_at BEFORE UPDATE ON states
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lgas_updated_at BEFORE UPDATE ON lgas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conflicts_updated_at BEFORE UPDATE ON conflicts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- GRANTS (adjust based on your user setup)
-- ================================================

-- Grant permissions to neondb_owner (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO neondb_owner;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO neondb_owner;

-- ================================================
-- SCHEMA MIGRATION COMPLETE
-- ================================================

-- To verify the schema:
-- \dt -- List all tables
-- \d conflicts -- Describe conflicts table
-- SELECT COUNT(*) FROM actors; -- Should return 33
-- SELECT COUNT(*) FROM conflict_types; -- Should return 13
-- SELECT COUNT(*) FROM regions; -- Should return 6
-- SELECT COUNT(*) FROM states; -- Should return 37
