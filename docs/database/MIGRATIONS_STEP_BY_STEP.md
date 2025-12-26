# Step-by-Step Guide: Applying Discover Uni DDL to PostgreSQL

This guide will walk you through applying the Discover Uni database schema (`002_discover_uni_data_schema.sql`) to your PostgreSQL database.

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] **PostgreSQL 12+** installed locally (see [LOCAL_POSTGRES_SETUP.md](./LOCAL_POSTGRES_SETUP.md))
- [ ] **Python 3.11+** installed
- [ ] **psycopg2-binary** Python package installed
- [ ] Access to the project directory

---

## Setup Steps

### Step 1: Install PostgreSQL Locally

See [LOCAL_POSTGRES_SETUP.md](./LOCAL_POSTGRES_SETUP.md) for detailed installation instructions for Windows.

### Step 2: Navigate to Project Root

```bash
cd D:\Downloads\Programming\projectSigma\projectsigma
```

### Step 3: Verify PostgreSQL is Running

```bash
# Check PostgreSQL service status (Windows PowerShell)
Get-Service postgresql*

# Verify connection
psql -U postgres -c "SELECT version();"
```

### Step 4: Install Python Dependencies

```bash
# Install psycopg2-binary for database connection
pip install psycopg2-binary
```

### Step 5: Configure Environment Variables

Create `.env` file in `server/` directory:

```env
POSTGRES_DB=university_recommender
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### Step 6: Run Database Initialization Script

```bash
# Navigate to database directory
cd server/database

# Run the initialization script
python init_db.py
```

**Expected Output:**
```
============================================================
PostgreSQL Database Initialization
============================================================
✓ Database 'university_recommender' created successfully
  → Running migration: 001_initial_schema.sql
  ✓ Migration 001_initial_schema applied successfully
  → Running migration: 002_discover_uni_data_schema.sql
  ✓ Migration 002_discover_uni_data_schema applied successfully
✓ All migrations completed successfully

============================================================
✓ Database initialization complete!
============================================================
```

### Step 7: Verify Schema Creation

```bash
# Connect to PostgreSQL
psql -U postgres -d university_recommender

# Once connected, run these commands:
\dt                    # List all tables
\d kiscourse          # Describe kiscourse table
\d institution        # Describe institution table
\q                    # Exit psql
```

**Expected Tables:**
- `institution`
- `kiscourse`
- `accreditation`
- `accreditation_table`
- `courselocation`
- `ucascourseid`
- `sbj`
- `entry`
- `tariff`
- `continuation`
- `employment`
- `jobtype`
- `common`
- `joblist`
- `gosalary`
- `gosecsal`
- `govoicework`
- `leo3`
- `leo3sec`
- `leo5`
- `leo5sec`
- `nss`
- `nsscountry`
- `tefoutcome`
- `accreditation_by_hep`
- `kis_aim`
- `location`
- Plus tables from `001_initial_schema.sql`

---

## Method 2: Using Local PostgreSQL Installation (Recommended for Learning)

This guide uses local PostgreSQL installation. **This is recommended for A-level coursework as it gives you full control and understanding of how PostgreSQL works.**

**📚 See `LOCAL_POSTGRES_SETUP.md` for complete local installation guide.**

### Step 1: Verify PostgreSQL is Installed

```bash
# Check PostgreSQL version
psql --version

# Expected: PostgreSQL 12.0 or higher
```

### Step 2: Start PostgreSQL Service

**Windows:**
```powershell
# Start PostgreSQL service
net start postgresql-x64-15

# Or use Services app: Services → PostgreSQL → Start
```

**macOS/Linux:**
```bash
# macOS (using Homebrew)
brew services start postgresql@15

# Linux (using systemd)
sudo systemctl start postgresql
```

### Step 3: Set Environment Variables

**Windows PowerShell:**
```powershell
$env:POSTGRES_DB = "university_recommender"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "postgres"
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
```

**Windows CMD:**
```cmd
set POSTGRES_DB=university_recommender
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=postgres
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5432
```

**macOS/Linux:**
```bash
export POSTGRES_DB=university_recommender
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
```

### Step 4: Install Python Dependencies

```bash
pip install psycopg2-binary
```

### Step 5: Navigate to Database Directory

```bash
cd server/database
```

### Step 6: Run Database Initialization Script

```bash
python init_db.py
```

**Expected Output:** Same as Method 1, Step 6

### Step 7: Verify Schema Creation

```bash
# Connect to PostgreSQL
psql -h localhost -U postgres -d university_recommender

# Once connected, run these commands:
\dt                    # List all tables
\d kiscourse          # Describe kiscourse table
\q                    # Exit psql
```

---

## Method 3: Manual SQL Execution

If you prefer to run SQL commands manually.

### Step 1: Start PostgreSQL Service

**Windows (PowerShell):** Ensure PostgreSQL service is running

### Step 2: Create Database (if it doesn't exist)

**Create Database:**
```bash
createdb -U postgres university_recommender
```

### Step 3: Run Migration Files Using init_db.py (Recommended)

Use the initialization script which handles migrations automatically:

```bash
cd server/database
python init_db.py
```

**Or manually run migrations:**
```bash
# Navigate to migrations directory
cd server/database/migrations

# Run first migration
psql -h localhost -U postgres -d university_recommender -f 001_initial_schema.sql

# Run second migration (Discover Uni schema)
psql -h localhost -U postgres -d university_recommender -f 002_discover_uni_data_schema.sql
```

### Step 4: Verify Schema Creation

Same as previous methods - use `\dt` to list tables.

---

## Verification Steps

After applying the schema, verify everything is correct:

### 1. Check All Tables Exist

```bash
psql -U postgres -d university_recommender -c "\dt"

# Local
psql -h localhost -U postgres -d university_recommender -c "\dt"
```

### 2. Check Table Structure

```bash
psql -U postgres -d university_recommender -c "\d kiscourse"

# Local
psql -h localhost -U postgres -d university_recommender -c "\d kiscourse"
```

### 3. Check Foreign Keys

```bash
psql -U postgres -d university_recommender -c "
SELECT 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name;
"

# Local (same query)
psql -h localhost -U postgres -d university_recommender -c "SELECT ..."
```

### 4. Check Indexes

```bash
psql -U postgres -d university_recommender -c "\di"

# Local
psql -h localhost -U postgres -d university_recommender -c "\di"
```

### 5. Count Tables

```bash
psql -U postgres -d university_recommender -c "
SELECT COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'public';
"

# Should return: 27+ tables (depending on initial schema)
```

---

## Troubleshooting

### Issue: "Database already exists"

**Solution:** This is normal if you've run the script before. The script will skip creating the database and proceed with migrations.

### Issue: "Migration already applied"

**Solution:** The migration tracking system prevents duplicate migrations. If you need to re-run:
1. Connect to database
2. Delete the migration record: `DELETE FROM schema_migrations WHERE version = '002_discover_uni_data_schema';`
3. Re-run the migration

### Issue: "Connection refused" or "Cannot connect"

**Solutions:**
- Ensure PostgreSQL service is running: `Get-Service postgresql*` (Windows)
- **Local:** Check PostgreSQL service is running
- Verify connection credentials (host, port, user, password)
- Check firewall settings

### Issue: "Permission denied"

**Solutions:**
- Ensure PostgreSQL user has CREATE DATABASE privilege
- Check file permissions on migration files
- On Windows, run PowerShell/CMD as Administrator if needed

### Issue: "Syntax error" or "Table already exists"

**Solutions:**
- Check PostgreSQL logs for detailed error messages
- Ensure you're running migrations in order (001 before 002)
- If tables exist from a previous run, you may need to drop them first:
  ```sql
  DROP SCHEMA public CASCADE;
  CREATE SCHEMA public;
  ```

### Issue: Foreign Key Constraint Errors

**Solutions:**
- Ensure `001_initial_schema.sql` ran successfully first
- Check that referenced tables exist
- Verify data types match between foreign key and referenced column

---

## Next Steps: Importing CSV Data

After the schema is created, you can import your CSV data. See `import_csv.py` or create a custom import script.

**Quick Example:**
```python
import psycopg2
import csv

conn = psycopg2.connect(
    host="localhost",
    database="university_recommender",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()

# Example: Import institution data
with open('data/INSTITUTION.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cur.execute("""
            INSERT INTO institution (pubukprn, ukprn, legal_name, ...)
            VALUES (%s, %s, %s, ...)
        """, (row['PUBUKPRN'], row['UKPRN'], row['LEGAL_NAME'], ...))

conn.commit()
cur.close()
conn.close()
```

---

## Using pgAdmin (Web Interface)

If you prefer a graphical interface:

### Step 1: Access pgAdmin

1. Start pgAdmin (installed with PostgreSQL):
   - Windows: Launch from Start Menu
   - macOS: Launch from Applications
   - Linux: Run `pgadmin4` command

2. Open browser: pgAdmin will open automatically, or go to http://localhost:5050

3. Login:
   - Email: `admin@admin.com`
   - Password: `admin123`

### Step 2: Add Server Connection

1. Right-click "Servers" → "Register" → "Server"
2. General tab:
   - Name: `University Recommender`
3. Connection tab:
   - Host: `localhost`
   - Port: `5432`
   - Database: `university_recommender`
   - Username: `postgres`
   - Password: `postgres`
4. Click "Save"

### Step 3: Run Migration

1. Right-click on `university_recommender` database
2. Select "Query Tool"
3. Open `002_discover_uni_data_schema.sql` file
4. Click "Execute" (F5)

---

## Summary

✅ **Quick Start:**
```bash
# Ensure PostgreSQL service is running
# Then run init script
cd server/database
python init_db.py
cd server/database
python init_db.py
```

✅ **Quick Start (Local):**
```bash
# Set environment variables
export POSTGRES_DB=university_recommender
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432

# Run initialization
cd server/database
python init_db.py
```

The schema is now ready for your Discover Uni data! 🎉

