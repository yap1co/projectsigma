# Database Setup Guide

## Quick Start (New Developers)

### Prerequisites
1. PostgreSQL 15+ installed and running
2. Python 3.11+ with venv
3. 7 HESA CSV files in `data/` directory

### Setup Steps

```bash
# 1. Clone repository
git clone https://github.com/yap1co/projectsigma.git
cd projectsigma

# 2. Activate virtual environment
# Windows:
.\venv\Scripts\activate

# 3. Run database setup (drops existing DB and creates fresh)
cd server/database
python setup_database.py
```

**That's it!** The script will:
1. Drop existing `university_recommender` database (if exists)
2. Create fresh database
3. Create all tables (application + HESA)
4. Import HESA CSV data (7 files)
5. Map HESA data to application tables

### Expected Output

```
======================================================================
FRESH DATABASE SETUP - Project Sigma
======================================================================

======================================================================
STEP 1: DROP AND CREATE DATABASE
======================================================================
Terminating existing connections to university_recommender...
Dropping database university_recommender...
Creating database university_recommender...
✅ Database created successfully

======================================================================
STEP 2: CREATE DATABASE SCHEMA
======================================================================
Creating schema_migrations table...
Creating application tables...
Creating HESA tables...
Creating indexes...
✅ Schema created successfully

======================================================================
STEP 3: IMPORT HESA CSV DATA
======================================================================
[Progress logs...]
✅ HESA data imported successfully

======================================================================
STEP 4: MAP HESA TO APPLICATION TABLES
======================================================================
[Progress logs...]
✅ HESA data mapped successfully

======================================================================
✅ DATABASE SETUP COMPLETE!
======================================================================

Database Statistics:
  - HESA Institutions: 478
  - HESA Courses: 30,835
  - Universities: 956
  - Courses: 5,400
  - Course Requirements: 6,986

Database ready for use! 🎉
```

## Database Configuration

Default settings (edit in `setup_database.py` if needed):
- **Host:** localhost
- **Port:** 5432
- **User:** postgres
- **Password:** postgres123
- **Database:** university_recommender

## Required CSV Files

Place these 7 files in `data/` directory:
1. `INSTITUTION.csv` - University details
2. `KISCOURSE.csv` - Course information
3. `EMPLOYMENT.csv` - Graduate employment outcomes
4. `ENTRY.csv` - Entry requirements statistics
5. `GOSALARY.csv` - Graduate salary data
6. `JOBLIST.csv` - Common job types for graduates
7. `LEO3.csv` - Longitudinal earnings data (3 years after graduation)

## Database Schema

### Application Tables (7 tables)
- `user` - User accounts
- `university` - University information
- `course` - Course catalog
- `course_requirement` - Entry requirements per course
- `user_preference` - User profile and preferences
- `user_feedback` - Course ratings and feedback
- `career_interest` - Career interests lookup

### HESA Tables (7 tables)
- `hesa_institution` - Raw HESA institution data
- `hesa_kiscourse` - Raw HESA course data
- `hesa_employment` - Employment outcomes
- `hesa_entry` - Entry qualifications
- `hesa_gosalary` - Graduate salary data
- `hesa_joblist` - Job destinations
- `hesa_leo3` - Longitudinal earnings

## Troubleshooting

### "Database connection failed"
- Check PostgreSQL is running: `psql -U postgres`
- Verify password matches in `setup_database.py`

### "CSV file not found"
- Ensure all 7 CSV files are in `data/` directory
- Check file names match exactly (case-sensitive)

### "Permission denied"
- Run with postgres superuser privileges
- Or grant CREATE DATABASE permission to your user

## Manual Setup (Alternative)

If you prefer manual control:

```bash
# 1. Create database
psql -U postgres -c "CREATE DATABASE university_recommender"

# 2. Run schema (creates tables)
psql -U postgres -d university_recommender -f migrations/complete_schema.sql

# 3. Import HESA data
python import_discover_uni_csv.py

# 4. Map to application tables
python map_hesa_to_main_tables.py
```

## Resetting Database

To start fresh:
```bash
python setup_database.py
```

The script automatically drops existing database before recreating.

## Next Steps

After setup:
1. Start backend server: `cd ../.. && python app.py`
2. Start frontend: `cd client && npm run dev`
3. Access application: `http://localhost:3000`

## Support

For issues, see:
- [PROJECT_STATUS.md](../../docs/PROJECT_STATUS.md)
- [TROUBLESHOOTING.md](../../docs/troubleshooting/)
