# Infrastructure Setup Instructions - macOS

## Prerequisites

1. **Docker Desktop for Mac**
   - Download from: https://www.docker.com/products/docker-desktop
   - Install Docker Desktop for Mac (Apple Silicon or Intel)
   - Start Docker Desktop from Applications
   - Verify it's running: Docker icon in menu bar

2. **Python 3.11+**
   - macOS comes with Python 2.7 (deprecated)
   - Install Python 3 using Homebrew:
     ```bash
     brew install python@3.11
     ```
   - Or download from: https://www.python.org/downloads/
   - Verify: `python3 --version`

3. **Homebrew** (optional but recommended)
   - Install: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
   - Useful for installing dependencies

## Step 1: Start Docker Desktop

1. Open Docker Desktop from Applications
2. Wait for it to fully start (whale icon in menu bar)
3. Verify Docker is running:
   ```bash
   docker ps
   ```

**Note:** On Apple Silicon Macs, Docker Desktop uses ARM64 architecture. PostgreSQL images are compatible.

## Step 2: Install Python Dependencies

```bash
# Install PostgreSQL adapter and data processing libraries
pip3 install psycopg2-binary pandas

# Or using Homebrew Python
python3 -m pip install psycopg2-binary pandas
```

## Step 3: Start PostgreSQL Database

```bash
# Navigate to project directory
cd /path/to/projectsigma

# Start PostgreSQL container
docker-compose up -d postgres

# Check if it's running
docker-compose ps

# View logs
docker-compose logs postgres
```

## Step 4: Initialize Database Schema

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
# Run setup script (automated - creates database, imports HESA data)
cd server/database
python3 setup_database.py
```

## Step 5: Prepare CSV Files

Place your CSV files in `server/database/data/` directory:

```bash
# Create data directory if it doesn't exist
mkdir -p server/database/data

# Copy your CSV files
cp /path/to/your/universities.csv server/database/data/
cp /path/to/your/courses.csv server/database/data/
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

## Step 6: Import CSV Data

### Option A: Using Python Script (Recommended)

```bash
# Navigate to database directory
cd server/database

# Run import
python3 import_csv.py
```

### Option B: Using Docker

```bash
# Copy CSV files to data directory first
# Then run import in container
docker-compose exec backend python3 /app/database/import_csv.py
```

### Option C: Specify Custom Paths

```bash
python3 import_csv.py \
  --universities /path/to/universities.csv \
  --courses /path/to/courses.csv \
  --data-dir /path/to/data/directory
```

## Step 7: Verify Data Import

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

## Step 8: Access pgAdmin (Optional)

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

## macOS-Specific Notes

### File Paths
- Use forward slashes: `/Users/username/projects/projectsigma`
- No drive letters (unlike Windows)
- Home directory: `~` or `/Users/username`

### Terminal
- Default terminal: Terminal.app or iTerm2
- Shell: zsh (default on macOS Catalina+) or bash
- Commands are Unix-based (same as Linux)

### Docker Desktop
- Runs natively on macOS
- Apple Silicon (M1/M2/M3): Uses ARM64 containers (compatible)
- Intel Macs: Uses x86_64 containers
- Both architectures work fine with PostgreSQL

### Python
- Use `python3` command (not `python`)
- System Python is at `/usr/bin/python3`
- Homebrew Python is at `/opt/homebrew/bin/python3` (Apple Silicon) or `/usr/local/bin/python3` (Intel)

### Permissions
- May need to grant Terminal full disk access (System Preferences > Security & Privacy)
- Docker Desktop may request permissions on first run

## Troubleshooting

### Docker Desktop Not Running
```
Error: Cannot connect to Docker daemon
```
**Solution:** 
- Start Docker Desktop from Applications
- Check menu bar icon is green
- Wait for "Docker Desktop is running" message

### Python Command Not Found
```
command not found: python
```
**Solution:** Use `python3` instead of `python`:
```bash
python3 --version
python3 import_csv.py
```

### Permission Denied
```
Permission denied: /usr/local/bin/python3
```
**Solution:** Use `pip3` with `--user` flag:
```bash
pip3 install --user psycopg2-binary pandas
```

### Port Already in Use
```
Error: Bind for 0.0.0.0:5432 failed: port is already allocated
```
**Solution:** 
- Check if PostgreSQL is already running: `lsof -i :5432`
- Stop existing service: `docker-compose down`
- Or change port in docker-compose.yml

### Database Connection Error
```
Error: could not connect to server
```
**Solution:**
- Check PostgreSQL is running: `docker-compose ps`
- Check logs: `docker-compose logs postgres`
- Wait for health check to pass
- Verify Docker Desktop is running

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
- macOS TextEdit may save as MacRoman - convert to UTF-8:
  ```bash
  iconv -f MACINTOSH -t UTF-8 input.csv > output.csv
  ```

## Quick Start Commands (macOS)

```bash
# 1. Start Docker Desktop (from Applications)

# 2. Install dependencies
pip3 install psycopg2-binary pandas

# 3. Navigate to project
cd ~/path/to/projectsigma

# 4. Start infrastructure
docker-compose up -d postgres pgadmin

# 5. Wait for PostgreSQL to be ready
docker-compose logs -f postgres

# 6. Verify database
docker-compose exec postgres psql -U postgres -d university_recommender -c "\dt"

# 7. Import your CSV files
# Place universities.csv and courses.csv in server/database/data/
cd server/database
python3 import_csv.py

# 8. Verify import
docker-compose exec postgres psql -U postgres -d university_recommender -c "SELECT COUNT(*) FROM university;"
```

## Differences from Windows

| Aspect | Windows | macOS |
|--------|---------|-------|
| Python command | `python` | `python3` |
| File paths | `C:\Users\...` | `/Users/...` |
| Shell | PowerShell/CMD | zsh/bash |
| Docker paths | `\\wsl$\...` | `/Users/...` |
| Line endings | CRLF | LF |
| Permissions | Less strict | More strict |

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
5. Check Docker Desktop status in menu bar

