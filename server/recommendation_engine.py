"""
Advanced recommendation engine that matches students with university courses
based on multiple weighted criteria including academic fit, preferences, and compatibility

Uses composition pattern with separate scorer components
Implements Top-K heap algorithm for efficient recommendation selection
"""

from typing import List, Dict, Any
import heapq
import json
from scoring_components import (
    SubjectMatchScorer, GradeMatchScorer, PreferenceMatchScorer,
    RankingScorer, EmployabilityScorer
)

class RecommendationEngine:
    """
    Advanced recommendation engine that matches students with university courses
    based on multiple weighted criteria including academic fit, preferences, and compatibility
    
    Uses composition pattern with separate scorer components
    Implements Top-K heap algorithm for efficient recommendation selection
    """
    
    def __init__(self):
        # Weight configuration for different criteria
        # Increased subject_match weight to better reflect subject diversity
        self.weights = {
            'subject_match': 0.35,      # A-level subject alignment (increased to prioritize diverse matches)
            'grade_match': 0.25,        # Predicted grades vs requirements
            'preference_match': 0.15,   # Student preferences (location, budget, etc.)
            'university_ranking': 0.15,  # University prestige/ranking
            'employability': 0.10       # Graduate employment prospects
        }
        
        # Composition: Use separate scorer components (OOP composition pattern)
        if SubjectMatchScorer:
            self.subject_scorer = SubjectMatchScorer()
            self.grade_scorer = GradeMatchScorer()
            self.preference_scorer = PreferenceMatchScorer()
            self.ranking_scorer = RankingScorer()
            self.employability_scorer = EmployabilityScorer()
        else:
            # Fallback to direct methods if components not available
            self.subject_scorer = None
            self.grade_scorer = None
            self.preference_scorer = None
            self.ranking_scorer = None
            self.employability_scorer = None
        
        # Grade conversion mapping (kept for backward compatibility)
        self.grade_values = {
            'A*': 8, 'A': 7, 'B': 6, 'C': 5, 'D': 4, 'E': 3, 'U': 0
        }
        
        # UK regions for location matching (kept for backward compatibility)
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
        
        # Subject mappings for finding related courses (used in subject matching)
        self.subject_mappings = {
            'english language': ['english', 'literature', 'language', 'writing', 'linguistics', 'humanities'],
            'english literature': ['english', 'literature', 'language', 'writing', 'humanities'],
            'philosophy': ['philosophy', 'ethics', 'theology', 'religious studies', 'politics', 'humanities', 'philosophical'],
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
        
        # Generic false positive prevention: terms that are too generic to match alone
        # These terms need to be part of a longer phrase or matched with specific subjects
        self.generic_terms = {'science', 'studies', 'business', 'management', 'technology', 'design', 'art'}
        
        # Subjects that can legitimately match generic terms (e.g., "computer science" can match "science")
        # This is a more generic approach - checks if the student subject contains the generic term
        # or if the generic term is part of a compound subject name
        self.legitimate_generic_matches = {
            'science': lambda subj: 'science' in subj.lower() or subj.lower() in ['physics', 'chemistry', 'biology'],
            'studies': lambda subj: 'studies' in subj.lower(),
            'business': lambda subj: 'business' in subj.lower() or 'economics' in subj.lower(),
            'management': lambda subj: 'business' in subj.lower() or 'management' in subj.lower(),
            'technology': lambda subj: 'technology' in subj.lower() or 'engineering' in subj.lower(),
            'design': lambda subj: 'design' in subj.lower() or 'art' in subj.lower(),
            'art': lambda subj: 'art' in subj.lower() or 'design' in subj.lower()
        }
        
        # Career interests data loaded from database (cached)
        # Load career interests using CAH-based mapping (replaces old keyword system)
        self.course_career_mapping = self._get_course_career_mapping()
        self._load_career_interests_from_db()
    
    def get_recommendations(self, a_level_subjects: List[str], 
                          predicted_grades: Dict[str, str],
                          preferences: Dict[str, Any],
                          criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate personalized course recommendations using Top-K heap algorithm
        
        Uses efficient heap-based selection for O(N log K) complexity instead of O(N log N)
        This is a Group A advanced algorithm implementation.
        
        Enhanced to consider ALL student subjects, not just required ones, to provide
        diverse recommendations based on the full subject profile.
        
        Prioritizes courses related to the student's highest predicted grade, assuming
        they would be most successful in that subject area, unless career interests are specified.
        
        Args:
            a_level_subjects: List of A-level subjects taken
            predicted_grades: Dictionary of subject -> predicted grade
            preferences: Student preferences (location, budget, etc.)
            criteria: Additional search criteria
            
        Returns:
            List of top 50 recommended courses with match scores
        """
        # Get all courses from database
        courses = self._get_all_courses()
        
        # Get student ID from criteria or preferences
        student_id = criteria.get('student_id') or preferences.get('student_id')
        
        # Identify highest predicted grade and subject
        # This assumes student would be most successful in their highest-graded subject
        highest_grade_subject = self._get_highest_grade_subject(predicted_grades)
        
        # Check if student has specified career interests that override grade-based prioritization
        has_career_interests = self._has_career_interests(preferences, criteria)
        
        # Prepare student data for scoring components
        student_data = {
            'aLevelSubjects': a_level_subjects,
            'predictedGrades': predicted_grades,
            'preferences': preferences,
            'highestGradeSubject': highest_grade_subject,
            'hasCareerInterests': has_career_interests
        }
        
        # Top-K heap selection algorithm (Group A: Advanced algorithm)
        k = 100  # Increased to 100 recommendations to show more diverse options
        heap = []  # Min-heap: stores (score, course_data) tuples
        # Use index to break ties when scores are equal (avoids dict comparison error)
        
        for idx, course in enumerate(courses):
            match_score = self._calculate_match_score(
                course, a_level_subjects, predicted_grades, preferences, criteria
            )
            
            # Lower threshold to show more courses, including close matches
            # This allows courses with ABB to show up even if they require slightly higher grades
            if match_score > 0.05:  # Very low threshold to show almost all courses
                # Use negative score for min-heap (we want max scores)
                # Heap stores (-score, index, course) so smallest negative = largest positive
                # Index breaks ties and prevents dict comparison
                if len(heap) < k:
                    # Heap not full, add course
                    heapq.heappush(heap, (-match_score, idx, course))
                elif match_score > -heap[0][0]:
                    # Current course is better than worst in heap, replace it
                    heapq.heapreplace(heap, (-match_score, idx, course))
        
        # Convert heap to sorted list (descending by score)
        # Heap is min-heap with negative scores, so we reverse to get descending order
        sorted_courses = sorted(heap, reverse=True)
        
        # Batch enrich all courses at once for better performance
        # This avoids N+1 query problem
        courses_to_enrich = [course for _, _, course in sorted_courses]
        enriched_courses_map = self._batch_enrich_courses_with_hesa_data(courses_to_enrich)
        
        # Get unique universities for best course lookup
        unique_universities = set()
        for _, _, course in sorted_courses:
            uni_name = course.get('university', {}).get('name')
            if uni_name:
                unique_universities.add(uni_name)
        
        # Batch fetch best courses for all universities
        best_courses_map = {}
        for uni_name in unique_universities:
            best_course = self._get_best_course_for_university(uni_name)
            if best_course:
                best_courses_map[uni_name] = best_course
        
        # Add diversity bonus: prioritize courses that match different subject combinations
        # This ensures varied recommendations for students with diverse subject profiles
        subject_diversity_bonus = {}
        highest_grade_bonus = {}  # Bonus for courses related to highest-graded subject
        career_interest_bonus = {}  # Bonus for courses matching career interests
        student_subjects_normalized = {s.lower().strip() for s in a_level_subjects}
        
        # Get career interests for matching using CAH-based mapping
        career_interests = preferences.get('careerInterests', [])
        
        # Get course-to-career mapping using CAH codes instead of keyword matching
        course_career_mapping = self._get_course_career_mapping()
        
        # Normalize highest grade subject for matching
        highest_grade_subject_normalized = None
        if highest_grade_subject and not has_career_interests:
            highest_grade_subject_normalized = highest_grade_subject.lower().strip()
        
        for neg_score, idx, course in sorted_courses:
            course_name = course.get('name', '').lower()
            course_id = course.get('course_id')
            
            # Count how many different student subjects this course relates to
            # Use strict matching to avoid false positives
            matching_count = 0
            matches_highest_grade = False
            course_name_words = set(course_name.replace('-', ' ').replace('_', ' ').replace('university', '').replace('of', '').split())
            
            for stud_subj in student_subjects_normalized:
                matched = False
                # Check 1: Exact subject name as whole word
                stud_subj_words = stud_subj.split()
                for word in course_name_words:
                    if len(word) > 2:
                        if stud_subj == word or (len(stud_subj_words) > 0 and stud_subj_words[0] == word):
                            matching_count += 1
                            matched = True
                            # Check if this matches the highest-graded subject
                            if highest_grade_subject_normalized and stud_subj == highest_grade_subject_normalized:
                                matches_highest_grade = True
                            break
                
                # Check 2: Subject mappings (only legitimate relationships)
                if not matched and stud_subj in self.subject_mappings:
                    for related_term in self.subject_mappings[stud_subj]:
                        # Only match longer, specific terms
                        if len(related_term) > 3:
                            if related_term in course_name_words or related_term in course_name:
                                # Generic check to prevent false positives
                                if self._is_legitimate_match(related_term, stud_subj):
                                    matching_count += 1
                                    matched = True
                                    # Check if this subject is the highest-graded one
                                    if highest_grade_subject_normalized and stud_subj == highest_grade_subject_normalized:
                                        matches_highest_grade = True
                                    break
            
            # Give bonus for courses matching multiple subjects (encourages diversity)
            # This ensures students with Maths + English + Philosophy get varied recommendations
            if matching_count > 1:
                subject_diversity_bonus[course_id] = min(0.15, (matching_count - 1) * 0.05)
            
            # Give significant bonus for courses related to highest-graded subject
            # This assumes student would be most successful in their strongest subject
            if matches_highest_grade and not has_career_interests:
                highest_grade_bonus[course_id] = 0.25  # Strong bonus for highest-grade subject
            
            # Give STRONG bonus for courses matching career interests using CAH mapping
            if has_career_interests and career_interests:
                course_matches_interest = False
                course_career_interests = course_career_mapping.get(course_id, set())
                
                # Check if any of the course's career interests match student's interests
                for student_interest in career_interests:
                    if student_interest in course_career_interests:
                        course_matches_interest = True
                        career_interest_bonus[course_id] = 0.4  # Strong bonus for career match
                        break
                
                # No additional conflict detection needed - CAH mapping is precise
        
        recommendations = []
        for neg_score, idx, course in sorted_courses:
            match_score = -neg_score  # Convert back to positive
            course_id = course.get('course_id')
            course_name_lower = course.get('name', '').lower()
            
            # CAREER INTEREST FILTERING: If career interests specified, only show matching courses
            if has_career_interests and career_interests:
                course_career_interests = course_career_mapping.get(course_id, set())
                
                # Check if course matches any of the student's career interests
                course_matches_career = any(interest in course_career_interests for interest in career_interests)
                
                # If no match, skip this course
                if not course_matches_career:
                    continue
                
                if not course_matches_career:
                    # Course doesn't match career interests - check if it conflicts
                # Career filtering already handled above using CAH mapping
                # No additional conflict checking needed
                    
                    if should_filter:
                        continue  # Skip this course - don't include in recommendations
                    
                    # If not conflicting but still doesn't match, filter it out completely
                    # NO EXCEPTIONS: When career interests are specified, only show matching courses
                    continue  # Skip this course - don't include in recommendations
            
            # Apply diversity bonus if course matches multiple subjects
            # BUT only if course matches career interests (when specified)
            if course_id in subject_diversity_bonus:
                if has_career_interests and career_interests:
                    # Only apply diversity bonus if course matches career interests
                    if course_id in career_interest_bonus:
                        match_score = min(match_score + subject_diversity_bonus[course_id], 1.0)
                else:
                    # No career interests specified - apply diversity bonus normally
                    match_score = min(match_score + subject_diversity_bonus[course_id], 1.0)
            
            # Apply highest-grade subject bonus (prioritizes courses in strongest subject)
            # BUT only if no career interests are specified (career interests override grade-based prioritization)
            if course_id in highest_grade_bonus and not has_career_interests:
                match_score = min(match_score + highest_grade_bonus[course_id], 1.0)
            
            # Apply career interest bonus (STRONG priority - overrides grade-based prioritization)
            # This ensures courses matching career interests rank higher than subject-based matches
            if course_id in career_interest_bonus:
                match_score = min(match_score + career_interest_bonus[course_id], 1.0)
            
            # FINAL STRICT FILTER: If career interests are specified, ONLY show courses that match
            # This is the final gate - no exceptions for non-matching courses
            # CRITICAL: This must happen BEFORE adding to recommendations list
            if has_career_interests and career_interests:
                course_name_for_check = course.get('name', '').lower()
                
                # CRITICAL CHECK: Explicitly filter out Computer Science, Physics, etc. when Business & Finance is selected
                # This must happen FIRST, before any other checks
                has_business_finance_final = any(
                    ('business' in interest.lower() and 'finance' in interest.lower()) or
                    (interest.lower() == 'business') or 
                    (interest.lower() == 'finance')
                    for interest in career_interests
                )
                
                if has_business_finance_final:
                    # Explicitly filter out these conflicting courses - NO EXCEPTIONS
                    conflicting_course_terms = ['computer science', 'computing', 'physics', 'chemistry', 'biology', 
                                               'engineering', 'technology', 'software', 'electrical', 'mechanical',
                                               'computer', 'tech']
                    if any(term in course_name_for_check for term in conflicting_course_terms):
                        # Special exception: "Business Information Systems" or similar should NOT be filtered
                        if 'business' in course_name_for_check or 'finance' in course_name_for_check:
                            pass  # Allow it - it's a business-related course
                        else:
                            # DEFINITELY filter out - this is a conflicting course (e.g., Computer Science)
                            continue  # Skip this course - don't include in recommendations
                
                # First: Check if course matches career interests
                course_matches_career = course_id in career_interest_bonus
                
                if not course_matches_career:
                    # Course doesn't match career interests - filter it out completely
                    # No exceptions - if career interests are specified, only show matching courses
                    # This ensures Physics/Computer Science are NOT shown when Business & Finance is selected
                    continue  # Skip this course - don't include in recommendations
                
                # Career filtering already completed above - no additional checks needed
            
            # Check if student meets all grade requirements
            meets_all_requirements = self._meets_all_grade_requirements(
                course, predicted_grades
            )
            
            # Get enriched course from batch (or use original if not enriched)
            enriched_course = enriched_courses_map.get(course_id, course)
            
            # Get the best course for this university (from batch)
            university_name = enriched_course.get('university', {}).get('name')
            best_course = None
            if university_name and university_name in best_courses_map:
                best_course = best_courses_map[university_name]
                # Only include if it's a different course
                if best_course and best_course.get('course_id') == enriched_course.get('course_id'):
                    best_course = None  # Don't show if it's the same course
            
            recommendation = {
                'course': enriched_course,
                'matchScore': match_score,
                'meetsRequirements': meets_all_requirements,
                'reasons': self._get_match_reasons(course, a_level_subjects, predicted_grades, preferences)
            }
            
            # Add best course info if available and different
            if best_course:
                recommendation['universityBestCourse'] = best_course
            
            recommendations.append(recommendation)
        
        # Re-sort by final match score (after diversity bonus)
        recommendations.sort(key=lambda x: x['matchScore'], reverse=True)
        
        # Return top 50 to ensure variety
        return recommendations[:50]
    
    def _get_best_course_for_university(self, university_name: str) -> Dict[str, Any]:
        """
        Get the best course (highest employability_score) for a given university
        
        Returns the course with the highest employability score from the university,
        which represents the university's most famous/strongest course.
        """
        if not university_name:
            return None
        
        try:
            from database_helper import get_db_connection
            from psycopg2.extras import RealDictCursor
            
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get the course with highest employability_score from this university
                    cur.execute("""
                        SELECT 
                            c.course_id, c.name, c.annual_fee, c.ucascourseid,
                            c.employability_score, c.typical_offer_text,
                            c.course_url,
                            u.university_id, u.name as university_name, u.region,
                            u.rank_overall, u.website_url
                        FROM course c
                        JOIN university u ON c.university_id = u.university_id
                        WHERE u.name = %s
                          AND c.employability_score IS NOT NULL
                        ORDER BY c.employability_score DESC NULLS LAST
                        LIMIT 1
                    """, (university_name,))
                    
                    best_course_row = cur.fetchone()
                    
                    if best_course_row:
                        best_course = dict(best_course_row)
                        
                        # Get entry requirements for the best course
                        cur.execute("""
                            SELECT s.subject_id, s.subject_name, csr.grade_req
                            FROM course_subject_requirement csr
                            JOIN subject s ON csr.cah_code = s.cah_code
                            WHERE csr.course_id = %s
                        """, (best_course['course_id'],))
                        
                        requirements = {}
                        subjects = []
                        for req_row in cur.fetchall():
                            req = dict(req_row)
                            subject_id = req['subject_id']
                            subject_name = req.get('subject_name', subject_id)
                            requirements[subject_id] = req['grade_req']
                            requirements[subject_name] = req['grade_req']
                            subjects.append(subject_id)
                            subjects.append(subject_name)
                        
                        # Format the best course
                        best_course['entryRequirements'] = {
                            'subjects': subjects,
                            'grades': requirements
                        }
                        best_course['fees'] = {
                            'uk': best_course.get('annual_fee', 0)
                        }
                        best_course['university'] = {
                            'name': best_course['university_name'],
                            'region': best_course.get('region'),
                            'ranking': {
                                'overall': best_course.get('rank_overall')
                            },
                            'websiteUrl': best_course.get('website_url')
                        }
                        best_course['courseUrl'] = best_course.get('course_url')
                        best_course['employability'] = {
                            'employmentRate': best_course.get('employability_score', 0),
                            'averageSalary': 30000  # Default
                        }
                        
                        # Enrich with HESA data if available
                        best_course = self._enrich_course_with_hesa_data(best_course)
                        
                        return best_course
            
            return None
            
        except Exception as e:
            print(f"Warning: Could not get best course for university {university_name}: {e}")
            return None
    
    def _batch_enrich_courses_with_hesa_data(self, courses: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Batch enrich multiple courses with HESA data for better performance
        Returns a dictionary mapping course_id -> enriched_course
        """
        if not courses:
            return {}
        
        try:
            from database_helper import get_db_connection
            from psycopg2.extras import RealDictCursor
            
            enriched_map = {}
            course_ids = [c.get('course_id') for c in courses if c.get('course_id')]
            
            if not course_ids:
                return {c.get('course_id'): c for c in courses}
            
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Batch fetch HESA identifiers for all courses
                    cur.execute("""
                        SELECT course_id, pubukprn, kiscourseid, kismode
                        FROM course
                        WHERE course_id = ANY(%s)
                    """, (course_ids,))
                    
                    hesa_links = {row['course_id']: row for row in cur.fetchall()}
                    
                    # Get all unique (pubukprn, kiscourseid, kismode) combinations
                    hesa_keys = []
                    hesa_keys_set = set()
                    for row in hesa_links.values():
                        if row.get('pubukprn') and row.get('kiscourseid'):
                            key = (row['pubukprn'], row['kiscourseid'], row.get('kismode') or '01')
                            if key not in hesa_keys_set:
                                hesa_keys.append(key)
                                hesa_keys_set.add(key)
                    
                    if not hesa_keys:
                        # No HESA links, return courses as-is
                        return {c.get('course_id'): c for c in courses}
                    
                    # Batch fetch all HESA data using temp table for better performance
                    # This is much faster than VALUES clause for large datasets
                    employment_data = {}
                    salary_data = {}
                    leo3_data = {}
                    job_types_data = {}
                    entry_stats_data = {}
                    
                    if hesa_keys and len(hesa_keys) > 0:
                        # Create temp table for batch lookups
                        cur.execute("""
                            CREATE TEMP TABLE temp_hesa_lookup (
                                pubukprn VARCHAR(10),
                                kiscourseid VARCHAR(50),
                                kismode VARCHAR(2),
                                PRIMARY KEY (pubukprn, kiscourseid, kismode)
                            ) ON COMMIT DROP
                        """)
                        
                        # Insert keys in batches for better performance
                        batch_size = 500
                        for i in range(0, len(hesa_keys), batch_size):
                            batch = hesa_keys[i:i+batch_size]
                            cur.executemany("""
                                INSERT INTO temp_hesa_lookup (pubukprn, kiscourseid, kismode)
                                VALUES (%s, %s, %s)
                                ON CONFLICT DO NOTHING
                            """, batch)
                        
                        # Create index on temp table for faster joins
                        cur.execute("""
                            CREATE INDEX idx_temp_hesa_lookup ON temp_hesa_lookup(pubukprn, kiscourseid, kismode)
                        """)
                        
                        # Batch fetch employment data
                        cur.execute("""
                            SELECT e.pubukprn, e.kiscourseid, e.kismode,
                                   e.work, e.study, e.unemp, e.workstudy,
                                   e.emppop, e.empagg
                            FROM hesa_employment e
                            INNER JOIN temp_hesa_lookup t ON 
                                e.pubukprn = t.pubukprn AND 
                                e.kiscourseid = t.kiscourseid AND 
                                e.kismode = t.kismode
                        """)
                        for row in cur.fetchall():
                            key = (row['pubukprn'], row['kiscourseid'], row['kismode'])
                            employment_data[key] = dict(row)
                        
                        # Batch fetch salary data
                        cur.execute("""
                            SELECT g.pubukprn, g.kiscourseid, g.kismode,
                                   g.instmed, g.instlwr, g.instupr
                            FROM hesa_gosalary g
                            INNER JOIN temp_hesa_lookup t ON 
                                g.pubukprn = t.pubukprn AND 
                                g.kiscourseid = t.kiscourseid AND 
                                g.kismode = t.kismode
                        """)
                        for row in cur.fetchall():
                            key = (row['pubukprn'], row['kiscourseid'], row['kismode'])
                            salary_data[key] = dict(row)
                        
                        # Batch fetch LEO3 data
                        cur.execute("""
                            SELECT l.pubukprn, l.kiscourseid, l.kismode,
                                   l.leo3instmed, l.leo3instlq, l.leo3instuq
                            FROM hesa_leo3 l
                            INNER JOIN temp_hesa_lookup t ON 
                                l.pubukprn = t.pubukprn AND 
                                l.kiscourseid = t.kiscourseid AND 
                                l.kismode = t.kismode
                        """)
                        for row in cur.fetchall():
                            key = (row['pubukprn'], row['kiscourseid'], row['kismode'])
                            leo3_data[key] = dict(row)
                        
                        # Note: hesa_joblist contains job percentages by category, not individual job listings
                        # Skip job types enrichment for now
                        
                        # Batch fetch entry statistics
                        cur.execute("""
                            SELECT en.pubukprn, en.kiscourseid, en.kismode,
                                   en.alevel, en.access, en.degree, en.foundation, en.noquals, en.other, en.entpop
                            FROM hesa_entry en
                            INNER JOIN temp_hesa_lookup t ON 
                                en.pubukprn = t.pubukprn AND 
                                en.kiscourseid = t.kiscourseid AND 
                                en.kismode = t.kismode
                        """)
                        for row in cur.fetchall():
                            key = (row['pubukprn'], row['kiscourseid'], row['kismode'])
                            entry_stats_data[key] = dict(row)
                    
                    # Enrich each course with batch-fetched data
                    for course in courses:
                        course_id = course.get('course_id')
                        if not course_id:
                            enriched_map[course_id] = course
                            continue
                        
                        enriched_course = course.copy()
                        hesa_link = hesa_links.get(course_id)
                        
                        if hesa_link and hesa_link.get('pubukprn') and hesa_link.get('kiscourseid'):
                            pubukprn = hesa_link['pubukprn']
                            kiscourseid = hesa_link['kiscourseid']
                            kismode = hesa_link.get('kismode') or '01'
                            key = (pubukprn, kiscourseid, kismode)
                            
                            # Add employment outcomes
                            if key in employment_data:
                                emp = employment_data[key]
                                enriched_course['employmentOutcomes'] = {
                                    'employed': emp.get('work'),
                                    'studying': emp.get('study'),
                                    'unemployed': emp.get('unemp'),
                                    'workingAndStudying': emp.get('workstudy'),
                                    'totalGraduates': emp.get('emppop')
                                }
                                
                                # Update employability
                                if emp.get('work') and emp.get('study') and emp.get('unemp'):
                                    total = emp['work'] + emp['study'] + emp['unemp']
                                    if total > 0:
                                        employment_rate = int((emp['work'] / total) * 100)
                                        enriched_course.setdefault('employability', {})['employmentRate'] = employment_rate
                            
                            # Add salary data
                            if key in salary_data:
                                sal = salary_data[key]
                                enriched_course['salaryData'] = {
                                    'medianSalary': sal.get('instmed'),
                                    'lowerQuartile': sal.get('instlwr'),
                                    'upperQuartile': sal.get('instupr')
                                }
                                if sal.get('instmed'):
                                    enriched_course.setdefault('employability', {})['averageSalary'] = sal['instmed']
                            
                            # Add earnings data
                            if key in leo3_data:
                                leo = leo3_data[key]
                                enriched_course['earningsData'] = {
                                    'median3Years': leo.get('leo3instmed'),
                                    'lowerQuartile3Years': leo.get('leo3instlq'),
                                    'upperQuartile3Years': leo.get('leo3instuq')
                                }
                                if not enriched_course.get('employability', {}).get('averageSalary') and leo.get('leo3instmed'):
                                    enriched_course.setdefault('employability', {})['averageSalary'] = leo['leo3instmed']
                            
                            # Note: Skip job types - data structure mismatch
                            
                            # Add entry statistics
                            if key in entry_stats_data:
                                ent = entry_stats_data[key]
                                enriched_course['entryStatistics'] = {
                                    'aLevelStudents': ent.get('alevel'),
                                    'accessStudents': ent.get('access'),
                                    'degreeStudents': ent.get('degree'),
                                    'foundationStudents': ent.get('foundation'),
                                    'noQualifications': ent.get('noquals'),
                                    'otherQualifications': ent.get('other'),
                                    'totalEntryPopulation': ent.get('entpop')
                                }
                        
                        enriched_map[course_id] = enriched_course
            
            return enriched_map
            
        except Exception as e:
            print(f"Warning: Could not batch enrich courses with HESA data: {e}")
            # Return courses as-is if enrichment fails
            return {c.get('course_id'): c for c in courses}
    
    def _enrich_course_with_hesa_data(self, course: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich course data with HESA employment, salary, and job outcomes"""
        try:
            from database_helper import get_db_connection
            from psycopg2.extras import RealDictCursor
            
            course_id = course.get('course_id')
            
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get HESA identifiers from course table (if stored)
                    cur.execute("""
                        SELECT pubukprn, kiscourseid, kismode
                        FROM course
                        WHERE course_id = %s
                    """, (course_id,))
                    
                    course_row = cur.fetchone()
                    
                    # First try to get from course dict (if already loaded)
                    pubukprn = course.get('pubukprn')
                    kiscourseid = course.get('kiscourseid')
                    kismode = course.get('kismode') or '01'
                    
                    # If not in course dict, try database
                    if not pubukprn:
                        if course_row and course_row.get('pubukprn'):
                            # Use stored HESA identifiers from database
                            pubukprn = course_row['pubukprn']
                            kiscourseid = course_row['kiscourseid']
                            kismode = course_row['kismode'] or '01'  # Default to full-time
                        else:
                            # Fallback: try to find by name matching
                            course_name = course.get('name', '')
                            university_name = course.get('university', {}).get('name', '')
                            cur.execute("""
                                SELECT kc.pubukprn, kc.kiscourseid, kc.kismode
                                FROM hesa_kiscourse kc
                                JOIN hesa_institution i ON kc.pubukprn = i.pubukprn
                                WHERE kc.title ILIKE %s 
                                  AND i.first_trading_name ILIKE %s
                                  AND kc.kismode = '01'
                                LIMIT 1
                            """, (f'%{course_name.split(" - ")[0] if " - " in course_name else course_name}%', f'%{university_name}%'))
                            
                            kiscourse_match = cur.fetchone()
                            if not kiscourse_match:
                                return course  # Can't find HESA data, return course as-is
                            
                            pubukprn = kiscourse_match['pubukprn']
                            kiscourseid = kiscourse_match['kiscourseid']
                            kismode = kiscourse_match['kismode']
                    
                    if pubukprn and kiscourseid:
                        # Get employment outcomes
                        cur.execute("""
                            SELECT 
                                work, study, unemp, workstudy,
                                emppop, empagg
                            FROM hesa_employment
                            WHERE pubukprn = %s AND kiscourseid = %s AND kismode = %s
                            LIMIT 1
                        """, (pubukprn, kiscourseid, kismode))
                        employment = cur.fetchone()
                        
                        # Get salary data
                        cur.execute("""
                            SELECT 
                                instmed, instlwr, instupr
                            FROM hesa_gosalary
                            WHERE pubukprn = %s AND kiscourseid = %s AND kismode = %s
                            LIMIT 1
                        """, (pubukprn, kiscourseid, kismode))
                        salary = cur.fetchone()
                        
                        # Get LEO3 earnings (3 years after graduation)
                        cur.execute("""
                            SELECT 
                                leo3instmed, leo3instlq, leo3instuq
                            FROM hesa_leo3
                            WHERE pubukprn = %s AND kiscourseid = %s AND kismode = %s
                            LIMIT 1
                        """, (pubukprn, kiscourseid, kismode))
                        leo3 = cur.fetchone()
                        
                        # Note: hesa_joblist contains job percentages by category, not individual job listings
                        # Skip job types for now
                        
                        # Get entry qualification statistics (aggregated)
                        cur.execute("""
                            SELECT 
                                alevel, access, degree, foundation, noquals, other,
                                entpop
                            FROM hesa_entry
                            WHERE pubukprn = %s AND kiscourseid = %s AND kismode = %s
                            LIMIT 1
                        """, (pubukprn, kiscourseid, kismode))
                        entry_stats = cur.fetchone()
                        
                        # Enrich course with this data
                        course['employmentOutcomes'] = {
                            'employed': employment['work'] if employment and employment.get('work') else None,
                            'studying': employment['study'] if employment and employment.get('study') else None,
                            'unemployed': employment['unemp'] if employment and employment.get('unemp') else None,
                            'workingAndStudying': employment['workstudy'] if employment and employment.get('workstudy') else None,
                            'totalGraduates': employment['emppop'] if employment and employment.get('emppop') else None
                        } if employment else None
                        
                        course['salaryData'] = {
                            'medianSalary': salary['instmed'] if salary and salary.get('instmed') else None,
                            'lowerQuartile': salary['instlwr'] if salary and salary.get('instlwr') else None,
                            'upperQuartile': salary['instupr'] if salary and salary.get('instupr') else None
                        } if salary else None
                        
                        course['earningsData'] = {
                            'median3Years': leo3['leo3instmed'] if leo3 and leo3.get('leo3instmed') else None,
                            'lowerQuartile3Years': leo3['leo3instlq'] if leo3 and leo3.get('leo3instlq') else None,
                            'upperQuartile3Years': leo3['leo3instuq'] if leo3 and leo3.get('leo3instuq') else None
                        } if leo3 else None
                        
                        # Note: Skip job types - data structure mismatch
                        
                        course['entryStatistics'] = {
                            'aLevelStudents': entry_stats['alevel'] if entry_stats and entry_stats.get('alevel') else None,
                            'accessStudents': entry_stats['access'] if entry_stats and entry_stats.get('access') else None,
                            'degreeStudents': entry_stats['degree'] if entry_stats and entry_stats.get('degree') else None,
                            'foundationStudents': entry_stats['foundation'] if entry_stats and entry_stats.get('foundation') else None,
                            'noQualifications': entry_stats['noquals'] if entry_stats and entry_stats.get('noquals') else None,
                            'otherQualifications': entry_stats['other'] if entry_stats and entry_stats.get('other') else None,
                            'totalEntryPopulation': entry_stats['entpop'] if entry_stats and entry_stats.get('entpop') else None
                        } if entry_stats else None
                        
                        # Update employability with real data
                        if employment and employment.get('work') and employment.get('study') and employment.get('unemp'):
                            total = employment['work'] + employment['study'] + employment['unemp']
                            if total > 0:
                                employment_rate = int((employment['work'] / total) * 100)
                                course['employability']['employmentRate'] = employment_rate
                        
                        if salary and salary.get('instmed'):
                            course['employability']['averageSalary'] = salary['instmed']
                        elif leo3 and leo3.get('leo3instmed'):
                            course['employability']['averageSalary'] = leo3['leo3instmed']
            
            return course
            
        except Exception as e:
            # If enrichment fails, return course as-is
            print(f"Warning: Could not enrich course with HESA data: {e}")
            return course
    
    def _meets_all_grade_requirements(self, course: Dict[str, Any], 
                                     predicted_grades: Dict[str, str]) -> bool:
        """Check if student meets all grade requirements for the course"""
        required_grades = course.get('entryRequirements', {}).get('grades', {})
        
        if not required_grades:
            return True  # No requirements = automatically meets
        
        for subject, required_grade in required_grades.items():
            if subject in predicted_grades:
                predicted_grade = predicted_grades[subject]
                required_value = self.grade_values.get(required_grade, 0)
                predicted_value = self.grade_values.get(predicted_grade, 0)
                
                if predicted_value < required_value:
                    return False  # Doesn't meet at least one requirement
        
        return True  # Meets all requirements
    
    def _calculate_match_score(self, course: Dict[str, Any], 
                            a_level_subjects: List[str],
                            predicted_grades: Dict[str, str],
                            preferences: Dict[str, Any],
                            criteria: Dict[str, Any]) -> float:
        """
        Calculate weighted match score for a course using composition pattern
        
        Uses separate scorer components (composition) instead of direct methods
        
        Returns:
            Float between 0 and 1 representing match quality
        """
        # Prepare student data for scorer components
        student_data = {
            'aLevelSubjects': a_level_subjects,
            'predictedGrades': predicted_grades,
            'preferences': preferences
        }
        
        # Use composition: delegate scoring to separate components (if available)
        # Otherwise fall back to direct methods for backward compatibility
        scores = {}
        if self.subject_scorer:
            scores['subject_match'] = self.subject_scorer.calculate_score(course, student_data)
            scores['grade_match'] = self.grade_scorer.calculate_score(course, student_data)
            scores['preference_match'] = self.preference_scorer.calculate_score(course, student_data)
            scores['university_ranking'] = self.ranking_scorer.calculate_score(course, student_data)
            scores['employability'] = self.employability_scorer.calculate_score(course, student_data)
        else:
            # Fallback to direct methods
            scores['subject_match'] = self._calculate_subject_match(course, a_level_subjects)
            scores['grade_match'] = self._calculate_grade_match(course, predicted_grades)
            scores['preference_match'] = self._calculate_preference_match(course, preferences)
            scores['university_ranking'] = self._calculate_ranking_score(course)
            scores['employability'] = self._calculate_employability_score(course)
        
        # Calculate weighted total
        total_score = sum(
            scores[criterion] * weight 
            for criterion, weight in self.weights.items()
        )
        
        return min(total_score, 1.0)  # Cap at 1.0
    
    def _calculate_subject_match(self, course: Dict[str, Any], 
                               a_level_subjects: List[str]) -> float:
        """
        Calculate how well student's subjects match course requirements
        Enhanced to consider ALL student subjects, not just required ones
        """
        required_subjects = course.get('entryRequirements', {}).get('subjects', [])
        course_name = course.get('name', '').lower()
        
        if not a_level_subjects:
            return 0.3  # Student has no subjects, low score
        
        # Normalize subjects for matching (handle both IDs and names)
        # Convert to lowercase for case-insensitive matching
        student_subjects_normalized = {s.lower().strip() for s in a_level_subjects}
        required_subjects_normalized = {s.lower().strip() for s in required_subjects} if required_subjects else set()
        
        # Subject mapping for related fields (e.g., "English Language" -> "English", "Literature")
        subject_mappings = {
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
        
        # Calculate required subject match (existing logic)
        matching_required = set()
        if required_subjects_normalized:
            # Try exact match first
            matching_required = student_subjects_normalized & required_subjects_normalized
            
            # If no exact match, try partial matching
            if not matching_required:
                for req_subj in required_subjects_normalized:
                    for stud_subj in student_subjects_normalized:
                        if req_subj in stud_subj or stud_subj in req_subj:
                            matching_required.add(req_subj)
                            break
        
        # Calculate relevance to ALL student subjects (new logic)
        # This finds courses that are relevant to student's subjects even if not explicitly required
        # BUT only when there's a clear, legitimate relationship
        matching_student_subjects = set()
        course_name_words = set(course_name.replace('-', ' ').replace('_', ' ').replace('university', '').replace('of', '').split())
        
        for stud_subj in student_subjects_normalized:
            # Only match if there's a clear, direct relationship
            # Check 1: Exact subject name appears as a whole word in course name
            # This prevents "science" matching "Business Studies" or "Biology"
            stud_subj_words = stud_subj.split()
            for word in course_name_words:
                if len(word) > 2:
                    # Check if the full subject name or its main word matches
                    if stud_subj == word or (len(stud_subj_words) > 0 and stud_subj_words[0] == word):
                        matching_student_subjects.add(stud_subj)
                        break
            
            # Check 2: Subject mappings for related fields (only legitimate relationships)
            # This is more strict - only match if the related term is a significant part of the course name
            if stud_subj in subject_mappings:
                for related_term in subject_mappings[stud_subj]:
                    # Only match if the related term appears as a whole word or significant phrase
                    # This prevents "science" from matching unrelated courses
                    if len(related_term) > 3:  # Only match terms longer than 3 characters
                        # Check if it's a whole word in the course name
                        if related_term in course_name_words or related_term in course_name:
                            # Generic check to prevent false positives
                            if self._is_legitimate_match(related_term, stud_subj):
                                matching_student_subjects.add(stud_subj)
                                break
        
        # Combine required matches and student subject relevance
        all_matching_subjects = matching_required | matching_student_subjects
        
        # Calculate base score from required subjects match
        if required_subjects_normalized:
            required_match_ratio = len(matching_required) / len(required_subjects_normalized)
        else:
            # No required subjects - use student subject relevance instead
            required_match_ratio = len(matching_student_subjects) / len(student_subjects_normalized) if student_subjects_normalized else 0.5
        
        # Bonus for matching multiple student subjects (encourages diverse recommendations)
        student_subject_bonus = 0.0
        if len(matching_student_subjects) > 0:
            # Give bonus based on how many student subjects match
            # This ensures courses relevant to multiple subjects score higher
            student_subject_bonus = min(0.3, len(matching_student_subjects) * 0.1)
        
        # Bonus for matching ALL required subjects
        if required_subjects_normalized and len(matching_required) == len(required_subjects_normalized):
            required_match_ratio = min(required_match_ratio + 0.2, 1.0)
        elif len(matching_required) > 0:
            # Partial match on required subjects
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
    
    def _calculate_grade_match(self, course: Dict[str, Any], 
                             predicted_grades: Dict[str, str]) -> float:
        """Calculate how well predicted grades match course requirements"""
        required_grades = course.get('entryRequirements', {}).get('grades', {})
        
        if not required_grades:
            # If no grade requirements, give a good score to encourage showing the course
            return 0.7  # Increased from 0.5 to show more courses
        
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
                        subject_score = max(0.001, predicted_value / required_value * 0.05)
                
                total_score += subject_score
                total_weight += 1
        
        # If no matching subjects found, return neutral score
        if total_weight == 0:
            return 0.5
        
        return total_score / total_weight
    
    def _calculate_preference_match(self, course: Dict[str, Any], 
                                  preferences: Dict[str, Any]) -> float:
        """Calculate how well course matches student preferences"""
        score = 0.5  # Start with neutral score
        factors = 0
        
        # Career interests - STRONG priority boost
        career_interests = preferences.get('careerInterests', [])
        if career_interests:
            course_name_lower = course.get('name', '').lower()
            course_matches_career = False
            
            # Map career interests to course keywords
            career_keywords = {
                'Business & Finance': ['business', 'finance', 'accounting', 'economics', 'management', 'banking', 'investment', 'marketing', 'entrepreneurship'],
                'Medicine & Healthcare': ['medicine', 'health', 'nursing', 'pharmacy', 'dentistry', 'veterinary', 'biomedical'],
                'Engineering & Technology': ['engineering', 'technology', 'computer', 'software', 'electrical', 'mechanical', 'civil'],
                'Law': ['law', 'legal', 'jurisprudence', 'criminology'],
                'Education': ['education', 'teaching', 'pedagogy'],
                'Arts & Humanities': ['arts', 'humanities', 'history', 'literature', 'philosophy', 'classics'],
                'Sciences': ['science', 'physics', 'chemistry', 'biology', 'mathematics', 'maths'],
                'Social Sciences': ['sociology', 'psychology', 'politics', 'international relations', 'anthropology'],
                'Creative Arts': ['art', 'design', 'creative', 'fine art', 'graphic design', 'fashion'],
                'Sports & Fitness': ['sports', 'fitness', 'exercise', 'physical education', 'kinesiology']
            }
            
            for interest in career_interests:
                keywords = career_keywords.get(interest, [])
                for keyword in keywords:
                    if keyword in course_name_lower:
                        course_matches_career = True
                        score += 0.5  # Strong boost for career match
                        factors += 1
                        break
                if course_matches_career:
                    break
            
            # Penalty if course doesn't match any career interest
            if not course_matches_career:
                score -= 0.3  # Penalty for not matching career interests
                factors += 1
        
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
        overall_rank = ranking.get('overall')
        subject_rank = ranking.get('subject')
        
        # Handle None values
        overall_rank = overall_rank if overall_rank is not None else 0
        subject_rank = subject_rank if subject_rank is not None else 0
        
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
    
    def _get_highest_grade_subject(self, predicted_grades: Dict[str, str]) -> str:
        """
        Identify the subject with the highest predicted grade.
        Returns the subject name, or None if no grades provided.
        """
        if not predicted_grades:
            return None
        
        highest_grade_value = -1
        highest_grade_subject = None
        
        for subject, grade in predicted_grades.items():
            grade_value = self.grade_values.get(grade, 0)
            if grade_value > highest_grade_value:
                highest_grade_value = grade_value
                highest_grade_subject = subject
        
        return highest_grade_subject
    
    def _has_career_interests(self, preferences: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """
        Check if student has specified career interests that should override
        grade-based prioritization.
        
        Returns True if career interests are specified, False otherwise.
        """
        # Check preferences for career-related fields
        career_fields = ['careerInterest', 'careerInterests', 'preferredCareer', 
                        'careerField', 'desiredCareer', 'careerPath']
        
        for field in career_fields:
            if field in preferences and preferences[field]:
                return True
        
        # Check criteria for career-related fields
        for field in career_fields:
            if field in criteria and criteria[field]:
                return True
        
        # Check for course subject preferences that might indicate career interest
        if 'preferredSubject' in preferences and preferences['preferredSubject']:
            return True
        if 'preferredSubject' in criteria and criteria['preferredSubject']:
            return True
        
        return False
    
    def _is_legitimate_match(self, related_term: str, student_subject: str) -> bool:
        """
        Generic method to check if a related term is a legitimate match for a student subject.
        Prevents false positives by checking if generic terms are part of compound subject names.
        
        Args:
            related_term: The related term from subject mappings (e.g., 'science', 'studies')
            student_subject: The student's subject (e.g., 'computer science', 'business studies')
            
        Returns:
            True if the match is legitimate, False if it's a false positive
        """
        # If the term is not generic, it's always legitimate
        if related_term not in self.generic_terms:
            return True
        
        # For generic terms, check if the student subject legitimately contains it
        if related_term in self.legitimate_generic_matches:
            return self.legitimate_generic_matches[related_term](student_subject)
        
        # Default: if generic term is part of the subject name, it's legitimate
        # (e.g., "computer science" contains "science")
        return related_term in student_subject.lower()
    
    def _load_career_interests_from_db(self):
        """Load career interests from CAH mapping (replaces old keyword system)"""
        # Career interests are now loaded via CAH mapping in _get_course_career_mapping()
        # This method exists for compatibility but no longer loads keywords/conflicts
        try:
            from database_helper import get_db_connection
            from psycopg2.extras import RealDictCursor
            
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get available career interests from CAH mapping
                    cur.execute("""
                        SELECT DISTINCT career_interest_name as interest_name
                        FROM subject_to_career
                        ORDER BY career_interest_name
                    """)
                    
                    career_interests = [row['interest_name'] for row in cur.fetchall()]
                    print(f"Loaded {len(career_interests)} career interests from CAH mapping: {career_interests}")
                    
        except Exception as e:
            print(f"Warning: Could not load career interests: {e}")
            print("Using default career interests")
            career_interests = [
                'Business & Finance', 'Medicine & Healthcare', 'Engineering & Technology',
                'Law', 'Education', 'Arts & Humanities', 'Sciences', 'Social Sciences',
                'Creative Arts', 'Sports & Fitness'
            ]
    
    def _get_course_career_mapping(self):
        """Get mapping of course_id to career interests using CAH codes"""
        try:
            from database_helper import get_db_connection
            from psycopg2.extras import RealDictCursor
            
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get course career interests via CAH mapping
            cursor.execute("""
                SELECT DISTINCT k.kiscourseid as course_id, ccm.career_interest_name
                FROM hesa_kiscourse k
                JOIN hesa_sbj s ON k.kiscourseid = s.kiscourseid
                JOIN subject_to_career ccm ON ccm.cah_code = SUBSTRING(s.sbj FROM 1 FOR 5)
                WHERE k.title IS NOT NULL
            """)
            
            mapping = {}
            for row in cursor.fetchall():
                course_id = row['course_id']
                career = row['career_interest_name']
                if course_id not in mapping:
                    mapping[course_id] = set()
                mapping[course_id].add(career)
            
            cursor.close()
            conn.close()
            
            return mapping
            
        except Exception as e:
            print(f"Error loading course career mapping: {e}")
            return {}
    
    def _get_highest_grade_subject(self, predicted_grades: Dict[str, str]) -> str:
        """Get the subject with the highest predicted grade"""
        if not predicted_grades:
            return None
        
        highest_grade = None
        highest_subject = None
        
        for subject, grade in predicted_grades.items():
            grade_value = self.grade_values.get(grade, 0)
            if highest_grade is None or grade_value > highest_grade:
                highest_grade = grade_value
                highest_subject = subject
        
        return highest_subject
    
    def _get_match_reasons(self, course: Dict[str, Any], 
                          a_level_subjects: List[str],
                          predicted_grades: Dict[str, str],
                          preferences: Dict[str, Any]) -> List[str]:
        """Generate human-readable reasons for the match"""
        reasons = []
        
        # Subject match reasons - check both required and relevant subjects
        required_subjects = course.get('entryRequirements', {}).get('subjects', [])
        course_name = course.get('name', '').lower()
        
        # Find matching required subjects
        matching_required = set(a_level_subjects) & set(required_subjects)
        
        # Find relevant student subjects (even if not required)
        student_subjects_normalized = {s.lower().strip() for s in a_level_subjects}
        relevant_subjects = set()
        course_name_words = set(course_name.replace('-', ' ').replace('_', ' ').split())
        
        # Subject mappings for finding related courses (use full mapping from class)
        subject_mappings = self.subject_mappings
        
        for stud_subj in student_subjects_normalized:
            # Only match if there's a clear, direct relationship
            # Check 1: Exact subject name appears as a whole word
            stud_subj_words = stud_subj.split()
            matched = False
            for word in course_name_words:
                if len(word) > 2:
                    if stud_subj == word or (len(stud_subj_words) > 0 and stud_subj_words[0] == word):
                        for orig_subj in a_level_subjects:
                            if orig_subj.lower().strip() == stud_subj:
                                relevant_subjects.add(orig_subj)
                                matched = True
                                break
                        if matched:
                            break
            
            # Check 2: Subject mappings (only legitimate relationships)
            if not matched and stud_subj in subject_mappings:
                for related_term in subject_mappings[stud_subj]:
                    # Only match longer, specific terms
                    if len(related_term) > 3:
                        if related_term in course_name_words or related_term in course_name:
                            # Generic check to prevent false positives
                            # Use generic term matching logic instead of hardcoded lists
                            if self._is_legitimate_match(related_term, stud_subj):
                                for orig_subj in a_level_subjects:
                                    if orig_subj.lower().strip() == stud_subj:
                                        relevant_subjects.add(orig_subj)
                                        matched = True
                                        break
                                if matched:
                                    break
        
        # Combine both types of matches
        all_matching = matching_required | relevant_subjects
        
        if all_matching:
            if matching_required:
                reasons.append(f"Matches your A-level subjects: {', '.join(matching_required)}")
            if relevant_subjects and relevant_subjects != matching_required:
                reasons.append(f"Relevant to your subjects: {', '.join(relevant_subjects - matching_required)}")
        
        # Add reason if course matches highest-graded subject
        highest_grade_subject = self._get_highest_grade_subject(predicted_grades)
        has_career_interests = self._has_career_interests(preferences, {})
        if highest_grade_subject and not has_career_interests:
            highest_grade_normalized = highest_grade_subject.lower().strip()
            course_name_lower = course.get('name', '').lower()
            
            # Check if course relates to highest-graded subject
            course_relates_to_highest = False
            if highest_grade_normalized in course_name_lower:
                course_relates_to_highest = True
            elif highest_grade_normalized in self.subject_mappings:
                # Check if any related term appears in course name
                for related_term in self.subject_mappings[highest_grade_normalized]:
                    if related_term in course_name_lower:
                        course_relates_to_highest = True
                        break
            
            if course_relates_to_highest:
                highest_grade = predicted_grades.get(highest_grade_subject, '')
                reasons.append(f"Related to your strongest subject ({highest_grade_subject}: {highest_grade}) - likely to excel in this field")
        
        # Grade match reasons
        required_grades = course.get('entryRequirements', {}).get('grades', {})
        unmet_requirements = []
        for subject, required_grade in required_grades.items():
            if subject in predicted_grades:
                predicted_grade = predicted_grades[subject]
                predicted_value = self.grade_values.get(predicted_grade, 0)
                required_value = self.grade_values.get(required_grade, 0)
                
                if predicted_value >= required_value:
                    reasons.append(f"Your predicted {subject} grade ({predicted_grade}) meets requirements ({required_grade})")
                else:
                    # Note unmet requirements
                    unmet_requirements.append(f"{subject}: {predicted_grade} (requires {required_grade})")
        
        # Add warning if requirements aren't met
        if unmet_requirements:
            reasons.append(f"Note: You don't meet all requirements: {', '.join(unmet_requirements)}")
        
        # Preference reasons
        if 'preferredRegion' in preferences:
            course_region = self._get_course_region(course)
            if course_region == preferences['preferredRegion']:
                reasons.append(f"Located in your preferred region: {course_region}")
        
        # University ranking reasons
        ranking = course.get('university', {}).get('ranking', {})
        overall_rank = ranking.get('overall')
        if overall_rank is not None and overall_rank > 0 and overall_rank <= 20:
            reasons.append(f"Top-ranked university (#{overall_rank})")
        
        # Employability reasons
        employability = course.get('employability', {})
        if employability.get('employmentRate', 0) >= 90:
            reasons.append(f"High graduate employment rate ({employability['employmentRate']}%)")
        
        # Career interest reasons (use CAH-based mapping)
        career_interests = preferences.get('careerInterests', [])
        if career_interests:
            course_id = course.get('course_id')
            course_career_interests = self.course_career_mapping.get(course_id, set())
            
            matched_interests = []
            for interest in career_interests:
                if interest in course_career_interests:
                    matched_interests.append(interest)
            
            if matched_interests:
                reasons.append(f"Matches your career interests: {', '.join(matched_interests)}")
        
        return reasons
    
    def _get_all_courses(self) -> List[Dict[str, Any]]:
        """Get all courses from PostgreSQL database"""
        try:
            from database_helper import get_db_connection
            from psycopg2.extras import RealDictCursor
            
            query = """
                SELECT 
                    c.course_id, c.name, c.annual_fee, c.ucascourseid,
                    c.typical_offer_text, c.typical_offer_tariff,
                    c.course_url,
                    u.university_id, u.name as university_name, u.region,
                    u.rank_overall, u.employability_score as uni_employability,
                    u.website_url,
                    c.employability_score as course_employability,
                    c.pubukprn, c.kiscourseid, c.kismode
                FROM course c
                JOIN university u ON c.university_id = u.university_id
            """
            
            courses = []
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query)
                    
                    for row in cur.fetchall():
                        course_dict = dict(row)
                        course_id = course_dict['course_id']
                        
                        # Get entry requirements
                        cur.execute("""
                            SELECT s.subject_id, s.subject_name, csr.grade_req
                            FROM course_subject_requirement csr
                            JOIN subject s ON csr.cah_code = s.cah_code
                            WHERE csr.course_id = %s
                        """, (course_id,))
                        
                        requirements = {}
                        subjects = []
                        for req_row in cur.fetchall():
                            req = dict(req_row)
                            subject_id = req['subject_id']
                            subject_name = req.get('subject_name', subject_id)
                            # Store both ID and name for flexible matching
                            requirements[subject_id] = req['grade_req']
                            requirements[subject_name] = req['grade_req']  # Also store by name
                            subjects.append(subject_id)
                            subjects.append(subject_name)  # Also include name for matching
                        
                        # Format for recommendation engine
                        course_dict['entryRequirements'] = {
                            'subjects': subjects,
                            'grades': requirements
                        }
                        course_dict['fees'] = {
                            'uk': course_dict.get('annual_fee', 0)
                        }
                        course_dict['university'] = {
                            'name': course_dict['university_name'],
                            'region': course_dict.get('region'),
                            'ranking': {
                                'overall': course_dict.get('rank_overall')
                            },
                            'websiteUrl': course_dict.get('website_url')
                        }
                        course_dict['courseUrl'] = course_dict.get('course_url')
                        course_dict['employability'] = {
                            'employmentRate': course_dict.get('course_employability') or course_dict.get('uni_employability', 50),
                            'averageSalary': 30000  # Default if not available
                        }
                        course_dict['subjects'] = subjects
                        
                        courses.append(course_dict)
            
            return courses
            
        except Exception as e:
            # Fallback to sample data if database connection fails
            print(f"Warning: Could not fetch courses from database: {e}")
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
                }
            ]
