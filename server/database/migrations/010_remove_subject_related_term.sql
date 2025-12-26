-- Migration: Remove subject_related_term table
-- Subject matching now uses CAH codes from subject_course_mapping instead of related terms

-- ============================================
-- 1. Drop subject_related_term table
-- ============================================
DROP TABLE IF EXISTS subject_related_term CASCADE;

-- ============================================
-- 2. Update comments (handle both old and new table names)
-- ============================================
DO $$
BEGIN
    -- Update comment on the table (check which name exists)
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE information_schema.tables.table_name = 'uni_recomm_subject_course_mapping') THEN
        COMMENT ON TABLE uni_recomm_subject_course_mapping IS 'Mapping table from A-Level subject names to CAH codes. Used for subject matching in recommendation engine.';
    ELSIF EXISTS (SELECT 1 FROM information_schema.tables WHERE information_schema.tables.table_name = 'subject_course_mapping') THEN
        COMMENT ON TABLE subject_course_mapping IS 'Mapping table from A-Level subject names to CAH codes. Used for subject matching in recommendation engine.';
    END IF;
END $$;

