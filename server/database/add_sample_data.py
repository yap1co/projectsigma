"""
Add sample universities and courses to the database for testing
This creates realistic UK university data with courses and requirements
"""

import sys
from pathlib import Path

# Add parent directory to path to import database_helper
sys.path.insert(0, str(Path(__file__).parent.parent))

from database_helper import get_db_connection, generate_id
from psycopg2.extras import RealDictCursor

# Sample UK Universities
SAMPLE_UNIVERSITIES = [
    {"name": "University of Oxford", "region": "South East", "rank": 1, "employability": 95},
    {"name": "University of Cambridge", "region": "East of England", "rank": 2, "employability": 94},
    {"name": "Imperial College London", "region": "London", "rank": 3, "employability": 93},
    {"name": "London School of Economics", "region": "London", "rank": 4, "employability": 92},
    {"name": "University of Edinburgh", "region": "Scotland", "rank": 5, "employability": 91},
    {"name": "University of Manchester", "region": "North West", "rank": 6, "employability": 90},
    {"name": "University College London", "region": "London", "rank": 7, "employability": 89},
    {"name": "King's College London", "region": "London", "rank": 8, "employability": 88},
    {"name": "University of Bristol", "region": "South West", "rank": 9, "employability": 87},
    {"name": "University of Warwick", "region": "Midlands", "rank": 10, "employability": 86},
    {"name": "University of Leeds", "region": "North East", "rank": 11, "employability": 85},
    {"name": "University of Birmingham", "region": "Midlands", "rank": 12, "employability": 84},
    {"name": "University of Nottingham", "region": "Midlands", "rank": 13, "employability": 83},
    {"name": "University of Southampton", "region": "South East", "rank": 14, "employability": 82},
    {"name": "University of York", "region": "North East", "rank": 15, "employability": 81},
    {"name": "Durham University", "region": "North East", "rank": 16, "employability": 80},
    {"name": "University of Exeter", "region": "South West", "rank": 17, "employability": 79},
    {"name": "University of Liverpool", "region": "North West", "rank": 18, "employability": 78},
    {"name": "University of Newcastle", "region": "North East", "rank": 19, "employability": 77},
    {"name": "University of Sheffield", "region": "North East", "rank": 20, "employability": 76},
    {"name": "Cardiff University", "region": "Wales", "rank": 21, "employability": 75},
    {"name": "University of Glasgow", "region": "Scotland", "rank": 22, "employability": 74},
    {"name": "Queen Mary University of London", "region": "London", "rank": 23, "employability": 73},
    {"name": "University of Reading", "region": "South East", "rank": 24, "employability": 72},
    {"name": "Loughborough University", "region": "Midlands", "rank": 25, "employability": 71},
]

# Sample Courses with entry requirements
SAMPLE_COURSES = [
    # Computer Science courses
    {"name": "Computer Science", "subjects": ["Mathematics", "Computer Science"], "grades": {"Mathematics": "A", "Computer Science": "A"}, "fee": 9250},
    {"name": "Computer Science", "subjects": ["Mathematics"], "grades": {"Mathematics": "A*"}, "fee": 9250},
    {"name": "Computer Science", "subjects": ["Mathematics", "Physics"], "grades": {"Mathematics": "A", "Physics": "B"}, "fee": 9250},
    {"name": "Computer Science", "subjects": ["Mathematics"], "grades": {"Mathematics": "A"}, "fee": 9250},
    {"name": "Computer Science", "subjects": ["Mathematics"], "grades": {"Mathematics": "B"}, "fee": 9250},
    
    # Mathematics courses
    {"name": "Mathematics", "subjects": ["Mathematics", "Further Mathematics"], "grades": {"Mathematics": "A*", "Further Mathematics": "A*"}, "fee": 9250},
    {"name": "Mathematics", "subjects": ["Mathematics"], "grades": {"Mathematics": "A"}, "fee": 9250},
    {"name": "Mathematics", "subjects": ["Mathematics"], "grades": {"Mathematics": "B"}, "fee": 9250},
    
    # Physics courses
    {"name": "Physics", "subjects": ["Mathematics", "Physics"], "grades": {"Mathematics": "A", "Physics": "A"}, "fee": 9250},
    {"name": "Physics", "subjects": ["Mathematics", "Physics"], "grades": {"Mathematics": "A", "Physics": "B"}, "fee": 9250},
    {"name": "Physics", "subjects": ["Mathematics"], "grades": {"Mathematics": "B"}, "fee": 9250},
    
    # Engineering courses
    {"name": "Mechanical Engineering", "subjects": ["Mathematics", "Physics"], "grades": {"Mathematics": "A", "Physics": "B"}, "fee": 9250},
    {"name": "Electrical Engineering", "subjects": ["Mathematics", "Physics"], "grades": {"Mathematics": "A", "Physics": "B"}, "fee": 9250},
    {"name": "Civil Engineering", "subjects": ["Mathematics", "Physics"], "grades": {"Mathematics": "B", "Physics": "B"}, "fee": 9250},
    
    # Business/Economics courses
    {"name": "Economics", "subjects": ["Mathematics"], "grades": {"Mathematics": "A"}, "fee": 9250},
    {"name": "Business Studies", "subjects": [], "grades": {}, "fee": 9250},
    {"name": "Accounting and Finance", "subjects": ["Mathematics"], "grades": {"Mathematics": "B"}, "fee": 9250},
    
    # Science courses
    {"name": "Chemistry", "subjects": ["Chemistry", "Mathematics"], "grades": {"Chemistry": "A", "Mathematics": "B"}, "fee": 9250},
    {"name": "Biology", "subjects": ["Biology", "Chemistry"], "grades": {"Biology": "A", "Chemistry": "B"}, "fee": 9250},
    {"name": "Biochemistry", "subjects": ["Chemistry", "Biology"], "grades": {"Chemistry": "A", "Biology": "B"}, "fee": 9250},
]

def add_sample_data():
    """Add sample universities and courses to the database"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # First, ensure subjects exist
        print("Creating subjects...")
        subjects_map = {}
        all_subjects = set()
        for course in SAMPLE_COURSES:
            all_subjects.update(course.get("subjects", []))
        
        for subject_name in all_subjects:
            if subject_name:
                # Check if subject already exists by name
                cur.execute("SELECT subject_id FROM subject WHERE subject_name = %s", (subject_name,))
                existing = cur.fetchone()
                if existing:
                    subject_id = existing['subject_id']
                else:
                    subject_id = subject_name.replace(" ", "_").replace("&", "and")
                    cur.execute("""
                        INSERT INTO subject (subject_id, subject_name)
                        VALUES (%s, %s)
                        ON CONFLICT (subject_id) DO NOTHING
                    """, (subject_id, subject_name))
                subjects_map[subject_name] = subject_id
        
        conn.commit()
        print(f"OK: Created/Found {len(subjects_map)} subjects")
        
        # Add universities
        print("\nAdding universities...")
        university_map = {}
        for uni in SAMPLE_UNIVERSITIES:
            uni_id = generate_id('UNIV_')
            cur.execute("""
                INSERT INTO university (university_id, name, region, rank_overall, employability_score)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (university_id) DO UPDATE
                SET name = EXCLUDED.name, region = EXCLUDED.region,
                    rank_overall = EXCLUDED.rank_overall, employability_score = EXCLUDED.employability_score
            """, (uni_id, uni["name"], uni["region"], uni["rank"], uni["employability"]))
            university_map[uni["name"]] = uni_id
        
        conn.commit()
        print(f"OK: Added {len(university_map)} universities")
        
        # Add courses
        print("\nAdding courses...")
        course_count = 0
        for uni in SAMPLE_UNIVERSITIES:
            uni_id = university_map[uni["name"]]
            
            # Add 2-3 courses per university
            courses_for_uni = SAMPLE_COURSES[:3] if course_count < len(SAMPLE_COURSES) else SAMPLE_COURSES[course_count % len(SAMPLE_COURSES):course_count % len(SAMPLE_COURSES) + 2]
            
            for course_data in courses_for_uni:
                course_id = generate_id('COURSE_')
                course_name = course_data["name"]
                
                cur.execute("""
                    INSERT INTO course (course_id, university_id, name, annual_fee, employability_score)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (course_id) DO UPDATE
                    SET name = EXCLUDED.name, annual_fee = EXCLUDED.annual_fee
                """, (course_id, uni_id, f"{course_name} - {uni['name']}", course_data["fee"], uni["employability"] - 5))
                
                # Add entry requirements
                for subject_name in course_data.get("subjects", []):
                    if subject_name in subjects_map:
                        subject_id = subjects_map[subject_name]
                        grade_req = course_data.get("grades", {}).get(subject_name, "B")
                        
                        req_id = generate_id('REQ_')
                        cur.execute("""
                            INSERT INTO course_requirement (req_id, course_id, subject_id, grade_req)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (req_id) DO NOTHING
                        """, (req_id, course_id, subject_id, grade_req))
                
                course_count += 1
                if course_count >= 50:  # Limit to 50 courses total
                    break
            
            if course_count >= 50:
                break
        
        conn.commit()
        print(f"OK: Added {course_count} courses with entry requirements")
        
        # Verify counts
        cur.execute("SELECT COUNT(*) as count FROM university")
        uni_count = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) as count FROM course")
        course_count_db = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) as count FROM course_requirement")
        req_count = cur.fetchone()['count']
        
        print("\n" + "="*60)
        print("Database Summary:")
        print(f"  Universities: {uni_count}")
        print(f"  Courses: {course_count_db}")
        print(f"  Course Requirements: {req_count}")
        print("="*60)
        
        cur.close()
        conn.close()
        
        print("\nOK: Sample data added successfully!")
        print("You should now be able to get recommendations!")
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR: Error adding sample data: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    print("="*60)
    print("Adding Sample Universities and Courses")
    print("="*60)
    add_sample_data()
