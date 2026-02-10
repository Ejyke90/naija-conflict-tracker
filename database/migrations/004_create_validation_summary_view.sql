-- Create Validation Summary View for Verification System
-- This view provides high-performance summary data for the validation queue

-- First, ensure the conflicts table has the required verification columns
DO $$
BEGIN
    -- Check if verified column exists, add if it doesn't
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'conflicts' AND column_name = 'verified'
    ) THEN
        ALTER TABLE conflicts ADD COLUMN verified BOOLEAN DEFAULT FALSE;
    END IF;
    
    -- Check if verification_level column exists, add if it doesn't
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'conflicts' AND column_name = 'verification_level'
    ) THEN
        ALTER TABLE conflicts ADD COLUMN verification_level VARCHAR(20) DEFAULT 'Unverified';
    END IF;
    
    -- Check if priority column exists, add if it doesn't
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'conflicts' AND column_name = 'priority'
    ) THEN
        ALTER TABLE conflicts ADD COLUMN priority VARCHAR(10) DEFAULT 'medium';
    END IF;
    
    -- Add indexes for performance
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'conflicts' AND indexname = 'idx_conflicts_verified'
    ) THEN
        CREATE INDEX idx_conflicts_verified ON conflicts(verified);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'conflicts' AND indexname = 'idx_conflicts_priority'
    ) THEN
        CREATE INDEX idx_conflicts_priority ON conflicts(priority);
    END IF;
END $$;

-- Create or replace the validation_summary view
CREATE OR REPLACE VIEW validation_summary AS
SELECT 
    -- Count of pending (unverified) conflicts
    COUNT(CASE WHEN verified = false THEN 1 END) as pending_count,
    
    -- Urgent logic: more than 5 high-priority unverified items
    COUNT(CASE WHEN priority = 'high' AND verified = false THEN 1 END) > 5 as is_urgent_logic,
    
    -- Count of high-priority unverified conflicts
    COUNT(CASE WHEN priority = 'high' AND verified = false THEN 1 END) as high_priority_count,
    
    -- Last verification activity (most recent verified timestamp)
    MAX(updated_at) FILTER (WHERE verified = true) as last_validation,
    
    -- Total count of verified conflicts
    COUNT(CASE WHEN verified = true THEN 1 END) as verified_count,
    
    -- Oldest pending item (earliest created timestamp of unverified)
    MIN(created_at) FILTER (WHERE verified = false) as oldest_pending
FROM conflicts;

-- Create a function to update priority based on severity
CREATE OR REPLACE FUNCTION update_conflict_priority()
RETURNS TRIGGER AS $$
BEGIN
    -- Auto-calculate priority based on casualties
    IF NEW.civilian_death_male + NEW.civilian_death_female + NEW.civilian_death_unknown +
       NEW.security_death_male + NEW.security_death_female + NEW.security_death_unknown >= 5 THEN
        NEW.priority = 'high';
    ELSIF NEW.kidnapped_male + NEW.kidnapped_female + NEW.kidnapped_unknown >= 3 THEN
        NEW.priority = 'high';
    ELSIF NEW.civilian_death_male + NEW.civilian_death_female + NEW.civilian_death_unknown +
           NEW.security_death_male + NEW.security_death_female + NEW.security_death_unknown > 0 OR
           NEW.kidnapped_male + NEW.kidnapped_female + NEW.kidnapped_unknown > 0 THEN
        NEW.priority = 'medium';
    ELSE
        NEW.priority = 'low';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update priority
DROP TRIGGER IF EXISTS trigger_update_conflict_priority ON conflicts;
CREATE TRIGGER trigger_update_conflict_priority
    BEFORE INSERT OR UPDATE ON conflicts
    FOR EACH ROW EXECUTE FUNCTION update_conflict_priority();

-- Create audit_log table if it doesn't exist (for verification tracking)
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    action VARCHAR(50) NOT NULL,
    resource VARCHAR(50) NOT NULL,
    details JSONB,
    success BOOLEAN DEFAULT true,
    timestamp TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for audit_log performance
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);

-- Update existing conflicts to have proper priority based on current data
UPDATE conflicts 
SET priority = CASE 
    WHEN (civilian_death_male + civilian_death_female + civilian_death_unknown +
          security_death_male + security_death_female + security_death_unknown) >= 5 THEN 'high'
    WHEN (kidnapped_male + kidnapped_female + kidnapped_unknown) >= 3 THEN 'high'
    WHEN (civilian_death_male + civilian_death_female + civilian_death_unknown +
          security_death_male + security_death_female + security_death_unknown) > 0 OR
          (kidnapped_male + kidnapped_female + kidnapped_unknown) > 0 THEN 'medium'
    ELSE 'low'
END
WHERE priority IS NULL OR priority = 'medium' AND verified = false;

-- Grant necessary permissions (adjust role names as needed)
-- GRANT USAGE ON SCHEMA public TO conflict_tracker_user;
-- GRANT SELECT ON validation_summary TO conflict_tracker_user;
-- GRANT SELECT, INSERT, UPDATE ON conflicts TO conflict_tracker_user;
-- GRANT SELECT, INSERT ON audit_log TO conflict_tracker_user;

COMMENT ON VIEW validation_summary IS 'High-performance summary view for conflict verification queue';
COMMENT ON TABLE audit_log IS 'Audit trail for all system actions including verifications';
