-- Add role column to users table
-- This migration adds the missing 'role' column that the User model expects

-- First, update any existing invalid role values to 'viewer'
UPDATE users 
SET role = 'viewer' 
WHERE role IS NULL OR role NOT IN ('admin', 'analyst', 'viewer');

-- Add role column if it doesn't exist
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS role VARCHAR(50) NOT NULL DEFAULT 'viewer';

-- Create index for role column
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Add check constraint for valid roles (PostgreSQL doesn't support IF NOT EXISTS for constraints)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'valid_role' 
        AND connamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
    ) THEN
        ALTER TABLE users 
        ADD CONSTRAINT valid_role 
        CHECK (role IN ('admin', 'analyst', 'viewer'));
    END IF;
END $$;
