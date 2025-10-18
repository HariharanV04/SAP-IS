-- Migration: Add polling control column to iflow_jobs table
-- Date: 2025-10-17
-- Purpose: Add is_polling_active flag to control frontend polling

-- Add is_polling_active column to iflow_jobs table
ALTER TABLE iflow_jobs
ADD COLUMN IF NOT EXISTS is_polling_active BOOLEAN DEFAULT false;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_iflow_jobs_is_polling_active
ON iflow_jobs(is_polling_active)
WHERE is_polling_active = true;

-- Add comment for documentation
COMMENT ON COLUMN iflow_jobs.is_polling_active IS
'Flag to control frontend polling. Set to true when iFlow generation starts, false when completed/failed.';

-- Update existing jobs to set is_polling_active based on status
UPDATE iflow_jobs
SET is_polling_active = true
WHERE status IN ('processing', 'analyzing', 'generating')
AND is_polling_active IS NULL;

UPDATE iflow_jobs
SET is_polling_active = false
WHERE status IN ('completed', 'failed', 'cancelled', 'pending')
AND is_polling_active IS NULL;
