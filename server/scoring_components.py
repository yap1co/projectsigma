"""
Scoring components for recommendation engine
Demonstrates OOP composition pattern
"""
from typing import Dict, List, Any
from abc import ABC, abstractmethod


class Scorer(ABC):
    """Abstract base class for scoring components (composition pattern)"""
    
    @abstractmethod
    def calculate_score(self, course: Dict[str, Any], student_data: Dict[str, Any]) -> float:
        """Calculate score for a course"""
        pass


class SubjectMatchScorer(Scorer):
    """Scorer for subject matching (composition component) - Enhanced to consider all student subjects"""
    
    def __init__(self):
        # Subject mapping for related fields
        self.subject_mappings = {
            'english language': ['english', 'literature', 'language', 'writing', 'linguistics'],
            'english literature': ['english', 'literature', 'language', 'writing', 'humanities'],
            'philosophy': ['philosophy', 'ethics', 'theology', 'religious studies', 'politics', 'humanities'],
            'mathematics': ['mathematics', 'maths', 'math', 'statistics', 'computing', 'computer science'],
            'further mathematics': ['mathematics', 'maths', 'math', 'statistics', 'computing', 'computer science'],
            'physics': ['physics', 'engineering', 'mathematics', 'computing', 'computer science'],
            'chemistry': ['chemistry', 'biology', 'medicine', 'pharmacy'],
            'biology': ['biology', 'medicine', 'pharmacy', 'chemistry', 'biochemistry'],
            'history': ['history', 'politics', 'archaeology', 'humanities'],
            'geography': ['geography', 'environmental', 'geology', 'urban planning'],
            'economics': ['economics', 'business', 'finance', 'accounting', 'politics'],
            'business studies': ['business', 'economics', 'finance', 'accounting', 'management'],
            'psychology': ['psychology', 'sociology', 'neuroscience', 'criminology'],
            'sociology': ['sociology', 'psychology', 'politics', 'criminology', 'social work'],
            'politics': ['politics', 'international relations', 'history', 'philosophy', 'economics'],
            'art': ['art', 'design', 'fine art', 'creative', 'visual arts'],
            'design technology': ['design', 'engineering', 'technology', 'product design'],
            'computer science': ['computer science', 'computing', 'software', 'it', 'mathematics', 'physics']
        }
    
    def calculate_score(self, course: Dict[str, Any], student_data: Dict[str, Any]) -> float:
        """Calculate subject match score - considers ALL student subjects, not just required ones"""
        required_subjects = course.get('entryRequirements', {}).get('subjects', [])
        student_subjects = student_data.get('aLevelSubjects', [])
        course_name = course.get('name', '').lower()
        
        if not student_subjects:
            return 0.3  # Student has no subjects, low score
        
        # Normalize subjects
        student_subjects_normalized = {s.lower().strip() for s in student_subjects}
        required_subjects_normalized = {s.lower().strip() for s in required_subjects} if required_subjects else set()
        
        # Calculate required subject match
        matching_required = set()
        if required_subjects_normalized:
            matching_required = student_subjects_normalized & required_subjects_normalized
            # Try partial matching
            if not matching_required:
                for req_subj in required_subjects_normalized:
                    for stud_subj in student_subjects_normalized:
                        if req_subj in stud_subj or stud_subj in req_subj:
                            matching_required.add(req_subj)
                            break
        
        # Calculate relevance to ALL student subjects (even if not required)
        # BUT only when there's a clear, legitimate relationship
        matching_student_subjects = set()
        course_name_words = set(course_name.replace('-', ' ').replace('_', ' ').replace('university', '').replace('of', '').split())
        
        for stud_subj in student_subjects_normalized:
            # Only match if there's a clear, direct relationship
            # Check 1: Exact subject name appears as a whole word in course name
            stud_subj_words = stud_subj.split()
            matched = False
            for word in course_name_words:
                if len(word) > 2:
                    # Check if the full subject name or its main word matches
                    if stud_subj == word or (len(stud_subj_words) > 0 and stud_subj_words[0] == word):
                        matching_student_subjects.add(stud_subj)
                        matched = True
                        break
            
            # Check 2: Subject mappings for related fields (only legitimate relationships)
            if not matched and stud_subj in self.subject_mappings:
                for related_term in self.subject_mappings[stud_subj]:
                    # Only match if the related term appears as a whole word or significant phrase
                    if len(related_term) > 3:  # Only match terms longer than 3 characters
                        # Check if it's a whole word in the course name
                        if related_term in course_name_words or related_term in course_name:
                            # Generic check to prevent false positives
                            # Note: This scorer doesn't have access to the full engine's generic matching
                            # So we use a simplified version - in practice, this should use the same _is_legitimate_match
                            # For now, we check if the generic term is part of the subject name
                            generic_terms = {'science', 'studies', 'business', 'management', 'technology', 'design', 'art'}
                            if related_term not in generic_terms or related_term in stud_subj.lower():
                                matching_student_subjects.add(stud_subj)
                                matched = True
                                break
        
        # Combine matches
        all_matching_subjects = matching_required | matching_student_subjects
        
        # Calculate base score from required subjects match
        if required_subjects_normalized:
            required_match_ratio = len(matching_required) / len(required_subjects_normalized)
        else:
            # No required subjects - use student subject relevance instead
            required_match_ratio = len(matching_student_subjects) / len(student_subjects_normalized) if student_subjects_normalized else 0.5
        
        # Bonus for matching multiple student subjects
        student_subject_bonus = 0.0
        if len(matching_student_subjects) > 0:
            student_subject_bonus = min(0.3, len(matching_student_subjects) * 0.1)
        
        # Bonus for matching ALL required subjects
        if required_subjects_normalized and len(matching_required) == len(required_subjects_normalized):
            required_match_ratio = min(required_match_ratio + 0.2, 1.0)
        elif len(matching_required) > 0:
            required_match_ratio = max(required_match_ratio, 0.4)
        
        # If no required subjects, base score on student subject relevance
        # BUT be much more strict - don't give high scores for weak matches
        if not required_subjects_normalized:
            if len(matching_student_subjects) > 0:
                # Only give decent score if there's a clear match
                base_score = 0.3 + (len(matching_student_subjects) / len(student_subjects_normalized)) * 0.2
            else:
                # No match at all - very low score
                base_score = 0.2
        else:
            base_score = required_match_ratio
        
        # Final score combines required match + student subject relevance bonus
        final_score = min(base_score + student_subject_bonus, 1.0)
        
        # Only ensure minimum score if there's a REQUIRED subject match
        # Don't give minimum score for weak relevance matches
        if len(matching_required) > 0:
            final_score = max(final_score, 0.4)
        elif len(matching_student_subjects) > 0 and required_subjects_normalized:
            # If there are required subjects but student subjects match, give some credit
            final_score = max(final_score, 0.3)
        elif len(matching_student_subjects) > 0 and not required_subjects_normalized:
            # No required subjects but student subjects match - moderate score
            final_score = max(final_score, 0.25)
        
        return final_score


class GradeMatchScorer(Scorer):
    """Scorer for grade matching (composition component)"""
    
    def __init__(self):
        self.grade_values = {
            'A*': 8, 'A': 7, 'B': 6, 'C': 5, 'D': 4, 'E': 3, 'U': 0
        }
    
    def calculate_score(self, course: Dict[str, Any], student_data: Dict[str, Any]) -> float:
        """Calculate grade match score"""
        required_grades = course.get('entryRequirements', {}).get('grades', {})
        predicted_grades = student_data.get('predictedGrades', {})
        
        if not required_grades:
            # If no grade requirements, give a good score to encourage showing the course
            return 0.7  # Increased from 0.5 to show more courses
        
        total_score = 0
        total_weight = 0
        
        for subject, required_grade in required_grades.items():
            if subject in predicted_grades:
                predicted_grade = predicted_grades[subject]
                required_value = self.grade_values.get(required_grade, 0)
                predicted_value = self.grade_values.get(predicted_grade, 0)
                
                if predicted_value >= required_value:
                    subject_score = 1.0
                else:
                    # Much stricter scoring: heavily penalize unmet requirements
                    # Courses where student doesn't meet requirements should score very low
                    grade_diff = required_value - predicted_value
                    if grade_diff == 1:  # One grade below (e.g., B vs A)
                        subject_score = 0.15  # Heavily penalized - doesn't meet requirement
                    elif grade_diff == 2:  # Two grades below (e.g., B vs A*)
                        subject_score = 0.05  # Very low score - significant gap
                    elif grade_diff == 3:  # Three grades below
                        subject_score = 0.01  # Minimal score - very unlikely
                    else:
                        # For larger gaps, near-zero score
                        subject_score = max(0.001, predicted_value / required_value * 0.05) if required_value > 0 else 0
                
                total_score += subject_score
                total_weight += 1
        
        return total_score / total_weight if total_weight > 0 else 0.5


class PreferenceMatchScorer(Scorer):
    """Scorer for preference matching (composition component)"""
    
    def __init__(self):
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
    
    def calculate_score(self, course: Dict[str, Any], student_data: Dict[str, Any]) -> float:
        """Calculate preference match score"""
        preferences = student_data.get('preferences', {})
        score = 0.5
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
                budget_ratio = course_fee / max_budget if max_budget > 0 else 0
                score += 0.2 * (1 - budget_ratio)
            else:
                score -= 0.3
            factors += 1
        
        return min(max(score / max(factors, 1), 0), 1)
    
    def _get_course_region(self, course: Dict[str, Any]) -> str:
        """Determine the region of a course's university"""
        university_name = course.get('university', {}).get('name', '').lower()
        
        for region, cities in self.regions.items():
            for city in cities:
                if city.lower() in university_name:
                    return region
        
        return 'Unknown'


class RankingScorer(Scorer):
    """Scorer for university ranking (composition component)"""
    
    def calculate_score(self, course: Dict[str, Any], student_data: Dict[str, Any]) -> float:
        """Calculate ranking score"""
        ranking = course.get('university', {}).get('ranking', {})
        
        if not ranking:
            return 0.5
        
        overall_rank = ranking.get('overall')
        subject_rank = ranking.get('subject')
        
        # Handle None values - convert to 0 if None
        overall_rank = overall_rank if overall_rank is not None else 0
        subject_rank = subject_rank if subject_rank is not None else 0
        
        rank_to_use = subject_rank if subject_rank > 0 else overall_rank
        
        if rank_to_use == 0 or rank_to_use is None:
            return 0.5
        
        if rank_to_use <= 10:
            return 1.0 - (rank_to_use - 1) * 0.01
        elif rank_to_use <= 50:
            return 0.9 - (rank_to_use - 10) * 0.01
        else:
            return max(0.1, 0.5 - (rank_to_use - 50) * 0.008)


class EmployabilityScorer(Scorer):
    """Scorer for employability (composition component)"""
    
    def calculate_score(self, course: Dict[str, Any], student_data: Dict[str, Any]) -> float:
        """Calculate employability score"""
        employability = course.get('employability', {})
        
        if not employability:
            return 0.5
        
        employment_rate = employability.get('employmentRate', 50)
        avg_salary = employability.get('averageSalary', 30000)
        salary_score = min(1.0, (avg_salary - 20000) / 40000) if avg_salary else 0.5
        
        return (employment_rate / 100) * 0.7 + salary_score * 0.3
