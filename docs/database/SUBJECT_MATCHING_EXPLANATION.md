# Subject Matching: How Student Subjects Match to Course Requirements

## The Problem

You've identified a critical issue: **subject IDs and subject names are the same** (both are CAH codes like "CAH01-01-02"), but students provide human-readable names like "Mathematics". This creates a mismatch in the matching logic.

## Current Flow

### 1. **Student Registration/Profile Update**

**Frontend sends** (ProfileSetup.tsx):
```typescript
aLevelSubjects: ["Mathematics", "Economics", "Physics"]
predictedGrades: {"Mathematics": "A", "Economics": "B", "Physics": "A"}
```

**Backend stores** (app.py lines 258-272):
```python
for subject_id in data['aLevelSubjects']:  # subject_id is actually "Mathematics"
    # Creates subject with same ID and name
    INSERT INTO subject (subject_id, subject_name)
    VALUES ('Mathematics', 'Mathematics')
    
    # Stores in student_grade
    INSERT INTO student_grade (student_id, subject_id, predicted_grade)
    VALUES (student_id, 'Mathematics', 'A')
```

**Database Result**:
- `subject` table: `subject_id = "Mathematics"`, `subject_name = "Mathematics"`
- `student_grade` table: `subject_id = "Mathematics"`, `predicted_grade = "A"`

### 2. **Course Requirements Storage**

Courses have requirements stored with **CAH codes**:
- `course_requirement.subject_id = "CAH01-01-02"` (CAH code)
- `subject.subject_id = "CAH01-01-02"`, `subject_name = "CAH01-01-02"` (same value)

### 3. **Loading Course Requirements** (recommendation_engine.py lines 1933-1950)

```python
# Query gets both subject_id and subject_name
SELECT s.subject_id, s.subject_name, cr.grade_req
FROM course_requirement cr
JOIN subject s ON cr.subject_id = s.subject_id
WHERE cr.course_id = %s

# Stores BOTH ID and name for matching
subjects = ["CAH01-01-02", "CAH01-01-02"]  # Both ID and name (same value)
requirements = {
    "CAH01-01-02": "A",  # By ID
    "CAH01-01-02": "A"   # By name (same key!)
}
```

### 4. **Loading Student Data** (database_helper.py lines 59-74)

```python
SELECT sg.subject_id, sg.predicted_grade, sub.subject_name
FROM student_grade sg
JOIN subject sub ON sg.subject_id = sub.subject_id
WHERE sg.student_id = %s

# Result:
student['aLevelSubjects'] = ["Mathematics", "Economics"]  # Subject IDs from database
student['predictedGrades'] = {"Mathematics": "A", "Economics": "B"}
```

### 5. **Matching Logic** (recommendation_engine.py _calculate_subject_match)

```python
# Student subjects
student_subjects_normalized = {"mathematics", "economics"}  # Lowercased

# Course required subjects
required_subjects_normalized = {"cah01-01-02", "cah01-01-02"}  # Lowercased CAH codes

# String matching
matching_required = student_subjects_normalized & required_subjects_normalized
# Result: set()  # EMPTY! They don't match!
```

## The Mismatch

**Student has**: `["Mathematics", "Economics"]`  
**Course requires**: `["CAH01-01-02", "CAH01-01-02"]`  
**Matching result**: ❌ **NO MATCH** (empty set)

## Why This Happens

The code was designed to handle flexible matching by storing both IDs and names, but there's an assumption that:
- Students might have subject IDs (CAH codes)
- Courses might have subject names

In reality:
- **Students have**: Human-readable names ("Mathematics")
- **Courses have**: CAH codes ("CAH01-01-02")
- **Database has**: Both stored as the same value (CAH codes for courses, names for students)

## HESA Data Analysis

**Important Finding**: The HESA data files **DO NOT contain human-readable subject names**. 

After checking the data files:
- ✅ `SBJ.csv` contains only CAH codes (e.g., "CAH01-01-02", "CAH02-05-01")
- ❌ No human-readable names in any HESA CSV files
- ❌ No mapping table in the provided data

**Where to get CAH code mappings:**
1. **HESA Official Documentation**: https://www.hesa.ac.uk/collection/C25061/filestructure
2. **CAH (Common Aggregation Hierarchy) specifications**: Available from HESA
3. **Create your own mapping**: Based on subject knowledge and course titles

The CAH codes follow a hierarchical structure:
- `CAH##-##-##` format
- Examples: `CAH01-01-02`, `CAH02-05-01`, `CAH03-02-01`
- You'll need to manually map these to A-Level subject names

**Common mappings** (examples - you'll need to verify with HESA docs):
- `CAH01-01-02` → Mathematics
- `CAH02-02-01` → Economics  
- `CAH03-02-01` → Physics
- `CAH03-03-01` → Chemistry
- `CAH03-04-01` → Biology

## Solutions

### Option 1: Create a Mapping Table (Recommended)

Create a `subject_mapping` table to translate between CAH codes and human-readable names:

```sql
CREATE TABLE subject_mapping (
    cah_code VARCHAR(50) PRIMARY KEY,
    human_readable_name VARCHAR(255) NOT NULL,
    UNIQUE(human_readable_name)
);

-- Example data (you'll need to populate this from HESA CAH documentation)
INSERT INTO subject_mapping VALUES
    ('CAH01-01-02', 'Mathematics'),
    ('CAH02-02-01', 'Economics'),
    ('CAH03-03-01', 'Physics'),
    ('CAH03-04-01', 'Biology'),
    ('CAH03-05-01', 'Chemistry');
    -- Add more mappings based on HESA CAH documentation
```

Then update the matching logic to:
1. Look up CAH code from student's subject name
2. Match CAH codes directly

### Option 2: Update Subject Table

Populate the `subject` table with proper human-readable names:

```sql
UPDATE subject 
SET subject_name = CASE 
    WHEN subject_id = 'CAH01-01-02' THEN 'Mathematics'
    WHEN subject_id = 'CAH02-02-01' THEN 'Economics'
    -- ... etc
END
WHERE subject_id LIKE 'CAH%';
```

Then ensure course requirements also store the human-readable name somewhere.

### Option 3: Store Human-Readable Names for Course Requirements

When importing course requirements, map CAH codes to human-readable names and store both:

```python
# When storing course requirements
cah_code = "CAH01-01-02"
human_name = map_cah_to_name(cah_code)  # Returns "Mathematics"

# Store both
subjects.append(cah_code)
subjects.append(human_name)
```

### Option 4: Normalize Student Subjects to CAH Codes

When a student registers, map their subject names to CAH codes:

```python
SUBJECT_NAME_TO_CAH = {
    "Mathematics": "CAH01-01-02",
    "Economics": "CAH02-02-01",
    # ... etc
}

# When storing student subjects
subject_name = "Mathematics"
cah_code = SUBJECT_NAME_TO_CAH.get(subject_name, subject_name)

# Store CAH code
INSERT INTO subject (subject_id, subject_name)
VALUES (cah_code, subject_name)  # Store CAH as ID, name as readable name
```

## Current Workaround

The current code attempts to work around this by:

1. **Storing both ID and name for courses** (lines 1949-1950):
   ```python
   subjects.append(subject_id)      # "CAH01-01-02"
   subjects.append(subject_name)    # "CAH01-01-02" (same value, doesn't help)
   ```

2. **String normalization and fuzzy matching** (scoring_components.py):
   - Normalizes to lowercase
   - Uses subject mappings (e.g., "mathematics" → ["mathematics", "maths", "math", "statistics"])
   - Matches against course names (not just subject IDs)

3. **Course name matching** as fallback:
   - Even if subject IDs don't match, it tries to match student subjects against course names
   - Example: Student has "Mathematics", course name contains "Mathematics" → match

## Recommended Fix

**Implement Option 1 (Mapping Table)** + **Option 4 (Normalize on Registration)**:

1. Create a `subject_mapping` table
2. Populate it with CAH code → human-readable name mappings
3. When student registers, look up CAH code for their subject name
4. Store CAH code as `subject_id`, human-readable name as `subject_name`
5. Matching will then work correctly (CAH codes match CAH codes)

This ensures:
- ✅ Students can input human-readable names (good UX)
- ✅ Courses use CAH codes (compatible with HESA data)
- ✅ Matching works correctly (both use CAH codes)
- ✅ Display can use human-readable names (from subject_name field)

## Code Changes Needed

1. **Create mapping table** (migration)
2. **Update registration endpoint** (app.py) to map names to CAH codes
3. **Update get_student_by_id** (database_helper.py) to return human-readable names from `subject_name`
4. **Update matching logic** to work with CAH codes consistently

This is a **critical bug** that needs to be fixed for the recommendation engine to work correctly!


# empty tables
SELECT * FROM public.accreditation_by_hep
ORDER BY accrediting_body_name ASC, hep ASC, kiscourseid ASC 

SELECT * FROM public.common
ORDER BY common_id ASC 

SELECT * FROM public.continuation
ORDER BY pubukprn ASC, kiscourseid ASC, kismode ASC 

SELECT * FROM public.course_required_exam
ORDER BY course_id ASC, exam_id ASC 

SELECT * FROM public.entrance_exam
ORDER BY exam_id ASC 
SELECT * FROM public.gosalary
ORDER BY pubukprn ASC, kiscourseid ASC, kismode ASC 

SELECT * FROM public.gosecsal
ORDER BY gosecsbj ASC, kismode ASC, kislevel ASC 

SELECT * FROM public.govoicework
ORDER BY pubukprn ASC, kiscourseid ASC, kismode ASC 

SELECT * FROM public.joblist
ORDER BY joblist_id ASC 

SELECT * FROM public.jobtype
ORDER BY pubukprn ASC, kiscourseid ASC, kismode ASC 

SELECT * FROM public.leo3
ORDER BY pubukprn ASC, kiscourseid ASC, kismode ASC 

SELECT * FROM public.leo3sec
ORDER BY leo3secsbj ASC, kismode ASC, kislevel ASC 

SELECT * FROM public.leo5
ORDER BY pubukprn ASC, kiscourseid ASC, kismode ASC 

SELECT * FROM public.leo5sec
ORDER BY leo5secsbj ASC, kismode ASC, kislevel ASC 

SELECT * FROM public.nss
ORDER BY pubukprn ASC, kiscourseid ASC, kismode ASC 

SELECT * FROM public.nsscountry
ORDER BY pubukprn ASC, kiscourseid ASC, kismode ASC 

SELECT * FROM public.tefoutcome
ORDER BY pubukprn ASC, ukprn ASC 