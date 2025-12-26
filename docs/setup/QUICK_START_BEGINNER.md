# Quick Start - For Complete Beginners

**⏱️ Estimated Time: 2-3 hours**

## 📋 Before You Start Checklist

- [ ] Computer with Windows 10/11
- [ ] Administrator access
- [ ] Internet connection
- [ ] 2-3 hours available

## 🚀 Fast Track Setup

### Step 1: Install Everything (30-45 minutes)

1. **Git** → https://git-scm.com/download/win
2. **Python** → https://www.python.org/downloads/ (Check "Add to PATH"!)
3. **Node.js** → https://nodejs.org/ (Download LTS version)
4. **PostgreSQL** → https://www.postgresql.org/download/windows/

**Verify each installation:**
```powershell
git --version
python --version
node --version
psql --version
```

### Step 2: Get the Code (5 minutes)

```powershell
# Navigate to where you want the project
cd D:\Downloads\Programming

# Download the project
git clone https://github.com/yap1co/projectsigma.git

# Go into the project folder
cd projectsigma
```

### Step 3: Set Up Python (10 minutes)

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
cd server
pip install -r requirements.txt
```

### Step 4: Set Up Frontend (10 minutes)

```powershell
# Open new PowerShell window
cd D:\Downloads\Programming\projectsigma\client

# Install dependencies
npm install
```

### Step 5: Set Up Database (15 minutes)

```powershell
# Make sure PostgreSQL service is running
Get-Service postgresql*
Start-Service postgresql-x64-15  # If needed

# Configure environment
cd D:\Downloads\Programming\projectsigma\server\database
# Edit setup_local_env.ps1 - change password!
. .\setup_local_env.ps1

# Initialize database (automated - creates all tables, imports HESA data)
python setup_database.py
```

### Step 6: Configure Environment (5 minutes)

Create `server/.env` file:
```env
POSTGRES_DB=university_recommender
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### Step 7: Run the App (2 minutes)

**Terminal 1 (Backend):**
```powershell
cd D:\Downloads\Programming\projectsigma
.\venv\Scripts\Activate.ps1
cd server
python app.py
```

**Terminal 2 (Frontend):**
```powershell
cd D:\Downloads\Programming\projectsigma\client
npm run dev
```

**Open Browser:** http://localhost:3000

## ✅ Success!

If you see the website, you're done! 🎉

## 📚 Need More Help?

See `COMPLETE_BEGINNER_SETUP_GUIDE.md` for detailed instructions.

## 🆘 Stuck?

1. Check error messages carefully
2. Verify each step completed successfully
3. Restart PowerShell/computer if needed
4. See troubleshooting section in full guide

