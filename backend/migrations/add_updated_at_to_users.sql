-- Migration: Add updated_at column to users table
-- Date: 2026-02-08
-- Fixes: PostgreSQL trigger error "record 'new' has no field 'updated_at'"

-- Add updated_at column with default value
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL;

-- Update existing rows to set updated_at = created_at
UPDATE users 
SET updated_at = created_at 
WHERE updated_at IS NULL;

-- Verify the column was added
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'users' 
  AND column_name = 'updated_at';
