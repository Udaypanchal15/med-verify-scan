-- Migration: Add approval status to medicines table
-- This allows admin to approve/reject medicines submitted by sellers

ALTER TABLE medicines 
ADD COLUMN IF NOT EXISTS approval_status VARCHAR(50) DEFAULT 'pending' 
CHECK (approval_status IN ('pending', 'approved', 'rejected'));

ALTER TABLE medicines 
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE medicines 
ADD COLUMN IF NOT EXISTS approved_by UUID REFERENCES users(id);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_medicines_approval_status ON medicines(approval_status);

-- Update existing medicines to 'approved' if they were created before this migration
UPDATE medicines SET approval_status = 'approved' WHERE approval_status IS NULL;



