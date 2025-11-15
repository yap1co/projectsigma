"""
CSV Import Script for University Course Recommender
Imports University and Course data from CSV files into PostgreSQL
"""

import os
import sys
import csv
import uuid
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
import pandas as pd
from typing import Dict, List, Optional

# Database configuration
DB_NAME = os.getenv('POSTGRES_DB', 'university_recommender')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')


def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def generate_id(prefix: str = '') -> str:
    """Generate unique ID with optional prefix"""
    return f"{prefix}{uuid.uuid4().hex[:12]}" if prefix else uuid.uuid4().hex[:12]


def import_subjects(cursor, subjects_file: Optional[str] = None):
    """Import subjects from CSV or create default A-Level subjects"""
    print("\n" + "="*60)
    print("Importing Subjects")
    print("="*60)
    
    if subjects_file and Path(subjects_file).exists():
        df = pd.read_csv(subjects_file)
        print(f"  → Reading subjects from {subjects_file}")
        
        subjects = []
        for _, row in df.iterrows():
            subject_id = str(row.get('subject_id', generate_id('SUBJ_')))
            subject_name = str(row.get('subject_name', row.get('name', ''))).strip()
            
            if subject_name:
                subjects.append((subject_id, subject_name))
        
        if subjects:
            execute_values(
                cursor,
                """
                INSERT INTO subject (subject_id, subject_name)
                VALUES %s
                ON CONFLICT (subject_id) DO UPDATE
                SET subject_name = EXCLUDED.subject_name
                """,
                subjects
            )
            print(f"  ✓ Imported {len(subjects)} subjects")
    else:
        # Default A-Level subjects
        default_subjects = [
            ('SUBJ_MATH', 'Mathematics'),
            ('SUBJ_PHYS', 'Physics'),
            ('SUBJ_CHEM', 'Chemistry'),
            ('SUBJ_BIO', 'Biology'),
            ('SUBJ_CS', 'Computer Science'),
            ('SUBJ_ENG', 'English Literature'),
            ('SUBJ_HIST', 'History'),
            ('SUBJ_GEO', 'Geography'),
            ('SUBJ_ECON', 'Economics'),
            ('SUBJ_PSYCH', 'Psychology'),
            ('SUBJ_BUS', 'Business Studies'),
            ('SUBJ_ART', 'Art'),
            ('SUBJ_MUS', 'Music'),
            ('SUBJ_FRENCH', 'French'),
            ('SUBJ_SPAN', 'Spanish'),
            ('SUBJ_GERM', 'German'),
        ]
        
        execute_values(
            cursor,
            """
            INSERT INTO subject (subject_id, subject_name)
            VALUES %s
            ON CONFLICT (subject_id) DO NOTHING
            """,
            default_subjects
        )
        print(f"  ✓ Created {len(default_subjects)} default A-Level subjects")


def import_entrance_exams(cursor, exams_file: Optional[str] = None):
    """Import entrance exams from CSV or create default exams"""
    print("\n" + "="*60)
    print("Importing Entrance Exams")
    print("="*60)
    
    if exams_file and Path(exams_file).exists():
        df = pd.read_csv(exams_file)
        print(f"  → Reading exams from {exams_file}")
        
        exams = []
        for _, row in df.iterrows():
            exam_id = str(row.get('exam_id', generate_id('EXAM_')))
            exam_name = str(row.get('name', row.get('exam_name', ''))).strip()
            
            if exam_name:
                exams.append((exam_id, exam_name))
        
        if exams:
            execute_values(
                cursor,
                """
                INSERT INTO entrance_exam (exam_id, name)
                VALUES %s
                ON CONFLICT (exam_id) DO UPDATE
                SET name = EXCLUDED.name
                """,
                exams
            )
            print(f"  ✓ Imported {len(exams)} entrance exams")
    else:
        # Default entrance exams
        default_exams = [
            ('EXAM_MAT', 'Mathematics Admissions Test (MAT)'),
            ('EXAM_STEP', 'Sixth Term Examination Paper (STEP)'),
            ('EXAM_PAT', 'Physics Aptitude Test (PAT)'),
            ('EXAM_TSA', 'Thinking Skills Assessment (TSA)'),
            ('EXAM_BMAT', 'Biomedical Admissions Test (BMAT)'),
            ('EXAM_UKCAT', 'UK Clinical Aptitude Test (UKCAT)'),
            ('EXAM_LNAT', 'Law National Aptitude Test (LNAT)'),
        ]
        
        execute_values(
            cursor,
            """
            INSERT INTO entrance_exam (exam_id, name)
            VALUES %s
            ON CONFLICT (exam_id) DO NOTHING
            """,
            default_exams
        )
        print(f"  ✓ Created {len(default_exams)} default entrance exams")


def import_universities(cursor, universities_file: str):
    """Import universities from CSV file"""
    print("\n" + "="*60)
    print("Importing Universities")
    print("="*60)
    
    if not Path(universities_file).exists():
        print(f"  ✗ File not found: {universities_file}")
        return
    
    df = pd.read_csv(universities_file)
    print(f"  → Reading {len(df)} universities from {universities_file}")
    
    universities = []
    for _, row in df.iterrows():
        university_id = str(row.get('university_id', generate_id('UNIV_')))
        name = str(row.get('name', '')).strip()
        region = str(row.get('region', row.get('location', ''))).strip() or None
        rank_overall = int(row.get('rank_overall', row.get('ranking', 0))) if pd.notna(row.get('rank_overall', row.get('ranking', None))) else None
        employability_score = int(row.get('employability_score', row.get('employability', 0))) if pd.notna(row.get('employability_score', row.get('employability', None))) else None
        website_url = str(row.get('website_url', row.get('website', ''))).strip() or None
        
        if name:
            universities.append((university_id, name, region, rank_overall, employability_score, website_url))
    
    if universities:
        execute_values(
            cursor,
            """
            INSERT INTO university (university_id, name, region, rank_overall, employability_score, website_url)
            VALUES %s
            ON CONFLICT (university_id) DO UPDATE
            SET name = EXCLUDED.name,
                region = EXCLUDED.region,
                rank_overall = EXCLUDED.rank_overall,
                employability_score = EXCLUDED.employability_score,
                website_url = EXCLUDED.website_url
            """,
            universities
        )
        print(f"  ✓ Imported {len(universities)} universities")
    else:
        print("  ✗ No valid universities found in CSV")


def import_courses(cursor, courses_file: str):
    """Import courses from CSV file"""
    print("\n" + "="*60)
    print("Importing Courses")
    print("="*60)
    
    if not Path(courses_file).exists():
        print(f"  ✗ File not found: {courses_file}")
        return
    
    df = pd.read_csv(courses_file)
    print(f"  → Reading {len(df)} courses from {courses_file}")
    
    # Import courses
    courses = []
    course_university_map = {}  # Track course_id -> university_id mapping
    
    for _, row in df.iterrows():
        course_id = str(row.get('course_id', generate_id('COURSE_')))
        university_id = str(row.get('university_id', '')).strip()
        ucas_code = str(row.get('ucas_code', row.get('ucas', ''))).strip() or None
        name = str(row.get('name', row.get('course_name', ''))).strip()
        annual_fee = int(row.get('annual_fee', row.get('fee', row.get('uk_fees', 0)))) if pd.notna(row.get('annual_fee', row.get('fee', row.get('uk_fees', None)))) else None
        subject_rank = int(row.get('subject_rank', row.get('subject_ranking', 0))) if pd.notna(row.get('subject_rank', row.get('subject_ranking', None))) else None
        employability_score = int(row.get('employability_score', row.get('employability', 0))) if pd.notna(row.get('employability_score', row.get('employability', None))) else None
        course_url = str(row.get('course_url', row.get('url', ''))).strip() or None
        typical_offer_text = str(row.get('typical_offer_text', row.get('typical_offer', ''))).strip() or None
        typical_offer_tariff = int(row.get('typical_offer_tariff', row.get('tariff', 0))) if pd.notna(row.get('typical_offer_tariff', row.get('tariff', None))) else None
        
        if name and university_id:
            courses.append((course_id, university_id, ucas_code, name, annual_fee, subject_rank, employability_score, course_url, typical_offer_text, typical_offer_tariff))
            course_university_map[course_id] = university_id
    
    if courses:
        execute_values(
            cursor,
            """
            INSERT INTO course (course_id, university_id, ucas_code, name, annual_fee, subject_rank, employability_score, course_url, typical_offer_text, typical_offer_tariff)
            VALUES %s
            ON CONFLICT (course_id) DO UPDATE
            SET university_id = EXCLUDED.university_id,
                ucas_code = EXCLUDED.ucas_code,
                name = EXCLUDED.name,
                annual_fee = EXCLUDED.annual_fee,
                subject_rank = EXCLUDED.subject_rank,
                employability_score = EXCLUDED.employability_score,
                course_url = EXCLUDED.course_url,
                typical_offer_text = EXCLUDED.typical_offer_text,
                typical_offer_tariff = EXCLUDED.typical_offer_tariff
            """,
            courses
        )
        print(f"  ✓ Imported {len(courses)} courses")
        
        # Import course requirements (if present in CSV)
        import_course_requirements(cursor, df, course_university_map)
        
        # Import course required exams (if present in CSV)
        import_course_exams(cursor, df, course_university_map)
    else:
        print("  ✗ No valid courses found in CSV")


def import_course_requirements(cursor, df: pd.DataFrame, course_map: Dict[str, str]):
    """Import course requirements from courses CSV"""
    print("\n  → Processing course requirements...")
    
    requirements = []
    req_count = 0
    
    for _, row in df.iterrows():
        course_id = str(row.get('course_id', ''))
        if not course_id or course_id not in course_map:
            continue
        
        # Check for subject requirements columns
        # Format: "required_subjects" or "subjects" (comma-separated)
        # Format: "required_grades" or "grades" (comma-separated or JSON)
        subjects_str = str(row.get('required_subjects', row.get('subjects', ''))).strip()
        grades_str = str(row.get('required_grades', row.get('grades', ''))).strip()
        
        if subjects_str:
            subject_list = [s.strip() for s in subjects_str.split(',') if s.strip()]
            grade_list = [g.strip() for g in grades_str.split(',') if g.strip()] if grades_str else []
            
            for idx, subject_name in enumerate(subject_list):
                # Look up subject_id by name
                cursor.execute(
                    "SELECT subject_id FROM subject WHERE LOWER(subject_name) = LOWER(%s)",
                    (subject_name,)
                )
                subject_result = cursor.fetchone()
                
                if subject_result:
                    subject_id = subject_result[0]
                    grade_req = grade_list[idx] if idx < len(grade_list) else 'B'  # Default grade
                    
                    req_id = generate_id('REQ_')
                    requirements.append((req_id, course_id, subject_id, grade_req))
                    req_count += 1
    
    if requirements:
        execute_values(
            cursor,
            """
            INSERT INTO course_requirement (req_id, course_id, subject_id, grade_req)
            VALUES %s
            ON CONFLICT (req_id) DO NOTHING
            """,
            requirements
        )
        print(f"  ✓ Imported {req_count} course requirements")
    else:
        print("  ⊙ No course requirements found in CSV")


def import_course_exams(cursor, df: pd.DataFrame, course_map: Dict[str, str]):
    """Import course required exams from courses CSV"""
    print("\n  → Processing course required exams...")
    
    course_exams = []
    exam_count = 0
    
    for _, row in df.iterrows():
        course_id = str(row.get('course_id', ''))
        if not course_id or course_id not in course_map:
            continue
        
        # Check for required_exams column (comma-separated exam names)
        exams_str = str(row.get('required_exams', row.get('entrance_exams', ''))).strip()
        
        if exams_str:
            exam_list = [e.strip() for e in exams_str.split(',') if e.strip()]
            
            for exam_name in exam_list:
                # Look up exam_id by name
                cursor.execute(
                    "SELECT exam_id FROM entrance_exam WHERE LOWER(name) LIKE LOWER(%s)",
                    (f'%{exam_name}%',)
                )
                exam_result = cursor.fetchone()
                
                if exam_result:
                    exam_id = exam_result[0]
                    course_exams.append((course_id, exam_id))
                    exam_count += 1
    
    if course_exams:
        execute_values(
            cursor,
            """
            INSERT INTO course_required_exam (course_id, exam_id)
            VALUES %s
            ON CONFLICT (course_id, exam_id) DO NOTHING
            """,
            course_exams
        )
        print(f"  ✓ Imported {exam_count} course-exam relationships")
    else:
        print("  ⊙ No course required exams found in CSV")


def main():
    """Main import function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import CSV data into PostgreSQL')
    parser.add_argument('--universities', type=str, help='Path to universities CSV file')
    parser.add_argument('--courses', type=str, help='Path to courses CSV file')
    parser.add_argument('--subjects', type=str, help='Path to subjects CSV file (optional)')
    parser.add_argument('--exams', type=str, help='Path to entrance exams CSV file (optional)')
    parser.add_argument('--data-dir', type=str, default='./data', help='Directory containing CSV files')
    
    args = parser.parse_args()
    
    print("="*60)
    print("CSV Data Import Tool")
    print("="*60)
    
    # Determine file paths
    data_dir = Path(args.data_dir)
    universities_file = args.universities or data_dir / 'universities.csv'
    courses_file = args.courses or data_dir / 'courses.csv'
    subjects_file = args.subjects or data_dir / 'subjects.csv' if (data_dir / 'subjects.csv').exists() else None
    exams_file = args.exams or data_dir / 'exams.csv' if (data_dir / 'exams.csv').exists() else None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Import in order: subjects, exams, universities, courses
        import_subjects(cursor, subjects_file)
        import_entrance_exams(cursor, exams_file)
        
        if Path(universities_file).exists():
            import_universities(cursor, str(universities_file))
        else:
            print(f"\n⚠ Universities file not found: {universities_file}")
            print("  Skipping university import")
        
        if Path(courses_file).exists():
            import_courses(cursor, str(courses_file))
        else:
            print(f"\n⚠ Courses file not found: {courses_file}")
            print("  Skipping course import")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("✓ Import completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error during import: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

