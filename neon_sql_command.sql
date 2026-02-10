-- Update user role for info@thenextier.com to give full access
-- Run this command in your Neon PostgreSQL console

UPDATE users 
SET role = 'analyst', updated_at = NOW()
WHERE email = 'info@thenextier.com';

-- Verify the update
SELECT id, email, role, created_at, updated_at 
FROM users 
WHERE email = 'info@thenextier.com';
