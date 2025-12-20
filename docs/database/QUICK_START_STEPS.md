# Quick Start Steps - PostgreSQL Setup

## Step-by-Step Commands

### Step 1: Connect to PostgreSQL
```bash
psql -U postgres -d postgres
```

### Step 2: Create the Database
```sql
CREATE DATABASE discover_uni_db;
```

### Step 3: Connect to the New Database
```sql
\c discover_uni_db
```

### Step 4: Set the Schema Path (Optional but Recommended)
```sql
CREATE SCHEMA IF NOT EXISTS discover_uni;
SET search_path TO discover_uni, public;
```

### Step 5: Run the DDL Script
```sql
\i server/database/traditional_ddl_setup.sql
```

Or if you're in a different directory:
```sql
\i D:/Downloads/Programming/projectSigma/projectsigma/server/database/traditional_ddl_setup.sql
```

### Step 6: Verify Tables Were Created
```sql
\dt discover_uni.*
```

Or:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'discover_uni' 
ORDER BY table_name;
```

### Step 7: Exit psql (Optional)
```sql
\q
```

### Step 8: Import Sample Data
```bash
python server/database/import_sample_data.py
```

### Step 9: Verify Relationships
```bash
psql -U postgres -d discover_uni_db -f server/database/verify_relationships.sql
```

## Alternative: Run DDL from Command Line

If you prefer to run the SQL file directly:

```bash
psql -U postgres -d discover_uni_db -f server/database/traditional_ddl_setup.sql
```

## Troubleshooting

### If database already exists:
```sql
DROP DATABASE IF EXISTS discover_uni_db;
CREATE DATABASE discover_uni_db;
```

### If you get permission errors:
Make sure you're using the `postgres` superuser account, or a user with CREATE DATABASE privileges.

### If file path doesn't work:
Use absolute path:
```sql
\i D:/Downloads/Programming/projectSigma/projectsigma/server/database/traditional_ddl_setup.sql
```

Or change directory first:
```sql
\cd D:/Downloads/Programming/projectSigma/projectsigma/server/database
\i traditional_ddl_setup.sql
```

