-- Nigeria Conflict Tracker - Complete Database Schema
-- This file contains all table definitions, indexes, and constraints
-- Generated: 2026-02-09
-- Usage: psql -f schema_dump.sql -d your_database

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================
-- AUTH TABLES (Migration 001)
-- ============================================================

CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public.users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    success BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- CONFLICT TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS public.conflict_events (
    id SERIAL PRIMARY KEY,
    event_date DATE NOT NULL,
    location_latitude DECIMAL(10, 8),
    location_longitude DECIMAL(11, 8),
    state VARCHAR(100),
    lga VARCHAR(100),
    conflict_type VARCHAR(255),
    notes TEXT,
    civilian_death_male INTEGER DEFAULT 0,
    civilian_death_female INTEGER DEFAULT 0,
    civilian_death_unknown INTEGER DEFAULT 0,
    security_death_male INTEGER DEFAULT 0,
    security_death_female INTEGER DEFAULT 0,
    security_death_unknown INTEGER DEFAULT 0,
    displaced_male INTEGER DEFAULT 0,
    displaced_female INTEGER DEFAULT 0,
    displaced_unknown INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- DATA QUALITY METRICS (Migration 002)
-- ============================================================

CREATE TABLE IF NOT EXISTS public.data_quality_metrics (
    id SERIAL PRIMARY KEY,
    metric_type VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10, 4),
    location VARCHAR(255),
    time_period DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- ALERT TABLES (Migration 004)
-- ============================================================

CREATE TABLE IF NOT EXISTS public.alert_events (
    id SERIAL PRIMARY KEY,
    conflict_event_id INTEGER REFERENCES public.conflict_events(id) ON DELETE SET NULL,
    alert_type VARCHAR(50) NOT NULL,
    risk_score DECIMAL(5, 2),
    priority INTEGER,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    location_state VARCHAR(100),
    location_lga VARCHAR(100),
    conflict_category VARCHAR(100),
    title TEXT NOT NULL,
    summary TEXT,
    dedup_key VARCHAR(64),
    acknowledged_at TIMESTAMP,
    acknowledged_by_user_id INTEGER REFERENCES public.users(id) ON DELETE SET NULL,
    acknowledgment_notes TEXT,
    resolved_at TIMESTAMP,
    resolved_by_user_id INTEGER REFERENCES public.users(id) ON DELETE SET NULL,
    resolution_notes TEXT,
    resolution_actions JSONB,
    notified_channels JSONB,
    notification_sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.alert_read_status (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER NOT NULL REFERENCES public.alert_events(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- AUDIT TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS public.conflict_audits (
    id SERIAL PRIMARY KEY,
    conflict_id INTEGER NOT NULL REFERENCES public.conflict_events(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES public.users(id) ON DELETE SET NULL,
    action VARCHAR(20) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- FORECAST TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS public.forecasts (
    id SERIAL PRIMARY KEY,
    location_type VARCHAR(50) NOT NULL,
    location_name VARCHAR(255) NOT NULL,
    forecast_date TIMESTAMP NOT NULL,
    predicted_incidents DECIMAL(10, 2),
    confidence_lower DECIMAL(10, 2),
    confidence_upper DECIMAL(10, 2),
    confidence_level DECIMAL(5, 2),
    model_type VARCHAR(50),
    forecast_horizon_weeks INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(location_type, location_name, forecast_date)
);

-- ============================================================
-- LOCATIONS TABLE (Migration 006)
-- ============================================================

CREATE TABLE IF NOT EXISTS public.locations (
    id SERIAL PRIMARY KEY,
    location_type VARCHAR(50) NOT NULL,
    state_name VARCHAR(100),
    lga_name VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    geometry GEOGRAPHY(POINT, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- PERFORMANCE INDEXES (Migration 005)
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON public.users(role);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON public.sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_conflicts_event_date ON public.conflict_events(event_date);
CREATE INDEX IF NOT EXISTS idx_conflicts_state ON public.conflict_events(state);
CREATE INDEX IF NOT EXISTS idx_conflicts_lga ON public.conflict_events(lga);
CREATE INDEX IF NOT EXISTS idx_conflicts_composite_state_date ON public.conflict_events(state, event_date);

CREATE INDEX IF NOT EXISTS idx_alerts_status ON public.alert_events(status);
CREATE INDEX IF NOT EXISTS idx_alerts_priority ON public.alert_events(priority);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON public.alert_events(created_at);
CREATE INDEX IF NOT EXISTS idx_alerts_state ON public.alert_events(location_state);
CREATE INDEX IF NOT EXISTS idx_alerts_dedup ON public.alert_events(dedup_key);

CREATE INDEX IF NOT EXISTS idx_forecasts_location ON public.forecasts(location_type, location_name);
CREATE INDEX IF NOT EXISTS idx_forecasts_date ON public.forecasts(forecast_date);

CREATE INDEX IF NOT EXISTS idx_locations_state ON public.locations(state_name);
CREATE INDEX IF NOT EXISTS idx_locations_type ON public.locations(location_type);
CREATE INDEX IF NOT EXISTS idx_locations_geometry ON public.locations USING GIST(geometry);

-- ============================================================
-- GRANT PERMISSIONS
-- ============================================================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO postgres;

-- ============================================================
-- SCHEMA INFO
-- ============================================================

COMMENT ON TABLE public.conflict_events IS 'Main table for conflict incident data across Nigeria';
COMMENT ON TABLE public.alert_events IS 'High-risk alerts generated from conflicts';
COMMENT ON TABLE public.forecasts IS 'Predictive forecasts for conflict incidents';
COMMENT ON TABLE public.locations IS 'Geographic locations including states and LGAs';
COMMENT ON TABLE public.users IS 'System users with role-based access control';

-- ============================================================
-- END OF SCHEMA
-- ============================================================
