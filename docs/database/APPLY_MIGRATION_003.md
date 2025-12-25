# Apply HESA Table Renaming

This guide explains how to apply the table renaming migration to your database.

## What This Migration Does

Renames HESA tables to have `hesa_` prefix for clarity:

- `institution` → `hesa_institution`
- `kiscourse` → `hesa_kiscourse`
- `employment` → `hesa_employment`
- `entry` → `hesa_entry`
- `gosalary` → `hesa_gosalary`
- `joblist` → `hesa_joblist`
- `leo3` → `hesa_leo3`

## Prerequisites

- PostgreSQL database `university_recommender` exists
- Tables `institution`, `kiscourse`, etc. exist (from migration 002)
- All code updates completed (recommendation_engine.py, map_hesa_to_main_tables.py)

## Apply Migration

### Option 1: Using psql (Recommended)

```bash
# Connect to database
psql -U postgres -d university_recommender

# Run migration
\i server/database/migrations/003_rename_hesa_tables.sql

# Verify
\dt hesa_*

# Expected output:
# hesa_employment
# hesa_entry
# hesa_gosalary
# hesa_institution
# hesa_joblist
# hesa_kiscourse
# hesa_leo3
```

### Option 2: Using Python Script

Create `server/database/run_migration_003.py`:

```python
import psycopg2
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from database_helper import get_db_connection

def run_migration():
    """Apply migration 003: Rename HESA tables"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("Applying migration 003: Rename HESA tables...")
        
        # Read migration file
        migration_path = Path(__file__).parent / 'migrations' / '003_rename_hesa_tables.sql'
        with open(migration_path, 'r') as f:
            sql = f.read()
        
        # Execute migration
        cur.execute(sql)
        conn.commit()
        
        print("✅ Migration 003 applied successfully")
        
        # Verify
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_name LIKE 'hesa_%'
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        print(f"\n✅ Renamed tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    run_migration()
```

Run it:
```bash
cd server/database
python run_migration_003.py
```

## Verify Migration

```sql
-- Check all hesa_ tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name LIKE 'hesa_%';

-- Verify old table names gone
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('institution', 'kiscourse', 'employment', 'entry', 'gosalary', 'joblist', 'leo3');
-- Should return 0 rows

-- Check migrations table
SELECT * FROM migrations ORDER BY version;
-- Should include version 3
```

## After Migration

### Test Recommendation Engine

```bash
cd server
python test_recommendations.py
```

Expected output:
```
Testing recommendation engine...
✅ Found 100 recommendations
✅ Top course: BSc Computer Science - University of Example (Score: 92)
✅ All courses have valid scores
```

### Test HESA Mapping

```bash
cd server/database
python map_hesa_to_main_tables.py
```

Should complete without errors.

## Rollback (If Needed)

If something goes wrong, rollback the migration:

```sql
BEGIN;

-- Rename back to original names
ALTER TABLE hesa_institution RENAME TO institution;
ALTER TABLE hesa_kiscourse RENAME TO kiscourse;
ALTER TABLE hesa_employment RENAME TO employment;
ALTER TABLE hesa_entry RENAME TO entry;
ALTER TABLE hesa_gosalary RENAME TO gosalary;
ALTER TABLE hesa_joblist RENAME TO joblist;
ALTER TABLE hesa_leo3 RENAME TO leo3;

-- Remove migration record
DELETE FROM migrations WHERE version = 3;

COMMIT;
```

Then revert code changes in `recommendation_engine.py` and `map_hesa_to_main_tables.py`.

## Next Steps

1. ✅ Run migration
2. ✅ Test recommendation engine
3. ✅ Test mapping script
4. Update frontend if needed (no changes required - backend API unchanged)
5. Commit changes to Git

```bash
git add server/database/migrations/003_rename_hesa_tables.sql
git add server/recommendation_engine.py
git add server/database/map_hesa_to_main_tables.py
git commit -m "Rename HESA tables with hesa_ prefix for clarity"
git push
```
