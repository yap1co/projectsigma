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

# Map CAH codes to their specific subject names (comprehensive mapping from HESA data)
CAH_TO_SUBJECT_NAME = {
    # Creative Arts & Design
    'CAH25-01-01': 'Creative Writing',
    'CAH25-01-03': 'Creative Design', 
    'CAH25-01-02': 'Art',
    'CAH25-02-04': 'Dance',
    'CAH25-02-03': 'Drama',
    'CAH25-02-02': 'Music',
    'CAH25-02-01': 'Performing Arts',
    'CAH17-01-02': 'Business Studies',
    'CAH17-01-06': 'Leisure And Recreation',
    'CAH17-01-08': 'Accounting',
    'CAH17-01-07': 'Business And Finance',
    'CAH13-01-02': 'Building Studies',
    'CAH10-01-08': 'Electronics Endorsement',
    'CAH10-01-01': 'Engineering',
    'CAH19-01-02': 'Geometric/Mechanical Drawing',
    'CAH01-01-01': 'Physiology',
    'CAH20-01-03': 'Archaeology',
    'CAH20-01-01': 'History',
    'CAH23-01-03': 'Humanities',
    'CAH19-01-02': 'English Language',
    'CAH19-04-01': 'French',
    'CAH19-04-02': 'German',
    'CAH19-04-03': 'Italian',
    'CAH19-04-05': 'Modern Studies',
    'CAH19-04-05': 'Russian',
    'CAH19-04-04': 'Spanish',
    'CAH19-02-03': 'Welsh',
    'CAH20-02-01': 'Philosophy',
    'CAH03-01-08': 'Biochemistry',
    'CAH03-01-02': 'Biology',
    'CAH11-01-01': 'Computer Science',
    'CAH11-01-02': 'Information Technology',
    'CAH11-01-04': 'Computer Programming',
    'CAH26-01-04': 'Environmental Science',
    'CAH07-04-03': 'Applied Science',
    'CAH26-01-06': 'Marine Science',
    'CAH05-01-01': 'Mathematics',
    'CAH26-01-01': 'Geography',
    'CAH07-02-01': 'Chemistry',
    'CAH07-04-01': 'Physical Science',
    'CAH07-01-01': 'Physics',
    'CAH03-02-01': 'Sports Science',
    'CAH15-01-04': 'Anthropology',
    'CAH24-01-05': 'Communication Studies',
    'CAH15-02-01': 'Economics',
    'CAH15-04-03': 'Health And Social Care',
    'CAH16-01-01': 'Law',
    'CAH15-03-01': 'Politics',
    'CAH04-01-01': 'Psychology',
    'CAH15-01-03': 'Social Policy',
    'CAH15-01-02': 'Sociology',
    'CAH06-01-02': 'Horticultural Science',
    'CAH06-01-03': 'Agriculture',
    'CAH10-03-04': 'Navigation',
    'CAH20-02-02': 'Religious Studies',
    'CAH17-01-05': 'Public And Social Admin',
    'CAH11-01-03': 'Information Studies',
    'CAH25-01-05': 'Craft',
    'CAH03-01-05': 'Zoology',
    'CAH05-01-03': 'Statistics',
    'CAH19-02-02': 'Gaelic',
    'CAH19-02-04': 'Irish',
    'CAH19-04-04': 'Portuguese',
    'CAH19-04-02': 'Swedish',
    'CAH19-04-02': 'Norwegian',
    'CAH19-04-09': 'Finnish Language',
    'CAH19-04-05': 'Polish',
    'CAH19-04-05': 'Czech',
    'CAH19-04-06': 'Chinese Language And Literature',
    'CAH19-04-05': 'Japanese',
    'CAH19-04-06': 'Hindi',
    'CAH19-04-06': 'Urdu',
    'CAH19-04-06': 'Bengali',
    'CAH19-04-06': 'India Studies',
    'CAH19-04-07': 'Arabic',
    'CAH19-04-07': 'Persian',
    'CAH25-01-04': 'Moving Image Arts',
    'CAH19-04-07': 'Modern Hebrew',
    'CAH23-01-01': 'General Studies',
    'CAH23-01-02': 'Extended Project',
    'CAH15-01-05': 'World Development',
    'CAH06-01-07': 'Domestic Science',
    'CAH19-04-09': 'Biblical Hebrew',
    'CAH20-01-05': 'Latin',
    'CAH19-04-02': 'Danish',
    'CAH19-04-09': 'Hungarian',
    'CAH19-04-07': 'Turkish',
}

# Map CAH codes to required A-level subjects for course requirements
CAH_TO_ALEVEL_REQUIREMENTS = {
    # Creative Arts & Design
    'CAH25-01-01': ['English Literature', 'English Language'],  # Creative Writing
    'CAH25-01-03': ['Art', 'Design Technology'],  # Creative Design
    'CAH25-01-02': ['Art'],  # Art
    'CAH25-02-04': ['Physical Education', 'Drama'],  # Dance
    'CAH25-02-03': ['Drama', 'English Literature'],  # Drama
    'CAH25-02-02': ['Music'],  # Music
    'CAH25-02-01': ['Drama', 'Music'],  # Performing Arts
    
    # Business Studies
    'CAH17-01-02': ['Business Studies', 'Economics'],  # Business Studies
    'CAH17-01-06': ['Physical Education', 'Business Studies'],  # Leisure And Recreation
    'CAH17-01-08': ['Mathematics', 'Economics'],  # Accounting
    'CAH17-01-07': ['Mathematics', 'Economics'],  # Business And Finance
    
    # Building & Engineering
    'CAH13-01-02': ['Design Technology', 'Physics'],  # Building Studies
    'CAH10-01-08': ['Physics', 'Mathematics'],  # Electronics Endorsement
    'CAH10-01-01': ['Mathematics', 'Physics'],  # Engineering
    'CAH19-01-02': ['Mathematics', 'Design Technology'],  # Geometric/Mechanical Drawing
    
    # Medical & Life Sciences
    'CAH01-01-01': ['Biology', 'Chemistry'],  # Physiology
    'CAH03-01-08': ['Biology', 'Chemistry'],  # Biochemistry
    'CAH03-01-02': ['Biology'],  # Biology
    'CAH26-01-04': ['Biology', 'Chemistry', 'Geography'],  # Environmental Science
    'CAH07-04-03': ['Physics', 'Chemistry'],  # Applied Science
    'CAH26-01-06': ['Biology', 'Geography'],  # Marine Science
    'CAH03-02-01': ['Physical Education', 'Biology'],  # Sports Science
    'CAH03-01-05': ['Biology'],  # Zoology
    
    # Humanities & Social Sciences
    'CAH20-01-03': ['History'],  # Archaeology
    'CAH20-01-01': ['History'],  # History
    'CAH23-01-03': ['History', 'English Literature'],  # Humanities
    'CAH20-02-01': ['Philosophy'],  # Philosophy
    'CAH15-01-04': ['Geography', 'Sociology'],  # Anthropology
    'CAH24-01-05': ['English Language', 'Media Studies'],  # Communication Studies
    'CAH15-02-01': ['Economics'],  # Economics
    'CAH15-04-03': ['Psychology', 'Sociology'],  # Health And Social Care
    'CAH16-01-01': ['History', 'English Literature'],  # Law
    'CAH15-03-01': ['Politics', 'History'],  # Politics
    'CAH04-01-01': ['Psychology'],  # Psychology
    'CAH15-01-03': ['Politics', 'Sociology'],  # Social Policy
    'CAH15-01-02': ['Sociology'],  # Sociology
    'CAH20-02-02': ['Religious Studies'],  # Religious Studies
    'CAH17-01-05': ['Politics', 'History'],  # Public And Social Admin
    
    # Mathematics & Sciences
    'CAH05-01-01': ['Mathematics'],  # Mathematics
    'CAH26-01-01': ['Geography'],  # Geography
    'CAH07-02-01': ['Chemistry'],  # Chemistry
    'CAH07-04-01': ['Physics'],  # Physical Science
    'CAH07-01-01': ['Physics'],  # Physics
    'CAH05-01-03': ['Mathematics'],  # Statistics
    
    # Computer Science & Technology
    'CAH11-01-01': ['Computer Science', 'Mathematics'],  # Computer Science
    'CAH11-01-02': ['Computer Science'],  # Information Technology
    'CAH11-01-04': ['Computer Science', 'Mathematics'],  # Computer Programming
    'CAH11-01-03': ['Computer Science', 'English Language'],  # Information Studies
    
    # Languages
    'CAH19-01-02': ['English Language', 'English Literature'],  # English Language
    'CAH19-04-01': ['French'],  # French
    'CAH19-04-02': ['German'],  # German
    'CAH19-04-03': ['Italian'],  # Italian
    'CAH19-04-05': ['Spanish'],  # Modern Studies/Russian
    'CAH19-04-04': ['Spanish'],  # Spanish
    'CAH19-02-03': ['Welsh'],  # Welsh
    'CAH19-02-02': ['Gaelic'],  # Gaelic
    'CAH19-02-04': ['Irish'],  # Irish
    'CAH19-04-04': ['Portuguese'],  # Portuguese
    'CAH19-04-02': ['Swedish'],  # Swedish/Norwegian
    'CAH19-04-09': ['Polish'],  # Finnish Language/Polish
    'CAH19-04-05': ['Czech'],  # Czech
    'CAH19-04-06': ['Chinese Language And Literature'],  # Chinese/Hindi/Urdu/Bengali
    'CAH19-04-07': ['Arabic'],  # Arabic/Persian/Modern Hebrew
    'CAH20-01-05': ['Latin'],  # Latin
    'CAH19-04-09': ['Hungarian'],  # Biblical Hebrew/Hungarian
    'CAH19-04-07': ['Turkish'],  # Turkish
    
    # Agriculture & Environmental
    'CAH06-01-02': ['Biology', 'Geography'],  # Horticultural Science
    'CAH06-01-03': ['Biology', 'Geography'],  # Agriculture
    'CAH10-03-04': ['Mathematics', 'Physics'],  # Navigation
    'CAH06-01-07': ['Design Technology'],  # Domestic Science
    
    # Arts & Media
    'CAH25-01-05': ['Art', 'Design Technology'],  # Craft
    'CAH25-01-04': ['Media Studies', 'Art'],  # Moving Image Arts
    
    # General Studies
    'CAH23-01-01': ['English Literature'],  # General Studies
    'CAH23-01-02': ['English Literature'],  # Extended Project
    'CAH15-01-05': ['Geography', 'Politics'],  # World Development
}

def enhance_subject_course_mapping():
    """Create enhanced subject-to-course mappings based on CAH codes"""
    logger.info("Starting enhanced subject-to-course mapping...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Clear existing subject and course_requirement tables to rebuild correctly
        logger.info("Clearing existing subject and course_requirement data...")
        cur.execute("DELETE FROM course_requirement")
        cur.execute("DELETE FROM subject")
        conn.commit()
        
        # Step 1: Create subjects using CAH codes as subject_id
        logger.info("Creating subjects with CAH codes as subject_id...")
        subjects_created = 0
        
        # First, create all CAH code subjects from the mapping
        for cah_code, subject_name in CAH_TO_SUBJECT_NAME.items():
            cur.execute("""
                INSERT INTO subject (subject_id, subject_name)
                VALUES (%s, %s)
                ON CONFLICT (subject_id) DO NOTHING
            """, (cah_code, subject_name))
            subjects_created += 1
        
        # Also create A-level subjects (these will be used as requirements)
        alevel_subjects = [
            'Mathematics', 'Further Mathematics', 'Physics', 'Chemistry', 'Biology',
            'English Literature', 'English Language', 'History', 'Geography', 'Economics',
            'Business Studies', 'Psychology', 'Sociology', 'Politics', 'Philosophy',
            'Art', 'Design Technology', 'Computer Science', 'French', 'Spanish',
            'German', 'Italian', 'Latin', 'Classical Civilisation', 'Religious Studies',
            'Music', 'Drama', 'Physical Education', 'Media Studies', 'Film Studies',
            'Geology', 'Welsh', 'Gaelic', 'Irish', 'Portuguese', 'Swedish', 'Norwegian',
            'Polish', 'Czech', 'Chinese Language And Literature', 'Hindi', 'Urdu', 'Bengali',
            'Arabic', 'Persian', 'Modern Hebrew', 'Turkish', 'Finnish Language', 'Hungarian',
            'Biblical Hebrew', 'Danish', 'Japanese', 'Russian'
        ]
        
        for subject_name in alevel_subjects:
            subject_id = subject_name.replace(" ", "_").replace("&", "and").lower()
            cur.execute("""
                INSERT INTO subject (subject_id, subject_name)
                VALUES (%s, %s)
                ON CONFLICT (subject_id) DO NOTHING
            """, (subject_id, subject_name))
            subjects_created += 1
        
        conn.commit()
        logger.info(f"Created {subjects_created} subjects (CAH codes + A-levels)")
        
        # Step 2: Create course requirements linking courses to A-level subjects based on CAH codes
        logger.info("Creating course requirements from HESA CAH codes...")
        
        requirements_created = 0
        
        # Get all courses with their CAH codes from hesa_sbj
        cur.execute("""
            SELECT DISTINCT c.course_id, c.name as course_name, hs.sbj as cahcode
            FROM course c
            JOIN hesa_sbj hs ON (c.pubukprn = hs.pubukprn 
                               AND c.kiscourseid = hs.kiscourseid 
                               AND c.kismode = hs.kismode)
            WHERE hs.sbj IS NOT NULL 
            AND hs.sbj != ''
        """)
        
        course_cah_mappings = cur.fetchall()
        logger.info(f"Found {len(course_cah_mappings)} courses with CAH codes")
        
        if len(course_cah_mappings) == 0:
            logger.warning("No courses with CAH codes found. This might be because:")
            logger.warning("1. HESA data import was not completed")
            logger.warning("2. No courses exist in the database yet")
            logger.warning("3. Courses don't have CAH code mappings")
            
            # Check if we have any courses at all
            cur.execute("SELECT COUNT(*) FROM course")
            total_courses = cur.fetchone()['count']
            logger.info(f"Total courses in database: {total_courses}")
            
            if total_courses == 0:
                logger.info("No courses found. Skipping course requirement creation.")
                logger.info("Run the full database setup to import courses first.")
            else:
                # Create some sample requirements for existing courses
                logger.info("Creating sample requirements for existing courses...")
                cur.execute("SELECT course_id, name FROM course LIMIT 50")
                sample_courses = cur.fetchall()
                
                for course in sample_courses:
                    # Create basic Math/English requirements for all courses
                    for subject_name, grade in [('Mathematics', 'B'), ('English Literature', 'C')]:
                        subject_id = subject_name.replace(" ", "_").replace("&", "and").lower()
                        req_id = f"{course['course_id'][:20]}_{subject_id[:20]}"
                        
                        cur.execute("""
                            INSERT INTO course_requirement (req_id, course_id, subject_id, grade_req)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (req_id) DO NOTHING
                        """, (req_id, course['course_id'], subject_id, grade))
                        requirements_created += 1
        else:
            # Process courses with CAH codes
            for course_mapping in course_cah_mappings:
                course_id = course_mapping['course_id']
                cah_code = course_mapping['cahcode']
                
                # Check if we have A-level requirements for this CAH code
                if cah_code in CAH_TO_ALEVEL_REQUIREMENTS:
                    alevel_requirements = CAH_TO_ALEVEL_REQUIREMENTS[cah_code]
                    
                    for subject_name in alevel_requirements:
                        # Convert to subject_id format
                        subject_id = subject_name.replace(" ", "_").replace("&", "and").lower()
                        
                        # Create requirement record using A-level subject as requirement
                        req_id = f"{course_id[:20]}_{subject_id[:20]}"
                        
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
                        """, (req_id, course_id, subject_id, grade_req))
                        
                        requirements_created += 1
                else:
                    # If no specific A-level mapping exists, create a general requirement
                    # based on the CAH code itself (for courses without clear A-level mappings)
                    req_id = f"{course_id[:20]}_{cah_code[-8:]}"
                    grade_req = 'B'  # Default for unmapped courses
                    
                    # Try to use the CAH code as subject_id if it exists in our subjects
                    cur.execute("SELECT subject_id FROM subject WHERE subject_id = %s", (cah_code,))
                    if cur.fetchone():
                        cur.execute("""
                            INSERT INTO course_requirement (req_id, course_id, subject_id, grade_req)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (req_id) DO NOTHING
                        """, (req_id, course_id, cah_code, grade_req))
                        
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
        
        logger.info("\nEnhanced subject-to-course mapping complete!")
        
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
        logger.info("Search functions created successfully!")
        
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