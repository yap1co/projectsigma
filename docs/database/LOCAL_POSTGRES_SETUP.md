# Local PostgreSQL Setup Guide (Windows)

This guide will help you install and configure PostgreSQL locally on Windows for your A-level project.

## Step 1: Download and Install PostgreSQL

### Option A: Official PostgreSQL Installer (Recommended)

1. **Download PostgreSQL:**
   - Visit: https://www.postgresql.org/download/windows/
   - Click "Download the installer"
   - Download PostgreSQL 15.x (or latest stable version)
   - File will be named something like: `postgresql-15.x-x-windows-x64.exe`

2. **Run the Installer:**
   - Double-click the downloaded installer
   - Click "Next" through the welcome screen
   - **Important:** Choose installation directory (default is fine: `C:\Program Files\PostgreSQL\15`)
   - **Select Components:** Make sure these are checked:
     - ✅ PostgreSQL Server
     - ✅ pgAdmin 4 (GUI tool - very useful!)
     - ✅ Stack Builder (optional, but useful)
     - ✅ Command Line Tools (IMPORTANT - includes psql)
   - **Data Directory:** Default is fine (`C:\Program Files\PostgreSQL\15\data`)
   - **Password:** Set a password for the `postgres` superuser
     - **Remember this password!** You'll need it.
     - Example: `postgres123` (or something secure)
   - **Port:** Default `5432` is fine
   - **Advanced Options:** Default locale is fine
   - Click "Next" and "Finish"

3. **Verify Installation:**
   - Open PowerShell (as Administrator recommended)
   - Check if PostgreSQL service is running:
     ```powershell
     Get-Service postgresql*
     ```
   - Check PostgreSQL version:
     ```powershell
     psql --version
     ```

### Option B: Using Chocolatey (If you have it)

```powershell
# Install PostgreSQL
choco install postgresql15 --params '/Password:postgres123'

# Or install with default settings
choco install postgresql15
```

## Step 2: Start PostgreSQL Service

PostgreSQL should start automatically after installation, but verify:

### Check Service Status

```powershell
# Check if PostgreSQL service is running
Get-Service postgresql*

# If not running, start it:
Start-Service postgresql-x64-15  # Adjust version number if different
```

### Start Service Manually (if needed)

**Method 1: PowerShell (as Administrator)**
```powershell
Start-Service postgresql-x64-15
```

**Method 2: Services GUI**
1. Press `Win + R`, type `services.msc`, press Enter
2. Find "postgresql-x64-15" (or similar)
3. Right-click → Start (if stopped)

## Step 3: Configure Environment Variables

### Set PostgreSQL Path (if psql not found)

Add PostgreSQL bin directory to PATH:

1. **Find PostgreSQL installation:**
   - Usually: `C:\Program Files\PostgreSQL\15\bin`

2. **Add to PATH:**
   - Press `Win + X` → System → Advanced system settings
   - Click "Environment Variables"
   - Under "System variables", find "Path", click "Edit"
   - Click "New" and add: `C:\Program Files\PostgreSQL\15\bin`
   - Click OK on all dialogs
   - **Restart PowerShell** for changes to take effect

3. **Verify:**
   ```powershell
   psql --version
   # Should show: psql (PostgreSQL) 15.x
   ```

## Step 4: Test PostgreSQL Connection

```powershell
# Connect to PostgreSQL (will prompt for password)
psql -U postgres

# Or specify database
psql -U postgres -d postgres

# If it asks for password, enter the one you set during installation
```

**If connection fails:**
- Check service is running: `Get-Service postgresql*`
- Check port 5432 is not blocked by firewall
- Verify password is correct

## Step 5: Configure Your Project

### Update Environment Variables

Create or update `.env` file in `server/` directory:

```env
# PostgreSQL Configuration (Local)
POSTGRES_DB=university_recommender
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/university_recommender
```

**Important:** Replace `postgres123` with your actual PostgreSQL password!

### Set Environment Variables in PowerShell (Alternative)

```powershell
# Set for current session
$env:POSTGRES_DB = "university_recommender"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "postgres123"  # Your password
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
```

### Or Create a Setup Script

Create `server/database/setup_local_env.ps1`:

```powershell
# Setup Local PostgreSQL Environment Variables
$env:POSTGRES_DB = "university_recommender"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "postgres123"  # CHANGE THIS!
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
$env:DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/university_recommender"

Write-Host "Environment variables set for local PostgreSQL" -ForegroundColor Green
Write-Host "POSTGRES_HOST: $env:POSTGRES_HOST" -ForegroundColor Cyan
Write-Host "POSTGRES_PORT: $env:POSTGRES_PORT" -ForegroundColor Cyan
```

Run it before using database commands:
```powershell
. .\server\database\setup_local_env.ps1
```

## Step 6: Initialize Database Schema

### Create Database Manually (First Time)

```powershell
# Connect to PostgreSQL
psql -U postgres

# Inside psql, run:
CREATE DATABASE university_recommender;

# Exit psql
\q
```

### Or Use the Init Script

```powershell
# Navigate to database directory
cd server\database

# Set environment variables (if not using .env file)
$env:POSTGRES_DB = "university_recommender"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "postgres123"  # Your password
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"

# Run initialization script
python init_db.py
```

## Step 7: Verify Everything Works

```powershell
# Connect to your database
psql -U postgres -d university_recommender

# List all tables
\dt

# Should see tables like:
# - institution
# - kiscourse
# - accreditation
# - etc.

# Exit
\q
```

## Step 8: Using pgAdmin 4 (GUI Tool)

pgAdmin 4 is a graphical tool that makes database management easier:

1. **Open pgAdmin 4:**
   - Search for "pgAdmin 4" in Start menu
   - Or go to: `http://127.0.0.1:xxxxx` (port shown in pgAdmin)

2. **Connect to Server:**
   - Right-click "Servers" → "Register" → "Server"
   - General tab:
     - Name: `Local PostgreSQL`
   - Connection tab:
     - Host: `localhost`
     - Port: `5432`
     - Database: `postgres` (or `university_recommender`)
     - Username: `postgres`
     - Password: Your PostgreSQL password
   - Click "Save"

3. **Use pgAdmin:**
   - Browse databases
   - Run SQL queries
   - View table structures
   - Import/export data

## Common Commands Reference

### PostgreSQL Service Management

```powershell
# Check service status
Get-Service postgresql*

# Start service
Start-Service postgresql-x64-15

# Stop service
Stop-Service postgresql-x64-15

# Restart service
Restart-Service postgresql-x64-15
```

### psql Commands

```powershell
# Connect to database
psql -U postgres -d university_recommender

# Run SQL file
psql -U postgres -d university_recommender -f migrations\002_discover_uni_data_schema.sql

# Run SQL command
psql -U postgres -d university_recommender -c "SELECT COUNT(*) FROM kiscourse;"

# List databases
psql -U postgres -c "\l"

# List tables
psql -U postgres -d university_recommender -c "\dt"
```

### Inside psql (Interactive Mode)

```sql
-- List databases
\l

-- Connect to database
\c university_recommender

-- List tables
\dt

-- Describe table
\d kiscourse

-- List indexes
\di

-- Show table structure
\d+ kiscourse

-- Exit
\q
```

## Troubleshooting

### Issue: "psql: command not found"

**Solution:**
- Add PostgreSQL bin to PATH (see Step 3)
- Restart PowerShell
- Or use full path: `"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres`

### Issue: "Connection refused" or "could not connect"

**Solutions:**
1. Check PostgreSQL service is running:
   ```powershell
   Get-Service postgresql*
   ```
2. Check port 5432 is not in use:
   ```powershell
   netstat -an | findstr 5432
   ```
3. Check firewall allows PostgreSQL
4. Verify connection string is correct

### Issue: "password authentication failed"

**Solutions:**
1. Verify password is correct
2. Check `pg_hba.conf` file (usually in `C:\Program Files\PostgreSQL\15\data\`)
3. Reset password if needed:
   ```powershell
   # Stop service first
   Stop-Service postgresql-x64-15
   
   # Edit pg_hba.conf, change "md5" to "trust" temporarily
   # Start service
   Start-Service postgresql-x64-15
   
   # Connect and change password
   psql -U postgres
   ALTER USER postgres WITH PASSWORD 'newpassword';
   ```

### Issue: "database does not exist"

**Solution:**
```powershell
# Connect to default postgres database
psql -U postgres

# Create database
CREATE DATABASE university_recommender;

# Exit
\q
```

### Issue: "permission denied"

**Solutions:**
- Run PowerShell as Administrator
- Check PostgreSQL user permissions
- Verify data directory permissions

## Next Steps

1. ✅ PostgreSQL installed locally
2. ✅ Database created
3. ✅ Schema initialized
4. 📝 **Next:** Import CSV data (see import guide)

## Benefits of Local Setup

- ✅ Full control over PostgreSQL configuration
- ✅ Learn how PostgreSQL works internally
- ✅ Better understanding of database administration
- ✅ Can customize settings for learning
- ✅ No Docker overhead
- ✅ Direct access to PostgreSQL files and logs

## Useful Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- pgAdmin Documentation: https://www.pgadmin.org/docs/
- PostgreSQL Tutorial: https://www.postgresqltutorial.com/

---

**Remember:** Keep your PostgreSQL password secure and documented for your project!

