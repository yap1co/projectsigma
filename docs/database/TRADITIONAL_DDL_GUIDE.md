# Traditional DDL Approach - Step by Step Guide

This guide walks you through creating the Discover Uni database using traditional SQL DDL (Data Definition Language) approach.

## Overview

We'll create the database step-by-step:
1. Create database and schema
2. Create tables using DDL
3. Establish relationships with foreign keys
4. Import sample data to verify concepts

## Prerequisites

- PostgreSQL installed and running
- Access to PostgreSQL command line (`psql`) or GUI tool (pgAdmin, DBeaver, etc.)
- CSV files in the `data/` directory

## Step 1: Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE discover_uni_db;

# Connect to the new database
\c discover_uni_db;
```

Or using environment variables:
```bash
export PGPASSWORD=postgres
psql -U postgres -d discover_uni_db
```

## Step 2: Run DDL Script

Run the DDL script to create all tables and relationships:

```bash
psql -U postgres -d discover_uni_db -f server/database/traditional_ddl_setup.sql
```

Or in psql:
```sql
\i server/database/traditional_ddl_setup.sql
```

This script will:
- Create a schema `discover_uni`
- Create lookup tables (kis_aim, accreditation_table, location)
- Create core entities (institution, kiscourse)
- Create related tables (accreditation, courselocation, sbj, entry, employment)
- Establish all foreign key relationships

## Step 3: Verify Table Creation

Check that tables were created:

```sql
-- List all tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'discover_uni' 
ORDER BY table_name;

-- Expected output:
-- accreditation
-- accreditation_table
-- courselocation
-- employment
-- entry
-- institution
-- kis_aim
-- kiscourse
-- location
-- sbj
```

## Step 4: Verify Foreign Key Relationships

Check foreign keys:

```sql
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
  AND tc.table_schema = 'discover_uni'
ORDER BY tc.table_name;
```

Expected relationships:
- `kiscourse.pubukprn` → `institution.pubukprn`
- `kiscourse.kisaimcode` → `kis_aim.kisaimcode`
- `accreditation` → `kiscourse` (composite key)
- `accreditation.acctype` → `accreditation_table.acctype`
- `courselocation` → `kiscourse` (composite key)
- `courselocation` → `location` (composite key)
- `sbj` → `kiscourse` (composite key)
- `entry` → `kiscourse` (composite key)
- `employment` → `kiscourse` (composite key)

## Step 5: Import Sample Data

Import just a few rows to understand the relationships:

```bash
python server/database/import_sample_data.py
```

Or with custom sample size:
```bash
python server/database/import_sample_data.py --sample-size 10
```

This will import:
- 5 rows from each lookup table
- 5 rows from core entities
- 5 rows from related entities
- Verify relationships with sample queries

## Step 6: Test Relationships with Queries

### Query 1: Get courses with their institutions

```sql
SELECT 
    i.legal_name AS institution,
    k.title AS course_title,
    k.kiscourseid
FROM discover_uni.institution i
JOIN discover_uni.kiscourse k ON i.pubukprn = k.pubukprn
LIMIT 10;
```

**What this shows:** One-to-Many relationship (one institution has many courses)

### Query 2: Get courses with qualification types

```sql
SELECT 
    k.title AS course_title,
    ka.kisaimlabel AS qualification_type
FROM discover_uni.kiscourse k
LEFT JOIN discover_uni.kis_aim ka ON k.kisaimcode = ka.kisaimcode
LIMIT 10;
```

**What this shows:** Many-to-One relationship (many courses share qualification types)

### Query 3: Get courses with accreditations

```sql
SELECT 
    k.title AS course_title,
    at.acctext AS accreditation_type
FROM discover_uni.kiscourse k
JOIN discover_uni.accreditation a ON k.pubukprn = a.pubukprn 
    AND k.kiscourseid = a.kiscourseid 
    AND k.kismode = a.kismode
JOIN discover_uni.accreditation_table at ON a.acctype = at.acctype
LIMIT 10;
```

**What this shows:** Many-to-Many relationship (courses can have multiple accreditations)

### Query 4: Get courses with locations

```sql
SELECT 
    k.title AS course_title,
    l.locname AS location_name,
    l.latitude,
    l.longitude
FROM discover_uni.kiscourse k
JOIN discover_uni.courselocation cl ON k.pubukprn = cl.pubukprn 
    AND k.kiscourseid = cl.kiscourseid 
    AND k.kismode = cl.kismode
LEFT JOIN discover_uni.location l ON cl.ukprn = l.ukprn AND cl.locid = l.locid
LIMIT 10;
```

**What this shows:** Many-to-Many relationship (courses can be taught at multiple locations)

### Query 5: Get courses with employment outcomes

```sql
SELECT 
    k.title AS course_title,
    e.work AS employed_count,
    e.study AS studying_count,
    e.unemp AS unemployed_count
FROM discover_uni.kiscourse k
LEFT JOIN discover_uni.employment e ON k.pubukprn = e.pubukprn 
    AND k.kiscourseid = e.kiscourseid 
    AND k.kismode = e.kismode
WHERE e.work IS NOT NULL
LIMIT 10;
```

**What this shows:** One-to-One relationship (each course has one employment record)

## Understanding the Relationships

### 1. One-to-Many (1:N)
- **Institution → KIS Course**: One institution offers many courses
- **KIS Course → Entry**: One course has one entry qualifications record
- **KIS Course → Employment**: One course has one employment record

### 2. Many-to-One (N:1)
- **KIS Course → Institution**: Many courses belong to one institution
- **KIS Course → KIS Aim**: Many courses share the same qualification type

### 3. Many-to-Many (M:N)
- **KIS Course ↔ Accreditation**: Courses can have multiple accreditations, accreditations apply to multiple courses
- **KIS Course ↔ Location**: Courses can be taught at multiple locations, locations host multiple courses
- **KIS Course ↔ Subject**: Courses can cover multiple subjects, subjects appear in multiple courses

### 4. Junction Tables
- `accreditation`: Links courses to accreditation types
- `courselocation`: Links courses to locations
- `sbj`: Links courses to subject codes

## Key Concepts Demonstrated

1. **Primary Keys**: Uniquely identify each row
   - Simple: `institution.pubukprn`
   - Composite: `kiscourse(pubukprn, kiscourseid, kismode)`

2. **Foreign Keys**: Link tables together
   - Enforce referential integrity
   - Cascade deletes/updates appropriately

3. **Indexes**: Speed up queries
   - Created on foreign key columns
   - Created on frequently queried columns

4. **Constraints**: Ensure data quality
   - NOT NULL constraints
   - UNIQUE constraints
   - CHECK constraints (if needed)

## Next Steps

1. **Explore the data**: Run more complex queries
2. **Add more tables**: Follow the same pattern for TARIFF, CONTINUATION, GOSALARY, etc.
3. **Create views**: For common queries
4. **Add indexes**: Based on your query patterns
5. **Import full data**: When ready, use the full import script

## Troubleshooting

### Foreign Key Violations
If you get foreign key violations:
- Ensure lookup tables are populated first
- Check that referenced values exist
- Verify data types match

### Missing Data
- Some relationships allow NULL (e.g., `courselocation.locid`)
- Use LEFT JOIN to handle missing relationships

### Performance
- Add indexes for frequently queried columns
- Use EXPLAIN ANALYZE to optimize queries

## Files Created

- `traditional_ddl_setup.sql` - Complete DDL script
- `import_sample_data.py` - Sample data import script
- `TRADITIONAL_DDL_GUIDE.md` - This guide

## Summary

This traditional approach:
1. ✅ Creates database structure using DDL
2. ✅ Establishes relationships with foreign keys
3. ✅ Imports sample data to verify concepts
4. ✅ Demonstrates how relationships work in practice

You now understand how the database structure works and can extend it as needed!

