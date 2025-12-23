"""
Unit tests for data models
"""
import pytest
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student
from models.course import Course, EntryRequirements, Fees, Ranking, Employability


class TestStudentModel:
    """Test Student model"""
    
    def test_student_creation(self):
        """Test creating a student instance"""
        student = Student(
            email='test@test.com',
            password='hashed_password',
            firstName='John',
            lastName='Doe'
        )
        assert student.email == 'test@test.com'
        assert student.firstName == 'John'
        assert student.lastName == 'Doe'
    
    def test_student_defaults(self):
        """Test student default values"""
        student = Student(
            email='test@test.com',
            password='hash',
            firstName='John',
            lastName='Doe'
        )
        assert student.yearGroup == 'Year 12'
        assert student.aLevelSubjects == []
        assert student.predictedGrades == {}
        assert student.preferences == {}
    
    def test_student_to_dict(self):
        """Test converting student to dictionary"""
        student = Student(
            email='test@test.com',
            password='hash',
            firstName='John',
            lastName='Doe'
        )
        student_dict = student.to_dict()
        assert isinstance(student_dict, dict)
        assert student_dict['email'] == 'test@test.com'
        assert student_dict['firstName'] == 'John'
    
    def test_student_from_dict(self):
        """Test creating student from dictionary"""
        data = {
            'email': 'test@test.com',
            'password': 'hash',
            'firstName': 'John',
            'lastName': 'Doe',
            'aLevelSubjects': ['Math', 'Physics'],
            'predictedGrades': {'Math': 'A'}
        }
        student = Student.from_dict(data)
        assert student.email == 'test@test.com'
        assert len(student.aLevelSubjects) == 2
    
    def test_student_is_complete_profile(self):
        """Test profile completeness check"""
        student = Student(
            email='test@test.com',
            password='hash',
            firstName='John',
            lastName='Doe'
        )
        assert not student.is_complete_profile()
        
        student.aLevelSubjects = ['Math']
        student.predictedGrades = {'Math': 'A'}
        student.preferences = {'region': 'London'}
        assert student.is_complete_profile()
    
    def test_student_get_full_name(self):
        """Test getting full name"""
        student = Student(
            email='test@test.com',
            password='hash',
            firstName='John',
            lastName='Doe'
        )
        assert student.get_full_name() == 'John Doe'


class TestCourseModel:
    """Test Course model"""
    
    def test_course_creation(self):
        """Test creating a course instance"""
        entry_req = EntryRequirements(
            subjects=['Mathematics'],
            grades={'Mathematics': 'A'}
        )
        fees = Fees(uk=9250)
        ranking = Ranking(overall=10)
        employability = Employability(employment_rate=90.0)
        
        course = Course(
            name='Computer Science',
            university={'name': 'Test University'},
            subjects=['Mathematics'],
            entry_requirements=entry_req,
            fees=fees,
            ranking=ranking,
            employability=employability
        )
        assert course.name == 'Computer Science'
        assert course.fees.uk == 9250
    
    def test_course_matches_subjects(self):
        """Test subject matching"""
        entry_req = EntryRequirements(
            subjects=['Mathematics', 'Physics'],
            grades={}
        )
        fees = Fees(uk=9250)
        ranking = Ranking()
        employability = Employability(employment_rate=80.0)
        
        course = Course(
            name='Test',
            university={},
            subjects=[],
            entry_requirements=entry_req,
            fees=fees,
            ranking=ranking,
            employability=employability
        )
        
        assert course.matches_subjects(['Mathematics', 'Physics'])
        assert course.matches_subjects(['Mathematics', 'Chemistry'])
        assert not course.matches_subjects(['Chemistry', 'Biology'])
    
    def test_course_meets_grade_requirements(self):
        """Test grade requirement checking"""
        entry_req = EntryRequirements(
            subjects=['Mathematics'],
            grades={'Mathematics': 'A'}
        )
        fees = Fees(uk=9250)
        ranking = Ranking()
        employability = Employability(employment_rate=80.0)
        
        course = Course(
            name='Test',
            university={},
            subjects=[],
            entry_requirements=entry_req,
            fees=fees,
            ranking=ranking,
            employability=employability
        )
        
        # Student exceeds requirements
        assert course.meets_grade_requirements({'Mathematics': 'A*'})
        # Student meets requirements
        assert course.meets_grade_requirements({'Mathematics': 'A'})
        # Student below requirements
        assert not course.meets_grade_requirements({'Mathematics': 'B'})
    
    def test_course_is_affordable(self):
        """Test budget checking"""
        fees = Fees(uk=9000)
        entry_req = EntryRequirements(subjects=[], grades={})
        ranking = Ranking()
        employability = Employability(employment_rate=80.0)
        
        course = Course(
            name='Test',
            university={},
            subjects=[],
            entry_requirements=entry_req,
            fees=fees,
            ranking=ranking,
            employability=employability
        )
        
        assert course.is_affordable(10000)
        assert course.is_affordable(9000)
        assert not course.is_affordable(8000)
