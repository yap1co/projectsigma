"""Test script to diagnose recommendation engine issues"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from recommendation_engine import RecommendationEngine
import traceback

try:
    print("Initializing recommendation engine...")
    engine = RecommendationEngine()
    
    print("Loading courses from database...")
    courses = engine._get_all_courses()
    print(f"OK: Loaded {len(courses)} courses")
    
    if courses:
        print(f"\nFirst course structure:")
        first_course = courses[0]
        print(f"  Keys: {list(first_course.keys())}")
        print(f"  Name: {first_course.get('name', 'N/A')}")
        print(f"  Entry requirements: {first_course.get('entryRequirements', {})}")
    
    print("\nTesting recommendation generation...")
    recommendations = engine.get_recommendations(
        a_level_subjects=['Mathematics', 'Computer Science', 'Physics'],
        predicted_grades={'Mathematics': 'A', 'Computer Science': 'B', 'Physics': 'B'},
        preferences={'preferredRegion': 'London'},
        criteria={}
    )
    print(f"OK: Generated {len(recommendations)} recommendations")
    
    if recommendations:
        print(f"\nFirst recommendation:")
        print(f"  Course: {recommendations[0]['course'].get('name', 'N/A')}")
        print(f"  Score: {recommendations[0].get('matchScore', 0)}")
    
    print("\nOK: All tests passed!")
    
except Exception as e:
    print(f"\nERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
