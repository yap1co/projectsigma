-- Cleanup Script: Remove Unused HESA Tables
-- Project Sigma - Scope Reduction for A-Level NEA
-- Keeps: Core tables (15) + employment table (1) = 16 tables
-- Removes: 26 unused HESA tables

-- Drop unused HESA reference/lookup tables
DROP TABLE IF EXISTS kis_aim CASCADE;
DROP TABLE IF EXISTS accreditation_table CASCADE;
DROP TABLE IF EXISTS location CASCADE;

-- Drop unused course detail tables
DROP TABLE IF EXISTS accreditation CASCADE;
DROP TABLE IF EXISTS accreditation_by_hep CASCADE;
DROP TABLE IF EXISTS courselocation CASCADE;
DROP TABLE IF EXISTS ucascourseid CASCADE;
DROP TABLE IF EXISTS sbj CASCADE;

-- Drop unused outcome tables (keeping employment)
DROP TABLE IF EXISTS continuation CASCADE;
DROP TABLE IF EXISTS entry CASCADE;
DROP TABLE IF EXISTS tariff CASCADE;
DROP TABLE IF EXISTS gosalary CASCADE;
DROP TABLE IF EXISTS gosecsal CASCADE;
DROP TABLE IF EXISTS govoicework CASCADE;
DROP TABLE IF EXISTS leo3 CASCADE;
DROP TABLE IF EXISTS leo3sec CASCADE;
DROP TABLE IF EXISTS leo5 CASCADE;
DROP TABLE IF EXISTS leo5sec CASCADE;
DROP TABLE IF EXISTS joblist CASCADE;
DROP TABLE IF EXISTS jobtype CASCADE;
DROP TABLE IF EXISTS nss CASCADE;
DROP TABLE IF EXISTS nsscountry CASCADE;
DROP TABLE IF EXISTS tefoutcome CASCADE;
DROP TABLE IF EXISTS common CASCADE;

-- Keep these mapping tables as they're needed for data import
-- institution (maps to university)
-- kiscourse (maps to course)
-- But they're not used by the recommendation engine after mapping

-- Verify remaining tables
\dt

-- Expected tables remaining:
-- 1. student
-- 2. student_grade
-- 3. subject
-- 4. university
-- 5. course
-- 6. course_requirement
-- 7. course_required_exam
-- 8. entrance_exam
-- 9. career_interest
-- 10. career_interest_keyword
-- 11. career_interest_conflict
-- 12. recommendation_run
-- 13. recommendation_result
-- 14. recommendation_feedback
-- 15. recommendation_settings
-- 16. employment (KEPT for course-level employability)
-- Plus: institution, kiscourse (for data import reference)
