# Quick Start: Local PostgreSQL Setup

## 🚀 Fast Setup (5 Steps)

### Step 1: Install PostgreSQL

1. Download: https://www.postgresql.org/download/windows/
2. Install with default settings
3. **Remember your password!** (you'll need it)

### Step 2: Start PostgreSQL Service

**Method 1: Services GUI (Easiest)**

1. Press `Windows Key + R`
2. Type `services.msc` and press Enter
3. Find **"postgresql-x64-18 - PostgreSQL Server 18"** (or your version)
4. Right-click → **Start**
5. Wait for status to change to **"Running"**

**Method 2: PowerShell as Administrator**
1. Press `Windows Key + X`
2. Select **"Windows PowerShell (Admin)"** or **"Terminal (Admin)"**
3. Click **"Yes"** when prompted
4. Run:
   ```powershell
   # Check if running
   Get-Service postgresql*
   
   # Start the service (replace 18 with your version if different)
   Start-Service postgresql-x64-18
   
   # Verify it's running
   Get-Service postgresql-x64-18
   ```

**Expected Output:**
```
Status   Name               DisplayName
------   ----               -----------
Running  postgresql-x64-18  postgresql-x64-18 - PostgreSQL Server 18
```

**Verify Connection:**
```powershell
# Test connection
psql -U postgres -c "SELECT version();"

# Or check port
netstat -an | findstr :5432
```

### Step 3: Add PostgreSQL to PATH (Optional but Recommended)

1. Add `C:\Program Files\PostgreSQL\18\bin` to System PATH
2. Restart PowerShell

**To set PostgreSQL to start automatically:**
```powershell
# Run PowerShell as Administrator
Set-Service postgresql-x64-18 -StartupType Automatic
```

### Step 4: Configure Environment

```powershell
# Navigate to project
cd D:\Downloads\Programming\projectSigma\projectsigma

# Run setup script (update password first!)
. .\server\database\setup_local_env.ps1
```

**⚠️ Edit `setup_local_env.ps1` first to set your PostgreSQL password!**

### Step 5: Initialize Database

```powershell
cd server\database
python init_db.py
```

**Done!** ✅

---

## 🔍 Verify It Worked

```powershell
# Connect to database
psql -U postgres -d university_recommender

# List tables
\dt

# Exit
\q
```

---

## 📚 Full Guide

See `LOCAL_POSTGRES_SETUP.md` for detailed instructions.

---

## ⚠️ Common Issues

**"psql: command not found"**
→ Add PostgreSQL bin to PATH and restart PowerShell

**"Connection refused" / "Connection refused (0x0000274D/10061)"**
→ PostgreSQL service is not running. Start it using Method 1 or 2 above.

**"Access Denied" when starting service**
→ Run PowerShell as Administrator (see Method 2 above)

**"Password authentication failed"**
→ Update password in `setup_local_env.ps1`

**"Port 5432 already in use"**
→ Another PostgreSQL instance might be running. Check: `netstat -an | findstr :5432`

