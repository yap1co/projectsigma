# Database Import Order - Quick Reference

## ⚠️ CRITICAL: Run scripts in this exact order

After running `init_db.py`, you **MUST** follow this sequence:

## Step-by-Step Import Process

### ✅ Step 1: Initialize Database Schema
```bash
cd server/database
python init_db.py
```
**Status:** ✓ Already done  
**What it does:** Creates all tables and runs migrations

---

### 📥 Step 2: Import HESA Discover Uni CSV Data
```bash
cd server/database
python import_discover_uni_csv.py
```

**What it does:**
- Imports HESA CSV files from `data/` directory
- Populates HESA tables: `institution`, `kiscourse`, `employment`, etc.
- **Note:** These are raw HESA tables, NOT used by recommendation engine yet

**Required files in `data/` directory:**
- `INSTITUTION.csv`
- `KISCOURSE.csv`
- `EMPLOYMENT.csv`
- `GOSALARY.csv`
- `LEO3.csv`
- `ENTRY.csv`
- `JOBLIST.csv`
- And other HESA CSV files

**Expected time:** 5-15 minutes (depending on data size)

**Verify:**
```sql
SELECT COUNT(*) FROM institution;  -- Should be > 0
SELECT COUNT(*) FROM kiscourse;    -- Should be > 0
```

---

### 🔄 Step 3: Map HESA Data to Main Tables ⚠️ REQUIRED
```bash
cd server/database
python map_hesa_to_main_tables.py
```

**What it does:**
- Maps `institution` → `university` table
- Maps `kiscourse` → `course` table
- Creates `course_requirement` entries
- **This is REQUIRED for recommendation engine to work!**

**Expected time:** 2-5 minutes

**Verify:**
```sql
SELECT COUNT(*) FROM university;        -- Should be > 0
SELECT COUNT(*) FROM course;            -- Should be > 0
SELECT COUNT(*) FROM course_requirement; -- Should be > 0
```

**⚠️ IMPORTANT:** Without this step, the recommendation engine will have no data to work with!

---

### (Optional) Step 4: Import Custom CSV Files
```bash
cd server/database
python import_csv.py
```

**When to use:**
- You have custom `universities.csv` and `courses.csv` files
- You want to supplement HESA data
- You're not using HESA data at all

**Skip this step** if you're using HESA data (Steps 2-3).

---

## Complete Command Sequence

```bash
# Navigate to database directory
cd server/database

# Step 1: Initialize schema (if not done)
python init_db.py

# Step 2: Import HESA CSV data
python import_discover_uni_csv.py

# Step 3: Map to main tables (REQUIRED!)
python map_hesa_to_main_tables.py

# Step 4: Verify data
psql -U postgres -d university_recommender -c "SELECT COUNT(*) FROM university;"
psql -U postgres -d university_recommender -c "SELECT COUNT(*) FROM course;"
```

---

## Quick Verification

After completing all steps, verify:

```sql
-- Check main tables (used by recommendation engine)
SELECT COUNT(*) as universities FROM university;
SELECT COUNT(*) as courses FROM course;
SELECT COUNT(*) as requirements FROM course_requirement;

-- Check HESA tables (raw data)
SELECT COUNT(*) as institutions FROM institution;
SELECT COUNT(*) as kis_courses FROM kiscourse;
SELECT COUNT(*) as employment_data FROM employment;

-- Sample data
SELECT name, region FROM university LIMIT 5;
SELECT name, university_id FROM course LIMIT 5;
```

**Expected results:**
- `universities`: 100-200+
- `courses`: 1000-5000+
- `requirements`: 2000-10000+

---

## Common Mistakes

### ❌ Mistake 1: Skipping Step 3
**Problem:** Recommendation engine has no data  
**Symptom:** `SELECT COUNT(*) FROM university;` returns 0  
**Solution:** Run `map_hesa_to_main_tables.py`

### ❌ Mistake 2: Running scripts out of order
**Problem:** Foreign key errors, missing data  
**Solution:** Always run: init_db → import_discover_uni_csv → map_hesa_to_main_tables

### ❌ Mistake 3: Missing CSV files
**Problem:** Import script fails or imports partial data  
**Solution:** Ensure all required CSV files are in `server/database/data/` directory

---

## Troubleshooting

### "No data in university/course tables"
→ You skipped Step 3. Run `map_hesa_to_main_tables.py`

### "Foreign key constraint violation"
→ Run scripts in correct order (init_db → import → map)

### "File not found" errors
→ Check CSV files are in `server/database/data/` directory

### "Connection refused"
→ Ensure PostgreSQL is running and credentials are correct

---

## Script Locations

- `server/database/init_db.py` - Schema initialization
- `server/database/import_discover_uni_csv.py` - HESA CSV import
- `server/database/map_hesa_to_main_tables.py` - Map to main tables
- `server/database/import_csv.py` - Custom CSV import

---

## Need More Help?

- **Detailed guide:** See `server/database/data/README.md`
- **Database setup:** See `server/database/README.md`
- **Troubleshooting:** Check error messages and database logs
