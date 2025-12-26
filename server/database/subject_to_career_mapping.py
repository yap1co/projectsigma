"""
Map HESA CAH (Common Aggregation Hierarchy) codes to career interests.
This uses the official UK government subject classification system.
"""

def get_cah_to_career_mapping():
    """
    Map CAH subject codes to our career interests.
    Based on HESA official classification system.
    """
    
    return {
        # Medicine & Healthcare
        'CAH01': 'Medicine & Healthcare',  # Medicine & dentistry
        'CAH02': 'Medicine & Healthcare',  # Subjects allied to medicine  
        'CAH03': 'Sciences',  # Biological sciences
        
        # Sciences & Agriculture
        'CAH04': 'Sciences',  # Veterinary science
        'CAH05': 'Sciences',  # Agriculture & related subjects
        'CAH06': 'Sciences',  # Physical sciences
        'CAH07': 'Engineering & Technology',  # Mathematical sciences
        
        # Engineering  
        'CAH09': 'Engineering & Technology',  # Architecture, building & planning
        
        # Social Studies  
        'CAH10': 'Social Sciences',  # Social studies
        'CAH11': 'Creative Arts',  # Mass communications & documentation
        'CAH13': 'Arts & Humanities',  # Historical and philosophical studies
        
        # Education
        'CAH15': 'Education',  # Education
        
        # Combined Studies (includes Law)
        'CAH16': 'Law',  # Combined studies (contains law courses)
        'CAH17': 'Business & Finance',  # Business & administrative studies
        
        # Computing
        'CAH19': 'Engineering & Technology',  # Computing
        'CAH20': 'Arts & Humanities',  # Humanities (general)
        
        # Additional Categories  
        'CAH22': 'Sciences',  # Sciences  
        'CAH23': 'Engineering & Technology',  # Engineering
        'CAH24': 'Creative Arts',  # Creative arts
        'CAH25': 'Creative Arts',  # Media, journalism and communications
        'CAH26': 'Sports & Fitness',  # Sport and exercise sciences
    }

def create_subject_to_career_table():
    """Create the CAH to career mapping table and populate it"""
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import database_helper as db
    
    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create mapping table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subject_to_career (
                id SERIAL PRIMARY KEY,
                cah_code VARCHAR(10) NOT NULL UNIQUE,
                career_interest_name VARCHAR(100) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Clear and populate
        cursor.execute("DELETE FROM subject_to_career")
        
        mapping = get_cah_to_career_mapping()
        
        for cah_code, career in mapping.items():
            cursor.execute("""
                INSERT INTO subject_to_career (cah_code, career_interest_name)
                VALUES (%s, %s)
            """, (cah_code, career))
        
        conn.commit()
        print(f"Successfully mapped {len(mapping)} CAH codes to career interests")
        
        # Show mapping stats
        cursor.execute("""
            SELECT career_interest_name, COUNT(*) as cah_count
            FROM subject_to_career
            GROUP BY career_interest_name  
            ORDER BY cah_count DESC
        """)
        
        print("\\nCareer interest distribution:")
        for career, count in cursor.fetchall():
            print(f"- {career}: {count} CAH categories")
            
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

def get_course_career_interests(course_id):
    """
    Get career interests for a course using the CAH mapping
    """
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import database_helper as db
    
    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get career interests via CAH codes
        cursor.execute("""
            SELECT DISTINCT ccm.career_interest_name
            FROM hesa_sbj s
            JOIN subject_to_career ccm ON (
                ccm.cah_code = SUBSTRING(s.sbj FROM 1 FOR 5)
            )
            WHERE s.kiscourseid = %s
        """, (course_id,))
        
        return [row[0] for row in cursor.fetchall()]
        
    except Exception as e:
        print(f"Error getting course career interests: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def analyze_course_career_distribution():
    """Analyze how courses are distributed across career interests"""
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import database_helper as db
    
    conn = db.get_db_connection()  
    cursor = conn.cursor()
    
    try:
        # Count courses per career interest via CAH mapping
        cursor.execute("""
            SELECT 
                ccm.career_interest_name,
                COUNT(DISTINCT s.kiscourseid) as course_count
            FROM hesa_sbj s
            JOIN subject_to_career ccm ON (
                ccm.cah_code = SUBSTRING(s.sbj FROM 1 FOR 5)  
            )
            JOIN hesa_kiscourse k ON k.kiscourseid = s.kiscourseid
            WHERE k.title IS NOT NULL
            GROUP BY ccm.career_interest_name
            ORDER BY course_count DESC
        """)
        
        print("Course distribution by career interest (via CAH mapping):")
        total_courses = 0
        for career, count in cursor.fetchall():
            print(f"- {career}: {count:,} courses")
            total_courses += count
            
        print(f"\\nTotal mapped courses: {total_courses:,}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Creating CAH-to-career interest mapping...")
    create_subject_to_career_table()
    print("\\nAnalyzing course distribution...")
    analyze_course_career_distribution()