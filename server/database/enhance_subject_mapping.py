"""
Enhance Subject-to-Course Mapping
=================================
This script improves the mapping between A-level subjects and university courses
by analyzing HESA CAH codes and creating better course requirements.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_CONFIG = {
    'dbname': 'university_recommender',
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

# Map CAH codes to A-level subjects
CAH_TO_ALEVEL_MAPPING = {
    # Mathematics & Statistics
    'CAH07-01-01': ['Mathematics', 'Further Mathematics'],  # Mathematics
    'CAH07-03-01': ['Mathematics', 'Further Mathematics'],  # Statistics
    
    # Physical Sciences
    'CAH06-01-01': ['Chemistry'],  # Chemistry
    'CAH06-02-01': ['Physics'],    # Physics
    'CAH06-02-02': ['Physics'],    # Astronomy
    'CAH06-03-01': ['Geography', 'Geology'],  # Geology
    'CAH06-03-02': ['Geography'],  # Physical Geography
    
    # Biological Sciences
    'CAH03-01-01': ['Biology'],    # Biology
    'CAH03-01-02': ['Biology'],    # Botany
    'CAH03-01-03': ['Biology'],    # Zoology
    'CAH03-01-04': ['Biology'],    # Genetics
    'CAH03-01-05': ['Biology'],    # Microbiology
    'CAH03-01-06': ['Biology', 'Chemistry'],  # Molecular Biology
    
    # Engineering & Technology
    'CAH08-01-01': ['Mathematics', 'Physics'],  # General Engineering
    'CAH08-02-01': ['Mathematics', 'Physics'],  # Civil Engineering
    'CAH08-03-01': ['Mathematics', 'Physics'],  # Mechanical Engineering
    'CAH08-03-02': ['Mathematics', 'Physics'],  # Aerospace Engineering
    'CAH08-04-01': ['Mathematics', 'Physics'],  # Electrical Engineering
    'CAH08-05-01': ['Mathematics', 'Physics'],  # Manufacturing Engineering
    'CAH08-06-01': ['Mathematics', 'Physics', 'Chemistry'],  # Chemical Engineering
    
    # Computer Science
    'CAH19-01-01': ['Computer Science', 'Mathematics'],  # Computer Science
    'CAH19-02-01': ['Computer Science', 'Mathematics'],  # Information Systems
    'CAH19-03-01': ['Computer Science', 'Mathematics'],  # Software Engineering
    
    # Languages
    'CAH14-03-01': ['English Literature', 'English Language'],  # English Studies
    'CAH14-10-01': ['French'],     # French Studies
    'CAH14-11-01': ['German'],     # German Studies
    'CAH14-12-01': ['Italian'],    # Italian Studies
    'CAH14-13-01': ['Spanish'],    # Spanish Studies
    
    # Historical & Philosophical Studies
    'CAH15-01-01': ['History'],    # History by Period
    'CAH15-01-02': ['History'],    # History by Area
    'CAH15-01-03': ['History'],    # History by Topic
    'CAH15-02-01': ['History'],    # Archaeology
    'CAH15-03-01': ['Philosophy'], # Philosophy
    'CAH15-04-01': ['Religious Studies'],  # Theology
    
    # Social Studies
    'CAH10-01-01': ['Economics'],  # Economics
    'CAH10-02-01': ['Politics'],   # Politics
    'CAH10-03-01': ['Sociology'],  # Sociology
    'CAH10-04-02': ['Sociology'],  # Criminology
    'CAH10-06-01': ['Geography'],  # Human Geography
    
    # Business & Administrative Studies
    'CAH12-01-01': ['Business Studies', 'Economics'],  # Business Studies
    'CAH12-01-02': ['Business Studies'],  # Management Studies
    'CAH12-01-03': ['Economics', 'Mathematics'],  # Finance
    'CAH12-02-01': ['Business Studies'],  # Marketing
    
    # Creative Arts & Design
    'CAH16-01-01': ['Art'],        # Fine Art
    'CAH16-01-02': ['Art', 'Design Technology'],  # Design Studies
    'CAH16-02-01': ['Music'],      # Music
    'CAH16-03-01': ['Drama'],      # Drama
    'CAH16-04-01': ['Physical Education'],  # Dance
    'CAH16-05-01': ['Media Studies', 'Film Studies'],  # Photography
    
    # Medicine & Healthcare
    'CAH01-01-01': ['Biology', 'Chemistry'],  # Pre-clinical Medicine
    'CAH01-02-01': ['Biology', 'Chemistry'],  # Clinical Medicine
    'CAH02-01-01': ['Biology'],    # Anatomy & Physiology
    'CAH02-01-02': ['Biology', 'Chemistry'],  # Pharmacology
    'CAH02-02-01': ['Psychology'], # Psychology
    'CAH02-06-01': ['Physical Education', 'Biology'],  # Sports Science
    
    # Education
    'CAH17-01-01': ['English Literature', 'Mathematics'],  # Teacher Training
    
    # Law
    'CAH11-01-01': ['History', 'English Literature'],  # Law by Area
    'CAH11-01-02': ['History', 'English Literature'],  # Law by Topic
}

def enhance_subject_course_mapping():
    """Create enhanced subject-to-course mappings based on CAH codes"""
    logger.info("Starting enhanced subject-to-course mapping...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # First, ensure all A-level subjects exist in the subject table
        alevel_subjects = [
            'Mathematics', 'Further Mathematics', 'Physics', 'Chemistry', 'Biology',
            'English Literature', 'English Language', 'History', 'Geography', 'Economics',
            'Business Studies', 'Psychology', 'Sociology', 'Politics', 'Philosophy',
            'Art', 'Design Technology', 'Computer Science', 'French', 'Spanish',
            'German', 'Italian', 'Latin', 'Classical Civilisation', 'Religious Studies',
            'Music', 'Drama', 'Physical Education', 'Media Studies', 'Film Studies'
        ]
        
        logger.info("Ensuring all A-level subjects exist in database...")
        for subject_name in alevel_subjects:
            subject_id = subject_name.replace(" ", "_").replace("&", "and").lower()
            cur.execute("""
                INSERT INTO subject (subject_id, subject_name)
                VALUES (%s, %s)
                ON CONFLICT (subject_id) DO NOTHING
            """, (subject_id, subject_name))
        
        conn.commit()
        logger.info(f"Ensured {len(alevel_subjects)} A-level subjects exist")
        
        # Now create course requirements based on CAH mappings
        logger.info("Creating course requirements based on CAH codes...")
        
        requirements_created = 0
        for cah_code, subjects in CAH_TO_ALEVEL_MAPPING.items():
            # Find courses with this CAH code
            cur.execute("""
                SELECT DISTINCT c.course_id, c.name as course_name
                FROM course c
                JOIN hesa_sbj hs ON (c.pubukprn = hs.pubukprn 
                                   AND c.kiscourseid = hs.kiscourseid 
                                   AND c.kismode = hs.kismode)
                WHERE hs.sbj = %s
            """, (cah_code,))
            
            courses = cur.fetchall()
            
            if courses:
                logger.info(f"Found {len(courses)} courses for CAH code {cah_code}")
                
                for course in courses:
                    for subject_name in subjects:
                        subject_id = subject_name.replace(" ", "_").replace("&", "and").lower()
                        
                        # Create requirement record
                        req_id = f"{course['course_id'][:20]}_{subject_id[:20]}"
                        
                        # Determine grade requirement based on subject
                        grade_req = 'A'  # Default
                        if subject_name in ['Mathematics', 'Physics', 'Chemistry']:
                            grade_req = 'A'  # STEM subjects often need higher grades
                        elif subject_name in ['Biology', 'Economics']:
                            grade_req = 'B'
                        else:
                            grade_req = 'C'
                        
                        cur.execute("""
                            INSERT INTO course_requirement (req_id, course_id, subject_id, grade_req)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (req_id) DO NOTHING
                        """, (req_id, course['course_id'], subject_id, grade_req))
                        
                        requirements_created += 1
        
        conn.commit()
        logger.info(f"Created {requirements_created} course requirements")
        
        # Create search indexes for better performance
        logger.info("Creating search indexes...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_course_req_subject 
            ON course_requirement(subject_id)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_subject_name_search 
            ON subject USING gin(to_tsvector('english', subject_name))
        """)
        
        conn.commit()
        
        # Show statistics
        cur.execute("SELECT COUNT(*) FROM course_requirement")
        total_requirements = cur.fetchone()['count']
        
        cur.execute("""
            SELECT s.subject_name, COUNT(cr.course_id) as course_count
            FROM subject s
            LEFT JOIN course_requirement cr ON s.subject_id = cr.subject_id
            GROUP BY s.subject_name
            ORDER BY course_count DESC
            LIMIT 10
        """)
        
        top_subjects = cur.fetchall()
        
        logger.info(f"\nMapping Statistics:")
        logger.info(f"Total course requirements: {total_requirements}")
        logger.info(f"Top subjects by course count:")
        for subject in top_subjects:
            logger.info(f"  {subject['subject_name']}: {subject['course_count']} courses")
        
        logger.info("\n✅ Enhanced subject-to-course mapping complete!")
        
    except Exception as e:
        logger.error(f"Error enhancing mapping: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def create_search_functions():
    """Create SQL functions for subject-based course search"""
    logger.info("Creating search functions...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Function to find courses by subject
        cur.execute("""
            CREATE OR REPLACE FUNCTION find_courses_by_subject(subject_names text[])
            RETURNS TABLE(
                course_id varchar,
                course_name text,
                university_name varchar,
                required_subjects text[],
                required_grades text[]
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT DISTINCT
                    c.course_id,
                    c.name as course_name,
                    u.name as university_name,
                    array_agg(s.subject_name) as required_subjects,
                    array_agg(cr.grade_req) as required_grades
                FROM course c
                JOIN university u ON c.university_id = u.university_id
                JOIN course_requirement cr ON c.course_id = cr.course_id
                JOIN subject s ON cr.subject_id = s.subject_id
                WHERE s.subject_name = ANY(subject_names)
                GROUP BY c.course_id, c.name, u.name
                ORDER BY c.name;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        # Function to find courses matching student profile
        cur.execute("""
            CREATE OR REPLACE FUNCTION match_courses_to_student(
                student_subjects text[],
                min_grade_match float DEFAULT 0.5
            )
            RETURNS TABLE(
                course_id varchar,
                course_name text,
                university_name varchar,
                match_percentage float,
                matching_subjects text[]
            ) AS $$
            BEGIN
                RETURN QUERY
                WITH course_requirements AS (
                    SELECT 
                        c.course_id,
                        c.name as course_name,
                        u.name as university_name,
                        array_agg(s.subject_name) as required_subjects,
                        COUNT(s.subject_name) as total_requirements
                    FROM course c
                    JOIN university u ON c.university_id = u.university_id
                    JOIN course_requirement cr ON c.course_id = cr.course_id
                    JOIN subject s ON cr.subject_id = s.subject_id
                    GROUP BY c.course_id, c.name, u.name
                ),
                matches AS (
                    SELECT 
                        cr.*,
                        array_agg(rs.subject) as matching_subjects,
                        COUNT(rs.subject) as matches_count
                    FROM course_requirements cr,
                    unnest(cr.required_subjects) as rs(subject)
                    WHERE rs.subject = ANY(student_subjects)
                    GROUP BY cr.course_id, cr.course_name, cr.university_name, 
                            cr.required_subjects, cr.total_requirements
                )
                SELECT 
                    m.course_id,
                    m.course_name,
                    m.university_name,
                    (m.matches_count::float / m.total_requirements::float) as match_percentage,
                    m.matching_subjects
                FROM matches m
                WHERE (m.matches_count::float / m.total_requirements::float) >= min_grade_match
                ORDER BY match_percentage DESC, m.course_name;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        conn.commit()
        logger.info("✅ Search functions created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating search functions: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def main():
    """Run the enhancement process"""
    enhance_subject_course_mapping()
    create_search_functions()
    
    logger.info("\n" + "="*60)
    logger.info("SUBJECT-TO-COURSE MAPPING ENHANCED!")
    logger.info("="*60)
    logger.info("\nYou can now search courses by:")
    logger.info("1. Individual subjects")
    logger.info("2. Student subject combinations")
    logger.info("3. Match percentage requirements")
    logger.info("\nExample SQL queries:")
    logger.info("SELECT * FROM find_courses_by_subject(ARRAY['Mathematics', 'Physics']);")
    logger.info("SELECT * FROM match_courses_to_student(ARRAY['Mathematics', 'Physics', 'Chemistry'], 0.6);")

if __name__ == '__main__':
    main()