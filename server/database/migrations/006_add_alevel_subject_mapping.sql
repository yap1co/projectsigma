-- Migration: Add A-Level Subject to CAH Code Mapping
-- This migration adds support for mapping A-Level subjects to CAH codes

-- ============================================
-- 1. Create A-Level Subject Mapping Table
-- ============================================
-- This table stores the mapping from A-Level subject names to CAH codes
CREATE TABLE IF NOT EXISTS subject_course_mapping (
    mapping_id SERIAL PRIMARY KEY,
    subject_id VARCHAR(50),  -- Original subject ID from mapping file
    a_level_subject VARCHAR(255) NOT NULL,  -- Original A-Level subject name
    subject_cleaned VARCHAR(255),  -- Cleaned/normalized subject name
    hecos_code VARCHAR(20),  -- HECoS code
    hecos_label VARCHAR(255),  -- HECoS label
    cah3_code VARCHAR(50) NOT NULL,  -- CAH3 code (e.g., CAH09-01-01)
    cah3_label VARCHAR(255),  -- CAH3 label
    cah2_code VARCHAR(50),  -- CAH2 code
    cah2_label VARCHAR(255),  -- CAH2 label
    cah1_code VARCHAR(50),  -- CAH1 code
    cah1_label VARCHAR(255),  -- CAH1 label
    hecos_cah_version VARCHAR(20),  -- Version of mapping
    mapping_method VARCHAR(50),  -- How the mapping was created (rule, language, etc.)
    generated_on DATE,  -- Date mapping was generated
    UNIQUE (a_level_subject, cah3_code)  -- One A-Level subject can map to multiple CAH codes
);

COMMENT ON TABLE subject_course_mapping IS 'Mapping table from A-Level subject names to CAH codes';
COMMENT ON COLUMN subject_course_mapping.cah3_code IS 'CAH3 code (e.g., CAH09-01-01) - used to link to sbj table';
COMMENT ON COLUMN subject_course_mapping.a_level_subject IS 'Original A-Level subject name as provided by students';

CREATE INDEX idx_subject_course_mapping_cah3 ON subject_course_mapping(cah3_code);
CREATE INDEX idx_subject_course_mapping_subject ON subject_course_mapping(a_level_subject);
CREATE INDEX idx_subject_course_mapping_cleaned ON subject_course_mapping(subject_cleaned);

-- ============================================
-- 2. Add A-Level Subject Info to sbj table
-- ============================================
-- Add columns to sbj table to store A-Level subject mappings
ALTER TABLE sbj 
    ADD COLUMN IF NOT EXISTS a_level_subjects TEXT[],  -- Array of A-Level subject names that map to this CAH code
    ADD COLUMN IF NOT EXISTS cah3_label VARCHAR(255),  -- CAH3 label for this code
    ADD COLUMN IF NOT EXISTS cah2_code VARCHAR(50),  -- CAH2 code
    ADD COLUMN IF NOT EXISTS cah2_label VARCHAR(255),  -- CAH2 label
    ADD COLUMN IF NOT EXISTS cah1_code VARCHAR(50),  -- CAH1 code
    ADD COLUMN IF NOT EXISTS cah1_label VARCHAR(255);  -- CAH1 label

COMMENT ON COLUMN sbj.a_level_subjects IS 'Array of A-Level subject names that map to this CAH code';
COMMENT ON COLUMN sbj.cah3_label IS 'CAH3 label for this subject code';

CREATE INDEX IF NOT EXISTS idx_sbj_cah3_label ON sbj(cah3_label);

-- ============================================
-- 3. Update subject table to use CAH3 codes
-- ============================================
-- Add CAH3 code column to subject table if it doesn't exist
ALTER TABLE subject 
    ADD COLUMN IF NOT EXISTS cah3_code VARCHAR(50),  -- CAH3 code (e.g., CAH09-01-01)
    ADD COLUMN IF NOT EXISTS cah3_label VARCHAR(255),  -- CAH3 label
    ADD COLUMN IF NOT EXISTS cah2_code VARCHAR(50),  -- CAH2 code
    ADD COLUMN IF NOT EXISTS cah2_label VARCHAR(255),  -- CAH2 label
    ADD COLUMN IF NOT EXISTS cah1_code VARCHAR(50),  -- CAH1 code
    ADD COLUMN IF NOT EXISTS cah1_label VARCHAR(255),  -- CAH1 label
    ADD COLUMN IF NOT EXISTS hecos_code VARCHAR(20),  -- HECoS code
    ADD COLUMN IF NOT EXISTS hecos_label VARCHAR(255);  -- HECoS label

COMMENT ON COLUMN subject.cah3_code IS 'CAH3 code linking to HESA data (sbj table)';
COMMENT ON COLUMN subject.subject_name IS 'Human-readable subject name (A-Level subject name or CAH label)';

CREATE INDEX IF NOT EXISTS idx_subject_cah3 ON subject(cah3_code);

-- ============================================
-- 4. Create view for easy querying
-- ============================================
-- View to join sbj with A-Level subject mappings
CREATE OR REPLACE VIEW sbj_with_subject_course_mapping AS
SELECT 
    s.pubukprn,
    s.ukprn,
    s.kiscourseid,
    s.kismode,
    s.sbj AS cah3_code,
    s.cah3_label,
    s.cah2_code,
    s.cah2_label,
    s.cah1_code,
    s.cah1_label,
    s.a_level_subjects,
    m.a_level_subject,
    m.subject_cleaned,
    m.hecos_code,
    m.hecos_label
FROM sbj s
LEFT JOIN subject_course_mapping m ON s.sbj = m.cah3_code;

COMMENT ON VIEW sbj_with_subject_course_mapping IS 'View joining sbj table with subject course mappings';

