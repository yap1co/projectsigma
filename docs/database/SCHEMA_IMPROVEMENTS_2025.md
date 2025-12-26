# Database Schema Improvements (December 2025)

## Overview

This document summarizes the database schema improvements made to meet AQA A-Level NEA requirements for proper relational database design and First Normal Form (1NF) compliance.

## Changes Made

### 1. Normalized Student Preferences (1NF Compliance)

**Problem:** Arrays violate First Normal Form (TEXT[] arrays in student table)

**Before:**
```sql
CREATE TABLE student (
    student_id VARCHAR(50) PRIMARY KEY,
    display_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATE DEFAULT CURRENT_DATE,
    region VARCHAR(100),
    tuition_budget INTEGER,
    preferred_exams TEXT[],        -- ❌ Violates 1NF
    career_interests TEXT[]        -- ❌ Violates 1NF
);
```

**After:**
```sql
CREATE TABLE student (
    student_id VARCHAR(50) PRIMARY KEY,
    display_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATE DEFAULT CURRENT_DATE,
    region VARCHAR(100),
    tuition_budget INTEGER
);

-- ✅ Proper junction tables (1NF compliant)
CREATE TABLE career_interest (
    career_interest_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE student_career_interest (
    student_id VARCHAR(50) REFERENCES student(student_id) ON DELETE CASCADE,
    career_interest_id VARCHAR(50) REFERENCES career_interest(career_interest_id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, career_interest_id)
);

CREATE TABLE student_preferred_exam (
    student_id VARCHAR(50) REFERENCES student(student_id) ON DELETE CASCADE,
    exam_id VARCHAR(50) REFERENCES entrance_exam(exam_id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, exam_id)
);
```

**Benefits:**
- ✅ Complies with First Normal Form (1NF)
- ✅ Enables referential integrity (foreign keys)
- ✅ Allows efficient filtering: `SELECT students WHERE 'Healthcare' IN career_interests`
- ✅ AQA marking scheme: "Complex data model in database (e.g. several interlinked tables)"

### 2. Added UNIQUE Constraint for HESA Identifiers

**Problem:** Missing uniqueness constraint on HESA course identifiers

**Before:**
```sql
CREATE TABLE course (
    course_id VARCHAR(255) PRIMARY KEY,
    university_id VARCHAR(255) REFERENCES university(university_id),
    pubukprn VARCHAR(8),
    kiscourseid VARCHAR(50),
    kismode VARCHAR(2),
    ...
);
-- No constraint preventing duplicate HESA courses
```

**After:**
```sql
CREATE TABLE course (
    course_id VARCHAR(255) PRIMARY KEY,
    university_id VARCHAR(255) REFERENCES university(university_id),
    pubukprn VARCHAR(8),
    kiscourseid VARCHAR(50),
    kismode VARCHAR(2),
    ...
    UNIQUE (pubukprn, kiscourseid, kismode)  -- ✅ Prevents duplicate HESA courses
);
```

**Benefits:**
- ✅ Data integrity: Each HESA course appears only once
- ✅ Prevents duplicate imports from CSV files
- ✅ Efficient lookups using UNIQUE index

### 3. Standardized VARCHAR Lengths for HESA Identifiers

**Problem:** Inconsistent VARCHAR sizes (8 vs 10) for UK Provider Reference Numbers

**Before:**
```sql
-- Inconsistent across tables:
hesa_institution.pubukprn VARCHAR(8)      -- ✅ Correct
hesa_kiscourse.pubukprn VARCHAR(8)        -- ✅ Correct
hesa_ucascourseid.pubukprn VARCHAR(10)    -- ❌ Wrong
hesa_sbj.pubukprn VARCHAR(10)             -- ❌ Wrong
hesa_tariff.pubukprn VARCHAR(10)          -- ❌ Wrong
```

**After:**
```sql
-- All tables now consistent:
hesa_institution.pubukprn VARCHAR(8)      -- ✅ UKPRN is always 8 digits
hesa_kiscourse.pubukprn VARCHAR(8)
hesa_ucascourseid.pubukprn VARCHAR(8)
hesa_sbj.pubukprn VARCHAR(8)
hesa_tariff.pubukprn VARCHAR(8)
```

**Benefits:**
- ✅ Schema consistency across 11 tables
- ✅ Correct representation of UK government standard (8 digits)
- ✅ Prevents invalid data (>8 characters) from being stored

### 4. Removed Redundant Indexes

**Problem:** Multiple indexes duplicating functionality of PRIMARY KEY and UNIQUE constraints

**Before:**
```sql
-- Redundant indexes:
CREATE INDEX idx_course_hesa ON course(pubukprn, kiscourseid, kismode);
-- ❌ Redundant - UNIQUE constraint already creates this index

CREATE INDEX idx_sbj_course ON hesa_sbj(pubukprn, kiscourseid, kismode);
-- ❌ Redundant - PK (pubukprn, kiscourseid, kismode, sbj) already covers these columns

CREATE INDEX idx_ucascourseid_course ON hesa_ucascourseid(...);
-- ❌ Redundant - UNIQUE constraint already creates index

CREATE INDEX idx_tariff_course ON hesa_tariff(...);
-- ❌ Redundant - PK already covers these columns
```

**After:**
```sql
-- Only essential indexes:
CREATE INDEX idx_course_university ON course(university_id);     -- ✅ FK lookup
CREATE INDEX idx_requirement_course ON course_requirement(course_id);  -- ✅ FK lookup

-- Removed 4 redundant indexes (reduces database size & maintenance overhead)
```

**Benefits:**
- ✅ Reduced database size
- ✅ Faster INSERT/UPDATE operations (fewer indexes to maintain)
- ✅ Cleaner schema documentation

### 5. Added Automatic updated_at Triggers

**Problem:** `updated_at` timestamp never updates (only set on INSERT)

**Before:**
```sql
CREATE TABLE course (
    ...
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- ❌ Never updates on UPDATE
);
```

**After:**
```sql
CREATE TABLE course (
    ...
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- ✅ Updates automatically
);

-- Trigger function (PostgreSQL)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables
CREATE TRIGGER update_course_updated_at
BEFORE UPDATE ON course
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_university_updated_at
BEFORE UPDATE ON university
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

**Benefits:**
- ✅ Automatic timestamp tracking (no manual updates needed)
- ✅ Demonstrates advanced database skills (triggers)
- ✅ AQA Group A technique: Database triggers for automated behavior

### 6. Environment Variable Configuration

**Problem:** Hardcoded database passwords in source code

**Before:**
```python
# Hardcoded credentials (security risk)
conn = psycopg2.connect(
    user='postgres',
    password='postgres123',  # ❌ Hardcoded
    host='localhost'
)
```

**After:**
```python
# Environment variables (secure)
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    user=os.getenv('POSTGRES_USER', 'postgres'),
    password=os.getenv('POSTGRES_PASSWORD'),  # ✅ From .env file
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    port=os.getenv('POSTGRES_PORT', '5432')
)
```

**Environment File (server/.env):**
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=university_recommender

JWT_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

**Benefits:**
- ✅ Security: Passwords not in source control
- ✅ Flexibility: Easy to change credentials per environment
- ✅ Best practice: Industry-standard configuration management

## Database Tables Summary

**Application Tables (9 tables):**
1. `student` - Student profiles
2. `student_grade` - Student A-level grades
3. `student_career_interest` - Junction table for career interests ✨ NEW
4. `student_preferred_exam` - Junction table for exam preferences ✨ NEW
5. `career_interest` - Career category lookup ✨ NEW
6. `entrance_exam` - Exam type lookup
7. `university` - University information
8. `course` - Course offerings
9. `course_requirement` - Course entry requirements

**HESA Data Tables (11 tables):**
1. `hesa_institution` - HESA institution data
2. `hesa_kiscourse` - HESA course data
3. `hesa_ucascourseid` - UCAS course codes
4. `hesa_sbj` - Subject (CAH) codes
5. `hesa_tariff` - Tariff point distributions
6. `hesa_entry` - Entry qualifications
7. `hesa_employment` - Employment outcomes
8. `hesa_joblist` - Graduate job types
9. `hesa_gosalary` - Graduate salary data (6 months)
10. `hesa_leo3` - Longitudinal education outcomes (3 years)

**Mapping Table:**
- `subject_to_career` - Maps 21 CAH subject codes to 10 career categories (derived/seeded by subject_to_career_mapping.py - custom logic layer)

**Total: 25 tables** (14 application + 10 HESA + 1 system)

**Application Tables (14):**
1. student
2. subject
3. student_grade
4. university
5. course
6. course_requirement
7. entrance_exam
8. career_interest (lookup table)
9. student_preferred_exam (junction table)
10. student_career_interest (junction table)
11. course_required_exam
12. recommendation_run
13. recommendation_result
14. subject_to_career (derived/lookup - seeded by subject_to_career_mapping.py)

**HESA Tables (10):**
15. hesa_institution
16. hesa_kiscourse
17. hesa_employment
18. hesa_entry
19. hesa_gosalary
20. hesa_joblist
21. hesa_leo3
22. hesa_ucascourseid
23. hesa_sbj
24. hesa_tariff

**System Table (1):**
25. schema_migrations

## AQA Marking Scheme Alignment

### Group A Technical Skills Demonstrated

✅ **Complex data model in database (e.g. several interlinked tables)**
- 24 interlinked tables with foreign key relationships
- 3 junction tables for many-to-many relationships

✅ **Cross-table parameterised SQL**
- Recommendation engine uses complex JOINs across 8+ tables
- Career interest filtering via junction table

✅ **Aggregate SQL functions**
- Employability score calculations
- Match score aggregations

✅ **Database Triggers**
- Automatic `updated_at` timestamp management
- Advanced PostgreSQL features (plpgsql functions)

### Excellent Coding Style Characteristics

✅ **Defensive programming**
- CHECK constraints on data ranges
- Foreign key RESTRICT prevents invalid deletes
- Environment variable validation with defaults

✅ **Good exception handling**
- Transaction rollback on errors
- Graceful handling of duplicate HESA identifiers

✅ **Cohesive modules**
- Separate scripts for setup, import, mapping
- Clear single responsibility per module

## Migration Notes

### Breaking Changes

**Backend API:** Updated to use junction tables (backward compatible - API still returns arrays)
**Frontend:** No changes required - API contract unchanged

### Files Modified

**Database:**
- `server/database/setup_database.py` - Schema definitions
- `server/database/seed_career_interests.py` - Career/exam seed data
- `server/database/map_hesa_to_main_tables.py` - Import logic
- `server/database/check_table_counts.py` - Environment variables
- `server/database/list_tables.py` - Environment variables

**Backend API:**
- `server/app.py` - Junction table CRUD operations
- Added helper functions: `career_name_to_id()`, `exam_name_to_id()`

**Configuration:**
- `server/.env` - Environment variables
- `server/.env.example` - Template

### Database Recreation Required

Run full database setup to apply changes:

```bash
cd c:/projects/projectsigma
source venv/Scripts/activate
python server/database/setup_database.py
```

Expected statistics:
- 25 tables created (14 application + 10 HESA + 1 system)
- 478 universities imported
- 30,835 HESA courses imported
- ~5,000 courses mapped to application tables (filtered/deduplicated subset - rules in map_hesa_to_main_tables.py)
- 10 career interests seeded
- 5 entrance exams seeded

## Verification Queries

### Check Junction Tables
```sql
-- Count career interests per student
SELECT s.student_id, s.display_name, COUNT(sci.career_interest_id) as interest_count
FROM student s
LEFT JOIN student_career_interest sci ON s.student_id = sci.student_id
GROUP BY s.student_id, s.display_name;

-- Find students interested in specific career
SELECT s.display_name, ci.name as career
FROM student s
JOIN student_career_interest sci ON s.student_id = sci.student_id
JOIN career_interest ci ON sci.career_interest_id = ci.career_interest_id
WHERE ci.career_interest_id = 'healthcare';
```

### Verify UNIQUE Constraint
```sql
-- Should return 0 (no duplicates)
SELECT pubukprn, kiscourseid, kismode, COUNT(*) 
FROM course 
GROUP BY pubukprn, kiscourseid, kismode 
HAVING COUNT(*) > 1;
```

### Check Trigger Functionality
```sql
-- Update a course
UPDATE course SET name = 'Updated Name' WHERE course_id = 'COURSE_abc123';

-- Verify updated_at changed
SELECT course_id, name, created_at, updated_at 
FROM course 
WHERE course_id = 'COURSE_abc123';
-- updated_at should be > created_at
```

## Documentation Updates Required

Update these documentation files to reflect changes:
- ✅ `docs/database/SCHEMA_IMPROVEMENTS_2025.md` (this file)
- ⏳ `docs/design/HIGH_LEVEL_DESIGN.md` - Update schema section
- ⏳ `docs/nea/02_DESIGN.md` - Update database design diagrams
- ⏳ `README.md` - Update setup instructions

## References

- AQA A-Level Computer Science Marking Scheme (Group A Technical Skills)
- HESA Discover Uni Dataset Documentation
- PostgreSQL 13+ Documentation (Triggers, UNIQUE constraints)
- First Normal Form (1NF) definition: No repeating groups or arrays
