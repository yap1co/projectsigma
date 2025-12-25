"""
Fresh Database Setup Script
===========================
This script drops and recreates the university_recommender database from scratch.

Steps:
1. Drop existing database (if exists)
2. Create new database
3. Create all tables (application + HESA)
4. Import HESA CSV data
5. Map HESA data to application tables

Usage:
    python setup_database.py

Requirements:
    - PostgreSQL running on localhost:5432
    - postgres user with password 'postgres123'
    - CSV files in ../../data/ directory
"""

import sys
import os
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database_helper import generate_id
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'dbname': 'postgres',  # Connect to postgres DB first
    'user': 'postgres',
    'password': 'postgres123',
    'host': 'localhost',
    'port': '5432'
}

TARGET_DB = 'university_recommender'

def drop_and_create_database():
    """Drop existing database and create fresh one"""
    logger.info("="*70)
    logger.info("STEP 1: DROP AND CREATE DATABASE")
    logger.info("="*70)
    
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    try:
        # Terminate existing connections
        logger.info(f"Terminating existing connections to {TARGET_DB}...")
        cur.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{TARGET_DB}'
              AND pid <> pg_backend_pid()
        """)
        
        # Drop database
        logger.info(f"Dropping database {TARGET_DB}...")
        cur.execute(f"DROP DATABASE IF EXISTS {TARGET_DB}")
        
        # Create database
        logger.info(f"Creating database {TARGET_DB}...")
        cur.execute(f"CREATE DATABASE {TARGET_DB}")
        
        logger.info("✅ Database created successfully\n")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def get_target_db_connection():
    """Get connection to target database"""
    config = DB_CONFIG.copy()
    config['dbname'] = TARGET_DB
    return psycopg2.connect(**config)

def create_schema():
    """Create all database tables"""
    logger.info("="*70)
    logger.info("STEP 2: CREATE DATABASE SCHEMA")
    logger.info("="*70)
    
    conn = get_target_db_connection()
    cur = conn.cursor()
    
    try:
        # Schema migrations tracking table
        logger.info("Creating schema_migrations table...")
        cur.execute("""
            CREATE TABLE schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Application tables
        logger.info("Creating application tables...")
        
        # User table
        cur.execute("""
            CREATE TABLE "user" (
                user_id VARCHAR(255) PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # University table
        cur.execute("""
            CREATE TABLE university (
                university_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                region VARCHAR(100),
                rank_overall INTEGER,
                employability_score INTEGER,
                website_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Course table
        cur.execute("""
            CREATE TABLE course (
                course_id VARCHAR(255) PRIMARY KEY,
                university_id VARCHAR(255) REFERENCES university(university_id),
                name TEXT NOT NULL,
                ucas_code VARCHAR(10) UNIQUE,
                annual_fee INTEGER,
                employability_score INTEGER,
                course_url TEXT,
                pubukprn VARCHAR(8),
                kiscourseid VARCHAR(20),
                kismode VARCHAR(2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Course requirements table
        cur.execute("""
            CREATE TABLE course_requirement (
                requirement_id VARCHAR(255) PRIMARY KEY,
                course_id VARCHAR(255) REFERENCES course(course_id),
                subject VARCHAR(255),
                grade VARCHAR(10),
                qualification_type VARCHAR(50) DEFAULT 'A-Level',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User preference table
        cur.execute("""
            CREATE TABLE user_preference (
                preference_id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255) REFERENCES "user"(user_id),
                preferred_regions TEXT[],
                career_interests TEXT[],
                subject_1 VARCHAR(100),
                subject_1_grade VARCHAR(2),
                subject_2 VARCHAR(100),
                subject_2_grade VARCHAR(2),
                subject_3 VARCHAR(100),
                subject_3_grade VARCHAR(2),
                ucas_points INTEGER,
                max_fee INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User feedback table
        cur.execute("""
            CREATE TABLE user_feedback (
                feedback_id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255) REFERENCES "user"(user_id),
                course_id VARCHAR(255) REFERENCES course(course_id),
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                feedback_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Career interests lookup table
        cur.execute("""
            CREATE TABLE career_interest (
                interest_id VARCHAR(255) PRIMARY KEY,
                interest_name VARCHAR(255) NOT NULL,
                keywords TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # HESA tables
        logger.info("Creating HESA tables...")
        
        # HESA Institution
        cur.execute("""
            CREATE TABLE hesa_institution (
                pubukprn VARCHAR(8) PRIMARY KEY,
                first_trading_name VARCHAR(255),
                legal_name VARCHAR(255),
                country VARCHAR(10),
                provurl TEXT
            )
        """)
        
        # HESA KIS Course
        cur.execute("""
            CREATE TABLE hesa_kiscourse (
                pubukprn VARCHAR(8),
                kiscourseid VARCHAR(20),
                kismode VARCHAR(2),
                title TEXT,
                ucasprogid VARCHAR(10),
                hecos VARCHAR(100),
                numstage INTEGER,
                crseurl TEXT,
                PRIMARY KEY (pubukprn, kiscourseid, kismode)
            )
        """)
        
        # HESA Employment
        cur.execute("""
            CREATE TABLE hesa_employment (
                pubukprn VARCHAR(8),
                kiscourseid VARCHAR(20),
                kismode VARCHAR(2),
                empagg VARCHAR(2),
                work INTEGER,
                study INTEGER,
                unemp INTEGER,
                workstudy INTEGER,
                emppop INTEGER,
                empresponse INTEGER,
                empresp_rate INTEGER,
                empsample INTEGER,
                PRIMARY KEY (pubukprn, kiscourseid, kismode, empagg)
            )
        """)
        
        # HESA Entry
        cur.execute("""
            CREATE TABLE hesa_entry (
                pubukprn VARCHAR(8),
                kiscourseid VARCHAR(20),
                kismode VARCHAR(2),
                entagg VARCHAR(2),
                entsbj VARCHAR(10),
                alevel INTEGER,
                access INTEGER,
                degree INTEGER,
                foundtn INTEGER,
                noquals INTEGER,
                "other" INTEGER,
                entpop INTEGER,
                PRIMARY KEY (pubukprn, kiscourseid, kismode, entagg, entsbj)
            )
        """)
        
        # HESA GO Salary
        cur.execute("""
            CREATE TABLE hesa_gosalary (
                pubukprn VARCHAR(8),
                kiscourseid VARCHAR(20),
                kismode VARCHAR(2),
                goagg VARCHAR(2),
                goinstmed INTEGER,
                goinstlq INTEGER,
                goinstuq INTEGER,
                gopop INTEGER,
                goresponse INTEGER,
                goresp_rate INTEGER,
                gosample INTEGER,
                PRIMARY KEY (pubukprn, kiscourseid, kismode, goagg)
            )
        """)
        
        # HESA Job List
        cur.execute("""
            CREATE TABLE hesa_joblist (
                pubukprn VARCHAR(8),
                kiscourseid VARCHAR(20),
                kismode VARCHAR(2),
                jobagg VARCHAR(2),
                job VARCHAR(255),
                perc INTEGER,
                "order" INTEGER,
                PRIMARY KEY (pubukprn, kiscourseid, kismode, jobagg, "order")
            )
        """)
        
        # HESA LEO3
        cur.execute("""
            CREATE TABLE hesa_leo3 (
                pubukprn VARCHAR(8),
                kiscourseid VARCHAR(20),
                kismode VARCHAR(2),
                leoagg VARCHAR(2),
                leo3instmed INTEGER,
                leo3instlq INTEGER,
                leo3instuq INTEGER,
                leo3pop INTEGER,
                PRIMARY KEY (pubukprn, kiscourseid, kismode, leoagg)
            )
        """)
        
        # Create indexes for performance
        logger.info("Creating indexes...")
        cur.execute("CREATE INDEX idx_course_university ON course(university_id)")
        cur.execute("CREATE INDEX idx_course_hesa ON course(pubukprn, kiscourseid, kismode)")
        cur.execute("CREATE INDEX idx_requirement_course ON course_requirement(course_id)")
        cur.execute("CREATE INDEX idx_preference_user ON user_preference(user_id)")
        cur.execute("CREATE INDEX idx_feedback_user ON user_feedback(user_id)")
        cur.execute("CREATE INDEX idx_feedback_course ON user_feedback(course_id)")
        
        # Record migration
        cur.execute("INSERT INTO schema_migrations (version) VALUES ('001_complete_schema')")
        
        conn.commit()
        logger.info("✅ Schema created successfully\n")
        
    except Exception as e:
        logger.error(f"❌ Error creating schema: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def import_hesa_data():
    """Import HESA CSV data"""
    logger.info("="*70)
    logger.info("STEP 3: IMPORT HESA CSV DATA")
    logger.info("="*70)
    
    # Import using existing script
    import import_discover_uni_csv
    import_discover_uni_csv.main()
    
    logger.info("✅ HESA data imported successfully\n")

def map_hesa_to_application():
    """Map HESA data to application tables"""
    logger.info("="*70)
    logger.info("STEP 4: MAP HESA TO APPLICATION TABLES")
    logger.info("="*70)
    
    # Import using existing script
    import map_hesa_to_main_tables
    map_hesa_to_main_tables.map_hesa_to_main_tables()
    
    logger.info("✅ HESA data mapped successfully\n")

def main():
    """Run complete database setup"""
    try:
        logger.info("\n" + "="*70)
        logger.info("FRESH DATABASE SETUP - Project Sigma")
        logger.info("="*70 + "\n")
        
        # Step 1: Drop and create database
        drop_and_create_database()
        
        # Step 2: Create schema
        create_schema()
        
        # Step 3: Import HESA data
        import_hesa_data()
        
        # Step 4: Map to application tables
        map_hesa_to_application()
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("✅ DATABASE SETUP COMPLETE!")
        logger.info("="*70)
        
        conn = get_target_db_connection()
        cur = conn.cursor()
        
        # Show counts
        logger.info("\nDatabase Statistics:")
        cur.execute("SELECT COUNT(*) FROM hesa_institution")
        logger.info(f"  - HESA Institutions: {cur.fetchone()[0]}")
        
        cur.execute("SELECT COUNT(*) FROM hesa_kiscourse")
        logger.info(f"  - HESA Courses: {cur.fetchone()[0]}")
        
        cur.execute("SELECT COUNT(*) FROM university")
        logger.info(f"  - Universities: {cur.fetchone()[0]}")
        
        cur.execute("SELECT COUNT(*) FROM course")
        logger.info(f"  - Courses: {cur.fetchone()[0]}")
        
        cur.execute("SELECT COUNT(*) FROM course_requirement")
        logger.info(f"  - Course Requirements: {cur.fetchone()[0]}")
        
        logger.info("\nDatabase ready for use! 🎉\n")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
