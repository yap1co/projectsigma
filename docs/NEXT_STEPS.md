# Next Steps: Database Setup & Full Test Suite

## 🎯 Goal
Initialize the database and get all 43 tests passing (currently 38/43).

## Step 1: Verify PostgreSQL is Running

### Check Service Status
```powershell
Get-Service postgresql-x64-18
```

### If Not Running, Start It

**Option A: Services GUI (Easiest)**
1. Press `Windows Key + R`
2. Type `services.msc` and press Enter
3. Find **"postgresql-x64-18 - PostgreSQL Server 18"**
4. Right-click → **Start**

**Option B: PowerShell as Admin**
1. Press `Windows Key + X`
2. Select **"Windows PowerShell (Admin)"**
3. Run:
   ```powershell
   Start-Service postgresql-x64-18
   Get-Service postgresql-x64-18
   ```

### Verify Connection
```powershell
psql -U postgres -c "SELECT version();"
```

If this works, you'll see PostgreSQL version info. If not, PostgreSQL isn't running or password is wrong.

---

## Step 2: Configure Environment Variables

### Option A: Update setup_local_env.ps1 (Recommended)

1. **Edit the setup script:**
   ```powershell
   notepad server\database\setup_local_env.ps1
   ```

2. **Update line 12** with your PostgreSQL password:
   ```powershell
   $env:POSTGRES_PASSWORD = "YOUR_ACTUAL_PASSWORD_HERE"
   ```

3. **Also update line 15** (DATABASE_URL):
   ```powershell
   $env:DATABASE_URL = "postgresql://postgres:YOUR_ACTUAL_PASSWORD_HERE@localhost:5432/university_recommender"
   ```

4. **Save and close**

### Option B: Create .env File

1. **Navigate to server directory:**
   ```powershell
   cd D:\Downloads\Programming\projectSigma\projectsigma\server
   ```

2. **Create .env file:**
   ```powershell
   New-Item -Path .env -ItemType File -Force
   ```

3. **Add content:**
   ```env
   POSTGRES_DB=university_recommender
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=YOUR_ACTUAL_PASSWORD_HERE
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD_HERE@localhost:5432/university_recommender
   JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
   FLASK_ENV=development
   ```

4. **Replace `YOUR_ACTUAL_PASSWORD_HERE`** with your PostgreSQL password

---

## Step 3: Initialize Database

### Run Setup Script (if using setup_local_env.ps1)
```powershell
cd D:\Downloads\Programming\projectSigma\projectsigma
. .\server\database\setup_local_env.ps1
```

### Initialize Database
```powershell
cd server\database
python setup_database.py
```

**Expected Output:**
```
============================================================
PostgreSQL Database Initialization
============================================================
✓ Database 'university_recommender' created successfully
✓ Running migration: 001_initial_schema.sql
✓ Migration applied successfully
✓ Database initialization complete!
```

**If you see errors:**
- **"Connection refused"** → PostgreSQL service not running (go back to Step 1)
- **"Password authentication failed"** → Wrong password (update Step 2)
- **"psql: command not found"** → Add PostgreSQL to PATH

---

## Step 4: Run Full Test Suite

### Run All Tests
```powershell
cd D:\Downloads\Programming\projectSigma\projectsigma\server
python -m pytest tests/ -v
```

### Expected Result
```
============================= test session starts =============================
...
43 passed in X.XXs
============================= 43 passed ==============================
```

**If some tests still fail:**
- Check that database is initialized (Step 3 completed)
- Verify environment variables are set correctly
- Check PostgreSQL service is running

---

## Step 5: Verify Everything Works

### Test Database Connection
```powershell
psql -U postgres -d university_recommender -c "\dt"
```

Should show all tables:
- student
- student_grade
- subject
- university
- course
- course_requirement
- recommendation_run
- recommendation_result
- schema_migrations

### Test API Health Endpoint
```powershell
cd D:\Downloads\Programming\projectSigma\projectsigma\server
python app.py
```

In another terminal:
```powershell
curl http://localhost:5000/api/health
```

Should return: `{"status": "healthy"}`

---

## ✅ Success Checklist

- [ ] PostgreSQL service is running
- [ ] Environment variables are configured
- [ ] Database is initialized (all tables created)
- [ ] All 43 tests pass
- [ ] API health endpoint responds

---

## 🆘 Troubleshooting

### "Connection refused (0x0000274D/10061)"
→ PostgreSQL service not running. Start it (Step 1).

### "Password authentication failed"
→ Wrong password. Update `setup_local_env.ps1` or `.env` file (Step 2).

### "Database does not exist"
→ Run `python setup_database.py` (Step 3).

### "psql: command not found"
→ Add PostgreSQL to PATH:
  1. Add `C:\Program Files\PostgreSQL\18\bin` to System PATH
  2. Restart PowerShell

### Tests still failing
→ Check:
  1. Database is initialized
  2. Environment variables are set
  3. PostgreSQL service is running
  4. Check test output for specific error messages

---

## 📚 Reference

- **PostgreSQL Setup**: `docs/database/QUICK_START_LOCAL.md`
- **Test Results**: `server/tests/TEST_RESULTS_SUMMARY.md`
- **Project Status**: `PROJECT_STATUS.md`
