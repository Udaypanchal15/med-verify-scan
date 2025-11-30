-- ================================================
-- Migration: Add Missing Columns to Sellers Table
-- ================================================
-- This script adds columns that are in schema.sql but missing from the actual database

-- Check if columns exist before adding them
-- license_type column
ALTER TABLE sellers 
ADD COLUMN IF NOT EXISTS license_type VARCHAR(100);

-- license_expiry column
ALTER TABLE sellers 
ADD COLUMN IF NOT EXISTS license_expiry DATE;

-- gstin column
ALTER TABLE sellers 
ADD COLUMN IF NOT EXISTS gstin VARCHAR(50);

-- address column
ALTER TABLE sellers 
ADD COLUMN IF NOT EXISTS address TEXT;

-- authorized_person column
ALTER TABLE sellers 
ADD COLUMN IF NOT EXISTS authorized_person VARCHAR(255);

-- authorized_person_contact column
ALTER TABLE sellers 
ADD COLUMN IF NOT EXISTS authorized_person_contact VARCHAR(20);

-- company_website column
ALTER TABLE sellers 
ADD COLUMN IF NOT EXISTS company_website TEXT;

-- public_key column
ALTER TABLE sellers 
ADD COLUMN IF NOT EXISTS public_key TEXT;

-- docs_url column
ALTER TABLE sellers 
ADD COLUMN IF NOT EXISTS docs_url TEXT;

-- documents column (JSONB)
ALTER TABLE sellers 
ADD COLUMN IF NOT EXISTS documents JSONB;

-- document_checksums column (JSONB)
ALTER TABLE sellers 
ADD COLUMN IF NOT EXISTS document_checksums JSONB;

-- approved_at column
ALTER TABLE sellers 
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP WITH TIME ZONE;

-- approved_by column
ALTER TABLE sellers 
ADD COLUMN IF NOT EXISTS approved_by UUID REFERENCES users(id);

-- ================================================
-- Verify columns were added
-- ================================================
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'sellers'
ORDER BY ordinal_position;

-- ================================================
-- Commit transaction
-- ================================================
COMMIT;
