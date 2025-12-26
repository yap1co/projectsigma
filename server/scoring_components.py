"""
Scoring components for recommendation engine
Demonstrates OOP composition pattern
"""
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod


class Scorer(ABC):
    """Abstract base class for scoring components (composition pattern)"""
    
    @abstractmethod
    def calculate_score(self, course: Dict[str, Any], student_data: Dict[str, Any]) -> float:
        """Calculate score for a course"""
        pass


class SubjectMatchScorer(Scorer):
    """Scorer for subject matching (composition component) - Enhanced to consider all student subjects"""
    
    def __init__(self, subject_mappings=None):
        # Load from database or use provided mappings
        if subject_mappings is not None:
            self.subject_mappings = subject_mappings
        else:
            # Fallback to empty dict - subject matching now uses CAH codes
            self.subject_mappings = {}
        
        # Generic terms removed - subject matching now uses CAH codes from subject_course_mapping
        self.generic_terms = set()
        self.legitimate_generic_matches = {}
    
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
            
            # Check 2: Subject mappings removed - now using CAH codes for matching
            # Subject matching is done via CAH codes from subject_course_mapping table
        
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
    
    def __init__(self, grade_values=None):
        if grade_values is not None:
            self.grade_values = grade_values
        else:
            # Fallback to defaults
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
    
    def __init__(self, regions=None):
        if regions is not None:
            self.regions = regions  # Now a list, not a dict
        else:
            # Fallback to defaults (list of region names)
            self.regions = ['London', 'South East', 'South West', 'Midlands', 'North West', 'North East', 'Scotland', 'Wales']
    
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
        """Determine the region of a course's university - get directly from university data"""
        # Get region directly from university data (from HESA)
        region = course.get('university', {}).get('region')
        if region:
            return region
        
        # Fallback: try to match from university name
        university_name = course.get('university', {}).get('name', '').lower()
        for region in self.regions:
            if region.lower() in university_name:
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
    
    def __init__(self):
        """Initialize the employability scorer with grade values for best subject detection"""
        # Grade values for determining best subject
        self.grade_values = {
            'A*': 8, 'A': 7, 'B': 6, 'C': 5, 'D': 4, 'E': 3, 'U': 0
        }
        # Cache for salary quartiles by CAH code to avoid repeated queries
        self._salary_quartiles_cache: Dict[str, Tuple[float, float, float]] = {}
    
    def _get_best_subject_cah3_code(self, student_data: Dict[str, Any]) -> Optional[str]:
        """
        Get the CAH3 code for the student's subject with the highest grade.
        
        Returns:
            CAH3 code (e.g., 'CAH09-01-01') or None if not found
        """
        predicted_grades = student_data.get('predictedGrades', {})
        if not predicted_grades:
            return None
        
        # Find subject with highest grade
        highest_grade_value = -1
        best_subject = None
        
        for subject, grade in predicted_grades.items():
            grade_value = self.grade_values.get(grade, 0)
            if grade_value > highest_grade_value:
                highest_grade_value = grade_value
                best_subject = subject
        
        if not best_subject:
            return None
        
        # Map subject to CAH3 code via database
        try:
            from database_helper import get_db_connection
            
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Query subject_course_mapping to get CAH3 code for this subject
                    cur.execute("""
                        SELECT DISTINCT cah3_code
                        FROM uni_recomm_subject_course_mapping
                        WHERE a_level_subject = %s
                        LIMIT 1
                    """, (best_subject,))
                    
                    row = cur.fetchone()
                    if row:
                        return row[0]
        except Exception as e:
            # Log error but don't fail - fall back to default normalization
            print(f"Warning: Could not get CAH3 code for subject '{best_subject}': {e}")
        
        return None
    
    def _get_salary_quartiles_for_cah3(self, cah3_code: str) -> Optional[Tuple[float, float, float]]:
        """
        Get salary quartiles (lower, median, upper) for a given CAH3 code from HESA data.
        
        Tries to match on CAH3 code first, then falls back to CAH2 and CAH1 codes if needed.
        
        Args:
            cah3_code: CAH3 code (e.g., 'CAH09-01-01')
            
        Returns:
            Tuple of (lower_quartile, median, upper_quartile) or None if not found
        """
        if not cah3_code:
            return None
        
        # Check cache first
        if cah3_code in self._salary_quartiles_cache:
            return self._salary_quartiles_cache[cah3_code]
        
        try:
            from database_helper import get_db_connection
            
            # Extract CAH2 and CAH1 codes from CAH3 code for fallback matching
            # CAH3 format: CAH09-01-01 -> CAH2: CAH09-01, CAH1: CAH09
            cah2_code = None
            cah1_code = None
            if '-' in cah3_code:
                parts = cah3_code.split('-')
                if len(parts) >= 2:
                    cah2_code = f"{parts[0]}-{parts[1]}"
                if len(parts) >= 1:
                    cah1_code = parts[0]
            
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Try CAH3 code first, then CAH2, then CAH1
                    for code_to_try in [cah3_code, cah2_code, cah1_code]:
                        if not code_to_try:
                            continue
                        
                        # Query HESA salary data aggregated by CAH code
                        # Use gosalsbj field which links to CAH code
                        # Each row already has quartiles, so we aggregate them (median of quartiles)
                        cur.execute("""
                            SELECT 
                                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY goinstlq) AS lower_quartile,
                                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY goinstmed) AS median,
                                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY goinstuq) AS upper_quartile
                            FROM hesa_gosalary
                            WHERE gosalsbj = %s
                              AND goinstmed IS NOT NULL
                              AND goinstlq IS NOT NULL
                              AND goinstuq IS NOT NULL
                        """, (code_to_try,))
                        
                        row = cur.fetchone()
                        if row and row[0] is not None and row[1] is not None and row[2] is not None:
                            quartiles = (float(row[0]), float(row[1]), float(row[2]))
                            # Cache the result with the original CAH3 code as key
                            self._salary_quartiles_cache[cah3_code] = quartiles
                            return quartiles
        except Exception as e:
            # Log error but don't fail - fall back to default normalization
            print(f"Warning: Could not get salary quartiles for CAH3 '{cah3_code}': {e}")
        
        return None
    
    def _normalize_salary_score(self, salary: float, lower_q: Optional[float], 
                                median: Optional[float], upper_q: Optional[float]) -> float:
        """
        Normalize salary to 0-1 scale using actual quartiles from HESA data.
        
        Args:
            salary: The salary to normalize
            lower_q: Lower quartile (25th percentile) for the subject area
            median: Median (50th percentile) for the subject area
            upper_q: Upper quartile (75th percentile) for the subject area
            
        Returns:
            Normalized score between 0.0 and 1.0
        """
        if not salary or salary <= 0:
            return 0.5  # Neutral score if no salary data
        
        # If we have quartiles, use them for normalization
        if lower_q and median and upper_q and lower_q < upper_q:
            # Normalize based on quartiles:
            # - Below lower quartile: 0.0 to 0.25
            # - Between lower and median: 0.25 to 0.5
            # - Between median and upper: 0.5 to 0.75
            # - Above upper quartile: 0.75 to 1.0
            
            if salary < lower_q:
                # Below lower quartile - linear scale from 0 to 0.25
                ratio = salary / lower_q if lower_q > 0 else 0
                return min(0.25, ratio * 0.25)
            elif salary < median:
                # Between lower quartile and median - linear scale from 0.25 to 0.5
                range_size = median - lower_q
                if range_size > 0:
                    ratio = (salary - lower_q) / range_size
                    return 0.25 + (ratio * 0.25)
                return 0.5
            elif salary < upper_q:
                # Between median and upper quartile - linear scale from 0.5 to 0.75
                range_size = upper_q - median
                if range_size > 0:
                    ratio = (salary - median) / range_size
                    return 0.5 + (ratio * 0.25)
                return 0.75
            else:
                # Above upper quartile - linear scale from 0.75 to 1.0
                # Use upper quartile as base, extend to 1.5x upper quartile for max score
                max_salary = upper_q * 1.5
                if max_salary > upper_q:
                    range_size = max_salary - upper_q
                    if range_size > 0:
                        ratio = min(1.0, (salary - upper_q) / range_size)
                        return 0.75 + (ratio * 0.25)
                return 1.0
        
        # Fallback: Use default normalization if quartiles not available
        # This maintains backward compatibility
        return min(1.0, max(0.0, (salary - 20000) / 40000)) if salary else 0.5
    
    def calculate_score(self, course: Dict[str, Any], student_data: Dict[str, Any]) -> float:
        """
        Calculate employability score using dynamic salary quartiles based on student's best subject.
        
        The salary normalization uses actual HESA data quartiles for the student's highest-grade
        subject's CAH code, rather than hardcoded ranges.
        """
        employability = course.get('employability', {})
        
        if not employability:
            return 0.5
        
        # Get employment rate (0-100%)
        employment_rate = employability.get('employmentRate', 50)
        
        # Get average salary from course data
        avg_salary = employability.get('averageSalary', 30000)
        
        # Get CAH3 code for student's best subject
        cah3_code = self._get_best_subject_cah3_code(student_data)
        
        # Get salary quartiles for that CAH3 code
        salary_quartiles = None
        if cah3_code:
            salary_quartiles = self._get_salary_quartiles_for_cah3(cah3_code)
        
        # Normalize salary using actual quartiles (or fallback to default)
        if salary_quartiles:
            lower_q, median, upper_q = salary_quartiles
            salary_score = self._normalize_salary_score(avg_salary, lower_q, median, upper_q)
        else:
            # Fallback to default normalization if quartiles not available
            salary_score = min(1.0, (avg_salary - 20000) / 40000) if avg_salary else 0.5
        
        # Combine employment rate and salary (70% employment, 30% salary)
        return (employment_rate / 100) * 0.7 + salary_score * 0.3
