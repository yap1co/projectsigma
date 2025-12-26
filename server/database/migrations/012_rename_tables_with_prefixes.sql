-- Migration 012: Rename all tables with prefixes
-- HESA tables: prefix with hesa_
-- Application tables: prefix with uni_recomm_
--
-- This migration renames all tables and updates:
-- - Foreign key constraints
-- - Indexes
-- - Views
-- - Sequences (if any)

-- ============================================
-- PART 1: RENAME HESA TABLES (prefix: hesa_)
-- ============================================

-- Lookup tables
ALTER TABLE IF EXISTS accreditation_table RENAME TO hesa_accreditation_table;
ALTER TABLE IF EXISTS kis_aim RENAME TO hesa_kis_aim;
ALTER TABLE IF EXISTS location RENAME TO hesa_location;

-- Core entities
ALTER TABLE IF EXISTS institution RENAME TO hesa_institution;
ALTER TABLE IF EXISTS kiscourse RENAME TO hesa_kiscourse;

-- Course related entities
ALTER TABLE IF EXISTS accreditation RENAME TO hesa_accreditation;
ALTER TABLE IF EXISTS courselocation RENAME TO hesa_courselocation;
ALTER TABLE IF EXISTS ucascourseid RENAME TO hesa_ucascourseid;
ALTER TABLE IF EXISTS sbj RENAME TO hesa_sbj;

-- Student outcomes
ALTER TABLE IF EXISTS entry RENAME TO hesa_entry;
ALTER TABLE IF EXISTS tariff RENAME TO hesa_tariff;
ALTER TABLE IF EXISTS continuation RENAME TO hesa_continuation;

-- Employment and salary
ALTER TABLE IF EXISTS employment RENAME TO hesa_employment;
ALTER TABLE IF EXISTS jobtype RENAME TO hesa_jobtype;
ALTER TABLE IF EXISTS common RENAME TO hesa_common;
ALTER TABLE IF EXISTS joblist RENAME TO hesa_joblist;
ALTER TABLE IF EXISTS gosalary RENAME TO hesa_gosalary;
ALTER TABLE IF EXISTS gosecsal RENAME TO hesa_gosecsal;
ALTER TABLE IF EXISTS govoicework RENAME TO hesa_govoicework;

-- LEO (Longitudinal Education Outcomes)
ALTER TABLE IF EXISTS leo3 RENAME TO hesa_leo3;
ALTER TABLE IF EXISTS leo3sec RENAME TO hesa_leo3sec;
ALTER TABLE IF EXISTS leo5 RENAME TO hesa_leo5;
ALTER TABLE IF EXISTS leo5sec RENAME TO hesa_leo5sec;

-- NSS (National Student Survey)
ALTER TABLE IF EXISTS nss RENAME TO hesa_nss;
ALTER TABLE IF EXISTS nsscountry RENAME TO hesa_nsscountry;

-- TEF (Teaching Excellence Framework)
ALTER TABLE IF EXISTS tefoutcome RENAME TO hesa_tefoutcome;

-- Additional tables
ALTER TABLE IF EXISTS accreditation_by_hep RENAME TO hesa_accreditation_by_hep;

-- ============================================
-- PART 2: RENAME APPLICATION TABLES (prefix: uni_recomm_)
-- ============================================

-- Core application tables
ALTER TABLE IF EXISTS student RENAME TO uni_recomm_student;
ALTER TABLE IF EXISTS subject RENAME TO uni_recomm_subject;
ALTER TABLE IF EXISTS student_grade RENAME TO uni_recomm_student_grade;
ALTER TABLE IF EXISTS university RENAME TO uni_recomm_university;
ALTER TABLE IF EXISTS course RENAME TO uni_recomm_course;
ALTER TABLE IF EXISTS course_requirement RENAME TO uni_recomm_course_requirement;
ALTER TABLE IF EXISTS entrance_exam RENAME TO uni_recomm_entrance_exam;
ALTER TABLE IF EXISTS course_required_exam RENAME TO uni_recomm_course_required_exam;

-- Recommendation system tables
ALTER TABLE IF EXISTS recommendation_run RENAME TO uni_recomm_recommendation_run;
ALTER TABLE IF EXISTS recommendation_result RENAME TO uni_recomm_recommendation_result;
ALTER TABLE IF EXISTS recommendation_feedback RENAME TO uni_recomm_recommendation_feedback;
ALTER TABLE IF EXISTS recommendation_settings RENAME TO uni_recomm_recommendation_settings;

-- Recommendation engine configuration tables
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE information_schema.tables.table_name = 'grade_value') 
       AND NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE information_schema.tables.table_name = 'uni_recomm_grade_value') THEN
        ALTER TABLE grade_value RENAME TO uni_recomm_grade_value;
    END IF;
END $$;
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE information_schema.tables.table_name = 'feedback_setting') 
       AND NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE information_schema.tables.table_name = 'uni_recomm_feedback_setting') THEN
        ALTER TABLE feedback_setting RENAME TO uni_recomm_feedback_setting;
    END IF;
END $$;
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE information_schema.tables.table_name = 'recommendation_weight') 
       AND NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE information_schema.tables.table_name = 'uni_recomm_recommendation_weight') THEN
        ALTER TABLE recommendation_weight RENAME TO uni_recomm_recommendation_weight;
    END IF;
END $$;

-- Career interests tables
ALTER TABLE IF EXISTS career_interest RENAME TO uni_recomm_career_interest;
ALTER TABLE IF EXISTS career_interest_keyword RENAME TO uni_recomm_career_interest_keyword;
ALTER TABLE IF EXISTS career_interest_conflict RENAME TO uni_recomm_career_interest_conflict;

-- Subject mapping tables
ALTER TABLE IF EXISTS subject_course_mapping RENAME TO uni_recomm_subject_course_mapping;

-- ============================================
-- PART 3: UPDATE FOREIGN KEY CONSTRAINTS
-- ============================================

-- Drop and recreate foreign keys for HESA tables
-- Note: PostgreSQL will automatically update FK constraints when tables are renamed,
-- but we need to update the constraint names to reflect new table names

-- HESA table foreign keys (these reference other HESA tables)
-- Most HESA tables reference hesa_institution or hesa_kiscourse
-- These should be automatically updated, but we'll verify and update constraint names

-- Application table foreign keys
-- Update references from uni_recomm tables to other uni_recomm tables

-- student_grade references
ALTER TABLE uni_recomm_student_grade 
    DROP CONSTRAINT IF EXISTS student_grade_student_id_fkey,
    DROP CONSTRAINT IF EXISTS fk_grade_student,
    DROP CONSTRAINT IF EXISTS student_grade_subject_id_fkey,
    DROP CONSTRAINT IF EXISTS fk_grade_subject;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_student_grade_student' 
        AND table_name = 'uni_recomm_student_grade'
    ) THEN
        ALTER TABLE uni_recomm_student_grade
            ADD CONSTRAINT fk_student_grade_student 
            FOREIGN KEY (student_id) REFERENCES uni_recomm_student(student_id) ON DELETE CASCADE;
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_student_grade_subject' 
        AND table_name = 'uni_recomm_student_grade'
    ) THEN
        ALTER TABLE uni_recomm_student_grade
            ADD CONSTRAINT fk_student_grade_subject 
            FOREIGN KEY (subject_id) REFERENCES uni_recomm_subject(subject_id) ON DELETE RESTRICT;
    END IF;
END $$;

-- course references
ALTER TABLE uni_recomm_course
    DROP CONSTRAINT IF EXISTS course_university_id_fkey,
    DROP CONSTRAINT IF EXISTS fk_course_university;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_course_university' 
        AND table_name = 'uni_recomm_course'
    ) THEN
        ALTER TABLE uni_recomm_course
            ADD CONSTRAINT fk_course_university 
            FOREIGN KEY (university_id) REFERENCES uni_recomm_university(university_id) ON DELETE CASCADE;
    END IF;
END $$;

-- course_requirement references
ALTER TABLE uni_recomm_course_requirement
    DROP CONSTRAINT IF EXISTS course_requirement_course_id_fkey,
    DROP CONSTRAINT IF EXISTS fk_req_course,
    DROP CONSTRAINT IF EXISTS course_requirement_subject_id_fkey,
    DROP CONSTRAINT IF EXISTS fk_req_subject;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_course_requirement_course' 
        AND table_name = 'uni_recomm_course_requirement'
    ) THEN
        ALTER TABLE uni_recomm_course_requirement
            ADD CONSTRAINT fk_course_requirement_course 
            FOREIGN KEY (course_id) REFERENCES uni_recomm_course(course_id) ON DELETE CASCADE;
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_course_requirement_subject' 
        AND table_name = 'uni_recomm_course_requirement'
    ) THEN
        ALTER TABLE uni_recomm_course_requirement
            ADD CONSTRAINT fk_course_requirement_subject 
            FOREIGN KEY (subject_id) REFERENCES uni_recomm_subject(subject_id) ON DELETE RESTRICT;
    END IF;
END $$;

-- course_required_exam references
ALTER TABLE uni_recomm_course_required_exam
    DROP CONSTRAINT IF EXISTS course_required_exam_course_id_fkey,
    DROP CONSTRAINT IF EXISTS fk_exam_course,
    DROP CONSTRAINT IF EXISTS course_required_exam_exam_id_fkey,
    DROP CONSTRAINT IF EXISTS fk_exam_exam;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_course_required_exam_course' 
        AND table_name = 'uni_recomm_course_required_exam'
    ) THEN
        ALTER TABLE uni_recomm_course_required_exam
            ADD CONSTRAINT fk_course_required_exam_course 
            FOREIGN KEY (course_id) REFERENCES uni_recomm_course(course_id) ON DELETE CASCADE;
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_course_required_exam_exam' 
        AND table_name = 'uni_recomm_course_required_exam'
    ) THEN
        ALTER TABLE uni_recomm_course_required_exam
            ADD CONSTRAINT fk_course_required_exam_exam 
            FOREIGN KEY (exam_id) REFERENCES uni_recomm_entrance_exam(exam_id) ON DELETE RESTRICT;
    END IF;
END $$;

-- recommendation_run references
ALTER TABLE uni_recomm_recommendation_run
    DROP CONSTRAINT IF EXISTS recommendation_run_student_id_fkey,
    DROP CONSTRAINT IF EXISTS fk_run_student;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_recommendation_run_student' 
        AND table_name = 'uni_recomm_recommendation_run'
    ) THEN
        ALTER TABLE uni_recomm_recommendation_run
            ADD CONSTRAINT fk_recommendation_run_student 
            FOREIGN KEY (student_id) REFERENCES uni_recomm_student(student_id) ON DELETE CASCADE;
    END IF;
END $$;

-- recommendation_result references
ALTER TABLE uni_recomm_recommendation_result
    DROP CONSTRAINT IF EXISTS recommendation_result_run_id_fkey,
    DROP CONSTRAINT IF EXISTS fk_result_run;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_recommendation_result_run' 
        AND table_name = 'uni_recomm_recommendation_result'
    ) THEN
        ALTER TABLE uni_recomm_recommendation_result
            ADD CONSTRAINT fk_recommendation_result_run 
            FOREIGN KEY (run_id) REFERENCES uni_recomm_recommendation_run(run_id) ON DELETE CASCADE;
    END IF;
END $$;

-- recommendation_feedback references
ALTER TABLE uni_recomm_recommendation_feedback
    DROP CONSTRAINT IF EXISTS recommendation_feedback_student_id_fkey,
    DROP CONSTRAINT IF EXISTS fk_feedback_student,
    DROP CONSTRAINT IF EXISTS recommendation_feedback_course_id_fkey,
    DROP CONSTRAINT IF EXISTS fk_feedback_course;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_recommendation_feedback_student' 
        AND table_name = 'uni_recomm_recommendation_feedback'
    ) THEN
        ALTER TABLE uni_recomm_recommendation_feedback
            ADD CONSTRAINT fk_recommendation_feedback_student 
            FOREIGN KEY (student_id) REFERENCES uni_recomm_student(student_id) ON DELETE CASCADE;
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_recommendation_feedback_course' 
        AND table_name = 'uni_recomm_recommendation_feedback'
    ) THEN
        ALTER TABLE uni_recomm_recommendation_feedback
            ADD CONSTRAINT fk_recommendation_feedback_course 
            FOREIGN KEY (course_id) REFERENCES uni_recomm_course(course_id) ON DELETE CASCADE;
    END IF;
END $$;

-- recommendation_settings references
ALTER TABLE uni_recomm_recommendation_settings
    DROP CONSTRAINT IF EXISTS recommendation_settings_updated_by_fkey;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_recommendation_settings_updated_by' 
        AND table_name = 'uni_recomm_recommendation_settings'
    ) THEN
        ALTER TABLE uni_recomm_recommendation_settings
            ADD CONSTRAINT fk_recommendation_settings_updated_by 
            FOREIGN KEY (updated_by) REFERENCES uni_recomm_student(student_id) ON DELETE SET NULL;
    END IF;
END $$;

-- career_interest_keyword references
ALTER TABLE uni_recomm_career_interest_keyword
    DROP CONSTRAINT IF EXISTS career_interest_keyword_interest_id_fkey,
    DROP CONSTRAINT IF EXISTS fk_keyword_interest;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_career_interest_keyword_interest' 
        AND table_name = 'uni_recomm_career_interest_keyword'
    ) THEN
        ALTER TABLE uni_recomm_career_interest_keyword
            ADD CONSTRAINT fk_career_interest_keyword_interest 
            FOREIGN KEY (interest_id) REFERENCES uni_recomm_career_interest(interest_id) ON DELETE CASCADE;
    END IF;
END $$;

-- career_interest_conflict references
ALTER TABLE uni_recomm_career_interest_conflict
    DROP CONSTRAINT IF EXISTS career_interest_conflict_interest_id_fkey,
    DROP CONSTRAINT IF EXISTS fk_conflict_interest,
    DROP CONSTRAINT IF EXISTS career_interest_conflict_conflicting_interest_id_fkey,
    DROP CONSTRAINT IF EXISTS fk_conflict_conflicting;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_career_interest_conflict_interest' 
        AND table_name = 'uni_recomm_career_interest_conflict'
    ) THEN
        ALTER TABLE uni_recomm_career_interest_conflict
            ADD CONSTRAINT fk_career_interest_conflict_interest 
            FOREIGN KEY (interest_id) REFERENCES uni_recomm_career_interest(interest_id) ON DELETE CASCADE;
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_career_interest_conflict_conflicting' 
        AND table_name = 'uni_recomm_career_interest_conflict'
    ) THEN
        ALTER TABLE uni_recomm_career_interest_conflict
            ADD CONSTRAINT fk_career_interest_conflict_conflicting 
            FOREIGN KEY (conflicting_interest_id) REFERENCES uni_recomm_career_interest(interest_id) ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================
-- PART 4: UPDATE VIEWS
-- ============================================

-- Drop and recreate views with new table names
DROP VIEW IF EXISTS sbj_with_subject_course_mapping;

CREATE OR REPLACE VIEW hesa_sbj_with_subject_course_mapping AS
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
FROM hesa_sbj s
LEFT JOIN uni_recomm_subject_course_mapping m ON s.sbj = m.cah3_code;

COMMENT ON VIEW hesa_sbj_with_subject_course_mapping IS 'View joining hesa_sbj table with subject course mappings';

-- ============================================
-- PART 5: UPDATE INDEX NAMES (Optional - for consistency)
-- ============================================

-- Note: Index names don't need to be updated for functionality,
-- but we can rename them for consistency if desired.
-- PostgreSQL will continue to work with old index names.
-- This is optional and can be done later if needed.

-- ============================================
-- PART 6: COMMENTS
-- ============================================

COMMENT ON SCHEMA public IS 'University Recommender Database - All HESA tables prefixed with hesa_, all application tables prefixed with uni_recomm_';

