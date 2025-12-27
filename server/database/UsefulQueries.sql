select u.pubukprn,u.name, c.*, sr.*, s.* from university u, course c, course_subject_requirement sr, subject s
where u.university_id = c.university_id 
and c.course_id = sr.course_id 
and s.cah_code = sr.cah_code
and u.name ilike '%university of bristol%'
and c.name ilike '%math%'

select u.name, u.region,u.website_url, c.name,c.length,c.ucas_code,c.ucasprogid,c.course_url,c.hecos,c.annual_fee, c.employability_score,c.typical_offer_tariff, c.kiscourseid, c.kismode 
from university u, course c
where u.university_id = c.university_id 
and u.name ilike '%university of bristol%'
and c.name ilike '%engineering mathematics%'

select u.name, u.region,u.website_url, c.name,c.length,c.ucas_code,c.ucasprogid,c.course_url,c.hecos,c.annual_fee, c.employability_score,c.typical_offer_tariff, c.kiscourseid, c.kismode 
from university u, course c
where u.university_id = c.university_id 
and u.name ilike '%leeds%'
and c.name ilike '%Mechatronics and Robotics Engineering%'


select * from hesa_employment e,hesa_gosalary g, hesa_leo3 l, hesa_entry ee
where
e.kiscourseid = g.kiscourseid and 
g.kiscourseid = l.kiscourseid and 
l.kiscourseid = ee.kiscourseid and 
e.kiscourseid = '4EMAT006UU-202425';

sekect
select * from hesa_gosalary  where kiscourseid = '4EMAT006UU-202425'
select * from hesa_leo3  where kiscourseid = '4EMAT006UU-202425'


select * from course where name ilike '%engineering mathematics%'

select * from course where kiscourseid  in ('4EMAT013UU-202425','4EMAT002UU-202425','4EMAT006UU-202425')


select * from hesa_kiscourse where kiscourseid  in ('4EMAT013UU-202425','4EMAT002UU-202425','4EMAT006UU-202425')

select kiscourseid, ucascourseid from hesa_ucascourseid where kiscourseid  in ('4EMAT013UU-202425','4EMAT002UU-202425','4EMAT006UU-202425')
select kiscourseid, ucas_code from course where kiscourseid  in ('4EMAT013UU-202425','4EMAT002UU-202425','4EMAT006UU-202425')

select * from hesa_entry
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
SELECT 'Course Requirement', COUNT(*) FROM course_subject_requirement
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