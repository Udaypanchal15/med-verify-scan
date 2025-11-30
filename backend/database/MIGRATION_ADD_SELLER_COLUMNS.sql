-- ================================================
-- Migration: Add missing columns to sellers table
-- ================================================

-- STEP 1: Add missing columns to sellers table
ALTER TABLE sellers
ADD COLUMN IF NOT EXISTS license_type VARCHAR(100),
ADD COLUMN IF NOT EXISTS license_expiry DATE,
ADD COLUMN IF NOT EXISTS gstin VARCHAR(50),
ADD COLUMN IF NOT EXISTS address TEXT,
ADD COLUMN IF NOT EXISTS authorized_person VARCHAR(255),
ADD COLUMN IF NOT EXISTS authorized_person_contact VARCHAR(20),
ADD COLUMN IF NOT EXISTS company_website TEXT,
ADD COLUMN IF NOT EXISTS documents JSONB,
ADD COLUMN IF NOT EXISTS document_checksums JSONB,
ADD COLUMN IF NOT EXISTS submission_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS viewed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS verifying_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS rejected_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS admin_remarks TEXT,
ADD COLUMN IF NOT EXISTS required_changes TEXT;

-- STEP 2: Verify the columns were added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'sellers'
ORDER BY ordinal_position;

-- STEP 3: Check if license_number has unique constraint
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'sellers' AND constraint_type = 'UNIQUE';

-- STEP 4: (Optional) Check for duplicate emails in users table
-- This might be causing the "email already exists" issue
SELECT LOWER(email), COUNT(*) as count
FROM users
GROUP BY LOWER(email)
HAVING COUNT(*) > 1;

-- STEP 5: Commit changes
COMMIT;

-- ================================================
-- If you see duplicates in STEP 4, run this:
-- ================================================
-- DELETE FROM users WHERE id IN (
--   SELECT id FROM (
--     SELECT id, ROW_NUMBER() OVER (PARTITION BY LOWER(email) ORDER BY created_at DESC) as rn
--     FROM users
--   ) numbered
--   WHERE rn > 1
-- );

-- STEP 6: Verify sellers table structure now matches schema.sql
\d sellers
