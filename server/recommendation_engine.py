"""
Advanced recommendation engine for university course matching
Implements weighted criteria scoring and matching algorithms
"""

import math
from typing import List, Dict, Any
from models.course import Course
from models.student import Student

class RecommendationEngine:
    """
    Advanced recommendation engine that matches students with university courses
    based on multiple weighted criteria including academic fit, preferences, and compatibility
    """
    
    def __init__(self):
        # Weight configuration for different criteria
        self.weights = {
            'subject_match': 0.30,      # A-level subject alignment
            'grade_match': 0.25,        # Predicted grades vs requirements
            'preference_match': 0.20,   # Student preferences (location, budget, etc.)
            'university_ranking': 0.15,  # University prestige/ranking
            'employability': 0.10       # Graduate employment prospects
        }
        
        # Grade conversion mapping
        self.grade_values = {
            'A*': 8, 'A': 7, 'B': 6, 'C': 5, 'D': 4, 'E': 3, 'U': 0
        }
        
        # UK regions for location matching
        self.regions = {
            'London': ['London'],
            'South East': ['Oxford', 'Cambridge', 'Brighton', 'Canterbury', 'Reading'],
            'South West': ['Bristol', 'Bath', 'Exeter', 'Plymouth'],
            'Midlands': ['Birmingham', 'Coventry', 'Leicester', 'Nottingham'],
            'North West': ['Manchester', 'Liverpool', 'Lancaster'],
            'North East': ['Newcastle', 'Durham', 'York'],
            'Scotland': ['Edinburgh', 'Glasgow', 'St Andrews', 'Aberdeen'],
            'Wales': ['Cardiff', 'Swansea', 'Bangor']
        }
    
    def get_recommendations(self, a_level_subjects: List[str], 
                          predicted_grades: Dict[str, str],
                          preferences: Dict[str, Any],
                          criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate personalized course recommendations based on student profile
        
        Args:
            a_level_subjects: List of A-level subjects taken
            predicted_grades: Dictionary of subject -> predicted grade
            preferences: Student preferences (location, budget, etc.)
            criteria: Additional search criteria
            
        Returns:
            List of recommended courses with match scores
        """
        # Get all courses from database (in real implementation)
        courses = self._get_all_courses()
        
        # Calculate match scores for each course
        scored_courses = []
        
        for course in courses:
            match_score = self._calculate_match_score(
                course, a_level_subjects, predicted_grades, preferences, criteria
            )
            
            if match_score > 0:  # Only include courses with some match
                scored_courses.append({
                    'course': course,
                    'matchScore': match_score,
                    'reasons': self._get_match_reasons(course, a_level_subjects, predicted_grades, preferences)
                })
        
        # Sort by match score (highest first)
        scored_courses.sort(key=lambda x: x['matchScore'], reverse=True)
        
        # Return top recommendations (limit to 50)
        return scored_courses[:50]
    
    def _calculate_match_score(self, course: Dict[str, Any], 
                            a_level_subjects: List[str],
                            predicted_grades: Dict[str, str],
                            preferences: Dict[str, Any],
                            criteria: Dict[str, Any]) -> float:
        """
        Calculate weighted match score for a course
        
        Returns:
            Float between 0 and 1 representing match quality
        """
        scores = {}
        
        # 1. Subject match score
        scores['subject_match'] = self._calculate_subject_match(course, a_level_subjects)
        
        # 2. Grade match score
        scores['grade_match'] = self._calculate_grade_match(course, predicted_grades)
        
        # 3. Preference match score
        scores['preference_match'] = self._calculate_preference_match(course, preferences)
        
        # 4. University ranking score
        scores['university_ranking'] = self._calculate_ranking_score(course)
        
        # 5. Employability score
        scores['employability'] = self._calculate_employability_score(course)
        
        # Calculate weighted total
        total_score = sum(
            scores[criterion] * weight 
            for criterion, weight in self.weights.items()
        )
        
        return min(total_score, 1.0)  # Cap at 1.0
    
    def _calculate_subject_match(self, course: Dict[str, Any], 
                               a_level_subjects: List[str]) -> float:
        """Calculate how well student's subjects match course requirements"""
        required_subjects = course.get('entryRequirements', {}).get('subjects', [])
        
        if not required_subjects:
            return 0.5  # Neutral score if no specific requirements
        
        # Count matching subjects
        matching_subjects = set(a_level_subjects) & set(required_subjects)
        match_ratio = len(matching_subjects) / len(required_subjects)
        
        # Bonus for having all required subjects
        if len(matching_subjects) == len(required_subjects):
            match_ratio = min(match_ratio + 0.2, 1.0)
        
        return match_ratio
    
    def _calculate_grade_match(self, course: Dict[str, Any], 
                             predicted_grades: Dict[str, str]) -> float:
        """Calculate how well predicted grades match course requirements"""
        required_grades = course.get('entryRequirements', {}).get('grades', {})
        
        if not required_grades:
            return 0.5  # Neutral score if no grade requirements
        
        total_score = 0
        total_weight = 0
        
        for subject, required_grade in required_grades.items():
            if subject in predicted_grades:
                predicted_grade = predicted_grades[subject]
                
                # Convert grades to numerical values
                required_value = self.grade_values.get(required_grade, 0)
                predicted_value = self.grade_values.get(predicted_grade, 0)
                
                # Calculate subject-specific score
                if predicted_value >= required_value:
                    subject_score = 1.0
                else:
                    # Partial credit for being close
                    subject_score = max(0, predicted_value / required_value)
                
                total_score += subject_score
                total_weight += 1
        
        return total_score / total_weight if total_weight > 0 else 0.5
    
    def _calculate_preference_match(self, course: Dict[str, Any], 
                                  preferences: Dict[str, Any]) -> float:
        """Calculate how well course matches student preferences"""
        score = 0.5  # Start with neutral score
        factors = 0
        
        # Location preference
        if 'preferredRegion' in preferences:
            course_region = self._get_course_region(course)
            if course_region == preferences['preferredRegion']:
                score += 0.3
            factors += 1
        
        # Budget preference
        if 'maxBudget' in preferences:
            course_fee = course.get('fees', {}).get('uk', 0)
            max_budget = preferences['maxBudget']
            
            if course_fee <= max_budget:
                # Bonus for being under budget
                budget_ratio = course_fee / max_budget
                score += 0.2 * (1 - budget_ratio)
            else:
                # Penalty for being over budget
                score -= 0.3
            factors += 1
        
        # University size preference
        if 'preferredUniSize' in preferences:
            uni_size = course.get('university', {}).get('size', 'medium')
            if uni_size == preferences['preferredUniSize']:
                score += 0.2
            factors += 1
        
        # Course length preference
        if 'preferredCourseLength' in preferences:
            course_length = course.get('duration', '3')
            if str(course_length) == str(preferences['preferredCourseLength']):
                score += 0.1
            factors += 1
        
        return min(max(score / max(factors, 1), 0), 1)
    
    def _calculate_ranking_score(self, course: Dict[str, Any]) -> float:
        """Calculate score based on university ranking"""
        ranking = course.get('university', {}).get('ranking', {})
        
        if not ranking:
            return 0.5  # Neutral score if no ranking data
        
        # Use overall ranking or subject-specific ranking
        overall_rank = ranking.get('overall', 0)
        subject_rank = ranking.get('subject', 0)
        
        # Prefer subject-specific ranking if available
        rank_to_use = subject_rank if subject_rank > 0 else overall_rank
        
        if rank_to_use == 0:
            return 0.5
        
        # Convert ranking to score (lower rank number = higher score)
        # Scale: 1st = 1.0, 10th = 0.9, 50th = 0.5, 100th+ = 0.1
        if rank_to_use <= 10:
            return 1.0 - (rank_to_use - 1) * 0.01
        elif rank_to_use <= 50:
            return 0.9 - (rank_to_use - 10) * 0.01
        else:
            return max(0.1, 0.5 - (rank_to_use - 50) * 0.008)
    
    def _calculate_employability_score(self, course: Dict[str, Any]) -> float:
        """Calculate score based on graduate employability"""
        employability = course.get('employability', {})
        
        if not employability:
            return 0.5  # Neutral score if no data
        
        # Employment rate (0-100%)
        employment_rate = employability.get('employmentRate', 50)
        
        # Average salary (normalize to 0-1 scale, assuming £20k-£60k range)
        avg_salary = employability.get('averageSalary', 30000)
        salary_score = min(1.0, (avg_salary - 20000) / 40000)
        
        # Combine employment rate and salary
        return (employment_rate / 100) * 0.7 + salary_score * 0.3
    
    def _get_course_region(self, course: Dict[str, Any]) -> str:
        """Determine the region of a course's university"""
        university_name = course.get('university', {}).get('name', '').lower()
        
        for region, cities in self.regions.items():
            for city in cities:
                if city.lower() in university_name:
                    return region
        
        return 'Unknown'
    
    def _get_match_reasons(self, course: Dict[str, Any], 
                          a_level_subjects: List[str],
                          predicted_grades: Dict[str, str],
                          preferences: Dict[str, Any]) -> List[str]:
        """Generate human-readable reasons for the match"""
        reasons = []
        
        # Subject match reasons
        required_subjects = course.get('entryRequirements', {}).get('subjects', [])
        matching_subjects = set(a_level_subjects) & set(required_subjects)
        
        if matching_subjects:
            reasons.append(f"Matches your A-level subjects: {', '.join(matching_subjects)}")
        
        # Grade match reasons
        required_grades = course.get('entryRequirements', {}).get('grades', {})
        for subject, required_grade in required_grades.items():
            if subject in predicted_grades:
                predicted_grade = predicted_grades[subject]
                if self.grade_values.get(predicted_grade, 0) >= self.grade_values.get(required_grade, 0):
                    reasons.append(f"Your predicted {subject} grade ({predicted_grade}) meets requirements ({required_grade})")
        
        # Preference reasons
        if 'preferredRegion' in preferences:
            course_region = self._get_course_region(course)
            if course_region == preferences['preferredRegion']:
                reasons.append(f"Located in your preferred region: {course_region}")
        
        # University ranking reasons
        ranking = course.get('university', {}).get('ranking', {})
        if ranking.get('overall', 0) <= 20:
            reasons.append(f"Top-ranked university (#{ranking['overall']})")
        
        # Employability reasons
        employability = course.get('employability', {})
        if employability.get('employmentRate', 0) >= 90:
            reasons.append(f"High graduate employment rate ({employability['employmentRate']}%)")
        
        return reasons
    
    def _get_all_courses(self) -> List[Dict[str, Any]]:
        """Get all courses from database (placeholder for now)"""
        # In real implementation, this would query the database
        # For now, return sample data
        return [
            {
                'name': 'Computer Science',
                'university': {'name': 'University of Cambridge', 'ranking': {'overall': 1}},
                'entryRequirements': {
                    'subjects': ['Mathematics', 'Physics'],
                    'grades': {'Mathematics': 'A*', 'Physics': 'A'}
                },
                'fees': {'uk': 9250},
                'employability': {'employmentRate': 95, 'averageSalary': 45000}
            },
            # Add more sample courses...
        ]
