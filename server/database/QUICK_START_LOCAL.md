# Quick Start: Local PostgreSQL Setup

## 🚀 Fast Setup (5 Steps)

### Step 1: Install PostgreSQL

1. Download: https://www.postgresql.org/download/windows/
2. Install with default settings
3. **Remember your password!** (you'll need it)

### Step 2: Start PostgreSQL Service

```powershell
# Check if running
Get-Service postgresql*

# If not running, start it:
Start-Service postgresql-x64-15
```

### Step 3: Add PostgreSQL to PATH

1. Add `C:\Program Files\PostgreSQL\15\bin` to System PATH
2. Restart PowerShell

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

**"Connection refused"**
→ Check service is running: `Get-Service postgresql*`

**"Password authentication failed"**
→ Update password in `setup_local_env.ps1`

