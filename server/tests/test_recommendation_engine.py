"""
Unit tests for RecommendationEngine
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recommendation_engine import RecommendationEngine


class TestRecommendationEngine:
    """Test cases for RecommendationEngine class"""
    
    def test_engine_initialization(self):
        """Test that RecommendationEngine initializes correctly"""
        engine = RecommendationEngine()
        assert engine is not None
        assert hasattr(engine, 'weights')
        assert hasattr(engine, 'grade_values')
    
    def test_weights_sum_to_one(self):
        """Test that recommendation weights sum to approximately 1.0"""
        engine = RecommendationEngine()
        total_weight = sum(engine.weights.values())
        assert abs(total_weight - 1.0) < 0.01, f"Weights sum to {total_weight}, expected ~1.0"
    
    def test_calculate_subject_match_perfect(self):
        """Test subject matching with perfect match"""
        engine = RecommendationEngine()
        course = {
            'entryRequirements': {
                'subjects': ['Mathematics', 'Physics']
            }
        }
        student_subjects = ['Mathematics', 'Physics', 'Chemistry']
        score = engine._calculate_subject_match(course, student_subjects)
        assert score > 0.8, f"Perfect match should score > 0.8, got {score}"
    
    def test_calculate_subject_match_partial(self):
        """Test subject matching with partial match"""
        engine = RecommendationEngine()
        course = {
            'entryRequirements': {
                'subjects': ['Mathematics', 'Physics', 'Chemistry']
            }
        }
        student_subjects = ['Mathematics', 'Physics']
        score = engine._calculate_subject_match(course, student_subjects)
        assert 0.3 < score < 0.9, f"Partial match should score between 0.3-0.9, got {score}"
    
    def test_calculate_subject_match_no_requirements(self):
        """Test subject matching when course has no requirements"""
        engine = RecommendationEngine()
        course = {
            'entryRequirements': {
                'subjects': []
            }
        }
        student_subjects = ['Mathematics', 'Physics']
        score = engine._calculate_subject_match(course, student_subjects)
        assert score == 0.5, f"No requirements should return 0.5, got {score}"
    
    def test_calculate_grade_match_exceeds(self):
        """Test grade matching when student grades exceed requirements"""
        engine = RecommendationEngine()
        course = {
            'entryRequirements': {
                'grades': {'Mathematics': 'A', 'Physics': 'B'}
            }
        }
        student_grades = {'Mathematics': 'A*', 'Physics': 'A'}
        score = engine._calculate_grade_match(course, student_grades)
        assert score >= 0.5, f"Exceeding grades should score >= 0.5, got {score}"
    
    def test_calculate_grade_match_meets(self):
        """Test grade matching when student grades meet requirements"""
        engine = RecommendationEngine()
        course = {
            'entryRequirements': {
                'grades': {'Mathematics': 'A', 'Physics': 'B'}
            }
        }
        student_grades = {'Mathematics': 'A', 'Physics': 'B'}
        score = engine._calculate_grade_match(course, student_grades)
        assert score >= 0.5, f"Meeting grades should score >= 0.5, got {score}"
    
    def test_calculate_grade_match_below(self):
        """Test grade matching when student grades are below requirements"""
        engine = RecommendationEngine()
        course = {
            'entryRequirements': {
                'grades': {'Mathematics': 'A', 'Physics': 'B'}
            }
        }
        student_grades = {'Mathematics': 'B', 'Physics': 'C'}
        score = engine._calculate_grade_match(course, student_grades)
        assert 0 <= score < 1.0, f"Below grades should score < 1.0, got {score}"
    
    def test_calculate_preference_match_region(self):
        """Test preference matching for region"""
        engine = RecommendationEngine()
        course = {
            'university': {'name': 'University of Cambridge'}
        }
        preferences = {'preferredRegion': 'South East'}
        score = engine._calculate_preference_match(course, preferences)
        assert 0 <= score <= 1.0, f"Preference score should be 0-1, got {score}"
    
    def test_calculate_preference_match_budget(self):
        """Test preference matching for budget"""
        engine = RecommendationEngine()
        course = {
            'fees': {'uk': 9000}
        }
        preferences = {'maxBudget': 10000}
        score = engine._calculate_preference_match(course, preferences)
        assert 0 <= score <= 1.0, f"Budget match score should be 0-1, got {score}"
    
    def test_calculate_ranking_score_top_ranked(self):
        """Test ranking score calculation for top-ranked university"""
        engine = RecommendationEngine()
        course = {
            'university': {
                'ranking': {'overall': 1}
            }
        }
        score = engine._calculate_ranking_score(course)
        assert score > 0.9, f"Top-ranked should score > 0.9, got {score}"
    
    def test_calculate_ranking_score_no_ranking(self):
        """Test ranking score when no ranking data"""
        engine = RecommendationEngine()
        course = {
            'university': {}
        }
        score = engine._calculate_ranking_score(course)
        assert score == 0.5, f"No ranking should return 0.5, got {score}"
    
    def test_calculate_match_score_weighted(self):
        """Test that weighted match score calculation works"""
        engine = RecommendationEngine()
        course = {
            'entryRequirements': {
                'subjects': ['Mathematics'],
                'grades': {'Mathematics': 'A'}
            },
            'university': {'ranking': {'overall': 10}},
            'fees': {'uk': 9000},
            'employability': {'employmentRate': 90, 'averageSalary': 40000}
        }
        student_subjects = ['Mathematics', 'Physics']
        student_grades = {'Mathematics': 'A*'}
        preferences = {'preferredRegion': 'London', 'maxBudget': 10000}
        criteria = {}
        
        score = engine._calculate_match_score(
            course, student_subjects, student_grades, preferences, criteria
        )
        assert 0 <= score <= 1.0, f"Match score should be 0-1, got {score}"
        assert score > 0, "Good match should have positive score"
