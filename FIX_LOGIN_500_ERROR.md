# Fix Login 500 Error

## Problem
Login endpoint returns `500 INTERNAL SERVER ERROR` when trying to login.

## Root Cause
**Database connection failure**: `password authentication failed for user "postgres"`

The Flask server cannot connect to PostgreSQL because the password doesn't match.

## Solution Steps

### Step 1: Verify PostgreSQL is Running
```powershell
# Check PostgreSQL service status
Get-Service | Where-Object {$_.Name -like "*postgres*"}

# If not running, start it:
Start-Service postgresql-x64-18
# Or for version 15:
Start-Service postgresql-x64-15
```

### Step 2: Verify PostgreSQL Password

The `.env` file has `POSTGRES_PASSWORD=postgres123`, but PostgreSQL might have a different password.

**Option A: Test the password**
```powershell
cd server
$env:PGPASSWORD="postgres123"
psql -U postgres -h localhost -c "SELECT version();"
```

**Option B: Reset PostgreSQL password**
```powershell
# Connect to PostgreSQL (you'll need the current password)
psql -U postgres

# Then in psql:
ALTER USER postgres WITH PASSWORD 'postgres123';
\q
```

**Option C: Update .env file to match PostgreSQL password**
Edit `server/.env` and `server/database/.env`:
```
POSTGRES_PASSWORD=your_actual_postgres_password
```

### Step 3: Restart Flask Server

After fixing the password, restart the Flask server:

```powershell
# Stop the current server (Ctrl+C)
# Then restart:
cd server
python app.py
```

### Step 4: Test Login

Try logging in again with:
- Email: `charsipiya@gmail.com`
- Password: `dbf7cwz-gpt-KAR7hgb`

## Quick Fix Script

If you know your PostgreSQL password, update both .env files:

```powershell
# Update server/.env
$password = "your_actual_password"
$content = Get-Content server\.env
$content = $content -replace 'POSTGRES_PASSWORD=.*', "POSTGRES_PASSWORD=$password"
$content | Set-Content server\.env

# Update server/database/.env
$content = Get-Content server\database\.env
$content = $content -replace 'POSTGRES_PASSWORD=.*', "POSTGRES_PASSWORD=$password"
$content | Set-Content server\database\.env
```

## Verify User Exists

Once database connection works, check if user exists:

```powershell
cd server
python -c "from database_helper import get_db_connection; from psycopg2.extras import RealDictCursor; conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor); cur.execute('SELECT email, display_name FROM student WHERE email = %s', ('charsipiya@gmail.com',)); print(cur.fetchone()); conn.close()"
```

## If User Doesn't Exist

Register the user first:

1. Go to: http://localhost:3000/auth/register
2. Fill in the registration form
3. Use email: `charsipiya@gmail.com`
4. Use password: `dbf7cwz-gpt-KAR7hgb`
5. Complete registration
6. Then try logging in

## Expected Result

After fixing the database connection:
- Login should return `200 OK` with access token
- You should be redirected to the dashboard
- No more 500 errors
