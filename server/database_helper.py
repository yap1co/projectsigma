"""
Database helper functions for PostgreSQL connection and utilities
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import uuid
from typing import Optional, Dict, Any

def get_db_connection():
    """Get PostgreSQL database connection"""
    # Load .env file if not already loaded
    from dotenv import load_dotenv
    from pathlib import Path
    
    # Try loading from server/.env first
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try server/database/.env
        db_env_path = Path(__file__).parent / 'database' / '.env'
        if db_env_path.exists():
            load_dotenv(db_env_path)
        else:
            # Fallback to current directory
            load_dotenv()
    
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'university_recommender'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )

def generate_id(prefix: str = '') -> str:
    """Generate a unique ID with optional prefix"""
    unique_id = str(uuid.uuid4()).replace('-', '')[:16]
    return f"{prefix}{unique_id}" if prefix else unique_id

def get_student_by_id(cursor, student_id: str) -> Optional[Dict[str, Any]]:
    """Get student by ID with all related data"""
    cursor.execute("""
        SELECT 
            s.student_id, s.display_name, s.email, s.password_hash,
            s.created_at, s.region, s.tuition_budget, s.preferred_exams,
            s.preferences
        FROM uni_recomm_student s
        WHERE s.student_id = %s
    """, (student_id,))
    
    row = cursor.fetchone()
    if not row:
        return None
    
    student = dict(row)
    
    # Get student grades
    cursor.execute("""
        SELECT sg.subject_id, sg.predicted_grade, sub.subject_name
        FROM uni_recomm_student_grade sg
        JOIN uni_recomm_subject sub ON sg.subject_id = sub.subject_id
        WHERE sg.student_id = %s
    """, (student_id,))
    
    grades = {}
    subjects = []
    for row in cursor.fetchall():
        grade_row = dict(row)
        subject_id = grade_row['subject_id']
        grades[subject_id] = grade_row['predicted_grade']
        subjects.append(subject_id)
    
    student['aLevelSubjects'] = subjects
    student['predictedGrades'] = grades
    
    # Build preferences dict - merge stored preferences with legacy fields
    stored_preferences = student.get('preferences') or {}
    if not isinstance(stored_preferences, dict):
        stored_preferences = {}
    
    # Merge stored preferences with legacy fields (for backward compatibility)
    student['preferences'] = {
        'preferredRegion': stored_preferences.get('preferredRegion') or student.get('region'),
        'maxBudget': stored_preferences.get('maxBudget') or student.get('tuition_budget'),
        'preferredExams': stored_preferences.get('preferredExams') or student.get('preferred_exams', []),
        'careerInterests': stored_preferences.get('careerInterests', [])
    }
    
    # Add firstName and lastName from display_name
    name_parts = student['display_name'].split(' ', 1)
    student['firstName'] = name_parts[0] if name_parts else ''
    student['lastName'] = name_parts[1] if len(name_parts) > 1 else ''
    
    return student

def get_student_by_email(cursor, email: str) -> Optional[Dict[str, Any]]:
    """Get student by email"""
    cursor.execute("SELECT student_id FROM uni_recomm_student WHERE email = %s", (email,))
    row = cursor.fetchone()
    if not row:
        return None
    
    # RealDictCursor returns a dict, not a tuple
    student_id = row['student_id'] if isinstance(row, dict) else row[0]
    return get_student_by_id(cursor, student_id)
