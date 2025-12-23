-- Migration: Add HESA data links to course table
-- This allows us to link courses back to HESA kiscourse data for employment/salary/job outcomes

ALTER TABLE course
ADD COLUMN IF NOT EXISTS pubukprn VARCHAR(10),
ADD COLUMN IF NOT EXISTS kiscourseid VARCHAR(50),
ADD COLUMN IF NOT EXISTS kismode VARCHAR(2);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_course_hesa_link ON course(pubukprn, kiscourseid, kismode);

COMMENT ON COLUMN course.pubukprn IS 'HESA Published UK Provider Reference Number - links to kiscourse table';
COMMENT ON COLUMN course.kiscourseid IS 'HESA KIS Course ID - links to kiscourse table';
COMMENT ON COLUMN course.kismode IS 'HESA KIS Mode (01=Full-time, 02=Part-time) - links to kiscourse table';
