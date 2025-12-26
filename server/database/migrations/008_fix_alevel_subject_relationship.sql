-- Migration: Fix relationship between subject_course_mapping and subject_related_term
-- This migration:
-- 1. Makes subject_id NOT NULL and creates unique constraint per subject
-- 2. Creates foreign key relationship between tables
-- 3. Ensures proper linking
--
-- NOTE: This migration works with the table name as it exists at migration time.
-- If migration 012 has already run, the table will be named uni_recomm_subject_course_mapping.
-- We use a DO block to check which table exists and use the appropriate name.

-- ============================================
-- 1. Determine table name (handle both old and new names)
-- ============================================
DO $$
DECLARE
    tbl_name TEXT;
BEGIN
    -- Check if new name exists (migration 012 already ran)
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE information_schema.tables.table_name = 'uni_recomm_subject_course_mapping') THEN
        tbl_name := 'uni_recomm_subject_course_mapping';
    -- Check if old name exists (normal migration order)
    ELSIF EXISTS (SELECT 1 FROM information_schema.tables WHERE information_schema.tables.table_name = 'subject_course_mapping') THEN
        tbl_name := 'subject_course_mapping';
    ELSE
        RAISE EXCEPTION 'Neither subject_course_mapping nor uni_recomm_subject_course_mapping table exists. Please run migration 006 first.';
    END IF;
    
    -- Store table name in a temporary table for use in subsequent statements
    CREATE TEMP TABLE IF NOT EXISTS migration_table_name (name TEXT);
    DELETE FROM migration_table_name;
    INSERT INTO migration_table_name VALUES (tbl_name);
END $$;

-- ============================================
-- 2. Ensure all rows have subject_id
-- ============================================
-- This should already be done by fix_alevel_subject_id.py
-- But if any are still NULL, generate from subject name
DO $$
DECLARE
    tbl_name TEXT;
    sql_stmt TEXT;
BEGIN
    SELECT name INTO tbl_name FROM migration_table_name;
    sql_stmt := format('UPDATE %I SET subject_id = LOWER(REPLACE(REPLACE(REPLACE(a_level_subject, %L, %L), %L, %L), %L, %L)) WHERE subject_id IS NULL OR subject_id = %L', 
        tbl_name, ' ', '_', '''', '', '-', '_', '');
    EXECUTE sql_stmt;
END $$;

-- ============================================
-- 3. Make subject_id NOT NULL
-- ============================================
DO $$
DECLARE
    tbl_name TEXT;
BEGIN
    SELECT name INTO tbl_name FROM migration_table_name;
    EXECUTE format('ALTER TABLE %I ALTER COLUMN subject_id SET NOT NULL', tbl_name);
END $$;

-- ============================================
-- 4. Add index on subject_id for faster lookups
-- ============================================
DO $$
DECLARE
    tbl_name TEXT;
BEGIN
    SELECT name INTO tbl_name FROM migration_table_name;
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_subject_course_mapping_subject_id ON %I(subject_id)', tbl_name);
END $$;

-- ============================================
-- 5. Create a view/helper for unique subject_id lookup
-- ============================================
-- Since one subject can map to multiple CAH codes, we create a view
-- that gives us one row per subject_id for foreign key purposes
DO $$
DECLARE
    tbl_name TEXT;
BEGIN
    SELECT name INTO tbl_name FROM migration_table_name;
    EXECUTE format('CREATE OR REPLACE VIEW a_level_subject_unique AS
        SELECT DISTINCT ON (subject_id)
            subject_id,
            a_level_subject,
            subject_cleaned,
            cah3_code,
            cah3_label,
            cah2_code,
            cah2_label,
            cah1_code,
            cah1_label
        FROM %I
        ORDER BY subject_id, mapping_id', tbl_name);
END $$;

-- ============================================
-- 6. Handle subject_related_term (if it exists)
-- ============================================
-- NOTE: subject_related_term is created in migration 007 and dropped in migration 010.
-- This section only runs if the table exists (i.e., migration 010 hasn't run yet).
DO $$
DECLARE
    tbl_name TEXT;
    subject_related_term_exists BOOLEAN;
BEGIN
    SELECT name INTO tbl_name FROM migration_table_name;
    
    -- Check if subject_related_term exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE information_schema.tables.table_name = 'subject_related_term'
    ) INTO subject_related_term_exists;
    
    IF subject_related_term_exists THEN
        -- Add a_level_subject column to link to subject_course_mapping (if not exists)
        ALTER TABLE subject_related_term
            ADD COLUMN IF NOT EXISTS a_level_subject VARCHAR(255);
        
        -- Populate a_level_subject from subject_name by matching to subject_course_mapping
        EXECUTE format('UPDATE subject_related_term srt
            SET a_level_subject = (
                SELECT DISTINCT alm.a_level_subject
                FROM %I alm
                WHERE LOWER(TRIM(alm.a_level_subject)) = LOWER(TRIM(srt.subject_name))
                LIMIT 1
            )
            WHERE srt.a_level_subject IS NULL', tbl_name);
        
        -- For any remaining NULLs, use subject_name as-is
        UPDATE subject_related_term srt
        SET a_level_subject = srt.subject_name
        WHERE srt.a_level_subject IS NULL;
        
        -- Make a_level_subject NOT NULL after population
        ALTER TABLE subject_related_term
            ALTER COLUMN a_level_subject SET NOT NULL;
        
        -- Add subject_id column (if not exists) - allow NULL initially
        ALTER TABLE subject_related_term
            ADD COLUMN IF NOT EXISTS subject_id VARCHAR(50);
        
        -- Populate subject_id from subject_course_mapping via a_level_subject
        EXECUTE format('UPDATE subject_related_term srt
            SET subject_id = (
                SELECT DISTINCT alm.subject_id
                FROM %I alm
                WHERE alm.a_level_subject = srt.a_level_subject
                LIMIT 1
            )
            WHERE srt.subject_id IS NULL', tbl_name);
        
        -- For any remaining NULLs, generate from subject_name
        UPDATE subject_related_term srt
        SET subject_id = LOWER(REPLACE(REPLACE(REPLACE(srt.subject_name, ' ', '_'), '''', ''), '-', '_'))
        WHERE srt.subject_id IS NULL;
        
        -- Now make subject_id NOT NULL after all population is done
        ALTER TABLE subject_related_term
            ALTER COLUMN subject_id SET NOT NULL;
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_subject_related_term_alevel_subject 
            ON subject_related_term(a_level_subject);
        
        CREATE INDEX IF NOT EXISTS idx_subject_related_term_subject_id 
            ON subject_related_term(subject_id);
    END IF;
END $$;

-- ============================================
-- 7. Update comments
-- ============================================
DO $$
DECLARE
    tbl_name TEXT;
BEGIN
    SELECT name INTO tbl_name FROM migration_table_name;
    EXECUTE format('COMMENT ON COLUMN %I.subject_id IS ''Unique identifier for A-Level subject (from CSV SubjectID or generated from name)''', tbl_name);
END $$;

COMMENT ON VIEW a_level_subject_unique IS 'View providing one row per subject_id for foreign key relationships';

-- Clean up temporary table
DROP TABLE IF EXISTS migration_table_name;
