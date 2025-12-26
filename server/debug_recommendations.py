#!/usr/bin/env python3
"""
Debug script for testing recommendation logic
Run with: python debug_recommendations.py
"""

import sys
import os

# Ensure we're using the correct virtual environment
def activate_venv():
    """Activate virtual environment programmatically"""
    venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'venv')
    
    if os.path.exists(venv_path):
        # Add venv packages to Python path
        site_packages = os.path.join(venv_path, 'Lib', 'site-packages')
        if site_packages not in sys.path:
            sys.path.insert(0, site_packages)
        
        # Set virtual env
        os.environ['VIRTUAL_ENV'] = venv_path
        os.environ['PATH'] = os.path.join(venv_path, 'Scripts') + os.pathsep + os.environ.get('PATH', '')
        
        print(f' Activated virtual environment: {venv_path}')
    else:
        print(f'  Virtual environment not found at: {venv_path}')

# Activate venv first
activate_venv()

from recommendation_engine import RecommendationEngine
from database_helper import get_db_connection
import json

def debug_recommendations():
    print('=== DEBUGGING RECOMMENDATION SYSTEM ===')
    engine = RecommendationEngine()
    
    # Test case: Your exact profile
    subjects = ['Physics', 'Mathematics', 'Computer Science']
    grades = {'Physics': 'A', 'Mathematics': 'A*', 'Computer Science': 'A'}
    preferences = {'careerInterests': ['Engineering & Technology']}
    criteria = {}
    
    print(f'Subjects: {subjects}')
    print(f'Grades: {grades}')
    print(f'Career Interest: {preferences["careerInterests"]}')
    
    print('\n=== TEST 1: WITH CAREER FILTER ===')
    recommendations = engine.get_recommendations(
        a_level_subjects=subjects,
        predicted_grades=grades,
        preferences=preferences,
        criteria=criteria
    )
    
    print(f'RESULTS: {len(recommendations)} recommendations')
    print(f'TYPE: {type(recommendations)}')
    if recommendations:
        print(f'FIRST COURSE: {recommendations[0]["course"]["name"]}')
        print(f'FIRST UNI: {recommendations[0]["course"]["university"]["name"]}')
    
    print(f'Total recommendations: {len(recommendations)}')
    
    if recommendations:
        print('\n=== TOP 10 RESULTS ===')
        universities = {}
        for i, rec in enumerate(recommendations[:10]):
            course = rec.get('course', {})
            course_name = course.get('name', 'Unknown')
            uni_name = course.get('university', {}).get('name', 'Unknown')
            score = rec.get('matchScore', 0)
            
            # Count universities
            universities[uni_name] = universities.get(uni_name, 0) + 1
            
            print(f'{i+1}. {course_name}')
            print(f'    University: {uni_name}')
            print(f'    Score: {score:.3f}')
            print()
        
        print('=== UNIVERSITY DISTRIBUTION ===')
        for uni, count in sorted(universities.items(), key=lambda x: x[1], reverse=True):
            print(f'{uni}: {count} courses')
    
    print('\n=== TEST 2: WITHOUT CAREER FILTER ===')
    recs_no_filter = engine.get_recommendations(
        a_level_subjects=subjects,
        predicted_grades=grades,
        preferences={},
        criteria={}
    )
    print(f'Without career filter: {len(recs_no_filter)} recommendations')
    
    if recs_no_filter:
        print('\nFirst 10 without filter:')
        universities_no_filter = {}
        for i, rec in enumerate(recs_no_filter[:10]):
            course = rec.get('course', {})
            course_name = course.get('name', 'Unknown')
            uni_name = course.get('university', {}).get('name', 'Unknown')
            score = rec.get('matchScore', 0)
            
            universities_no_filter[uni_name] = universities_no_filter.get(uni_name, 0) + 1
            
            print(f'{i+1}. {course_name} at {uni_name} (Score: {score:.3f})')
        
        print('\nUniversity distribution (no filter):')
        for uni, count in sorted(universities_no_filter.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f'{uni}: {count} courses')

def debug_career_mapping():
    print('\n=== CAREER MAPPING DEBUG ===')
    engine = RecommendationEngine()
    
    # Check the career mapping
    course_career_mapping = engine._get_course_career_mapping()
    print(f'Total courses in career mapping: {len(course_career_mapping)}')
    
    # Check how many are Engineering & Technology
    eng_tech_courses = []
    for course_id, careers in course_career_mapping.items():
        if 'Engineering & Technology' in careers:
            eng_tech_courses.append(course_id)
    
    print(f'Courses mapped to Engineering & Technology: {len(eng_tech_courses)}')
    
    # Check what careers Computer Science courses are mapped to
    comp_sci_careers = []
    for course_id, careers in course_career_mapping.items():
        if 'computer' in course_id.lower() or 'computing' in course_id.lower():
            comp_sci_careers.append((course_id, list(careers)))
            if len(comp_sci_careers) >= 5:
                break
    
    print('\nSample Computer Science course career mappings:')
    for course_id, careers in comp_sci_careers:
        print(f'{course_id}: {careers}')

def debug_database():
    print('\n=== DATABASE DEBUG ===')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total_courses FROM course")
    total_courses = cursor.fetchone()[0]
    print(f'Total courses in database: {total_courses}')
    
    cursor.execute("SELECT COUNT(DISTINCT university_id) as total_unis FROM course")
    total_unis = cursor.fetchone()[0]
    print(f'Total universities: {total_unis}')
    
    cursor.execute("""
        SELECT u.name, COUNT(*) as course_count 
        FROM course c 
        JOIN university u ON c.university_id = u.university_id 
        GROUP BY u.name 
        ORDER BY course_count DESC 
        LIMIT 10
    """)
    top_unis = cursor.fetchall()
    print('\nTop universities by course count:')
    for uni_name, count in top_unis:
        print(f'{uni_name}: {count} courses')
    
    # Check subject distribution
    cursor.execute("""
        SELECT s.subject_name, COUNT(*) as course_count
        FROM course_requirement cr
        JOIN subject s ON cr.subject_id = s.subject_id
        WHERE s.subject_name IN ('Physics', 'Mathematics', 'Computer Science', 'Computing')
        GROUP BY s.subject_name
        ORDER BY course_count DESC
    """)
    subject_counts = cursor.fetchall()
    print('\nCourses requiring your subjects:')
    for subject, count in subject_counts:
        print(f'{subject}: {count} courses')
    
    cursor.close()
    conn.close()

def main():
    """Main debug function - run all tests"""
    # Check Python environment
    import sys
    print(f'Python executable: {sys.executable}')
    print(f'Python path: {sys.path[0]}')
    if 'venv' in sys.executable:
        print('Using virtual environment')
    else:
        print('WARNING: Not using virtual environment!')
    print()
    
    debug_recommendations()
    debug_career_mapping()
    debug_database()
    
    print('\n=== SUMMARY ===')
    print('1. If career filter returns 0: Career mapping issue')
    print('2. If all courses from same uni: Database diversity issue')
    print('3. Check career mappings for Computer Science courses')

if __name__ == '__main__':
    main()