# Infrastructure Setup Instructions

**Platform:** Windows | **For macOS, see:** [SETUP_INSTRUCTIONS_MAC.md](./SETUP_INSTRUCTIONS_MAC.md)

## Prerequisites

1. **Docker Desktop** must be installed and running
   - Download from: https://www.docker.com/products/docker-desktop
   - Start Docker Desktop application
   - Verify it's running: Docker icon should be visible in system tray

2. **Python 3.11+** (for import scripts)
   - Verify: `python --version`
   - **Note:** On macOS, use `python3` instead of `python`

## Step 1: Start Docker Desktop

1. Open Docker Desktop application
2. Wait for it to fully start (whale icon in system tray)
3. Verify Docker is running:
   ```bash
   docker ps
   ```

## Step 2: Start PostgreSQL Database

```bash
# Start PostgreSQL container
docker-compose up -d postgres

# Check if it's running
docker-compose ps

# View logs
docker-compose logs postgres
```

## Step 3: Initialize Database Schema

The database schema will be automatically initialized when PostgreSQL starts (migrations are mounted).

To verify:
```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d university_recommender

# List tables
\dt

# Exit
\q
```

Or manually initialize:
```bash
# Install Python dependencies first
pip install psycopg2-binary pandas

# Run setup script (automated - creates database, imports HESA data)
cd server/database
python setup_database.py
```

## Step 4: Prepare CSV Files

Place your CSV files in `server/database/data/` directory:

```
server/database/data/
├── universities.csv
├── courses.csv
├── subjects.csv (optional)
└── exams.csv (optional)
```

### CSV File Format

See `server/database/data/README.md` for detailed format specifications.

**Minimum required columns:**

**universities.csv:**
- `name` (required)
- `university_id` (optional, auto-generated if missing)
- `region`, `rank_overall`, `employability_score`, `website_url` (optional)

**courses.csv:**
- `name` or `course_name` (required)
- `university_id` (required - must exist in universities.csv)
- `course_id` (optional, auto-generated if missing)
- Other columns optional (see README.md)

## Step 5: Import CSV Data

### Option A: Using Python Script (Recommended)

```bash
# Install dependencies
pip install psycopg2-binary pandas

# Run import
cd server/database
python import_csv.py
```

### Option B: Using Docker

```bash
# Copy CSV files to data directory first
# Then run import in container
docker-compose exec backend python /app/database/import_csv.py
```

### Option C: Specify Custom Paths

```bash
python import_csv.py \
  --universities /path/to/universities.csv \
  --courses /path/to/courses.csv \
  --data-dir /path/to/data/directory
```

## Step 6: Verify Data Import

```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d university_recommender

# Check counts
SELECT COUNT(*) FROM university;
SELECT COUNT(*) FROM course;
SELECT COUNT(*) FROM subject;
SELECT COUNT(*) FROM entrance_exam;

# View sample data
SELECT * FROM university LIMIT 5;
SELECT * FROM course LIMIT 5;
```

## Step 7: Access pgAdmin (Optional)

1. Start pgAdmin:
   ```bash
   docker-compose up -d pgadmin
   ```

2. Open browser: http://localhost:8081

3. Login:
   - Email: `admin@admin.com`
   - Password: `admin123`

4. Add Server:
   - Name: `University Recommender`
   - Host: `postgres` (or `localhost` if connecting from host)
   - Port: `5432`
   - Database: `university_recommender`
   - Username: `postgres`
   - Password: `postgres`

## Troubleshooting

### Docker Desktop Not Running
```
Error: Cannot connect to Docker daemon
```
**Solution:** Start Docker Desktop application

### Port Already in Use
```
Error: Bind for 0.0.0.0:5432 failed: port is already allocated
```
**Solution:** 
- Stop existing PostgreSQL: `docker-compose down`
- Or change port in docker-compose.yml

### Database Connection Error
```
Error: could not connect to server
```
**Solution:**
- Check PostgreSQL is running: `docker-compose ps`
- Check logs: `docker-compose logs postgres`
- Wait for health check to pass

### CSV Import Errors

**Foreign Key Violation:**
- Ensure `university_id` in courses.csv exists in universities.csv
- Check for typos in university IDs

**Subject Not Found:**
- Subject names must match exactly (case-insensitive)
- Or provide subjects.csv file

**Encoding Issues:**
- Ensure CSV files are UTF-8 encoded
- Check for special characters

## Quick Start Commands

```bash
# 1. Start Docker Desktop (manual)

# 2. Start infrastructure
docker-compose up -d postgres pgadmin

# 3. Wait for PostgreSQL to be ready
docker-compose logs -f postgres

# 4. Verify database
docker-compose exec postgres psql -U postgres -d university_recommender -c "\dt"

# 5. Import your CSV files
# Place universities.csv and courses.csv in server/database/data/
cd server/database
python import_csv.py

# 6. Verify import
docker-compose exec postgres psql -U postgres -d university_recommender -c "SELECT COUNT(*) FROM university;"
```

## Next Steps

After importing data:
1. Start backend: `docker-compose up -d backend`
2. Start frontend: `docker-compose up -d frontend`
3. Test API endpoints
4. Run recommendation algorithm

## Support

For issues:
1. Check Docker logs: `docker-compose logs`
2. Check database logs: `docker-compose logs postgres`
3. Verify CSV format matches README.md specifications
4. Check database connection: `docker-compose exec postgres pg_isready`

 