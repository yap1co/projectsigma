# Complete Beginner Setup Guide - From Scratch

**Welcome!** This guide will walk you through setting up the University Course Recommender project from scratch, even if you've never used these tools before. Follow each step carefully.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Install Required Software](#step-1-install-required-software)
3. [Step 2: Clone the Project](#step-2-clone-the-project)
4. [Step 3: Set Up Python Backend](#step-3-set-up-python-backend)
5. [Step 4: Set Up Node.js Frontend](#step-4-set-up-nodejs-frontend)
6. [Step 5: Set Up PostgreSQL Database](#step-5-set-up-postgresql-database)
7. [Step 6: Configure Environment Variables](#step-6-configure-environment-variables)
8. [Step 7: Initialize Database Schema](#step-7-initialize-database-schema)
9. [Step 8: Run Database Migrations](#step-8-run-database-migrations)
10. [Step 9: Start the Application](#step-9-start-the-application)
11. [Step 10: Verify Everything Works](#step-10-verify-everything-works)
12. [Troubleshooting](#troubleshooting)
13. [Next Steps](#next-steps)

---

## Prerequisites

Before starting, ensure you have:

- ✅ **Windows 10/11** (or macOS/Linux - see platform-specific guides)
- ✅ **Administrator access** (for installing software)
- ✅ **Internet connection**
- ✅ **2-3 hours** for initial setup
- ✅ **Basic computer skills** (opening files, typing commands)

---

## Step 1: Install Required Software

Install these tools in order:

### 1.1 Install Git

**What it does:** Git lets you download code from GitHub.

1. **Download Git:**
   - Go to: https://git-scm.com/download/win
   - Click "Download for Windows"
   - File: `Git-2.xx.x-64-bit.exe`

2. **Install Git:**
   - Double-click the downloaded file
   - Click "Next" through all screens
   - **Important:** Choose "Git from the command line and also from 3rd-party software"
   - Click "Install"
   - Wait for completion

3. **Verify Installation:**
   ```powershell
   git --version
   ```
   Expected: `git version 2.xx.x`

**Troubleshooting:**
- If "command not found": Restart computer and try again
- Make sure you selected "Git from the command line" during installation

### 1.2 Install Python 3.11+

**What it does:** Python runs the backend server code.

1. **Download Python:**
   - Go to: https://www.python.org/downloads/
   - Click "Download Python 3.11.x" (or latest 3.11+)
   - File: `python-3.11.x-amd64.exe`

2. **Install Python:**
   - Double-click the downloaded file
   - ⚠️ **CRITICAL:** Check "Add Python to PATH" at the bottom!
   - Click "Install Now"
   - Wait for completion
   - Click "Close"

3. **Verify Installation:**
   ```powershell
   python --version
   ```
   Expected: `Python 3.11.x`

**Troubleshooting:**
- If "command not found": You didn't check "Add Python to PATH"
  - Solution: Reinstall Python and check that box
- Or manually add Python to PATH (advanced)

### 1.3 Install Node.js 18+

**What it does:** Node.js runs the frontend (website) code.

1. **Download Node.js:**
   - Go to: https://nodejs.org/
   - Click the green "LTS" button (Long Term Support)
   - File: `node-v20.x.x-x64.msi`

2. **Install Node.js:**
   - Double-click the downloaded file
   - Click "Next" through all screens (defaults are fine)
   - Click "Install"
   - Wait for completion
   - Click "Finish"

3. **Verify Installation:**
   ```powershell
   node --version
   npm --version
   ```
   Expected: `v20.x.x` and `10.x.x`

**Troubleshooting:**
- If commands don't work: Restart your computer

### 1.4 Install PostgreSQL 15+

**What it does:** PostgreSQL stores all the data (courses, students, etc.).

1. **Download PostgreSQL:**
   - Go to: https://www.postgresql.org/download/windows/
   - Click "Download the installer"
   - Download PostgreSQL 15.x (or latest)

2. **Install PostgreSQL:**
   - Run the installer
   - Use default settings
   - **Remember your password!** (you'll need it later)
   - Default port `5432` is fine
   - Complete the installation

3. **Verify Installation:**
   ```powershell
   psql --version
   ```
   Expected: `psql (PostgreSQL) 15.x`

**Note:** If `psql` command doesn't work:
- Add `C:\Program Files\PostgreSQL\15\bin` to System PATH
- Restart PowerShell

4. **Start PostgreSQL Service:**
   ```powershell
   # Check if running
   Get-Service postgresql*
   
   # If stopped, start it (replace 15 with your version)
   Start-Service postgresql-x64-15
   
   # Set to start automatically
   Set-Service postgresql-x64-15 -StartupType Automatic
   ```

### 1.5 Install Visual Studio Code (Optional but Recommended)

**What it does:** Code editor for viewing and editing code.

1. **Download VS Code:**
   - Go to: https://code.visualstudio.com/
   - Click "Download for Windows"
   - Install with default settings

2. **Install Useful Extensions:**
   - Open VS Code
   - Click Extensions icon (left sidebar)
   - Search and install:
     - **Python** (by Microsoft)
     - **GitLens** (Git history viewer)
     - **Prettier** (code formatter)

---

## Step 2: Clone the Project

Download the project code to your computer.

### 2.1 Find the Project Repository

1. **Go to GitHub:**
   - Open your web browser
   - Go to: https://github.com/yap1co/projectsigma
   - (Or your project repository URL)

2. **Copy the Repository URL:**
   - Click the green "Code" button
   - Click the copy icon next to the HTTPS URL
   - URL: `https://github.com/yap1co/projectsigma.git`

### 2.2 Clone (Download) the Project

1. **Open PowerShell:**
   - Press `Win + X`
   - Click "Windows PowerShell" or "Terminal"

2. **Navigate to Where You Want the Project:**
   ```powershell
   # Example: Navigate to Downloads folder
   cd D:\Downloads\Programming
   
   # Or create a new folder for projects
   cd C:\Users\YourName\Documents
   mkdir Projects
   cd Projects
   ```

3. **Clone the Repository:**
   ```powershell
   git clone https://github.com/yap1co/projectsigma.git
   ```
   
   **What happens:**
   - Git downloads all project files
   - Creates a folder called `projectsigma`
   - This may take a few minutes

4. **Navigate into the Project Folder:**
   ```powershell
   cd projectsigma
   ```

5. **Verify Files Are There:**
   ```powershell
   ls
   ```
   
   You should see:
   - `server/` - Backend code
   - `client/` - Frontend code
   - `docs/` - Documentation
   - `README.md` - Project documentation

**Troubleshooting:**
- **"git: command not found"**: Git isn't installed or PATH isn't set. Reinstall Git.
- **"Permission denied"**: Make sure you have write access to the folder
- **"Repository not found"**: Check the URL is correct

---

## Step 3: Set Up Python Backend

Python projects use "virtual environments" to keep dependencies separate.

### 3.1 Create a Virtual Environment

1. **Navigate to Project Root:**
   ```powershell
   cd D:\Downloads\Programming\projectSigma\projectsigma
   ```
   (Replace with your actual path)

2. **Create Virtual Environment:**
   ```powershell
   python -m venv venv
   ```
   
   **What this does:** Creates a folder called `venv` with a clean Python environment

3. **Activate the Virtual Environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   **What you'll see:** Your prompt changes to show `(venv)` at the beginning
   
   **If you get an error about execution policy:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
   Then try activating again.

### 3.2 Install Python Dependencies

1. **Navigate to Server Folder:**
   ```powershell
   cd server
   ```

2. **Install Required Packages:**
   ```powershell
   pip install -r requirements.txt
   ```
   
   **What this does:** Downloads and installs all Python libraries the project needs
   - This may take 5-10 minutes
   - You'll see lots of text scrolling by

3. **Verify Installation:**
   ```powershell
   pip list
   ```
   
   You should see packages like:
   - `flask`
   - `psycopg2-binary`
   - `pandas`
   - `flask-jwt-extended`
   - etc.

**Troubleshooting:**
- **"pip: command not found"**: Make sure virtual environment is activated
- **"Permission denied"**: Make sure you activated the venv
- **Slow download**: This is normal, be patient

---

## Step 4: Set Up Node.js Frontend

Now let's set up the website frontend.

### 4.1 Install Frontend Dependencies

1. **Navigate to Client Folder:**
   ```powershell
   # From project root
   cd client
   ```

2. **Install Node Packages:**
   ```powershell
   npm install
   ```
   
   **What this does:** Downloads all JavaScript libraries needed for the frontend
   - This may take 5-10 minutes
   - Creates a `node_modules` folder (this is normal and large)

3. **Verify Installation:**
   ```powershell
   npm list --depth=0
   ```
   
   You should see packages listed

**Troubleshooting:**
- **"npm: command not found"**: Node.js isn't installed or PATH isn't set
- **Errors during install**: Try deleting `node_modules` folder and `package-lock.json`, then run `npm install` again

---

## Step 5: Set Up PostgreSQL Database

The database stores all your data. Let's set it up.

### 5.1 Start PostgreSQL Service

1. **Check if PostgreSQL is Running:**
   ```powershell
   Get-Service postgresql*
   ```
   
   **If it says "Stopped":**
   ```powershell
   Start-Service postgresql-x64-15
   ```
   (Adjust version number if different)

2. **Verify Connection:**
   ```powershell
   psql -U postgres -c "SELECT version();"
   ```
   
   Enter your PostgreSQL password when prompted.

### 5.2 Create Database

**Option A: Using the Script (Recommended)**

```powershell
# Navigate to database folder
cd D:\Downloads\Programming\projectSigma\projectsigma\server\database

# Run setup script (automated - creates database + imports HESA data)
python setup_database.py
```

**What this does:**
- Creates the `university_recommender` database
- Creates all tables
- Sets up the schema

**Option B: Manual Creation**

```powershell
# Connect to PostgreSQL
psql -U postgres

# Inside psql, type:
CREATE DATABASE university_recommender;

# Exit psql
\q
```

**Troubleshooting:**
- **"Connection refused"**: PostgreSQL service isn't running
- **"Password authentication failed"**: Wrong password
- **"Database already exists"**: That's fine, script will skip creation

📚 **For detailed PostgreSQL setup:** See [docs/database/QUICK_START_LOCAL.md](../database/QUICK_START_LOCAL.md)

---

## Step 6: Configure Environment Variables

The application needs to know how to connect to the database.

### 6.1 Create Environment File

1. **Navigate to Server Folder:**
   ```powershell
   cd D:\Downloads\Programming\projectSigma\projectsigma\server
   ```

2. **Create `.env` File:**
   - Create a new file named `.env` (just `.env`, no extension)
   - Add these lines:
   ```env
   POSTGRES_DB=university_recommender
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_postgres_password_here
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   DATABASE_URL=postgresql://postgres:your_postgres_password_here@localhost:5432/university_recommender
   JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
   FLASK_ENV=development
   ```
   
   **Important:** Replace `your_postgres_password_here` with your actual PostgreSQL password!

3. **Save the File**

**Note:** The `.env` file is in `.gitignore`, so it won't be uploaded to GitHub (this is good for security).

### 6.2 Create Frontend Environment File

1. **Navigate to Client Folder:**
   ```powershell
   cd D:\Downloads\Programming\projectSigma\projectsigma\client
   ```

2. **Create `.env.local` File:**
   - Create a new file named `.env.local`
   - Add this line:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:5000
   ```

3. **Save the File**

---

## Step 7: Initialize Database Schema

Now let's create all the database tables.

### 7.1 Run Database Initialization

1. **Make Sure Environment is Set:**
   ```powershell
   # From server/database folder
   cd D:\Downloads\Programming\projectSigma\projectsigma\server\database
   ```

2. **Run Setup Script:**
   ```powershell
   python setup_database.py
   ```

**What you'll see:**
```
============================================================
PostgreSQL Database Initialization
============================================================
✓ Database 'university_recommender' already exists
  → Running migration: 001_initial_schema.sql
  ✓ Migration 001_initial_schema applied successfully
  → Running migration: 002_discover_uni_data_schema.sql
  ✓ Migration 002_discover_uni_data_schema applied successfully
  → Running migration: 003_add_hesa_links.sql
  ✓ Migration 003_add_hesa_links applied successfully
  → Running migration: 004_recommendation_feedback.sql
  ✓ Migration 004_recommendation_feedback applied successfully
  → Running migration: 005_career_interests.sql
  ✓ Migration 005_career_interests applied successfully
✓ All migrations completed successfully
```

### 7.2 Verify Tables Were Created

```powershell
# Connect to database
psql -U postgres -d university_recommender

# List tables
\dt

# You should see tables like:
# - student
# - university
# - course
# - subject
# - course_requirement
# - career_interest
# - career_interest_keyword
# - recommendation_feedback
# etc.

# Exit
\q
```

**Troubleshooting:**
- **"Migration already applied"**: That's fine, means it's already done
- **"Table already exists"**: Tables are already created, that's okay

📚 **For detailed database setup:** See [docs/database/MIGRATIONS_STEP_BY_STEP.md](../database/MIGRATIONS_STEP_BY_STEP.md)

---

## Step 8: Run Database Migrations

Additional migrations may be needed for specific features.

### 8.1 Run Career Interests Migration

```powershell
# From server/database folder
cd D:\Downloads\Programming\projectSigma\projectsigma\server\database
python run_career_interests_migration.py
```

**What this does:**
- Creates `career_interest`, `career_interest_keyword`, `career_interest_conflict` tables
- Populates with default career interests data

### 8.2 Run Feedback Migration

```powershell
python run_feedback_migration.py
```

**What this does:**
- Creates `recommendation_feedback` and `recommendation_settings` tables
- Sets up feedback system

**Note:** These migrations are usually run automatically by `setup_database.py`, but you can run them manually if needed.

---

## Step 9: Start the Application

Now let's start the application!

### 9.1 Start the Backend Server

1. **Open First PowerShell Window:**
   ```powershell
   # Navigate to project
   cd D:\Downloads\Programming\projectSigma\projectsigma
   
   # Activate virtual environment
   .\venv\Scripts\Activate.ps1
   
   # Navigate to server
   cd server
   
   # Start Flask server
   python app.py
   ```

2. **What You'll See:**
   ```
   * Running on http://127.0.0.1:5000
   * Debug mode: on
   ```

3. **Keep This Window Open!** The server needs to keep running.

### 9.2 Start the Frontend Server

1. **Open Second PowerShell Window:**
   ```powershell
   # Navigate to project
   cd D:\Downloads\Programming\projectSigma\projectsigma
   
   # Navigate to client
   cd client
   
   # Start Next.js development server
   npm run dev
   ```

2. **What You'll See:**
   ```
   ▲ Next.js 14.x.x
   - Local:        http://localhost:3000
   - Ready in 2.3s
   ```

3. **Keep This Window Open Too!**

### 9.3 Access the Application

1. **Open Your Web Browser**
2. **Go to:** http://localhost:3000
3. **You should see the application!** 🎉

**What's Running:**
- **Backend:** http://localhost:5000 (API server)
- **Frontend:** http://localhost:3000 (Website)

### 9.4 Stop the Application

When you're done:
1. Go to each PowerShell window
2. Press `Ctrl + C` to stop each server
3. Close the windows

---

## Step 10: Verify Everything Works

Let's test that everything is working correctly.

### 10.1 Test Backend API

1. **Open a new PowerShell window:**
   ```powershell
   # Test health endpoint
   curl http://localhost:5000/api/health
   ```

   Expected response:
   ```json
   {
     "status": "OK",
     "timestamp": "2024-01-01T00:00:00",
     "environment": "development"
   }
   ```

2. **Test root endpoint:**
   ```powershell
   curl http://localhost:5000/
   ```

### 10.2 Test Frontend

1. **Open browser:** http://localhost:3000
2. **You should see the application homepage**
3. **Try creating an account:**
   - Click "Register" or "Sign Up"
   - Fill in the form
   - Submit

### 10.3 Test Database Connection

```powershell
# Connect to database
psql -U postgres -d university_recommender

# Check career interests are loaded
SELECT COUNT(*) FROM career_interest;
SELECT COUNT(*) FROM career_interest_keyword;

# Check feedback tables
SELECT COUNT(*) FROM recommendation_feedback;
SELECT COUNT(*) FROM recommendation_settings;

# Exit
\q
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: "Command not found" errors

**Solution:**
- Make sure you installed the software
- Restart PowerShell/computer
- Check PATH environment variable

#### Issue: Python virtual environment won't activate

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Issue: PostgreSQL connection errors

**Solutions:**
1. Check service is running: `Get-Service postgresql*`
2. Verify password in `.env` file
3. Check PostgreSQL is listening on port 5432: `netstat -an | findstr :5432`

#### Issue: Port already in use

**Solution:**
- Another program is using port 5000 or 3000
- Close other applications
- Or change ports in configuration files

#### Issue: npm install fails

**Solution:**
```powershell
# Delete and reinstall
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

#### Issue: Database migration errors

**Solution:**
- Check PostgreSQL is running
- Verify password is correct
- Check database exists: `psql -U postgres -l`

#### Issue: Module not found errors

**Solution:**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Getting Help

1. **Check Documentation:**
   - [docs/README.md](../README.md) - Complete documentation index
   - [docs/troubleshooting/](../troubleshooting/) - Troubleshooting guides
   - [docs/modules/](../modules/) - Module documentation

2. **Check Error Messages:**
   - Read the full error message
   - Google the error message
   - Check GitHub Issues

3. **Ask for Help:**
   - Include the full error message
   - Say what step you're on
   - Include what you've already tried

---

## Next Steps

Once everything is running:

### 1. Explore the Application
- Try creating an account
- Browse courses
- Test the recommendation system
- Give feedback on recommendations

### 2. Import Data (Optional)
- See [docs/guides/hesa_data.md](../guides/hesa_data.md) for importing HESA data
- Or use pgAdmin to import data manually

### 3. Learn More
- Read the code in `server/` and `client/` folders
- Check out the API endpoints
- Explore the database schema
- Read module documentation: [docs/modules/](../modules/)

### 4. Development Workflow
- Make changes to code
- Test locally
- Commit changes: `git add .` then `git commit -m "Description"`
- Push to GitHub: `git push` (when ready)

---

## Quick Reference Commands

### Daily Startup

```powershell
# Terminal 1: Backend
cd D:\Downloads\Programming\projectSigma\projectsigma
.\venv\Scripts\Activate.ps1
cd server
python app.py

# Terminal 2: Frontend
cd D:\Downloads\Programming\projectSigma\projectsigma\client
npm run dev
```

### Database Commands

```powershell
# Connect to database
psql -U postgres -d university_recommender

# List tables
\dt

# Run database setup
cd server\database
python setup_database.py
```

### Git Commands (For Later)

```powershell
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push
```

---

## Checklist

Use this to track your progress:

- [ ] Git installed and verified
- [ ] Python installed and verified
- [ ] Node.js installed and verified
- [ ] PostgreSQL installed and verified
- [ ] PostgreSQL service running
- [ ] Project cloned from GitHub
- [ ] Python virtual environment created and activated
- [ ] Python dependencies installed
- [ ] Node.js dependencies installed
- [ ] Database created
- [ ] Environment variables configured (`.env` file)
- [ ] Database schema initialized
- [ ] Career interests migration run
- [ ] Feedback migration run
- [ ] Backend server running
- [ ] Frontend server running
- [ ] Application accessible in browser
- [ ] Health check endpoint working
- [ ] Can create account and login

---

## Congratulations! 🎉

You've successfully set up the University Course Recommender! You now have:

- ✅ A working development environment
- ✅ Database set up and running
- ✅ Backend API server
- ✅ Frontend web application
- ✅ Understanding of how everything connects

**Remember:**
- Keep both servers running while developing
- Use `Ctrl + C` to stop servers
- Always activate virtual environment before running Python code
- Check `.env` file if connection issues occur

**Next:**
- Read [Module Documentation](../modules/) to understand the code
- Explore [User Guides](../guides/) for system features
- Check [Troubleshooting](../troubleshooting/) if you encounter issues

**Happy coding!** 🚀
