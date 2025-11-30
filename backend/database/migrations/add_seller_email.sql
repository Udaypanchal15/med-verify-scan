-- Add missing email column to sellers table
ALTER TABLE sellers
ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE;

-- Create index for email if not exists
CREATE UNIQUE INDEX IF NOT EXISTS idx_sellers_email_lower ON sellers (LOWER(email));
