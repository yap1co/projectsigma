# PostgreSQL Migration Summary

## Overview

This document summarizes the migration from MongoDB to PostgreSQL and the addition of comprehensive database design documentation to the High-Level Design document.

## Changes Made

### 1. High-Level Design Document Updates (`High_Level_Design_Draft.md`)

#### Section 4.1 - Database Schema (Updated)
- **Updated schema to match ER diagrams**:
  - Changed from `id SERIAL` to `VARCHAR(50)` primary keys (matching ER diagram conventions)
  - Renamed tables to match ER diagrams:
    - `students` → `student`
    - `student_predicted_grades` → `student_grade` (with composite PK)
    - `universities` → `university`
    - `courses` → `course`
    - `course_entry_requirements` → `course_requirement`
    - `recommendations` → `recommendation_run` and `recommendation_result`
  - Added new tables:
    - `subject` (separate entity for subjects)
    - `entrance_exam` (entrance exam catalog)
    - `course_required_exam` (junction table for many-to-many relationship)
  - Updated field names to match ER diagrams:
    - `student_id`, `university_id`, `course_id` (instead of `id`)
    - `display_name`, `password_hash`, `region`, `tuition_budget`, `preferred_exams`
    - `rank_overall`, `employability_score`, `website_url`
    - `ucas_code`, `annual_fee`, `typical_offer_tariff`
  - Changed `recommendation_result.items` to JSONB array format

#### Section 4.3 - Key Constraints (Data Integrity) - NEW
- **Primary Key Constraints**: Composite PKs for `student_grade` and `course_required_exam`
- **Foreign Key Constraints**: All FKs with ON DELETE rules (CASCADE/RESTRICT)
- **Check Constraints**: Data validation (employability scores, fees, JSONB array type)

#### Section 4.4 - Index Strategy (Performance) - NEW
- **Join/Filter Indexes (BTREE)**: Indexes on foreign keys and common filter columns
- **UI Filter Indexes**: Region, ranking, budget, UCAS code, case-insensitive name searches
- **Array/JSONB Indexes (GIN)**: For `preferred_exams` array and `items` JSONB column

#### Section 4.5 - Example Queries - NEW
- Budget + Region + Rank Order Query
- Filter by Required Exams Subset (using array containment)
- Explode Recommendation Result Items (JSONB array expansion)

#### Section 6 - Recommendation Algorithm Design (Completely Rewritten)
- **6.2.1 Purpose**: Fast, explainable, relational matching pipeline
- **6.2.2 Inputs & Normalization**: 
  - UCAS tariff mapping (A*→56, A→48, etc.)
  - Score normalization functions (grade match, subject match, rank score, etc.)
  - Penalty rules for missing requirements
- **6.2.3 Candidate Pre-Filter (SQL)**: Complex SQL query with CTEs for pre-filtering
- **6.2.4 Pseudocode**: Detailed scoring algorithm with Top-K heap selection
- **6.2.5 Persistence & Traceability**: JSONB storage for auditability
- **6.2.6 Worked Example**: Complete calculation walkthrough

### 2. Database Migration Files Created

#### `server/database/migrations/001_initial_schema.sql`
Complete PostgreSQL schema including:
- All 10 tables (student, subject, student_grade, university, course, course_requirement, entrance_exam, course_required_exam, recommendation_run, recommendation_result)
- All foreign key constraints with ON DELETE rules
- All check constraints
- All indexes (BTREE and GIN)

#### `server/database/init_db.py`
Python script for database initialization:
- Creates database if it doesn't exist
- Runs migrations in order
- Tracks applied migrations in `schema_migrations` table
- Error handling and rollback support

#### `server/database/README.md`
Complete documentation for:
- Database setup instructions
- Environment variables
- Migration process
- Schema overview
- Troubleshooting guide

### 3. Docker Configuration Updates

#### `docker-compose.yml`
- **Replaced MongoDB with PostgreSQL**:
  - PostgreSQL 15 Alpine image
  - Health checks for service dependencies
  - Volume mounting for migrations
- **Replaced Mongo Express with pgAdmin**:
  - Web-based PostgreSQL administration
  - Accessible at http://localhost:8081
- **Updated Backend Environment Variables**:
  - `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
  - `POSTGRES_HOST`, `POSTGRES_PORT`
  - `DATABASE_URL` connection string
- **Service Dependencies**:
  - Backend waits for PostgreSQL health check
  - Proper service startup order

## Key Features

### Database Design Highlights

1. **Normalized Schema**: Follows ER diagram structure with proper relationships
2. **Data Integrity**: Comprehensive constraints ensure data quality
3. **Performance**: Strategic indexes for common query patterns
4. **Auditability**: JSONB storage for recommendation runs and results
5. **Scalability**: Efficient indexes support large datasets

### Algorithm Design Highlights

1. **SQL Pre-Filtering**: Reduces candidate set before scoring
2. **Weighted Scoring**: Transparent, explainable algorithm
3. **Top-K Selection**: Efficient heap-based selection (O(N log K))
4. **Traceability**: Complete audit trail with JSONB storage
5. **Normalization**: Proper score normalization for fair comparisons

## Next Steps

### Backend Implementation
1. Update Flask models to use SQLAlchemy with PostgreSQL
2. Implement database connection using `psycopg2` or SQLAlchemy
3. Update recommendation engine to use new SQL query
4. Implement Top-K heap selection algorithm
5. Add JSONB serialization for recommendation results

### Testing
1. Test database initialization script
2. Test migration files
3. Test recommendation algorithm with sample data
4. Performance testing with large datasets

### Documentation
1. Update API documentation
2. Create data import scripts
3. Add sample data fixtures
4. Update deployment guide

## File Structure

```
projectsigma/
├── High_Level_Design_Draft.md          # Updated with new sections
├── POSTGRESQL_MIGRATION_SUMMARY.md     # This file
├── docker-compose.yml                  # Updated for PostgreSQL
└── server/
    └── database/
        ├── migrations/
        │   └── 001_initial_schema.sql # Complete schema
        ├── init_db.py                  # Initialization script
        └── README.md                   # Database documentation
```

## Usage

### Initialize Database

```bash
# Using Docker Compose (recommended)
docker-compose up -d postgres

# Or manually
cd server/database
python init_db.py
```

### Access pgAdmin

1. Navigate to http://localhost:8081
2. Login with:
   - Email: `admin@admin.com`
   - Password: `admin123`
3. Add server:
   - Host: `postgres`
   - Port: `5432`
   - Database: `university_recommender`
   - Username: `postgres`
   - Password: `postgres`

### Verify Schema

```bash
# Connect to database
psql -h localhost -U postgres -d university_recommender

# List tables
\dt

# Describe table
\d student

# List indexes
\di
```

## Migration Notes

### Breaking Changes
- **Table names**: Changed from plural to singular
- **Primary keys**: Changed from `SERIAL` to `VARCHAR(50)`
- **Field names**: Updated to match ER diagrams
- **Recommendation storage**: Changed from relational tables to JSONB arrays

### Compatibility
- Old MongoDB data will need migration script
- API endpoints may need updates for new schema
- Frontend may need updates for new data structure

## References

- ER Diagrams: See attached images in design document
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- JSONB Guide: https://www.postgresql.org/docs/current/datatype-json.html

