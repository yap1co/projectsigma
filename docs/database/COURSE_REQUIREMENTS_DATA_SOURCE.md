# Course Requirements Data Source

## Overview

Course requirements in the `course_requirement` table are **NOT directly imported from CSV files**. Instead, they are **derived from HESA data** during the mapping process from HESA tables to the main application tables.

---

## Data Flow

```
HESA Data (Raw)                    Application Data (Normalized)
┌─────────────────┐                ┌──────────────────────┐
│  sbj table      │ ────────────> │  course_requirement  │
│  (CAH codes)    │                │  (subject_id,        │
└─────────────────┘                │   grade_req)         │
┌─────────────────┐                └──────────────────────┘
│  entry table    │ ────────────> │  (grade inference)   │
│  (alevel count) │                └──────────────────────┘
└─────────────────┘
```

---

## Source: HESA Tables

### 1. **SBJ Table** (Primary Source for Subjects)

**Table**: `sbj` (HESA Discover Uni data)

**Schema**:
```sql
CREATE TABLE sbj (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    sbj VARCHAR(50) NOT NULL,  -- CAH subject code (e.g., CAH09-01-01)
    PRIMARY KEY (pubukprn, kiscourseid, kismode, sbj)
);
```

**Purpose**: Contains CAH (Common Aggregation Hierarchy) subject codes for each course.

**Example Data**:
```
pubukprn | kiscourseid | kismode | sbj
---------|-------------|---------|------------
10007784 | ABC123      | 01      | CAH09-01-01  (Computer Science)
10007784 | ABC123      | 01      | CAH10-01-01  (Mathematics)
```

**CSV Source**: `SBJ.csv` (imported via `import_discover_uni_csv.py`)

---

### 2. **ENTRY Table** (Source for Grade Inference)

**Table**: `entry` (HESA Discover Uni data)

**Schema**:
```sql
CREATE TABLE entry (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    entsbj VARCHAR(50),      -- Entry subject
    alevel INTEGER,           -- A-Level qualifications count
    access INTEGER,           -- Access qualifications count
    degree INTEGER,
    foundtn INTEGER,
    noquals INTEGER,
    other INTEGER,
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);
```

**Purpose**: Contains entry qualification statistics (how many students entered with A-Levels, Access courses, etc.).

**Example Data**:
```
pubukprn | kiscourseid | kismode | alevel | entsbj
---------|-------------|---------|--------|--------
10007784 | ABC123      | 01      | 150    | CAH09-01-01
```

**CSV Source**: `ENTRY.csv` (imported via `import_discover_uni_csv.py`)

---

## Mapping Process

### Location: `server/database/map_hesa_to_main_tables.py`

### Step-by-Step Process

#### Step 1: Fetch Course Data
```python
# Get all KIS courses
cur.execute("""
    SELECT pubukprn, kiscourseid, kismode, title
    FROM kiscourse
""")
courses_data = cur.fetchall()
```

#### Step 2: For Each Course, Get Entry Data
```python
# Get entry qualifications (A-level requirements)
cur.execute("""
    SELECT entsbj, alevel
    FROM entry
    WHERE pubukprn = %s AND kiscourseid = %s AND kismode = %s
    LIMIT 1
""", (pubukprn, kiscourseid, kismode))

entry_data = cur.fetchone()
```

**Purpose**: Check if course accepts A-Level students (`alevel > 0`)

#### Step 3: Get Subjects from SBJ Table
```python
# Get subjects from SBJ table
cur.execute("""
    SELECT DISTINCT sbj
    FROM sbj
    WHERE pubukprn = %s AND kiscourseid = %s AND kismode = %s
""", (pubukprn, kiscourseid, kismode))

subjects = [row['sbj'] for row in cur.fetchall() if row['sbj']]
```

**Result**: List of CAH codes (e.g., `['CAH09-01-01', 'CAH10-01-01']`)

#### Step 4: Create Course Requirements
```python
# Limit to 3 subjects (most courses require 2-3 subjects)
for subject_name in subjects[:3]:
    if subject_name:
        # Ensure subject exists in subject table
        subject_id = subject_name.replace(" ", "_").replace("&", "and")[:50]
        
        # Check if subject exists, create if not
        cur.execute("""
            SELECT subject_id FROM subject 
            WHERE subject_name = %s OR subject_id = %s
            LIMIT 1
        """, (subject_name, subject_id))
        
        existing_subj = cur.fetchone()
        if existing_subj:
            subject_id = existing_subj['subject_id']
        else:
            # Create subject if it doesn't exist
            cur.execute("""
                INSERT INTO subject (subject_id, subject_name)
                VALUES (%s, %s)
                ON CONFLICT (subject_id) DO NOTHING
            """, (subject_id, subject_name))
        
        # Infer grade requirement from entry data
        # If entry data shows A-levels, use A; otherwise use B
        default_grade = 'A' if (entry_data and entry_data.get('alevel', 0) > 0) else 'B'
        
        # Insert course requirement
        req_id = generate_id('REQ_')
        cur.execute("""
            INSERT INTO course_requirement (req_id, course_id, subject_id, grade_req)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (req_id) DO NOTHING
        """, (req_id, course_id, subject_id, default_grade))
```

---

## Key Points

### ✅ What IS Used:
1. **SBJ Table**: CAH codes (subject codes) for each course
2. **ENTRY Table**: A-Level acceptance count (to infer grade requirements)
3. **Subject Table**: Created/updated with CAH codes as subject IDs

### ❌ What is NOT Used:
1. **Direct CSV import** - No CSV file directly contains course requirements
2. **Explicit grade requirements** - HESA data doesn't have explicit grade requirements (A*, A, B, etc.)
3. **Subject names** - Uses CAH codes, not human-readable subject names

### ⚠️ Limitations:

1. **Grade Inference**:
   - **Not accurate**: Uses default grades ('A' or 'B') based on whether course accepts A-Levels
   - **No real grade requirements**: HESA data doesn't specify exact grade requirements (A*, A, B, etc.)
   - **Could be improved**: Could use `typical_offer_text` from `kiscourse` table to parse actual requirements

2. **Subject Limit**:
   - **Only 3 subjects**: Code limits to first 3 subjects from SBJ table
   - **May miss requirements**: Some courses might require more subjects

3. **CAH Code Mapping**:
   - **CAH codes, not A-Level subjects**: Uses CAH codes (e.g., `CAH09-01-01`) as subject IDs
   - **Needs mapping**: Should use `subject_course_mapping` table to map CAH codes to A-Level subjects

---

## Current Implementation Issues

### Problem 1: CAH Codes vs A-Level Subjects
**Current**: Uses CAH codes (e.g., `CAH09-01-01`) directly as `subject_id`

**Issue**: Recommendation engine expects A-Level subject names (e.g., "Mathematics", "Computer Science")

**Solution Needed**: Map CAH codes to A-Level subjects using `subject_course_mapping` table

### Problem 2: Default Grades
**Current**: Uses 'A' or 'B' as default grade

**Issue**: Not accurate - real courses have varied requirements (A*A*A, AAB, BBB, etc.)

**Solution Needed**: Parse `typical_offer_text` from `kiscourse` table to extract actual grade requirements

### Problem 3: Subject Limit
**Current**: Only takes first 3 subjects from SBJ table

**Issue**: May miss important required subjects

**Solution Needed**: Use all subjects or prioritize based on course structure

---

## Alternative Data Sources

### Option 1: Parse `typical_offer_text` from `kiscourse` Table

**Location**: `kiscourse.typical_offer_text`

**Example Values**:
- "AAB including Mathematics"
- "AAA with A* in Mathematics"
- "BBB or ABC"

**Benefit**: Would provide accurate grade requirements

**Challenge**: Requires natural language parsing

### Option 2: Use `subject_course_mapping` Table

**Location**: `subject_course_mapping` table

**Purpose**: Maps A-Level subjects to CAH codes

**Benefit**: Could convert CAH codes to A-Level subject names

**Usage**: 
```sql
SELECT a_level_subject 
FROM subject_course_mapping 
WHERE cah3_code = 'CAH09-01-01'
```

---

## Database Schema

### `course_requirement` Table
```sql
CREATE TABLE course_requirement (
    req_id VARCHAR(50) PRIMARY KEY,
    course_id VARCHAR(50) REFERENCES course(course_id) ON DELETE CASCADE,
    subject_id VARCHAR(50) REFERENCES subject(subject_id) ON DELETE RESTRICT,
    grade_req VARCHAR(5) NOT NULL CHECK (grade_req IN ('A*', 'A', 'B', 'C', 'D', 'E'))
);
```

**Columns**:
- `req_id`: Unique requirement ID (generated)
- `course_id`: Links to course
- `subject_id`: Links to subject (currently CAH code)
- `grade_req`: Required grade (currently inferred as 'A' or 'B')

---

## Import Order

1. **Import HESA CSV files** (`import_discover_uni_csv.py`)
   - Imports `SBJ.csv` → `sbj` table
   - Imports `ENTRY.csv` → `entry` table
   - Imports `KISCOURSE.csv` → `kiscourse` table

2. **Map HESA to Main Tables** (`map_hesa_to_main_tables.py`)
   - Reads from `sbj` and `entry` tables
   - Creates `course_requirement` entries
   - **This is where course requirements are created**

3. **Verify**:
```sql
SELECT COUNT(*) FROM course_requirement;  -- Should be > 0
```

---

## Summary

**Course requirements come from**:
1. ✅ **SBJ table** (HESA) - Provides CAH subject codes
2. ✅ **ENTRY table** (HESA) - Provides A-Level acceptance info (for grade inference)
3. ✅ **Mapping script** (`map_hesa_to_main_tables.py`) - Combines data to create requirements

**Current limitations**:
- ❌ Uses default grades ('A' or 'B') - not accurate
- ❌ Uses CAH codes as subject IDs - needs mapping to A-Level subjects
- ❌ Only takes first 3 subjects - may miss requirements

**Future improvements needed**:
- Parse `typical_offer_text` for accurate grade requirements
- Map CAH codes to A-Level subjects using `subject_course_mapping`
- Use all subjects, not just first 3

