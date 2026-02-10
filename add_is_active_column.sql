-- Add is_active column to users table for proper authentication
-- This fixes the 401 error in the Incident Review Queue

-- Add the is_active column with default value true
ALTER TABLE users 
ADD COLUMN is_active BOOLEAN DEFAULT true;

-- Update existing users to be active by default
UPDATE users 
SET is_active = true 
WHERE is_active IS NULL;

-- Add index for better performance on user status queries
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Verify the changes
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'is_active';
