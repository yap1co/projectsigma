# Complete Beginner Setup Guide - Project Sigma

**Welcome!** This guide will walk you through setting up Project Sigma from scratch, even if you've never used GitHub before. Follow each step carefully.

## 📋 Table of Contents

1. [What You'll Need](#what-youll-need)
2. [Understanding GitHub Basics](#understanding-github-basics)
3. [Step 1: Install Prerequisites](#step-1-install-prerequisites)
4. [Step 2: Get the Project from GitHub](#step-2-get-the-project-from-github)
5. [Step 3: Set Up Python Environment](#step-3-set-up-python-environment)
6. [Step 4: Set Up Node.js and Frontend](#step-4-set-up-nodejs-and-frontend)
7. [Step 5: Set Up PostgreSQL Database](#step-5-set-up-postgresql-database)
8. [Step 6: Configure Environment Variables](#step-6-configure-environment-variables)
9. [Step 7: Initialize Database Schema](#step-7-initialize-database-schema)
10. [Step 8: Run the Application](#step-8-run-the-application)
11. [Troubleshooting](#troubleshooting)
12. [Next Steps](#next-steps)

---

## What You'll Need

Before starting, make sure you have:

- ✅ A computer running **Windows 10/11** (this guide is for Windows)
- ✅ Administrator access (for installing software)
- ✅ Internet connection
- ✅ About 2-3 hours for initial setup
- ✅ Basic computer skills (opening files, typing commands)

---

## Understanding GitHub Basics

### What is GitHub?

**GitHub** is a website where developers store their code. Think of it like Google Drive, but specifically for code projects.

- **Repository (Repo)**: A project folder stored on GitHub
- **Clone**: Downloading a repository to your computer
- **Commit**: Saving changes to the code
- **Push**: Uploading your changes to GitHub
- **Pull**: Downloading the latest changes from GitHub

### Why We Use GitHub

- ✅ Keep track of code changes
- ✅ Work with others on the same project
- ✅ Access your code from any computer
- ✅ Backup your work

**Don't worry!** For this setup, you only need to **download** the code. You don't need to upload anything yet.

---

## Step 1: Install Prerequisites

You need to install several tools. Install them in this order:

### 1.1 Install Git (Version Control)

**What it does:** Git lets you download code from GitHub.

1. **Download Git:**
   - Go to: https://git-scm.com/download/win
   - Click "Download for Windows"
   - File will be named something like: `Git-2.xx.x-64-bit.exe`

2. **Install Git:**
   - Double-click the downloaded file
   - Click "Next" through all screens (default options are fine)
   - **Important:** Choose "Git from the command line and also from 3rd-party software"
   - Click "Install"
   - Wait for installation to complete

3. **Verify Installation:**
   - Open **PowerShell** (Press `Win + X`, then click "Windows PowerShell" or "Terminal")
   - Type: `git --version`
   - You should see: `git version 2.xx.x`
   - ✅ If you see a version number, Git is installed!

**Troubleshooting:**
- If you see "command not found", restart your computer and try again
- Make sure you selected "Git from the command line" during installation

### 1.2 Install Python

**What it does:** Python runs the backend server code.

1. **Download Python:**
   - Go to: https://www.python.org/downloads/
   - Click the big yellow "Download Python 3.xx" button
   - File will be named something like: `python-3.11.x-amd64.exe`

2. **Install Python:**
   - Double-click the downloaded file
   - ⚠️ **IMPORTANT:** Check the box "Add Python to PATH" at the bottom!
   - Click "Install Now"
   - Wait for installation to complete
   - Click "Close"

3. **Verify Installation:**
   - Open a **new** PowerShell window (close and reopen)
   - Type: `python --version`
   - You should see: `Python 3.11.x` (or similar)
   - ✅ If you see a version number, Python is installed!

**Troubleshooting:**
- If you see "command not found", you didn't check "Add Python to PATH"
  - Solution: Reinstall Python and make sure to check that box
- Or manually add Python to PATH (advanced)

### 1.3 Install Node.js

**What it does:** Node.js runs the frontend (website) code.

1. **Download Node.js:**
   - Go to: https://nodejs.org/
   - Click the green "LTS" button (Long Term Support version)
   - File will be named something like: `node-v20.x.x-x64.msi`

2. **Install Node.js:**
   - Double-click the downloaded file
   - Click "Next" through all screens (default options are fine)
   - Click "Install"
   - Wait for installation to complete
   - Click "Finish"

3. **Verify Installation:**
   - Open a **new** PowerShell window
   - Type: `node --version`
   - You should see: `v20.x.x` (or similar)
   - Type: `npm --version`
   - You should see: `10.x.x` (or similar)
   - ✅ If you see version numbers, Node.js is installed!

**Troubleshooting:**
- If commands don't work, restart your computer

### 1.4 Install PostgreSQL

**What it does:** PostgreSQL stores all the data (courses, students, etc.).

📚 **Detailed instructions:** See `server/database/LOCAL_POSTGRES_SETUP.md`

**Quick Steps:**

1. **Download PostgreSQL:**
   - Go to: https://www.postgresql.org/download/windows/
   - Click "Download the installer"
   - Download PostgreSQL 15.x

2. **Install PostgreSQL:**
   - Run the installer
   - Use default settings
   - **Remember your password!** (you'll need it later)
   - Default port `5432` is fine
   - Complete the installation

3. **Verify Installation:**
   - Open PowerShell
   - Type: `psql --version`
   - You should see: `psql (PostgreSQL) 15.x`
   - ✅ If you see a version, PostgreSQL is installed!

**Note:** If `psql` command doesn't work, add PostgreSQL to PATH:
- Add `C:\Program Files\PostgreSQL\15\bin` to System PATH
- Restart PowerShell

### 1.5 Install a Code Editor (Optional but Recommended)

**Visual Studio Code** is free and beginner-friendly:

1. **Download VS Code:**
   - Go to: https://code.visualstudio.com/
   - Click "Download for Windows"
   - Install with default settings

2. **Install Useful Extensions:**
   - Open VS Code
   - Click the Extensions icon (left sidebar)
   - Search and install:
     - **Python** (by Microsoft)
     - **GitLens** (Git history viewer)
     - **Prettier** (code formatter)

---

## Step 2: Get the Project from GitHub

Now let's download the project code to your computer.

### 2.1 Find the Project Repository

1. **Go to GitHub:**
   - Open your web browser
   - Go to: https://github.com/yap1co/projectsigma
   - (Or wherever your project is hosted)

2. **Copy the Repository URL:**
   - Click the green "Code" button
   - Click the copy icon next to the HTTPS URL
   - URL looks like: `https://github.com/yap1co/projectsigma.git`

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
   - Git downloads all the project files
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
   
   You should see folders like:
   - `server/` - Backend code
   - `client/` - Frontend code
   - `data/` - Data files
   - `README.md` - Project documentation

**Troubleshooting:**
- **"git: command not found"**: Git isn't installed or PATH isn't set. Reinstall Git.
- **"Permission denied"**: Make sure you have write access to the folder
- **"Repository not found"**: Check the URL is correct

---

## Step 3: Set Up Python Environment

Python projects use "virtual environments" to keep dependencies separate.

### 3.1 Create a Virtual Environment

1. **Navigate to Project Root:**
   ```powershell
   cd D:\Downloads\Programming\projectSigma\projectsigma
   ```

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
   - etc.

**Troubleshooting:**
- **"pip: command not found"**: Make sure virtual environment is activated
- **"Permission denied"**: Make sure you activated the venv
- **Slow download**: This is normal, be patient

---

## Step 4: Set Up Node.js and Frontend

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

### 5.2 Configure Environment Variables

1. **Navigate to Database Folder:**
   ```powershell
   cd D:\Downloads\Programming\projectSigma\projectsigma\server\database
   ```

2. **Edit Setup Script:**
   - Open `setup_local_env.ps1` in a text editor (Notepad or VS Code)
   - Find this line: `$env:POSTGRES_PASSWORD = "postgres123"`
   - Change `postgres123` to **your actual PostgreSQL password**
   - Save the file

3. **Run Setup Script:**
   ```powershell
   . .\setup_local_env.ps1
   ```
   
   **What you'll see:** Environment variables are set and connection is tested

### 5.3 Create Database

**Option A: Using the Script (Recommended)**

```powershell
# Make sure you're in server/database folder
python init_db.py
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
- **"Password authentication failed"**: Wrong password in setup script
- **"Database already exists"**: That's fine, script will skip creation

📚 **For detailed PostgreSQL setup:** See `server/database/LOCAL_POSTGRES_SETUP.md`

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

---

## Step 7: Initialize Database Schema

Now let's create all the database tables.

### 7.1 Run Database Initialization

1. **Make Sure Environment is Set:**
   ```powershell
   # From server/database folder
   . .\setup_local_env.ps1
   ```

2. **Run Initialization:**
   ```powershell
   python init_db.py
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
✓ All migrations completed successfully
```

### 7.2 Verify Tables Were Created

```powershell
# Connect to database
psql -U postgres -d university_recommender

# List tables
\dt

# You should see tables like:
# - institution
# - kiscourse
# - student
# - etc.

# Exit
\q
```

**Troubleshooting:**
- **"Migration already applied"**: That's fine, means it's already done
- **"Table already exists"**: Tables are already created, that's okay

📚 **For detailed database setup:** See `server/database/migrations/STEP_BY_STEP_GUIDE.md`

---

## Step 8: Run the Application

Now let's start the application!

### 8.1 Start the Backend Server

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

### 8.2 Start the Frontend Server

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

### 8.3 Access the Application

1. **Open Your Web Browser**
2. **Go to:** http://localhost:3000
3. **You should see the application!** 🎉

**What's Running:**
- **Backend:** http://localhost:5000 (API server)
- **Frontend:** http://localhost:3000 (Website)

### 8.4 Stop the Application

When you're done:
1. Go to each PowerShell window
2. Press `Ctrl + C` to stop each server
3. Close the windows

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
3. Check PostgreSQL is listening on port 5432

#### Issue: Port already in use

**Solution:**
- Another program is using port 5000 or 3000
- Close other applications
- Or change ports in configuration files

#### Issue: npm install fails

**Solution:**
```powershell
# Delete and reinstall
rm -r node_modules
rm package-lock.json
npm install
```

#### Issue: Database migration errors

**Solution:**
- Check PostgreSQL is running
- Verify password is correct
- Check database exists: `psql -U postgres -l`

### Getting Help

1. **Check Documentation:**
   - `README.md` - Project overview
   - `SETUP_INSTRUCTIONS.md` - Setup details
   - `server/database/LOCAL_POSTGRES_SETUP.md` - Database setup

2. **Check Error Messages:**
   - Read the full error message
   - Google the error message
   - Check GitHub Issues (if project has them)

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

### 2. Import Data (Optional)
- See `server/database/import_csv.py` for importing CSV data
- Or use pgAdmin to import data manually

### 3. Learn More
- Read the code in `server/` and `client/` folders
- Check out the API endpoints
- Explore the database schema

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

# Run migrations
cd server\database
python init_db.py
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
- [ ] Project cloned from GitHub
- [ ] Python virtual environment created and activated
- [ ] Python dependencies installed
- [ ] Node.js dependencies installed
- [ ] PostgreSQL service running
- [ ] Database created
- [ ] Environment variables configured
- [ ] Database schema initialized
- [ ] Backend server running
- [ ] Frontend server running
- [ ] Application accessible in browser

---

## Congratulations! 🎉

You've successfully set up Project Sigma! You now have:
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

**Happy coding!** 🚀

