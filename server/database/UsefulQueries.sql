-- Check subject table structure
SELECT subject_id, subject_name FROM subject LIMIT 10;


-- Verify university table has pubukprn
SELECT university_id, pubukprn, name FROM university LIMIT 5;

-- Check database statistics
SELECT 'Subjects' as table_name, COUNT(*) as count FROM subject
UNION ALL
SELECT 'Universities', COUNT(*) FROM university
UNION ALL
SELECT 'Courses', COUNT(*) FROM course
UNION ALL
SELECT 'Course Requirements', COUNT(*) FROM course_requirement;