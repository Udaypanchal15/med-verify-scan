-- Fix email case-sensitivity issue
-- This script fixes the existing users table to support case-insensitive email lookups

-- Step 1: Remove the old UNIQUE constraint if it exists
ALTER TABLE IF EXISTS users DROP CONSTRAINT IF EXISTS users_email_key CASCADE;

-- Step 2: Create case-insensitive unique index
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_lower ON users (LOWER(email));

-- Step 3: Normalize all existing emails to lowercase
UPDATE users SET email = LOWER(email) WHERE email != LOWER(email);

-- Verify the fix
-- SELECT COUNT(*) as total_users FROM users;
-- SELECT email FROM users ORDER BY email;
