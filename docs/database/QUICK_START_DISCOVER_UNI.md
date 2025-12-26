# Quick Start: Import Discover Uni CSV Files

## Overview

This guide helps you import all Discover Uni CSV files into PostgreSQL with proper relationships established.

## Prerequisites

1. **PostgreSQL Database** - Local installation (see [LOCAL_POSTGRES_SETUP.md](./LOCAL_POSTGRES_SETUP.md))
2. **Database Schema** - Run the migration script first:
   ```bash
   psql -U postgres -d university_recommender -f server/database/migrations/002_discover_uni_data_schema.sql
   ```
3. **Python Dependencies**:
   ```bash
   pip install psycopg2-binary
   ```

## Quick Import

```bash
# From project root directory
python server/database/import_discover_uni_csv.py
```

The script will:
1. Import lookup tables (KISAIM, ACCREDITATIONTABLE, LOCATION)
2. Import core entities (INSTITUTION, KISCOURSE)
3. Import course-related entities (ACCREDITATION, COURSELOCATION, UCASCOURSEID, SBJ)
4. Import student outcomes (ENTRY, TARIFF, CONTINUATION)
5. Import employment data (EMPLOYMENT, JOBTYPE, COMMON, JOBLIST, GOSALARY, GOVOICEWORK)

## How Relationships Are Established

### Foreign Key Constraints

The database schema (`002_discover_uni_data_schema.sql`) defines foreign key relationships that automatically link tables:

1. **INSTITUTION → KISCOURSE**
   - Every course references an institution via `pubukprn`

2. **KISCOURSE → All Course Data**
   - All course-related tables reference `(pubukprn, kiscourseid, kismode)`
   - This composite key ensures data integrity

3. **LOCATION → COURSELOCATION**
   - Course locations link to location details via `(ukprn, locid)`

4. **KIS_ AIM → KISCOURSE**
   - Courses link to qualification aims (BA, BSc, etc.) via `kisaimcode`

5. **ACCREDITATION_TABLE → ACCREDITATION**
   - Accreditation records link to accreditation type descriptions

### Example Queries

**Get all courses for an institution:**
```sql
SELECT i.legal_name, k.title, ka.kisaimlabel
FROM institution i
JOIN kiscourse k ON i.pubukprn = k.pubukprn
LEFT JOIN kis_aim ka ON k.kisaimcode = ka.kisaimcode
WHERE i.pubukprn = '10000291';
```

**Get course with employment data:**
```sql
SELECT k.title, e.work, e.study, gs.goinstmed AS median_salary
FROM kiscourse k
LEFT JOIN employment e ON k.pubukprn = e.pubukprn 
    AND k.kiscourseid = e.kiscourseid 
    AND k.kismode = e.kismode
LEFT JOIN gosalary gs ON k.pubukprn = gs.pubukprn 
    AND k.kiscourseid = gs.kiscourseid 
    AND k.kismode = gs.kismode
WHERE k.pubukprn = '10000291';
```

## Import Order (Why It Matters)

The import follows a specific order to respect foreign key constraints:

1. **Lookup Tables** - No dependencies
2. **Core Entities** - Depend on lookup tables
3. **Course-Related** - Depend on KISCOURSE
4. **Student Outcomes** - Depend on KISCOURSE
5. **Employment** - Depend on KISCOURSE

If you try to import in the wrong order, PostgreSQL will reject the import due to foreign key violations.

## Troubleshooting

**Foreign Key Violations:**
- Ensure lookup tables are imported first
- Check that INSTITUTION.csv is imported before KISCOURSE.csv

**Missing Data:**
- Some CSV files have nullable foreign keys (e.g., `courselocation.locid`)
- The import script handles these gracefully

**Performance:**
- Large files (30K+ rows) use batch processing
- Full import may take 5-10 minutes

## Files Created

- `import_discover_uni_csv.py` - Main import script
- `DISCOVER_UNI_IMPORT_GUIDE.md` - Detailed documentation
- `QUICK_START_DISCOVER_UNI.md` - This file

## Next Steps

After importing:
1. Verify data with sample queries
2. Create indexes if needed for your use case
3. Set up your application to query the database
4. Consider creating views for common queries

## Support

For detailed information about:
- Table structures: See `002_discover_uni_data_schema.sql`
- CSV file formats: See `data/readme.txt`
- Relationship diagrams: See ERD images in project documentation

