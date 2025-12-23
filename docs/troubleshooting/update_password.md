# ⚡ Quick Password Update Guide

## 🎯 Update the Password in the Existing `.env` File

### Step 1: Update `.env` File

**File:** `server/database/.env` (this file already exists!)

**What to do:**
1. Open `server/database/.env` in a text editor:
   ```powershell
   notepad server\database\.env
   ```
2. Find this line (currently shows `postgres123`):
   ```
   POSTGRES_PASSWORD=postgres123
   ```
3. Replace `postgres123` with your actual PostgreSQL password
4. Also update this line:
   ```
   DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/university_recommender
   ```
   Replace `postgres123` with the same password

### Step 2: Update `setup_local_env.ps1` (Optional - only if using PowerShell setup script)

**File:** `server/database/setup_local_env.ps1`

**What to do:**
1. Open `server/database/setup_local_env.ps1`
2. Find line 12:
   ```powershell
   $env:POSTGRES_PASSWORD = "postgres123"
   ```
3. Replace `"postgres123"` with your actual password
4. Also update line 15 (DATABASE_URL) with the same password

---

## 🚀 After Updating

Run the initialization:

```powershell
cd D:\Downloads\Programming\projectSigma\projectsigma\server\database
python init_db.py
```

---

## 🔍 How to Find Your Password

If you don't remember your PostgreSQL password:

1. **Try common defaults:**
   - `postgres`
   - `postgres123`
   - Password you set during installation

2. **Test it:**
   ```powershell
   psql -U postgres
   ```
   Enter password when prompted. If it works, that's your password!

3. **If you forgot it completely:**
   - You may need to reset PostgreSQL password
   - Or reinstall PostgreSQL with a known password

---

## ✅ Quick Command to Edit

```powershell
# Edit .env file
notepad server\.env

# Edit setup script
notepad server\database\setup_local_env.ps1
```

**Remember:** Replace `YOUR_PASSWORD_HERE` with your actual password in BOTH files!
