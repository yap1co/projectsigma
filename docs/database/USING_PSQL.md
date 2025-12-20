# Using psql with Docker PostgreSQL

Since you're using Docker for PostgreSQL, `psql` is not available directly on your Windows system. Here are your options:

## Option 1: Use psql Through Docker (Recommended)

### Basic Commands

```powershell
# Check PostgreSQL version
docker-compose exec postgres psql -U postgres --version

# Connect to database interactively
docker-compose exec postgres psql -U postgres -d university_recommender

# Run a single SQL command
docker-compose exec postgres psql -U postgres -d university_recommender -c "SELECT version();"

# List all tables
docker-compose exec postgres psql -U postgres -d university_recommender -c "\dt"

# Describe a table
docker-compose exec postgres psql -U postgres -d university_recommender -c "\d kiscourse"
```

### Interactive Session

```powershell
# Start interactive psql session
docker-compose exec postgres psql -U postgres -d university_recommender

# Once inside psql, you can use commands like:
# \dt          - List tables
# \d table     - Describe table
# \di          - List indexes
# \df          - List functions
# \q           - Quit
```

### Common psql Commands

```sql
-- List all tables
\dt

-- List tables with pattern
\dt kiscourse*

-- Describe table structure
\d kiscourse

-- List indexes
\di

-- List foreign keys
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

-- Count rows in a table
SELECT COUNT(*) FROM kiscourse;

-- Show table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Option 2: Install PostgreSQL Client Tools Locally

If you want `psql` available directly in PowerShell:

### Download PostgreSQL Client Tools

1. **Download PostgreSQL for Windows** (you only need the client tools):
   - Visit: https://www.postgresql.org/download/windows/
   - Or use: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
   - Download the installer (you can skip installing the server, just install client tools)

2. **During Installation:**
   - Select "Command Line Tools" component
   - Add PostgreSQL bin directory to PATH (usually `C:\Program Files\PostgreSQL\15\bin`)

3. **Verify Installation:**
   ```powershell
   # Restart PowerShell, then:
   psql --version
   ```

### Connect to Docker PostgreSQL

Once `psql` is installed locally:

```powershell
# Connect to Docker PostgreSQL
psql -h localhost -p 5432 -U postgres -d university_recommender

# Password: postgres
```

## Option 3: Create PowerShell Aliases

Make Docker psql commands easier to use:

### Create a PowerShell Profile Function

```powershell
# Open PowerShell profile
notepad $PROFILE

# Add these functions:
function psql-docker {
    docker-compose exec postgres psql -U postgres -d university_recommender $args
}

function psql-version {
    docker-compose exec postgres psql -U postgres --version
}

# Save and reload:
. $PROFILE
```

Then you can use:
```powershell
psql-docker -c "\dt"
psql-version
```

## Quick Reference: Docker vs Local psql

| Task | Docker Method | Local psql (if installed) |
|------|---------------|---------------------------|
| Connect | `docker-compose exec postgres psql -U postgres -d university_recommender` | `psql -h localhost -U postgres -d university_recommender` |
| Version | `docker-compose exec postgres psql -U postgres --version` | `psql --version` |
| Run SQL | `docker-compose exec postgres psql -U postgres -d university_recommender -c "SELECT ..."` | `psql -h localhost -U postgres -d university_recommender -c "SELECT ..."` |

## Recommended Approach

**For this project, use Option 1 (Docker method)** because:
- ✅ No additional installation needed
- ✅ Consistent with your Docker setup
- ✅ Works immediately
- ✅ All team members can use the same commands

You can create shortcuts/aliases if you use psql frequently!

