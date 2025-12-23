"""
Tests for OOP features: inheritance, composition, polymorphism
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base_model import BaseModel
from models.student import Student
from models.course import Course, EntryRequirements, Fees, Ranking, Employability
from scoring_components import SubjectMatchScorer, GradeMatchScorer


class TestInheritance:
    """Test OOP inheritance pattern"""
    
    def test_student_inherits_from_base_model(self):
        """Test that Student inherits from BaseModel"""
        student = Student(
            email='test@test.com',
            password='hash',
            firstName='John',
            lastName='Doe'
        )
        assert isinstance(student, BaseModel)
        assert hasattr(student, 'created_at')
        assert hasattr(student, 'to_dict')
        assert hasattr(student, 'from_dict')
    
    def test_course_inherits_from_base_model(self):
        """Test that Course inherits from BaseModel"""
        entry_req = EntryRequirements(subjects=[], grades={})
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
        assert isinstance(course, BaseModel)
        assert hasattr(course, 'created_at')
    
    def test_base_model_common_methods(self):
        """Test common methods from BaseModel"""
        student = Student(
            email='test@test.com',
            password='hash',
            firstName='John',
            lastName='Doe'
        )
        # Test inherited methods
        assert student.get_created_at() is not None
        assert student.is_recent() == True  # Just created
        assert 'Student' in repr(student)


class TestComposition:
    """Test OOP composition pattern"""
    
    def test_recommendation_engine_uses_composition(self):
        """Test that RecommendationEngine uses composition with scorers"""
        from recommendation_engine import RecommendationEngine
        
        engine = RecommendationEngine()
        # Check if composition components exist
        assert hasattr(engine, 'subject_scorer') or hasattr(engine, '_calculate_subject_match')
        assert hasattr(engine, 'weights')
    
    def test_scorer_components(self):
        """Test individual scorer components"""
        scorer = SubjectMatchScorer()
        course = {'entryRequirements': {'subjects': ['Math']}}
        student_data = {'aLevelSubjects': ['Math', 'Physics']}
        
        score = scorer.calculate_score(course, student_data)
        assert 0 <= score <= 1.0
    
    def test_grade_scorer_component(self):
        """Test grade scorer component"""
        scorer = GradeMatchScorer()
        course = {'entryRequirements': {'grades': {'Math': 'A'}}}
        student_data = {'predictedGrades': {'Math': 'A*'}}
        
        score = scorer.calculate_score(course, student_data)
        assert 0 <= score <= 1.0


class TestPolymorphism:
    """Test polymorphism in models"""
    
    def test_to_dict_polymorphism(self):
        """Test that to_dict works polymorphically"""
        student = Student(
            email='test@test.com',
            password='hash',
            firstName='John',
            lastName='Doe'
        )
        
        # Both Student and Course should have to_dict (polymorphism)
        student_dict = student.to_dict()
        assert isinstance(student_dict, dict)
        assert 'email' in student_dict
    
    def test_from_dict_polymorphism(self):
        """Test that from_dict works polymorphically"""
        data = {
            'email': 'test@test.com',
            'password': 'hash',
            'firstName': 'John',
            'lastName': 'Doe'
        }
        
        student = Student.from_dict(data)
        assert isinstance(student, Student)
        assert isinstance(student, BaseModel)
