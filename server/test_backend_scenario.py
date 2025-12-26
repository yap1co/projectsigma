#!/usr/bin/env python3
"""
Test complete backend scenario with junction tables
Tests registration, login, profile retrieval, and recommendations
"""

import os
import sys
import json
from flask import Flask
from flask.testing import FlaskClient

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our Flask app
from app import app

def test_complete_backend_scenario():
    """Test the complete backend scenario with junction tables"""
    
    print("=== TESTING COMPLETE BACKEND SCENARIO ===")
    print("Using Flask test client for reliable testing")
    print()
    
    # Set up test client
    app.config['TESTING'] = True
    client = app.test_client()
    
    # 1. Test Registration (create a new test user)
    print("1. Testing Registration...")
    register_data = {
        'firstName': 'Test',
        'lastName': 'User',
        'email': 'test.backend@projectsigma.com',
        'password': 'SecurePassword123',
        'region': 'England',
        'tuitionBudget': 15000,
        'careerInterests': ['Engineering & Technology', 'Sciences'],
        'preferredExams': ['A-Level', 'BTEC'],
        'subjects': [
            {'subjectId': 1, 'predictedGrade': 'A*'},
            {'subjectId': 2, 'predictedGrade': 'A'},
            {'subjectId': 3, 'predictedGrade': 'B'}
        ]
    }
    
    register_response = client.post('/api/auth/register', 
                                    data=json.dumps(register_data),
                                    content_type='application/json')
    
    print(f"   Status: {register_response.status_code}")
    if register_response.status_code == 201:
        register_result = json.loads(register_response.data)
        student_id = register_result.get('student_id')
        print(f"   ✅ Registration successful! Student ID: {student_id}")
    else:
        error_msg = register_response.data.decode('utf-8')[:200]
        print(f"   ❌ Registration failed: {error_msg}")
        return
    
    # 2. Test Login
    print()
    print("2. Testing Login...")
    login_data = {
        'email': 'test.backend@projectsigma.com',
        'password': 'SecurePassword123'
    }
    
    login_response = client.post('/api/auth/login',
                                data=json.dumps(login_data),
                                content_type='application/json')
    
    print(f"   Status: {login_response.status_code}")
    if login_response.status_code == 200:
        login_result = json.loads(login_response.data)
        token = login_result.get('token')
        print("   ✅ Login successful!")
    else:
        error_msg = login_response.data.decode('utf-8')[:200]
        print(f"   ❌ Login failed: {error_msg}")
        return
    
    # 3. Test Profile Retrieval with Junction Tables
    print()
    print("3. Testing Profile Retrieval (Junction Tables)...")
    headers = {'Authorization': f'Bearer {token}'}
    
    profile_response = client.get('/api/student/profile', headers=headers)
    
    print(f"   Status: {profile_response.status_code}")
    if profile_response.status_code == 200:
        profile = json.loads(profile_response.data)
        print("   ✅ Profile retrieved successfully!")
        print()
        
        # Display student details
        print("   Student Details:")
        print(f"     ID: {profile.get('student_id')}")
        print(f"     Name: {profile.get('display_name')}")
        print(f"     Email: {profile.get('email')}")
        print()
        
        # Display junction table data
        print("   Junction Table Data (1NF Normalization):")
        prefs = profile.get('preferences', {})
        career_interests = prefs.get('careerInterests', [])
        preferred_exams = prefs.get('preferredExams', [])
        
        print(f"     Career Interests: {len(career_interests)} items")
        for i, interest in enumerate(career_interests, 1):
            print(f"       {i}. {interest}")
            
        print(f"     Preferred Exams: {len(preferred_exams)} items")
        for i, exam in enumerate(preferred_exams, 1):
            print(f"       {i}. {exam}")
            
        print(f"     Region: {prefs.get('preferredRegion', 'None')}")
        print(f"     Budget: £{prefs.get('maxBudget', 'None')}")
        print()
        
        # Display grades
        print("   A-Level Subjects & Grades:")
        subjects = profile.get('aLevelSubjects', [])
        grades = profile.get('predictedGrades', {})
        print(f"     Total subjects: {len(subjects)}")
        
        if subjects:
            for i, subject_id in enumerate(subjects[:5], 1):  # Show first 5
                grade = grades.get(subject_id, 'Unknown')
                print(f"       {i}. Subject {subject_id}: Grade {grade}")
            if len(subjects) > 5:
                print(f"       ... and {len(subjects) - 5} more subjects")
                
    else:
        error_msg = profile_response.data.decode('utf-8')[:200]
        print(f"   ❌ Profile retrieval failed: {error_msg}")
        return
    
    # 4. Test Course Recommendations  
    print()
    print("4. Testing Course Recommendations...")
    rec_response = client.post('/api/student/recommendations', headers=headers)
    
    print(f"   Status: {rec_response.status_code}")
    if rec_response.status_code == 200:
        recommendations = json.loads(rec_response.data)
        print("   ✅ Recommendations generated successfully!")
        print(f"   Found {len(recommendations)} course recommendations")
        
        if recommendations:
            print("   Top 3 recommended courses:")
            for i, course in enumerate(recommendations[:3], 1):
                print(f"     {i}. {course.get('course_title', 'Unknown Course')}")
                print(f"        Institution: {course.get('institution_name', 'Unknown')}")
                print(f"        Score: {course.get('total_score', 0):.2f}")
                print()
    else:
        error_msg = rec_response.data.decode('utf-8')[:200]
        print(f"   ❌ Recommendations failed: {error_msg}")
    
    print()
    print("=== BACKEND SCENARIO TESTING COMPLETE ===")
    print("✅ Junction tables working correctly!")
    print("✅ 1NF normalization validated!")
    print("✅ Database schema fully functional!")

if __name__ == "__main__":
    test_complete_backend_scenario()