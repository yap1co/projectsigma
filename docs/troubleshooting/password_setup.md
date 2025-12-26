# Where to Update PostgreSQL Password

## 🔑 Password Authentication Error

You're seeing: `password authentication failed for user "postgres"`

This means the password in your configuration doesn't match your actual PostgreSQL password.

---

## 📍 Option 1: Update `setup_local_env.ps1` (Recommended for PowerShell)

**File Location:** `server/database/setup_local_env.ps1`

**What to change:**

1. **Open the file:**
   ```powershell
   notepad server\database\setup_local_env.ps1
   ```

2. **Update line 12:**
   ```powershell
   $env:POSTGRES_PASSWORD = "YOUR_ACTUAL_PASSWORD_HERE"
   ```
   Replace `YOUR_ACTUAL_PASSWORD_HERE` with your PostgreSQL password.

3. **Update line 15 (DATABASE_URL):**
   ```powershell
   $env:DATABASE_URL = "postgresql://postgres:YOUR_ACTUAL_PASSWORD_HERE@localhost:5432/university_recommender"
   ```
   Replace `YOUR_ACTUAL_PASSWORD_HERE` with the same password.

4. **Save the file**

5. **Run the setup script before setup_database.py:**
   ```powershell
   cd D:\Downloads\Programming\projectSigma\projectsigma
   . .\server\database\setup_local_env.ps1
   cd server\database
   python setup_database.py
   ```

---

## 📍 Option 2: Create/Update `.env` File (Recommended for Python)

**File Location:** `server/.env` (in the `server` directory, not `server/database`)

**Steps:**

1. **Navigate to server directory:**
   ```powershell
   cd D:\Downloads\Programming\projectSigma\projectsigma\server
   ```

2. **Create or edit .env file:**
   ```powershell
   notepad .env
   ```

3. **Add/Update these lines:**
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

4. **Replace `YOUR_ACTUAL_PASSWORD_HERE`** with your actual PostgreSQL password

5. **Save the file**

6. **Now run setup_database.py:**
   ```powershell
   cd database
   python setup_database.py
   ```

**Note:** The `app.py` uses `load_dotenv()` which automatically loads `.env` from the `server/` directory.

---

## 📍 Option 3: Set Environment Variables Directly (Temporary)

**For current PowerShell session only:**

```powershell
$env:POSTGRES_PASSWORD = "YOUR_ACTUAL_PASSWORD_HERE"
$env:POSTGRES_DB = "university_recommender"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"

cd server\database
python setup_database.py
```

**Note:** This only works for the current PowerShell session. Close the terminal and you'll need to set them again.

---

## 🔍 How to Find Your PostgreSQL Password

If you don't remember your PostgreSQL password:

1. **Try common defaults:**
   - `postgres`
   - `postgres123`
   - The password you set during PostgreSQL installation

2. **Reset PostgreSQL password** (if needed):
   - See: `docs/database/QUICK_START_LOCAL.md` for instructions
   - Or search online for "reset PostgreSQL password Windows"

3. **Test your password:**
   ```powershell
   psql -U postgres -c "SELECT version();"
   ```
   If it prompts for a password and accepts it, that's your password.

---

## ✅ Quick Fix (Choose One)

### Method A: Using .env file (Easiest)
```powershell
# 1. Create .env file in server directory
cd D:\Downloads\Programming\projectSigma\projectsigma\server
notepad .env

# 2. Add this line (replace with your password):
POSTGRES_PASSWORD=your_password_here

# 3. Run setup
cd database
python setup_database.py
```

### Method B: Using setup script
```powershell
# 1. Edit setup script
notepad server\database\setup_local_env.ps1

# 2. Update line 12 with your password

# 3. Run setup script
. .\server\database\setup_local_env.ps1
cd server\database
python setup_database.py
```

---

## 🎯 Recommended Approach

**Use Option 2 (.env file)** because:
- ✅ Works automatically with `load_dotenv()` in `app.py`
- ✅ Persists across sessions
- ✅ Standard Python practice
- ✅ Easy to update

**File to create/edit:** `server/.env`

**Minimum required line:**
```env
POSTGRES_PASSWORD=your_actual_password_here
```

---

## ⚠️ Important Notes

1. **Password is case-sensitive** - Make sure you type it exactly as you set it
2. **No spaces** - Don't add spaces around the `=` sign
3. **File location matters** - `.env` should be in `server/` directory, not `server/database/`
4. **Don't commit .env** - The `.env` file is in `.gitignore` for security

---

## 🆘 Still Not Working?

1. **Verify PostgreSQL is running:**
   ```powershell
   Get-Service postgresql-x64-18
   ```

2. **Test password manually:**
   ```powershell
   psql -U postgres
   ```
   Enter password when prompted. If it works, use that exact password.

3. **Check for typos** in the password

4. **Try resetting PostgreSQL password** if you've forgotten it
