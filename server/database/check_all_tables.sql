-- ================================================================================
-- COMPREHENSIVE DATABASE TABLE CHECK - Project Sigma
-- Quick SQL query to check all table counts
-- ================================================================================

-- HESA IMPORT TABLES
SELECT 'HESA_INSTITUTION' as table_name, COUNT(*) as count FROM hesa_institution
UNION ALL
SELECT 'HESA_KISCOURSE', COUNT(*) FROM hesa_kiscourse  
UNION ALL
SELECT 'HESA_SBJ', COUNT(*) FROM hesa_sbj
UNION ALL
SELECT 'HESA_ENTRY', COUNT(*) FROM hesa_entry
UNION ALL
SELECT 'HESA_TARIFF', COUNT(*) FROM hesa_tariff
UNION ALL  
SELECT 'HESA_EMPLOYMENT', COUNT(*) FROM hesa_employment
UNION ALL
SELECT 'HESA_JOBLIST', COUNT(*) FROM hesa_joblist
UNION ALL
SELECT 'HESA_GOSALARY', COUNT(*) FROM hesa_gosalary
UNION ALL
SELECT 'HESA_LEO3', COUNT(*) FROM hesa_leo3
UNION ALL
SELECT 'HESA_UCASCOURSEID', COUNT(*) FROM hesa_ucascourseid

-- Separator
UNION ALL SELECT '--- APPLICATION TABLES ---', 0

-- APPLICATION TABLES  
UNION ALL
SELECT 'University', COUNT(*) FROM university
UNION ALL
SELECT 'Course', COUNT(*) FROM course
UNION ALL
SELECT 'Subject', COUNT(*) FROM subject
UNION ALL
SELECT 'Course Requirement', COUNT(*) FROM course_requirement
UNION ALL
SELECT 'Career Interest', COUNT(*) FROM career_interest
UNION ALL
SELECT 'Entrance Exam', COUNT(*) FROM entrance_exam
UNION ALL
SELECT 'Subject To Career', COUNT(*) FROM subject_to_career
UNION ALL
SELECT 'Student', COUNT(*) FROM student
UNION ALL
SELECT 'Student Grade', COUNT(*) FROM student_grade  
UNION ALL
SELECT 'Student Career Interest', COUNT(*) FROM student_career_interest
UNION ALL
SELECT 'Student Preferred Exam', COUNT(*) FROM student_preferred_exam
UNION ALL
SELECT 'Course Required Exam', COUNT(*) FROM course_required_exam
UNION ALL
SELECT 'Recommendation Run', COUNT(*) FROM recommendation_run
UNION ALL
SELECT 'Recommendation Result', COUNT(*) FROM recommendation_result

-- Separator  
UNION ALL SELECT '--- SYSTEM TABLES ---', 0

-- SYSTEM TABLES
UNION ALL
SELECT 'Schema Migrations', COUNT(*) FROM schema_migrations

ORDER BY table_name;