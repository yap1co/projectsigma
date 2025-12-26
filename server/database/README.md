# Database Setup Guide

## 🚀 Quick Start (Recommended for New Developers)

**Single command to set up everything:**

```bash
cd server/database
python setup_database.py
```

This automated script will:
1. ✅ Drop existing database (if exists)
2. ✅ Create fresh `university_recommender` database
3. ✅ Create all tables (application + HESA)
4. ✅ Import all 7 HESA CSV files
5. ✅ Map HESA data to application tables

**📖 Detailed Guide:** See [SETUP_GUIDE.md](./SETUP_GUIDE.md)

---

## Prerequisites

1. **PostgreSQL 15+** installed and running
2. **Python 3.11+** with dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```
3. **10 HESA CSV files** in `../../data/` directory

## Database Configuration

Default settings (configured via environment variables):
- Host: `localhost` (default)
- Port: `5432` (default)
- User: `postgres` (default)
- Password: Must be set in `.env` file (POSTGRES_PASSWORD)
- Database: `university_recommender`

## Required CSV Files

Place these in `data/` directory:
1. `INSTITUTION.csv` - University information (478 institutions)
2. `KISCOURSE.csv` - Course catalog (~30,835 courses)
3. `EMPLOYMENT.csv` - Graduate employment statistics
4. `ENTRY.csv` - Entry requirements
5. `GOSALARY.csv` - Graduate salaries
6. `JOBLIST.csv` - Job destinations
7. `LEO3.csv` - Earnings data (Longitudinal Education Outcomes)
8. `SBJ.csv` - Subject codes/classifications
9. `TARIFF.csv` - UCAS tariff points
10. `UCASCOURSEID.csv` - UCAS course identifiers

---

## Manual Setup (Advanced)

If you need more control:

3. **Map HESA data to main tables** (REQUIRED):
   ```bash
   python map_hesa_to_main_tables.py
   ```

4. **(Optional) Import custom CSV files**:
   ```bash
   python import_csv.py
   ```

**Note:** Step 3 is **critical** - without it, the recommendation engine will have no data to work with!

### Option 2: Manual Setup

1. Create database:
   ```bash
   createdb university_recommender
   ```

2. Run migrations:
   ```bash
   psql -d university_recommender -f migrations/001_initial_schema.sql
### Step 1: Create Database
```bash
psql -U postgres -c "CREATE DATABASE university_recommender"
```

### Step 2: Run Schema
```bash
cd migrations
psql -U postgres -d university_recommender -f 001_initial_schema.sql
psql -U postgres -d university_recommender -f 002_discover_uni_data_schema.sql
```

### Step 3: Import Data
```bash
cd ..
python import_discover_uni_csv.py
```

### Step 4: Map HESA Data
```bash
python map_hesa_to_main_tables.py
```

---

## Database Schema

### Application Tables (7 tables)
- **user** - User accounts
- **university** - Universities (mapped from HESA)
- **course** - Courses (mapped from HESA)
- **course_requirement** - Entry requirements per course
- **user_preference** - User preferences and grades
- **user_feedback** - Course ratings and feedback
- **career_interest** - Career interests lookup

### HESA Tables (7 tables)
- **hesa_institution** - Raw HESA institution data
- **hesa_kiscourse** - Raw HESA course data
- **hesa_employment** - Employment outcomes
- **hesa_entry** - Entry qualifications
- **hesa_gosalary** - Graduate salaries
- **hesa_joblist** - Job destinations
- **hesa_leo3** - Longitudinal earnings (3 years)

### Relationships
- `course.university_id` → `university.university_id`
- `course.(pubukprn, kiscourseid, kismode)` → HESA tables
- `course_requirement.course_id` → `course.course_id`
- `user_preference.user_id` → `user.user_id`
- `user_feedback.course_id` → `course.course_id`

---

## Resetting Database

To start completely fresh:
```bash
python setup_database.py
```

The script safely drops existing database before recreating.

---

## Verification

After setup, verify the database:

```bash
# Connect to database
psql -U postgres -d university_recommender

# Check tables
\dt

# Check data counts
SELECT 'HESA Institutions' as table_name, COUNT(*) FROM hesa_institution
UNION ALL
SELECT 'HESA Courses', COUNT(*) FROM hesa_kiscourse
UNION ALL
SELECT 'Universities', COUNT(*) FROM university
UNION ALL
SELECT 'Courses', COUNT(*) FROM course;

# Exit
\q
```

Expected counts:
- HESA Institutions: ~478
- HESA Courses: ~30,835
- Universities: ~956
- Courses: ~5,400

---

## Troubleshooting

### "Database connection failed"
- Check PostgreSQL is running: `psql -U postgres`
- Verify credentials in `setup_database.py`

### "CSV file not found"
- Ensure all 7 CSV files are in `../../data/` directory
- Check file names match exactly

### "Permission denied"
- Ensure postgres user has CREATE DATABASE privilege
- Run: `psql -U postgres -c "ALTER USER postgres CREATEDB;"`

---

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `setup_database.py` | **Automated setup** - Drops and recreates everything |
| `import_discover_uni_csv.py` | Import 7 HESA CSV files |
| `map_hesa_to_main_tables.py` | Map HESA → application tables |
| `init_db.py` | Legacy: Create DB and run migrations |
| `add_sample_data.py` | Add test data for development |

**For new developers:** Use `setup_database.py` only.

---

## Support

- **Setup Issues:** See [SETUP_GUIDE.md](./SETUP_GUIDE.md)
- **Project Status:** See [../../docs/PROJECT_STATUS.md](../../docs/PROJECT_STATUS.md)
- **Troubleshooting:** See [../../docs/troubleshooting/](../../docs/troubleshooting/)

psql -d university_recommender -c "\di"  # List indexes
psql -d university_recommender -c "\d student"  # Describe table
```

## Troubleshooting

### Connection Errors
- Ensure PostgreSQL is running: `pg_isready`
- Check connection credentials
- Verify firewall/network settings

### Migration Errors
- Check PostgreSQL logs
- Ensure previous migrations completed successfully
- Manually verify schema_migrations table

### Permission Errors
- Ensure database user has CREATE DATABASE privilege
- Check file permissions on migration files

