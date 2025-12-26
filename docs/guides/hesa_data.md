# Importing HESA Data (C25061)

This guide explains how to import official HESA (Higher Education Statistics Agency) data from https://www.hesa.ac.uk/collection/C25061/filestructure into the database.

## Current Status

✅ **HESA schema tables exist** (institution, kiscourse, entry, sbj, employment, etc.)
❌ **HESA data not yet imported** (0 records in HESA tables)
✅ **Main tables exist** (university, course) - currently have sample data

## Step-by-Step Import Process

### Step 1: Download HESA C25061 Data

1. Visit: https://www.hesa.ac.uk/collection/C25061/filestructure
2. Download the CSV files for the latest academic year
3. Required files include:
   - `INSTITUTION.csv` - University/institution data
   - `KISCOURSE.csv` - Course data
   - `ENTRY.csv` - Entry qualification data
   - `SBJ.csv` - Subject data
   - `EMPLOYMENT.csv` - Employment outcomes
   - `LOCATION.csv` - Location data
   - `KISAIM.csv` - KIS Aim lookup
   - `ACCREDITATIONTABLE.csv` - Accreditation lookup
   - And other related files

### Step 2: Place Files in Data Directory

Copy all downloaded CSV files to:
```
server/database/data/
```

### Step 3: Run HESA Data Import

```bash
cd server/database
python import_discover_uni_csv.py --data-dir ./data
```

This will:
- Import lookup tables (KISAIM, ACCREDITATIONTABLE, LOCATION)
- Import core entities (INSTITUTION, KISCOURSE)
- Import course-related data (ACCREDITATION, COURSELOCATION, UCASCOURSEID, SBJ)
- Import student outcomes (ENTRY, etc.)
- Import employment data (EMPLOYMENT, etc.)

### Step 4: Map HESA Data to Main Tables

After HESA data is imported, map it to the main tables used by the recommendation engine:

```bash
cd server/database
python map_hesa_to_main_tables.py
```

This script will:
- Map `institution` → `university` table
- Map `kiscourse` → `course` table
- Extract entry requirements from `entry` and `sbj` tables
- Extract employability data from `employment` table
- Create course requirements with subject and grade mappings

### Step 5: Verify Import

Check the database counts:

```bash
cd server/database
python check_hesa_data.py
```

Or manually:
```bash
cd server
python -c "from database_helper import get_db_connection; from psycopg2.extras import RealDictCursor; conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor); cur.execute('SELECT COUNT(*) as count FROM university'); print('Universities:', cur.fetchone()['count']); cur.execute('SELECT COUNT(*) as count FROM course'); print('Courses:', cur.fetchone()['count']); cur.close(); conn.close()"
```

## Expected Results

After successful import, you should have:
- **150+ universities** (all UK higher education institutions)
- **Thousands of courses** (all courses from HESA data)
- **Course requirements** (subjects and inferred grade requirements)
- **Real employability data** (from HESA employment statistics)

## Important Notes

1. **Grade Requirements**: HESA data doesn't include explicit A-level grade requirements. The mapping script will:
   - Use subject requirements from `SBJ` table
   - Infer grade requirements based on entry qualification data
   - Default to reasonable grades (A/B) based on course type

2. **Data Volume**: HESA data is extensive. The mapping script limits to 5000 courses initially to avoid overwhelming the system. You can adjust this limit in `map_hesa_to_main_tables.py`.

3. **Schema**: The HESA data uses a different schema structure. The mapping script bridges this gap.

4. **Sample Data**: The current sample data (25 universities, 50 courses) will be supplemented, not replaced, by HESA data.

## Troubleshooting

### "Table does not exist" errors
- Run the setup script: `python setup_database.py` (creates all 25 tables)
- This automatically creates both application and HESA tables

### "File not found" errors
- Ensure CSV files are in `server/database/data/` directory
- Check file names match exactly (case-sensitive on some systems)

### "No data imported"
- Check CSV file encoding (should be UTF-8)
- Verify CSV files have headers matching HESA structure
- Check for errors in import script output

## Next Steps After Import

Once HESA data is imported and mapped:
1. The recommendation engine will use real UK university data
2. You'll have access to all courses from official HESA sources
3. Recommendations will be based on actual course requirements
4. You can remove sample data if desired (or keep it for testing)

## Files Reference

- **Import Script**: `server/database/import_discover_uni_csv.py`
- **Mapping Script**: `server/database/map_hesa_to_main_tables.py`
- **Check Script**: `server/database/check_hesa_data.py`
- **Schema**: `server/database/migrations/002_discover_uni_data_schema.sql`
- **Data Directory**: `server/database/data/`
