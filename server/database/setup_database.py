"""
Database schema creation and HESA data import and transformation script. 

1. Drop existing database (if exists)
2. Create new relational POSTGRES database
3. Create all tables (HESA +application) normalised to 3NF with PK, KF and referential integrity
4. uses junction tables for many-to-many relationships
5. Add index for performance and triggers for updated_at timestamps
6.    checks constraints for data validity (grades as A*-U, non-null fields, unique fields, etc)
7. Import HESA CSV data
8. Map HESA data to application tables
9. Enhance subject-to-course mappings for better search

Requires
    1. CSV files in ../../data/ directory
    2. PostgreSQL running on localhost:5432
    3. .env file with database password    - 
"""
import sys
import os
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from dotenv import load_dotenv

TARGET_DB = 'university_recommender'

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file for Database configuration
load_dotenv()
db_password = os.getenv('POSTGRES_PASSWORD')
if not db_password:
    raise RuntimeError(
        "POSTGRES_PASSWORD must be added in server/.env file. "
    )
DB_CONFIG = {
    'dbname': 'postgres',  # Connect to postgres DB first
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': db_password,
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}


def drop_and_create_database():
    """Drop existing database and create fresh one"""
    logger.info("="*70)
    logger.info("Running function: DROP AND CREATE DATABASE")
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
        
        logger.info("Database created successfully\n")
        
    except Exception as e:
        logger.error(f"Error: {e}")
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
        
        # Student table (core entity)
        cur.execute("""
            CREATE TABLE student (
                student_id VARCHAR(50) PRIMARY KEY,
                display_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at DATE DEFAULT CURRENT_DATE,
                region VARCHAR(100),
                tuition_budget INTEGER
            )
        """)
        
        # Subject table
        cur.execute("""
            CREATE TABLE subject (
                subject_id VARCHAR(50) PRIMARY KEY,
                subject_name VARCHAR(255) NOT NULL,
                cah_code VARCHAR(50)
            )
        """)
        
        # StudentGrade table
        cur.execute("""
            CREATE TABLE student_grade (
                student_id VARCHAR(50) REFERENCES student(student_id) ON DELETE CASCADE,
                subject_id VARCHAR(50) REFERENCES subject(subject_id) ON DELETE RESTRICT,
                predicted_grade VARCHAR(5) NOT NULL CHECK (predicted_grade IN ('A*', 'A', 'B', 'C', 'D', 'E', 'U')),
                PRIMARY KEY (student_id, subject_id)
            )
        """)
        
        # University table
        cur.execute("""
            CREATE TABLE university (
                university_id VARCHAR(255) PRIMARY KEY,
                pubukprn VARCHAR(8) UNIQUE,
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
                ucasprogid VARCHAR(50),
                hecos INTEGER,
                length VARCHAR(50),
                annual_fee INTEGER,
                employability_score INTEGER,
                course_url TEXT,
                typical_offer_text VARCHAR(255),
                typical_offer_tariff INTEGER,
                pubukprn VARCHAR(8),
                kiscourseid VARCHAR(50),
                kismode VARCHAR(2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (pubukprn, kiscourseid, kismode)
            )
        """)
        
        # Course subject requirements table (maps courses to required CAH codes with grades)
        cur.execute("""
            CREATE TABLE course_subject_requirement (
                req_id VARCHAR(50) PRIMARY KEY,
                course_id VARCHAR(255) REFERENCES course(course_id) ON DELETE CASCADE,
                cah_code VARCHAR(50) NOT NULL,
                tariff_points INTEGER,
                grade_req VARCHAR(5) NOT NULL CHECK (grade_req IN ('A*', 'A', 'B', 'C', 'D', 'E')),
                requirement_source VARCHAR(20) DEFAULT 'HESA_SBJ',
                UNIQUE (course_id, cah_code)
            )
        """)
        
        # EntranceExam table
        cur.execute("""
            CREATE TABLE entrance_exam (
                exam_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE
            )
        """)
        
        # Career interest table (10 categories)
        cur.execute("""
            CREATE TABLE career_interest (
                career_interest_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE
            )
        """)
        
        # Student preferred exam junction table
        cur.execute("""
            CREATE TABLE student_preferred_exam (
                student_id VARCHAR(50) REFERENCES student(student_id) ON DELETE CASCADE,
                exam_id VARCHAR(50) REFERENCES entrance_exam(exam_id) ON DELETE CASCADE,
                PRIMARY KEY (student_id, exam_id)
            )
        """)
        
        # Student career interest junction table
        cur.execute("""
            CREATE TABLE student_career_interest (
                student_id VARCHAR(50) REFERENCES student(student_id) ON DELETE CASCADE,
                career_interest_id VARCHAR(50) REFERENCES career_interest(career_interest_id) ON DELETE CASCADE,
                PRIMARY KEY (student_id, career_interest_id)
            )
        """)
        
        # CourseRequiredExam table
        cur.execute("""
            CREATE TABLE course_required_exam (
                course_id VARCHAR(255) REFERENCES course(course_id) ON DELETE CASCADE,
                exam_id VARCHAR(50) REFERENCES entrance_exam(exam_id) ON DELETE RESTRICT,
                PRIMARY KEY (course_id, exam_id)
            )
        """)
        
        # RecommendationRun table
        cur.execute("""
            CREATE TABLE recommendation_run (
                run_id VARCHAR(50) PRIMARY KEY,
                student_id VARCHAR(50) REFERENCES student(student_id) ON DELETE CASCADE,
                run_at DATE DEFAULT CURRENT_DATE,
                weights JSONB,
                prefs_snapshot JSONB
            )
        """)
        
        # RecommendationResult table
        cur.execute("""
            CREATE TABLE recommendation_result (
                result_id VARCHAR(50) PRIMARY KEY,
                run_id VARCHAR(50) REFERENCES recommendation_run(run_id) ON DELETE CASCADE,
                items JSONB NOT NULL CHECK (jsonb_typeof(items) = 'array')
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
                provurl TEXT,
                provaddress TEXT,
                provtel VARCHAR(50),
                pubukprncountry VARCHAR(10)
            )
        """)
        
        # HESA KIS Course
        cur.execute("""
            CREATE TABLE hesa_kiscourse (
                pubukprn VARCHAR(8),
                ukprn VARCHAR(8),
                kiscourseid VARCHAR(50),
                title TEXT,
                kismode VARCHAR(2),
                ucasprogid VARCHAR(50),
                length VARCHAR(50),          -- Maps to NUMSTAGE
                levelcode VARCHAR(10),       -- Maps to KISLEVEL
                locid VARCHAR(50),           -- Maps to KISAIMCODE
                distance VARCHAR(1),
                honours VARCHAR(1),
                sandwich VARCHAR(1),
                yearabroad VARCHAR(1),
                foundationyear VARCHAR(1),   -- Maps to FOUNDATION
                hecos INTEGER,               -- First HECOS code (6-digit numeric)
                coursepageurl TEXT,          -- Maps to CRSEURL
                supporturl TEXT,
                employabilityurl TEXT,       -- Maps to EMPLOYURL
                PRIMARY KEY (pubukprn, kiscourseid, kismode)
            )
        """)
        
        # HESA Employment
        cur.execute("""
            CREATE TABLE hesa_employment (
                pubukprn VARCHAR(8),
                ukprn VARCHAR(8),
                kiscourseid VARCHAR(50),
                kismode VARCHAR(2),
                empunavailreason VARCHAR(50),
                emppop INTEGER,
                empagg VARCHAR(2),
                empaggyear VARCHAR(20),
                empyear1 VARCHAR(20),
                empyear2 VARCHAR(20),
                empsbj VARCHAR(20),
                workstudy INTEGER,
                work INTEGER,
                study INTEGER,
                unemp INTEGER,
                "other" INTEGER,
                PRIMARY KEY (pubukprn, kiscourseid, kismode)
            )
        """)
        
        # HESA Entry
        cur.execute("""
            CREATE TABLE hesa_entry (
                pubukprn VARCHAR(8),
                ukprn VARCHAR(8),
                kiscourseid VARCHAR(50),
                kismode VARCHAR(2),
                entunavailreason VARCHAR(50),
                entpop INTEGER,
                entagg VARCHAR(2),
                entaggyear VARCHAR(20),
                entyear1 VARCHAR(20),
                entyear2 VARCHAR(20),
                entsbj VARCHAR(20),
                access INTEGER,
                alevel INTEGER,
                bacc INTEGER,
                degree INTEGER,
                foundtn INTEGER,
                noquals INTEGER,
                "other" INTEGER,
                otherhe INTEGER,
                PRIMARY KEY (pubukprn, kiscourseid, kismode)
            )
        """)
        
        # HESA GO Salary
        cur.execute("""
            CREATE TABLE hesa_gosalary (
                pubukprn VARCHAR(8),
                ukprn VARCHAR(8),
                kiscourseid VARCHAR(50),
                kismode VARCHAR(2),
                gosalunavailreason VARCHAR(50),
                gosalpop INTEGER,
                gosalresponse INTEGER,
                gosalsample INTEGER,
                gosalresp_rate INTEGER,
                gosalagg VARCHAR(2),
                gosalaggyear VARCHAR(20),
                gosalyear1 VARCHAR(20),
                gosalyear2 VARCHAR(20),
                gosalsbj VARCHAR(20),
                goinstlq INTEGER,
                goinstmed INTEGER,
                goinstuq INTEGER,
                goprov_pc_uk INTEGER,
                goprov_pc_e INTEGER,
                goprov_pc_ni INTEGER,
                goprov_pc_s INTEGER,
                goprov_pc_w INTEGER,
                PRIMARY KEY (pubukprn, kiscourseid, kismode)
            )
        """)
        
        # HESA Job List
        cur.execute("""
            CREATE TABLE hesa_joblist (
                pubukprn VARCHAR(8),
                ukprn VARCHAR(8),
                kiscourseid VARCHAR(50),
                kismode VARCHAR(2),
                comsbj VARCHAR(20),
                job VARCHAR(200),
                perc INTEGER,
                "order" INTEGER,
                hs INTEGER,
                PRIMARY KEY (pubukprn, kiscourseid, kismode, job)
            )
        """)
        
        # HESA LEO3
        cur.execute("""
            CREATE TABLE hesa_leo3 (
                pubukprn VARCHAR(8),
                ukprn VARCHAR(8),
                kiscourseid VARCHAR(50),
                kismode VARCHAR(2),
                leo3unavailreason VARCHAR(50),
                leo3pop INTEGER,
                leo3agg VARCHAR(2),
                leo3aggyear VARCHAR(20),
                leo3sbj VARCHAR(20),
                leo3instlq INTEGER,
                leo3instmed INTEGER,
                leo3instuq INTEGER,
                leo3prov_pc_uk INTEGER,
                leo3prov_pc_e INTEGER,
                leo3prov_pc_nw INTEGER,
                leo3prov_pc_ne INTEGER,
                leo3prov_pc_em INTEGER,
                leo3prov_pc_wm INTEGER,
                leo3prov_pc_ee INTEGER,
                leo3prov_pc_se INTEGER,
                leo3prov_pc_sw INTEGER,
                leo3prov_pc_yh INTEGER,
                leo3prov_pc_ln INTEGER,
                leo3prov_pc_ni INTEGER,
                leo3prov_pc_s INTEGER,
                leo3prov_pc_ed INTEGER,
                leo3prov_pc_gl INTEGER,
                leo3prov_pc_w INTEGER,
                leo3prov_pc_cf INTEGER,
                PRIMARY KEY (pubukprn, kiscourseid, kismode)
            )
        """)
        
        # HESA UCASCOURSEID - UCAS course identifiers
        cur.execute("""
            CREATE TABLE hesa_ucascourseid (
                ucascourseid_id SERIAL PRIMARY KEY,
                pubukprn VARCHAR(8) NOT NULL,
                ukprn VARCHAR(8) NOT NULL,
                kiscourseid VARCHAR(50) NOT NULL,
                kismode VARCHAR(2) NOT NULL,
                locid VARCHAR(50),
                ucascourseid VARCHAR(50) NOT NULL,
                UNIQUE (pubukprn, kiscourseid, kismode, locid, ucascourseid)
            )
        """)
        
        # HESA SBJ - Subject codes (CAH) for courses
        cur.execute("""
            CREATE TABLE hesa_sbj (
                pubukprn VARCHAR(8) NOT NULL,
                ukprn VARCHAR(8) NOT NULL,
                kiscourseid VARCHAR(50) NOT NULL,
                kismode VARCHAR(2) NOT NULL,
                sbj VARCHAR(50) NOT NULL,
                PRIMARY KEY (pubukprn, kiscourseid, kismode, sbj)
            )
        """)

        # HESA TARIFF - Tariff point distributions
        cur.execute("""
            CREATE TABLE hesa_tariff (
                pubukprn VARCHAR(8) NOT NULL,
                ukprn VARCHAR(8) NOT NULL,
                kiscourseid VARCHAR(50) NOT NULL,
                kismode VARCHAR(2) NOT NULL,
                tarunavailreason VARCHAR(2),
                tarpop INTEGER,
                taragg VARCHAR(2),
                taraggyear VARCHAR(10),
                taryear1 VARCHAR(10),
                taryear2 VARCHAR(10),
                tarsbj VARCHAR(50),
                t001 INTEGER,
                t048 INTEGER,
                t064 INTEGER,
                t080 INTEGER,
                t096 INTEGER,
                t112 INTEGER,
                t128 INTEGER,
                t144 INTEGER,
                t160 INTEGER,
                t176 INTEGER,
                t192 INTEGER,
                t208 INTEGER,
                t224 INTEGER,
                t240 INTEGER,
                PRIMARY KEY (pubukprn, kiscourseid, kismode)
            )
        """)
        
        # Create indexes for performance
        logger.info("Creating indexes...")
        cur.execute("CREATE INDEX idx_course_university ON course(university_id)")
        cur.execute("CREATE INDEX idx_requirement_course ON course_subject_requirement(course_id)")
        # Note: Removed redundant indexes where PK/UNIQUE constraints already create indexes:
        # - idx_course_hesa: course has UNIQUE(pubukprn, kiscourseid, kismode)
        # - idx_sbj_course: hesa_sbj PK covers (pubukprn, kiscourseid, kismode, sbj)
        # - idx_ucascourseid_course: hesa_ucascourseid UNIQUE covers those columns
        # - idx_tariff_course: hesa_tariff PK covers those columns
        
        # Create trigger function for updating updated_at timestamp
        logger.info("Creating triggers...")
        cur.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        # Apply trigger to tables with updated_at
        cur.execute("""
            CREATE TRIGGER update_university_updated_at
            BEFORE UPDATE ON university
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)
        
        cur.execute("""
            CREATE TRIGGER update_course_updated_at
            BEFORE UPDATE ON course
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)
        
        # Record migration
        cur.execute("INSERT INTO schema_migrations (version) VALUES ('001_complete_schema')")
        
        conn.commit()
        logger.info("Schema created successfully\n")
        
    except Exception as e:
        logger.error(f"Error creating schema: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def import_hesa_data():
    """Import HESA CSV data"""
    logger.info("="*70)
    logger.info("STEP 3: IMPORT HESA CSV DATA")
   
    # Import using existing script
    import import_discover_uni_csv
    import_discover_uni_csv.main()
    
    logger.info("HESA data imported successfully\n")

def map_hesa_to_application():
    """Map HESA data to application tables"""
    logger.info("="*70)
    logger.info("STEP 4: MAP HESA TO APPLICATION TABLES")
    logger.info("="*70)
    
    # Import using existing script
    import map_hesa_to_main_tables
    map_hesa_to_main_tables.map_hesa_to_main_tables()
    
    logger.info("HESA data mapped successfully\n")

def create_career_mappings():
    """Create subject to career interest mappings and seed career interests"""
    logger.info("="*70)
    logger.info("STEP 5: CREATE CAREER INTEREST MAPPINGS")
    logger.info("="*70)
    
    # Import and run career mapping script
    import subject_to_career_mapping
    subject_to_career_mapping.create_subject_to_career_table()
    
    # Seed career interests for student profile
    import seed_career_interests
    seed_career_interests.seed_career_interests()
    
    logger.info("Career interest mappings created successfully\n")

def enhance_subject_mappings():
    """Enhance subject-to-course mappings for better search"""
    logger.info("="*70)
    logger.info("STEP 6: ENHANCE SUBJECT-TO-COURSE MAPPINGS")
    logger.info("="*70)
    
    # Import and run subject mapping enhancement
    import enhance_subject_mapping
    enhance_subject_mapping.main()
    
    logger.info("Subject-to-course mappings enhanced successfully\n")

def main():
    """Run complete database setup"""
    try:
        logger.info("\n" + "="*70)
        logger.info("FRESH DATABASE SETUP - Project Sigma")
        
        drop_and_create_database()
        create_schema()
        import_hesa_data()
        map_hesa_to_application()
        create_career_mappings()
        enhance_subject_mappings()
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("DATABASE SETUP COMPLETE!")
     
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
        
        cur.execute("SELECT COUNT(*) FROM course_subject_requirement")
        logger.info(f"  - Course Requirements: {cur.fetchone()[0]}")
        
        logger.info("\nDatabase ready for use!\n")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"\nSetup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()