# Quick Start: Apply Discover Uni DDL

## 🚀 Quick Setup

```bash
# 1. Ensure PostgreSQL is installed and running
# See LOCAL_POSTGRES_SETUP.md for installation

# 2. Configure environment variables in server/.env
# POSTGRES_DB=university_recommender
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=your_password
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432

# 3. Run migrations
cd server/database
python init_db.py
```

**Done!** ✅

---

## 📋 What Happens

1. ✅ Creates database `university_recommender` (if needed)
2. ✅ Runs `001_initial_schema.sql` (core tables)
3. ✅ Runs `002_discover_uni_data_schema.sql` (Discover Uni tables)
4. ✅ Creates 27+ tables for Discover Uni data
5. ✅ Sets up all foreign keys and indexes

---

## 🔍 Verify It Worked

```bash
# Check tables were created
psql -U postgres -d university_recommender -c "\dt"

# Should see tables like:
# - institution
# - kiscourse
# - accreditation
# - nss
# - leo3
# - etc.
```

---

## ⚠️ Troubleshooting

**"Connection refused"**
→ Check PostgreSQL service is running: `Get-Service postgresql*` (Windows)

**"Migration already applied"**
→ Normal! It won't run twice.

**"Permission denied"**
→ Run PowerShell as Administrator (Windows) or check PostgreSQL user permissions

---

## 📚 Full Guide

See [MIGRATIONS_STEP_BY_STEP.md](./MIGRATIONS_STEP_BY_STEP.md) for detailed instructions.

