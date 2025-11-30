-- ============================================
-- RELATIONSHIP VERIFICATION QUERIES
-- Run these after importing sample data
-- ============================================

SET search_path TO discover_uni, public;

-- ============================================
-- 1. VERIFY BASIC COUNTS
-- ============================================

SELECT 'Institutions' AS table_name, COUNT(*) AS record_count FROM institution
UNION ALL
SELECT 'KIS Courses', COUNT(*) FROM kiscourse
UNION ALL
SELECT 'KIS Aims', COUNT(*) FROM kis_aim
UNION ALL
SELECT 'Locations', COUNT(*) FROM location
UNION ALL
SELECT 'Accreditations', COUNT(*) FROM accreditation
UNION ALL
SELECT 'Course Locations', COUNT(*) FROM courselocation
UNION ALL
SELECT 'Subjects', COUNT(*) FROM sbj
UNION ALL
SELECT 'Entry Records', COUNT(*) FROM entry
UNION ALL
SELECT 'Employment Records', COUNT(*) FROM employment;

-- ============================================
-- 2. VERIFY ONE-TO-MANY RELATIONSHIPS
-- ============================================

-- Institution → KIS Course (One institution has many courses)
SELECT 
    'Institution → Courses' AS relationship,
    i.legal_name AS institution,
    COUNT(k.kiscourseid) AS course_count
FROM institution i
LEFT JOIN kiscourse k ON i.pubukprn = k.pubukprn
GROUP BY i.legal_name
ORDER BY course_count DESC
LIMIT 5;

-- ============================================
-- 3. VERIFY MANY-TO-ONE RELATIONSHIPS
-- ============================================

-- KIS Course → KIS Aim (Many courses share qualification types)
SELECT 
    'Course → Qualification Type' AS relationship,
    ka.kisaimlabel AS qualification_type,
    COUNT(k.kiscourseid) AS course_count
FROM kis_aim ka
LEFT JOIN kiscourse k ON ka.kisaimcode = k.kisaimcode
GROUP BY ka.kisaimlabel
ORDER BY course_count DESC
LIMIT 5;

-- ============================================
-- 4. VERIFY MANY-TO-MANY RELATIONSHIPS
-- ============================================

-- Course ↔ Accreditation (Many-to-Many)
SELECT 
    'Course ↔ Accreditation' AS relationship,
    k.title AS course_title,
    COUNT(DISTINCT a.acctype) AS accreditation_count
FROM kiscourse k
LEFT JOIN accreditation a ON k.pubukprn = a.pubukprn 
    AND k.kiscourseid = a.kiscourseid 
    AND k.kismode = a.kismode
GROUP BY k.title
HAVING COUNT(DISTINCT a.acctype) > 0
ORDER BY accreditation_count DESC
LIMIT 5;

-- Course ↔ Location (Many-to-Many)
SELECT 
    'Course ↔ Location' AS relationship,
    k.title AS course_title,
    COUNT(DISTINCT cl.locid) AS location_count
FROM kiscourse k
LEFT JOIN courselocation cl ON k.pubukprn = cl.pubukprn 
    AND k.kiscourseid = cl.kiscourseid 
    AND k.kismode = cl.kismode
GROUP BY k.title
HAVING COUNT(DISTINCT cl.locid) > 0
ORDER BY location_count DESC
LIMIT 5;

-- Course ↔ Subject (Many-to-Many)
SELECT 
    'Course ↔ Subject' AS relationship,
    k.title AS course_title,
    COUNT(DISTINCT s.sbj) AS subject_count
FROM kiscourse k
LEFT JOIN sbj s ON k.pubukprn = s.pubukprn 
    AND k.kiscourseid = s.kiscourseid 
    AND k.kismode = s.kismode
GROUP BY k.title
HAVING COUNT(DISTINCT s.sbj) > 0
ORDER BY subject_count DESC
LIMIT 5;

-- ============================================
-- 5. COMPREHENSIVE COURSE VIEW
-- ============================================

-- Show a complete course with all relationships
SELECT 
    i.legal_name AS institution,
    k.title AS course_title,
    ka.kisaimlabel AS qualification_type,
    COUNT(DISTINCT a.acctype) AS accreditation_count,
    COUNT(DISTINCT cl.locid) AS location_count,
    COUNT(DISTINCT s.sbj) AS subject_count,
    CASE WHEN e.work IS NOT NULL THEN 'Yes' ELSE 'No' END AS has_employment_data,
    CASE WHEN en.entpop IS NOT NULL THEN 'Yes' ELSE 'No' END AS has_entry_data
FROM kiscourse k
JOIN institution i ON k.pubukprn = i.pubukprn
LEFT JOIN kis_aim ka ON k.kisaimcode = ka.kisaimcode
LEFT JOIN accreditation a ON k.pubukprn = a.pubukprn 
    AND k.kiscourseid = a.kiscourseid 
    AND k.kismode = a.kismode
LEFT JOIN courselocation cl ON k.pubukprn = cl.pubukprn 
    AND k.kiscourseid = cl.kiscourseid 
    AND k.kismode = cl.kismode
LEFT JOIN sbj s ON k.pubukprn = s.pubukprn 
    AND k.kiscourseid = s.kiscourseid 
    AND k.kismode = s.kismode
LEFT JOIN employment e ON k.pubukprn = e.pubukprn 
    AND k.kiscourseid = e.kiscourseid 
    AND k.kismode = e.kismode
LEFT JOIN entry en ON k.pubukprn = en.pubukprn 
    AND k.kiscourseid = en.kiscourseid 
    AND k.kismode = en.kismode
GROUP BY i.legal_name, k.title, ka.kisaimlabel, e.work, en.entpop
LIMIT 10;

-- ============================================
-- 6. VERIFY FOREIGN KEY INTEGRITY
-- ============================================

-- Check for orphaned records (should return 0 rows)
SELECT 
    'Orphaned Courses' AS check_type,
    COUNT(*) AS orphan_count
FROM kiscourse k
LEFT JOIN institution i ON k.pubukprn = i.pubukprn
WHERE i.pubukprn IS NULL

UNION ALL

SELECT 
    'Orphaned Accreditations',
    COUNT(*)
FROM accreditation a
LEFT JOIN kiscourse k ON a.pubukprn = k.pubukprn 
    AND a.kiscourseid = k.kiscourseid 
    AND a.kismode = k.kismode
WHERE k.pubukprn IS NULL

UNION ALL

SELECT 
    'Orphaned Course Locations',
    COUNT(*)
FROM courselocation cl
LEFT JOIN kiscourse k ON cl.pubukprn = k.pubukprn 
    AND cl.kiscourseid = k.kiscourseid 
    AND cl.kismode = k.kismode
WHERE k.pubukprn IS NULL;

-- ============================================
-- 7. SAMPLE RELATIONSHIP QUERIES
-- ============================================

-- Find courses at a specific location
SELECT 
    l.locname AS location,
    k.title AS course_title,
    i.legal_name AS institution
FROM location l
JOIN courselocation cl ON l.ukprn = cl.ukprn AND l.locid = cl.locid
JOIN kiscourse k ON cl.pubukprn = k.pubukprn 
    AND cl.kiscourseid = k.kiscourseid 
    AND cl.kismode = k.kismode
JOIN institution i ON k.pubukprn = i.pubukprn
LIMIT 10;

-- Find courses with specific accreditation
SELECT 
    at.acctext AS accreditation_type,
    k.title AS course_title,
    i.legal_name AS institution
FROM accreditation_table at
JOIN accreditation a ON at.acctype = a.acctype
JOIN kiscourse k ON a.pubukprn = k.pubukprn 
    AND a.kiscourseid = k.kiscourseid 
    AND a.kismode = k.kismode
JOIN institution i ON k.pubukprn = i.pubukprn
LIMIT 10;

-- Find courses with employment data
SELECT 
    k.title AS course_title,
    i.legal_name AS institution,
    e.work AS employed_count,
    e.study AS studying_count,
    e.unemp AS unemployed_count,
    ROUND(100.0 * e.work / NULLIF(e.work + e.study + e.unemp, 0), 2) AS employment_rate
FROM kiscourse k
JOIN institution i ON k.pubukprn = i.pubukprn
JOIN employment e ON k.pubukprn = e.pubukprn 
    AND k.kiscourseid = e.kiscourseid 
    AND k.kismode = e.kismode
WHERE e.work IS NOT NULL
ORDER BY employment_rate DESC
LIMIT 10;

-- ============================================
-- END OF VERIFICATION QUERIES
-- ============================================

