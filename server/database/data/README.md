# Data Import Guide

This directory contains CSV files for importing data into the PostgreSQL database.

## ⚠️ IMPORTANT: Import Script Order

After running `init_db.py` to set up the database schema, you **MUST** run the import scripts in this exact order:

### Step 1: Initialize Database Schema (Already Done)
```bash
cd server/database
python init_db.py
```
This creates all tables and runs migrations.

### Step 2: Import HESA Discover Uni CSV Data
```bash
cd server/database
python import_discover_uni_csv.py
```

**What it does:**
- Imports all HESA Discover Uni CSV files from `data/` directory
- Populates HESA tables: `institution`, `kiscourse`, `employment`, `gosalary`, `leo3`, `entry`, `joblist`, etc.
- These are the **raw HESA data tables** (not used directly by recommendation engine)

**Required CSV files:**
- `INSTITUTION.csv` - University/institution data
- `KISCOURSE.csv` - Course data
- `EMPLOYMENT.csv` - Employment outcomes
- `GOSALARY.csv` - Graduate salary data
- `LEO3.csv` - 3-year earnings data
- `ENTRY.csv` - Entry statistics
- `JOBLIST.csv` - Job type data
- And other HESA CSV files

**Expected output:**
```
============================================================
DISCOVER UNI CSV DATA IMPORT
============================================================
IMPORTING LOOKUP TABLES
[1/3] Importing KISAIM.csv...
[2/3] Importing SBJ.csv...
[3/3] Importing COMMON.csv...

IMPORTING CORE ENTITIES
[1/2] Importing INSTITUTION.csv...
[2/2] Importing KISCOURSE.csv...

IMPORTING COURSE RELATED ENTITIES
[1/3] Importing COURSELOCATION.csv...
...

✓ Import completed successfully!
```

### Step 3: Map HESA Data to Main Tables
```bash
cd server/database
python map_hesa_to_main_tables.py
```

**What it does:**
- Reads from HESA tables (`institution`, `kiscourse`)
- Maps data to **main tables** used by recommendation engine:
  - `university` table (from `institution`)
  - `course` table (from `kiscourse`)
  - `course_requirement` table (from HESA entry data)
- This is the **critical step** that makes data available to the recommendation engine

**Expected output:**
```
============================================================
MAPPING HESA DATA TO MAIN TABLES
============================================================

[1/3] Mapping institutions to universities...
  OK: Mapped 150 institutions to universities

[2/3] Mapping KIS courses to courses...
  OK: Mapped 5000 courses

[3/3] Mapping course requirements...
  OK: Mapped 15000 course requirements

============================================================
MAPPING COMPLETE - Database Summary:
  Universities: 150
  Courses: 5000
  Course Requirements: 15000
============================================================
```

### Step 4: (Optional) Import Custom CSV Files
If you have custom CSV files (not HESA data), use:

```bash
cd server/database
python import_csv.py
```

**When to use:**
- You have custom `universities.csv` and `courses.csv` files
- You want to supplement HESA data with additional courses
- You're not using HESA data at all

**See below for CSV format requirements.**

---

## Quick Start: Complete Import Sequence

```bash
# 1. Initialize schema (if not done)
cd server/database
python init_db.py

# 2. Import HESA CSV data
python import_discover_uni_csv.py

# 3. Map to main tables (REQUIRED for recommendation engine)
python map_hesa_to_main_tables.py

# 4. Verify data
psql -U postgres -d university_recommender -c "SELECT COUNT(*) FROM university;"
psql -U postgres -d university_recommender -c "SELECT COUNT(*) FROM course;"
```

---

## Import Script Details

### `import_discover_uni_csv.py`

**Purpose:** Import HESA Discover Uni CSV files into HESA tables

**Location:** `server/database/import_discover_uni_csv.py`

**Data Directory:** `server/database/data/` (default)

**Command:**
```bash
python import_discover_uni_csv.py
```

**Options:**
```bash
python import_discover_uni_csv.py --data-dir /path/to/data
python import_discover_uni_csv.py --skip-lookup  # Skip lookup tables
python import_discover_uni_csv.py --skip-core    # Skip core entities
```

**Imports in order:**
1. **Lookup Tables**: KISAIM, SBJ, COMMON
2. **Core Entities**: INSTITUTION, KISCOURSE
3. **Course Related**: COURSELOCATION, UCASCOURSEID
4. **Student Outcomes**: CONTINUATION, ENTRY
5. **Employment**: EMPLOYMENT, GOSALARY, LEO3, JOBLIST
6. **Remaining**: NSS, TEF, etc.

**Tables populated:**
- `institution` - University/institution data
- `kiscourse` - Course data
- `employment` - Employment outcomes
- `gosalary` - Salary data
- `leo3` - 3-year earnings
- `entry` - Entry statistics
- `joblist` - Job types
- And other HESA tables

### `map_hesa_to_main_tables.py`

**Purpose:** Map HESA data to main tables used by recommendation engine

**Location:** `server/database/map_hesa_to_main_tables.py`

**Command:**
```bash
python map_hesa_to_main_tables.py
```

**What it does:**
1. Maps `institution` → `university` table
2. Maps `kiscourse` → `course` table
3. Creates `course_requirement` entries from HESA entry data
4. Links courses to universities via `university_id`

**Critical:** This step is **REQUIRED** for the recommendation engine to work. Without it, the `university` and `course` tables will be empty.

### `import_csv.py`

**Purpose:** Import custom CSV files (universities, courses)

**Location:** `server/database/import_csv.py`

**When to use:** Only if you have custom CSV files (not HESA data)

**Command:**
```bash
# Option 1: Place files in data/ directory
python import_csv.py

# Option 2: Specify file paths
python import_csv.py \
  --universities /path/to/universities.csv \
  --courses /path/to/courses.csv \
  --subjects /path/to/subjects.csv \
  --exams /path/to/exams.csv
```

---

## CSV File Formats

### For HESA Data (import_discover_uni_csv.py)

The HESA CSV files should follow the Discover Uni C25061 specification. Files are automatically detected in the `data/` directory.

**Key files:**
- `INSTITUTION.csv` - Institution/university data
- `KISCOURSE.csv` - Course data
- `EMPLOYMENT.csv` - Employment outcomes
- `GOSALARY.csv` - Graduate salary data
- `LEO3.csv` - 3-year earnings
- `ENTRY.csv` - Entry statistics
- `JOBLIST.csv` - Job types

### For Custom CSV Files (import_csv.py)

#### `universities.csv`

Required columns:
- `university_id` (or will be auto-generated)
- `name` (required)
- `region` (optional)
- `rank_overall` (optional)
- `employability_score` (optional, 0-100)
- `website_url` (optional)

Example:
```csv
university_id,name,region,rank_overall,employability_score,website_url
UNIV_001,University of Oxford,South East,1,95,https://www.ox.ac.uk
UNIV_002,University of Cambridge,East of England,2,94,https://www.cam.ac.uk
```

#### `courses.csv`

Required columns:
- `course_id` (or will be auto-generated)
- `university_id` (required - must match university in universities.csv)
- `name` or `course_name` (required)
- `ucas_code` (optional)
- `annual_fee` or `fee` or `uk_fees` (optional)
- `subject_rank` or `subject_ranking` (optional)
- `employability_score` or `employability` (optional, 0-100)
- `course_url` or `url` (optional)
- `typical_offer_text` or `typical_offer` (optional)
- `typical_offer_tariff` or `tariff` (optional)
- `required_subjects` or `subjects` (optional, comma-separated)
- `required_grades` or `grades` (optional, comma-separated)
- `required_exams` or `entrance_exams` (optional, comma-separated)

Example:
```csv
course_id,university_id,name,ucas_code,annual_fee,required_subjects,required_grades,typical_offer_tariff
COURSE_001,UNIV_001,Computer Science,G400,9250,"Mathematics,Computer Science","A*,A",152
COURSE_002,UNIV_002,Mathematics,G100,9250,"Mathematics,Further Mathematics","A*,A*",168
```

#### `subjects.csv` (Optional)

If not provided, default A-Level subjects will be created.

Columns:
- `subject_id` (or will be auto-generated)
- `subject_name` or `name` (required)

#### `exams.csv` (Optional)

If not provided, default entrance exams will be created.

Columns:
- `exam_id` (or will be auto-generated)
- `name` or `exam_name` (required)

---

## CSV Format Tips

1. **Headers**: First row should contain column names
2. **Encoding**: Use UTF-8 encoding
3. **Quotes**: Use double quotes for fields containing commas
4. **Missing Values**: Leave empty or use NULL
5. **IDs**: If not provided, unique IDs will be auto-generated

---

## Data Validation

The import scripts will:
- Auto-generate IDs if not provided
- Validate foreign key relationships (university_id must exist)
- Handle duplicate entries (ON CONFLICT DO UPDATE)
- Create default subjects and exams if CSV files not provided
- Report errors for invalid data

---

## Verification

After importing, verify the data:

```bash
# Connect to database
psql -U postgres -d university_recommender

# Check HESA tables (after Step 2)
SELECT COUNT(*) FROM institution;
SELECT COUNT(*) FROM kiscourse;
SELECT COUNT(*) FROM employment;

# Check main tables (after Step 3)
SELECT COUNT(*) FROM university;
SELECT COUNT(*) FROM course;
SELECT COUNT(*) FROM course_requirement;

# Check sample data
SELECT * FROM university LIMIT 5;
SELECT * FROM course LIMIT 5;
```

---

## Troubleshooting

### Common Issues

1. **"No data in university/course tables"**
   - **Solution**: You must run `map_hesa_to_main_tables.py` after importing HESA data
   - The recommendation engine uses `university` and `course` tables, not HESA tables directly

2. **"Foreign Key Errors"**
   - **Solution**: Ensure `university_id` in courses.csv exists in universities.csv
   - Or run imports in correct order: institutions first, then courses

3. **"Subject Not Found"**
   - **Solution**: Subject names must match exactly (case-insensitive)
   - Or provide subjects.csv file

4. **"Encoding Issues"**
   - **Solution**: Ensure CSV files are UTF-8 encoded
   - Check for special characters

5. **"Missing Columns"**
   - **Solution**: Use column aliases (e.g., `fee` instead of `annual_fee`)
   - Check CSV file headers match expected format

6. **"Import script not found"**
   - **Solution**: Make sure you're in `server/database/` directory
   - Check file exists: `ls import_discover_uni_csv.py`

### Debug Mode

For verbose output, check the script logs. Most scripts use Python logging:

```bash
# Check script output for detailed information
python import_discover_uni_csv.py 2>&1 | tee import.log
```

---

## Import Script Summary

| Script | Purpose | When to Run | Required Files |
|--------|---------|-------------|----------------|
| `init_db.py` | Create schema | First time setup | None |
| `import_discover_uni_csv.py` | Import HESA CSV data | After schema setup | HESA CSV files in `data/` |
| `map_hesa_to_main_tables.py` | Map HESA to main tables | **After HESA import** | None (reads from HESA tables) |
| `import_csv.py` | Import custom CSV | Optional (if not using HESA) | `universities.csv`, `courses.csv` |

---

## Next Steps

After importing data:

1. **Verify data**: Check counts in database
2. **Test recommendation engine**: Generate recommendations for a test student
3. **Check HESA enrichment**: Verify HESA data is linked to courses
4. **Update URLs**: Run `update_university_urls.py` if needed

---

## Additional Resources

- **Database Schema**: See `server/database/migrations/` for table structures
- **HESA Data Documentation**: See `data/readme.txt` for HESA file specifications
- **Troubleshooting**: See main `server/database/README.md` for database setup issues
