# Discover Uni CSV Import Guide

This guide explains how to import Discover Uni CSV files into PostgreSQL and establish the relationships between tables.

## Overview

The Discover Uni dataset contains comprehensive information about UK higher education courses, including:
- Course details and locations
- Entry requirements and tariff points
- Student outcomes (employment, salaries, continuation)
- National Student Survey (NSS) results
- Teaching Excellence Framework (TEF) ratings
- Longitudinal Education Outcomes (LEO) data

## Database Relationships

### Core Entity Relationships

Based on the ERD diagrams, the main relationships are:

```
INSTITUTION (pubukprn)
  └── KISCOURSE (pubukprn, kiscourseid, kismode)
      ├── ACCREDITATION (via pubukprn, kiscourseid, kismode)
      ├── COURSELOCATION (via pubukprn, kiscourseid, kismode)
      │   └── UCASCOURSEID (via pubukprn, kiscourseid, kismode, locid)
      ├── SBJ (via pubukprn, kiscourseid, kismode)
      ├── ENTRY (via pubukprn, kiscourseid, kismode)
      ├── TARIFF (via pubukprn, kiscourseid, kismode)
      ├── CONTINUATION (via pubukprn, kiscourseid, kismode)
      ├── EMPLOYMENT (via pubukprn, kiscourseid, kismode)
      ├── JOBTYPE (via pubukprn, kiscourseid, kismode)
      ├── COMMON (via pubukprn, kiscourseid, kismode)
      │   └── JOBLIST (via pubukprn, kiscourseid, kismode, comsbj)
      ├── GOSALARY (via pubukprn, kiscourseid, kismode)
      ├── GOVOICEWORK (via pubukprn, kiscourseid, kismode)
      ├── LEO3 (via pubukprn, kiscourseid, kismode)
      ├── LEO5 (via pubukprn, kiscourseid, kismode)
      ├── NSS (via pubukprn, kiscourseid, kismode)
      └── NSSCOUNTRY (via pubukprn, kiscourseid, kismode)

LOCATION (ukprn, locid)
  └── COURSELOCATION (via ukprn, locid)

KIS_ AIM (kisaimcode)
  └── KISCOURSE (via kisaimcode)

ACCREDITATION_TABLE (acctype)
  └── ACCREDITATION (via acctype)
```

### Key Foreign Key Relationships

1. **INSTITUTION → KISCOURSE**
   - `kiscourse.pubukprn` → `institution.pubukprn`
   - One institution can have many courses

2. **KISCOURSE → All Course-Related Tables**
   - All course-related tables reference `(pubukprn, kiscourseid, kismode)`
   - Composite primary key ensures unique course instances

3. **LOCATION → COURSELOCATION**
   - `courselocation(ukprn, locid)` → `location(ukprn, locid)`
   - Links courses to their teaching locations

4. **KIS_ AIM → KISCOURSE**
   - `kiscourse.kisaimcode` → `kis_aim.kisaimcode`
   - Links courses to their qualification aim (BA, BSc, MEng, etc.)

5. **ACCREDITATION_TABLE → ACCREDITATION**
   - `accreditation.acctype` → `accreditation_table.acctype`
   - Links accreditation records to accreditation type descriptions

## Import Order

The import must follow this order to respect foreign key constraints:

1. **Lookup Tables** (no dependencies)
   - `KISAIM.csv` → `kis_aim`
   - `ACCREDITATIONTABLE.csv` → `accreditation_table`
   - `LOCATION.csv` → `location`

2. **Core Entities** (depend on lookup tables)
   - `INSTITUTION.csv` → `institution`
   - `KISCOURSE.csv` → `kiscourse` (references `institution` and `kis_aim`)

3. **Course-Related Entities** (depend on `kiscourse`)
   - `ACCREDITATION.csv` → `accreditation`
   - `COURSELOCATION.csv` → `courselocation`
   - `UCASCOURSEID.csv` → `ucascourseid` (depends on `courselocation`)
   - `SBJ.csv` → `sbj`

4. **Student Outcomes** (depend on `kiscourse`)
   - `ENTRY.csv` → `entry`
   - `TARIFF.csv` → `tariff`
   - `CONTINUATION.csv` → `continuation`

5. **Employment & Salary** (depend on `kiscourse`)
   - `EMPLOYMENT.csv` → `employment`
   - `JOBTYPE.csv` → `jobtype`
   - `COMMON.csv` → `common`
   - `JOBLIST.csv` → `joblist` (depends on `common`)
   - `GOSALARY.csv` → `gosalary`
   - `GOVOICEWORK.csv` → `govoicework`
   - `GOSECSAL.csv` → `gosecsal`

6. **LEO Data** (depend on `kiscourse`)
   - `LEO3.csv` → `leo3`
   - `LEO3SEC.csv` → `leo3sec`
   - `LEO5.csv` → `leo5`
   - `LEO5SEC.csv` → `leo5sec`

7. **NSS Data** (depend on `kiscourse`)
   - `NSS.csv` → `nss`
   - `NSSCOUNTRY.csv` → `nsscountry`

8. **TEF Data** (depends on `institution`)
   - `TEFOutcome.csv` → `tefoutcome`

9. **Additional Tables**
   - `AccreditationByHep.csv` → `accreditation_by_hep`

## Usage

### Prerequisites

1. PostgreSQL database running (via Docker Compose or local installation)
2. Database schema created (run `002_discover_uni_data_schema.sql` migration)
3. Python 3.8+ with required packages:
   ```bash
   pip install psycopg2-binary
   ```

### Running the Import

```bash
# Basic usage (imports all CSV files from ./data directory)
python server/database/import_discover_uni_csv.py

# Specify custom data directory
python server/database/import_discover_uni_csv.py --data-dir /path/to/csv/files

# Skip lookup tables (if already imported)
python server/database/import_discover_uni_csv.py --skip-lookup

# Skip core entities (if already imported)
python server/database/import_discover_uni_csv.py --skip-core
```

### Environment Variables

Set these environment variables if your database configuration differs:

```bash
export POSTGRES_DB=university_recommender
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
```

### Using Docker Compose

If using Docker Compose:

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Wait for database to be ready, then run import
python server/database/import_discover_uni_csv.py
```

## Relationship Examples

### Query: Get all courses for an institution

```sql
SELECT 
    i.legal_name,
    k.title,
    k.kiscourseid,
    ka.kisaimlabel
FROM institution i
JOIN kiscourse k ON i.pubukprn = k.pubukprn
LEFT JOIN kis_aim ka ON k.kisaimcode = ka.kisaimcode
WHERE i.pubukprn = '10000291'
ORDER BY k.title;
```

### Query: Get course locations

```sql
SELECT 
    k.title,
    l.locname,
    l.latitude,
    l.longitude
FROM kiscourse k
JOIN courselocation cl ON k.pubukprn = cl.pubukprn 
    AND k.kiscourseid = cl.kiscourseid 
    AND k.kismode = cl.kismode
LEFT JOIN location l ON cl.ukprn = l.ukprn AND cl.locid = l.locid
WHERE k.pubukprn = '10000291';
```

### Query: Get course accreditations

```sql
SELECT 
    k.title,
    a.acctype,
    at.acctext
FROM kiscourse k
JOIN accreditation a ON k.pubukprn = a.pubukprn 
    AND k.kiscourseid = a.kiscourseid 
    AND k.kismode = a.kismode
JOIN accreditation_table at ON a.acctype = at.acctype
WHERE k.pubukprn = '10000291';
```

### Query: Get employment outcomes for a course

```sql
SELECT 
    k.title,
    e.work,
    e.study,
    e.unemp,
    e.workstudy,
    gs.goinstmed AS median_salary
FROM kiscourse k
LEFT JOIN employment e ON k.pubukprn = e.pubukprn 
    AND k.kiscourseid = e.kiscourseid 
    AND k.kismode = e.kismode
LEFT JOIN gosalary gs ON k.pubukprn = gs.pubukprn 
    AND k.kiscourseid = gs.kiscourseid 
    AND k.kismode = gs.kismode
WHERE k.pubukprn = '10000291' AND k.kiscourseid = 'K00009';
```

## Troubleshooting

### Foreign Key Violations

If you encounter foreign key violations:
1. Ensure lookup tables are imported first
2. Check that `INSTITUTION.csv` is imported before `KISCOURSE.csv`
3. Verify CSV files contain valid reference values

### Missing Data

Some CSV files may have nullable foreign keys (e.g., `courselocation.locid`). The import script handles these gracefully.

### Performance

For large CSV files (like `KISCOURSE.csv` with 30K+ rows), the import uses batch processing. Expect the full import to take several minutes.

## File Mapping

| CSV File | Database Table | Key Columns |
|----------|---------------|-------------|
| KISAIM.csv | kis_aim | kisaimcode |
| ACCREDITATIONTABLE.csv | accreditation_table | acctype |
| LOCATION.csv | location | ukprn, locid |
| INSTITUTION.csv | institution | pubukprn |
| KISCOURSE.csv | kiscourse | pubukprn, kiscourseid, kismode |
| ACCREDITATION.csv | accreditation | pubukprn, kiscourseid, kismode, acctype |
| COURSELOCATION.csv | courselocation | pubukprn, kiscourseid, kismode, locid |
| UCASCOURSEID.csv | ucascourseid | pubukprn, kiscourseid, kismode, locid |
| SBJ.csv | sbj | pubukprn, kiscourseid, kismode, sbj |
| ENTRY.csv | entry | pubukprn, kiscourseid, kismode |
| TARIFF.csv | tariff | pubukprn, kiscourseid, kismode |
| CONTINUATION.csv | continuation | pubukprn, kiscourseid, kismode |
| EMPLOYMENT.csv | employment | pubukprn, kiscourseid, kismode |
| JOBTYPE.csv | jobtype | pubukprn, kiscourseid, kismode |
| COMMON.csv | common | pubukprn, kiscourseid, kismode, comsbj |
| JOBLIST.csv | joblist | pubukprn, kiscourseid, kismode, comsbj |
| GOSALARY.csv | gosalary | pubukprn, kiscourseid, kismode |
| GOVOICEWORK.csv | govoicework | pubukprn, kiscourseid, kismode |
| GOSECSAL.csv | gosecsal | gosecsbj, kismode, kislevel |
| LEO3.csv | leo3 | pubukprn, kiscourseid, kismode |
| LEO3SEC.csv | leo3sec | leo3secsbj, kismode, kislevel |
| LEO5.csv | leo5 | pubukprn, kiscourseid, kismode |
| LEO5SEC.csv | leo5sec | leo5secsbj, kismode, kislevel |
| NSS.csv | nss | pubukprn, kiscourseid, kismode |
| NSSCOUNTRY.csv | nsscountry | pubukprn, kiscourseid, kismode |
| TEFOutcome.csv | tefoutcome | pubukprn |
| AccreditationByHep.csv | accreditation_by_hep | pubukprn |

## Notes

- All CSV files use uppercase column names
- Some relationships allow NULL values (e.g., `courselocation.locid`)
- The `kismode` field typically indicates: `01` = Full-time, `02` = Part-time
- Welsh translations are included in many tables (columns ending with `w`)

