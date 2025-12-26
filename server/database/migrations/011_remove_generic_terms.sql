-- Migration: Remove generic_term and generic_term_rule tables
-- Subject matching now uses CAH codes from subject_course_mapping instead

-- ============================================
-- 1. Drop generic_term_rule table first (has foreign key)
-- ============================================
DROP TABLE IF EXISTS generic_term_rule CASCADE;

-- ============================================
-- 2. Drop generic_term table
-- ============================================
DROP TABLE IF EXISTS generic_term CASCADE;

-- ============================================
-- 3. Update comments (handle both old and new table names)
-- ============================================
DO $$
BEGIN
    -- Update comment on the table (check which name exists)
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE information_schema.tables.table_name = 'uni_recomm_subject_course_mapping') THEN
        COMMENT ON TABLE uni_recomm_subject_course_mapping IS 'Mapping table from A-Level subject names to CAH codes. Used for subject matching in recommendation engine via CAH codes.';
    ELSIF EXISTS (SELECT 1 FROM information_schema.tables WHERE information_schema.tables.table_name = 'subject_course_mapping') THEN
        COMMENT ON TABLE subject_course_mapping IS 'Mapping table from A-Level subject names to CAH codes. Used for subject matching in recommendation engine via CAH codes.';
    END IF;
END $$;

