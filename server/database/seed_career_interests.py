"""
Seed career_interest and entrance_exam tables with standard data.
Matches ProfileSetup.tsx frontend categories.
"""

import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def seed_career_interests():
    """Populate career_interest table with standard categories."""
    
    # Require password to be set explicitly
    db_password = os.getenv('POSTGRES_PASSWORD')
    if not db_password:
        raise RuntimeError(
            "POSTGRES_PASSWORD environment variable is not set. "
            "Please create server/.env file with database credentials."
        )
    
    # Career interests matching frontend
    career_interests = [
        ('healthcare', 'Medicine & Healthcare'),
        ('engineering', 'Engineering & Technology'),
        ('business', 'Business & Finance'),
        ('law', 'Law'),
        ('education', 'Education'),
        ('humanities', 'Arts & Humanities'),
        ('sciences', 'Sciences'),
        ('social_sciences', 'Social Sciences'),
        ('creative_arts', 'Creative Arts'),
        ('sports', 'Sports & Fitness')
    ]
    
    # Entrance exams (common UK qualifications)
    entrance_exams = [
        ('a_level', 'A-Level'),
        ('btec', 'BTEC'),
        ('ib', 'International Baccalaureate'),
        ('scottish_highers', 'Scottish Highers'),
        ('access_course', 'Access Course')
    ]
    
    conn = psycopg2.connect(
        dbname="university_recommender",
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=db_password,
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )
    
    try:
        cur = conn.cursor()
        
        print("Seeding career_interest table...")
        
        for career_id, career_name in career_interests:
            cur.execute("""
                INSERT INTO career_interest (career_interest_id, name)
                VALUES (%s, %s)
                ON CONFLICT (career_interest_id) DO NOTHING
            """, (career_id, career_name))
            print(f"  Added career: {career_name}")
        
        print("\nSeeding entrance_exam table...")
        
        for exam_id, exam_name in entrance_exams:
            cur.execute("""
                INSERT INTO entrance_exam (exam_id, name)
                VALUES (%s, %s)
                ON CONFLICT (exam_id) DO NOTHING
            """, (exam_id, exam_name))
            print(f"  Added exam: {exam_name}")
        
        conn.commit()
        print(f"\nSuccessfully seeded {len(career_interests)} career interests and {len(entrance_exams)} entrance exams")
        
        # Verify
        cur.execute("SELECT COUNT(*) FROM career_interest")
        career_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM entrance_exam")
        exam_count = cur.fetchone()[0]
        print(f"Total in database - Career interests: {career_count}, Entrance exams: {exam_count}")
        
        cur.close()
        
    except Exception as e:
        conn.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    seed_career_interests()
