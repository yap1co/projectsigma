# Database Setup Guide

This directory contains PostgreSQL database migration files and initialization scripts.

## Structure

```
database/
├── migrations/
│   └── 001_initial_schema.sql    # Initial database schema
├── init_db.py                     # Database initialization script
└── README.md                      # This file
```

## Prerequisites

1. PostgreSQL 12+ installed and running
2. Python 3.11+ with `psycopg2` installed:
   ```bash
   pip install psycopg2-binary
   ```

## Environment Variables

Set these environment variables before running initialization:

```bash
export POSTGRES_DB=university_recommender
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
```

Or create a `.env` file:
```
POSTGRES_DB=university_recommender
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## Initialization

### Option 1: Using Python Script

```bash
cd server/database
python init_db.py
```

This script will:
1. Create the database if it doesn't exist
2. Run all migration files in order
3. Track applied migrations in `schema_migrations` table

## Data Import

**⚠️ IMPORTANT:** After running `init_db.py`, you must import data in the correct order.

### Quick Reference

See **[IMPORT_ORDER.md](./IMPORT_ORDER.md)** for a quick step-by-step guide.

### Detailed Guide

See **[data/README.md](./data/README.md)** for comprehensive import instructions.

### Import Sequence

1. **Initialize schema** (already done):
   ```bash
   python init_db.py
   ```

2. **Import HESA CSV data**:
   ```bash
   python import_discover_uni_csv.py
   ```

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
   ```

## Migration Files

Migration files are numbered sequentially (001_, 002_, etc.) and should be run in order.

Each migration file contains:
- CREATE TABLE statements
- ALTER TABLE statements for constraints
- CREATE INDEX statements
- Any data transformations

## Schema Overview

The database schema includes:

### Core Tables
- `student` - Student user accounts
- `subject` - A-Level subjects catalog
- `student_grade` - Student predicted grades per subject
- `university` - University information
- `course` - Course information
- `course_requirement` - Course entry requirements
- `entrance_exam` - Entrance exam catalog
- `course_required_exam` - Course-exam junction table
- `recommendation_run` - Recommendation run metadata
- `recommendation_result` - Recommendation results (JSONB)

### Constraints
- Primary keys (including composite PKs)
- Foreign keys with ON DELETE rules
- Check constraints for data validation
- Unique constraints

### Indexes
- BTREE indexes for JOINs and filters
- GIN indexes for arrays and JSONB
- Functional indexes for case-insensitive searches
- Partial indexes for common query patterns

## Verification

After initialization, verify the schema:

```bash
psql -d university_recommender -c "\dt"  # List tables
psql -d university_recommender -c "\di"  # List indexes
psql -d university_recommender -c "\d student"  # Describe table
```

## Local PostgreSQL Setup

See [docs/database/LOCAL_POSTGRES_SETUP.md](../../docs/database/LOCAL_POSTGRES_SETUP.md) for detailed installation and setup instructions.

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

