# RecommendationEngine - Technical Documentation

## Overview

The `RecommendationEngine` is the core component of the university course recommendation system. It uses advanced algorithms to match students with university courses based on multiple weighted criteria including academic fit, preferences, and compatibility.

**Location**: `server/recommendation_engine.py`  
**Class**: `RecommendationEngine`  
**Lines**: ~1994 lines

## Architecture

### Design Pattern: Composition

The engine uses the **composition pattern** with separate scorer components:

```python
from scoring_components import (
    SubjectMatchScorer, GradeMatchScorer, PreferenceMatchScorer,
    RankingScorer, EmployabilityScorer
)
```

- `SubjectMatchScorer`: Matches courses based on A-level subjects
- `GradeMatchScorer`: Evaluates predicted grades vs course requirements
- `PreferenceMatchScorer`: Matches student preferences (location, budget, etc.)
- `RankingScorer`: Considers university prestige/ranking
- `EmployabilityScorer`: Evaluates graduate employment prospects

### Algorithm: Top-K Heap Selection

Uses a heap-based algorithm (`heapq`) for efficient recommendation selection:

- **Complexity**: O(N log K) instead of O(N log N)
- **K**: Top 100 courses maintained in heap
- **N**: Total number of courses (50,000+)

This allows the system to handle large datasets efficiently.

## Class Structure

### Initialization

```python
def __init__(self):
```

**Data Structures Initialized:**

1. **`self.weights`** (Dict[str, float]):
   ```python
   {
       'subject_match': 0.35,
       'grade_match': 0.25,
       'preference_match': 0.15,
       'university_ranking': 0.15,
       'employability': 0.10
   }
   ```
   - Total: 1.0
   - Configurable via database

2. **`self.grade_values`** (Dict[str, int]):
   ```python
   {
       'A*': 8, 'A': 7, 'B': 6, 'C': 5, 
       'D': 4, 'E': 3, 'U': 0
   }
   ```
   - Used for grade comparison
   - Numerical conversion for calculations

3. **`self.regions`** (Dict[str, List[str]]):
   ```python
   {
       'London': ['London'],
       'South East': ['Oxford', 'Cambridge', 'Brighton', ...],
       ...
   }
   ```
   - UK geographical regions
   - Maps regions to cities

4. **`self.subject_mappings`** (Dict[str, List[str]]):
   ```python
   {
       'mathematics': ['mathematics', 'maths', 'math', 'statistics', 'computing', 'computer science'],
       'economics': ['economics', 'business', 'finance', 'accounting', 'politics'],
       ...
   }
   ```
   - Maps A-level subjects to related course terms
   - Used for intelligent subject matching

5. **`self.generic_terms`** (Set[str]):
   ```python
   {'science', 'studies', 'business', 'management', 'technology', 'design', 'art'}
   ```
   - Terms too generic to match alone
   - Prevents false positives

6. **`self.legitimate_generic_matches`** (Dict[str, Callable]):
   ```python
   {
       'science': lambda subj: 'science' in subj.lower() or subj.lower() in ['physics', 'chemistry', 'biology'],
       'studies': lambda subj: 'studies' in subj.lower(),
       ...
   }
   ```
   - Lambda functions for generic term validation
   - Prevents false matches

7. **`self.feedback_settings`** (Dict[str, Any]):
   ```python
   {
       'feedback_weight': 0.15,
       'feedback_decay_days': 90,
       'min_feedback_count': 3,
       'positive_feedback_boost': 0.2,
       'negative_feedback_penalty': -0.3
   }
   ```
   - Tunable feedback parameters
   - Loaded from database

8. **`self.career_keywords_map`** (Dict[str, List[str]]):
   ```python
   {
       'Business & Finance': ['business', 'finance', 'accounting', ...],
       'Medicine & Healthcare': ['medicine', 'health', 'nursing', ...],
       ...
   }
   ```
   - Loaded from database
   - Maps career interests to keywords

9. **`self.conflicting_career_fields`** (Dict[str, List[str]]):
   ```python
   {
       'Business & Finance': ['Engineering & Technology', 'Sciences', 'Medicine & Healthcare'],
       ...
   }
   ```
   - Loaded from database
   - Defines conflicting career interests

**Scorer Components:**
- `self.subject_scorer`: SubjectMatchScorer instance
- `self.grade_scorer`: GradeMatchScorer instance
- `self.preference_scorer`: PreferenceMatchScorer instance
- `self.ranking_scorer`: RankingScorer instance
- `self.employability_scorer`: EmployabilityScorer instance

**Database Loading:**
- Calls `self._load_career_interests_from_db()` on initialization
- Falls back to hardcoded values if database fails

## Methods

### Public Methods

#### `get_recommendations()`

**Signature:**
```python
def get_recommendations(
    self, 
    a_level_subjects: List[str], 
    predicted_grades: Dict[str, str],
    preferences: Dict[str, Any],
    criteria: Dict[str, Any]
) -> List[Dict[str, Any]]
```

**Parameters:**
- `a_level_subjects`: List[str] - Student's A-level subjects (e.g., `['Mathematics', 'Economics', 'English Literature']`)
- `predicted_grades`: Dict[str, str] - Subject -> grade mapping (e.g., `{'Mathematics': 'B', 'Economics': 'A*'}`)
- `preferences`: Dict[str, Any] - Student preferences:
  ```python
  {
      'careerInterests': ['Business & Finance'],
      'preferredRegion': 'London',
      'maxBudget': 9250,
      'preferredExams': ['A-Level']
  }
  ```
- `criteria`: Dict[str, Any] - Additional search criteria:
  ```python
  {
      'student_id': 'STU123456',
      'limit': 20
  }
  ```

**Returns:**
```python
List[Dict[str, Any]]  # Top 50 recommendations
```

Each recommendation dictionary:
```python
{
    'course': {
        'course_id': 'COU123456',
        'name': 'Business Management',
        'university': {
            'name': 'University of London',
            'region': 'London',
            'ranking': {'overall': 20}
        },
        'entryRequirements': {
            'subjects': ['Mathematics', 'Economics'],
            'grades': {'Mathematics': 'B', 'Economics': 'A'}
        },
        'fees': {'uk': 9250},
        'employability': {
            'employmentRate': 85,
            'averageSalary': 35000
        },
        # ... HESA data if available
    },
    'matchScore': 0.85,  # Float 0.0-1.0
    'meetsRequirements': True,  # Boolean
    'reasons': [
        'Matches your A-level subjects: Economics',
        'Matches your career interests: Business & Finance',
        'Top-ranked university (#20)'
    ],
    'universityBestCourse': {...}  # Optional: best course from same university
}
```

**Algorithm Flow:**

1. **Load Courses**:
   ```python
   courses = self._get_all_courses()  # List[Dict[str, Any]]
   ```

2. **Load Settings**:
   ```python
   self._load_feedback_settings()
   ```

3. **Top-K Heap Selection**:
   ```python
   k = 100
   heap = []  # Min-heap: stores (-score, index, course) tuples
   
   for idx, course in enumerate(courses):
       match_score = self._calculate_match_score(...)
       if match_score > 0.05:
           if len(heap) < k:
               heapq.heappush(heap, (-match_score, idx, course))
           elif match_score > -heap[0][0]:
               heapq.heapreplace(heap, (-match_score, idx, course))
   ```

4. **Sort and Process**:
   ```python
   sorted_courses = sorted(heap, reverse=True)
   ```

5. **Batch Enrichment**:
   ```python
   enriched_courses_map = self._batch_enrich_courses_with_hesa_data(courses_to_enrich)
   ```

6. **Career Interest Matching**:
   - Identify courses matching career interests
   - Mark conflicting courses
   - Calculate bonuses

7. **Filtering**:
   - Apply strict career interest filtering
   - Remove conflicting courses
   - Apply diversity and grade bonuses

8. **Final Processing**:
   - Apply feedback scores
   - Generate match reasons
   - Sort by final score
   - Return top 50

**Data Structures Used:**
- `List[Dict[str, Any]]`: Courses list
- `heapq`: Min-heap for Top-K selection
- `Dict[str, Dict[str, Any]]`: Enriched courses map
- `Dict[str, float]`: Feedback scores
- `Set[str]`: Conflicting courses
- `Dict[str, float]`: Bonuses (diversity, grade, career)

**Time Complexity**: O(N log K) where N = courses, K = 100

### Private Methods

#### `_calculate_match_score()`

**Signature:**
```python
def _calculate_match_score(
    self,
    course: Dict[str, Any],
    a_level_subjects: List[str],
    predicted_grades: Dict[str, str],
    preferences: Dict[str, Any],
    criteria: Dict[str, Any]
) -> float
```

**Returns:** Float between 0.0 and 1.0

**Algorithm:**
```python
# Prepare student data
student_data = {
    'aLevelSubjects': a_level_subjects,
    'predictedGrades': predicted_grades,
    'preferences': preferences
}

# Use composition: delegate to scorer components
scores = {
    'subject_match': self.subject_scorer.calculate_score(course, student_data),
    'grade_match': self.grade_scorer.calculate_score(course, student_data),
    'preference_match': self.preference_scorer.calculate_score(course, student_data),
    'university_ranking': self.ranking_scorer.calculate_score(course, student_data),
    'employability': self.employability_scorer.calculate_score(course, student_data)
}

# Weighted sum
total_score = sum(
    scores[criterion] * weight 
    for criterion, weight in self.weights.items()
)

return min(total_score, 1.0)
```

**Data Structures:**
- `Dict[str, float]`: Individual scores
- `Dict[str, float]`: Weights

#### `_calculate_subject_match()`

**Signature:**
```python
def _calculate_subject_match(
    self,
    course: Dict[str, Any],
    a_level_subjects: List[str]
) -> float
```

**Returns:** Float 0.0-1.0

**Algorithm:**
1. Extract required subjects and course name
2. Normalize subjects (lowercase, strip)
3. Calculate required subject match ratio
4. Calculate relevance to ALL student subjects
5. Apply bonuses for multiple matches
6. Return combined score

**Data Structures:**
- `Set[str]`: Normalized subjects
- `Set[str]`: Matching subjects
- `Dict[str, List[str]]`: Subject mappings

#### `_calculate_grade_match()`

**Signature:**
```python
def _calculate_grade_match(
    self,
    course: Dict[str, Any],
    predicted_grades: Dict[str, str]
) -> float
```

**Returns:** Float 0.0-1.0

**Algorithm:**
```python
for subject, required_grade in required_grades.items():
    if subject in predicted_grades:
        predicted_value = self.grade_values.get(predicted_grade, 0)
        required_value = self.grade_values.get(required_grade, 0)
        
        if predicted_value >= required_value:
            subject_score = 1.0
        else:
            # Penalty based on grade difference
            grade_diff = required_value - predicted_value
            subject_score = calculate_penalty(grade_diff)
        
        total_score += subject_score
        total_weight += 1

return total_score / total_weight if total_weight > 0 else 0.5
```

**Data Structures:**
- `Dict[str, str]`: Required grades
- `Dict[str, str]`: Predicted grades
- `Dict[str, int]`: Grade values

#### `_calculate_preference_match()`

**Signature:**
```python
def _calculate_preference_match(
    self,
    course: Dict[str, Any],
    preferences: Dict[str, Any]
) -> float
```

**Returns:** Float 0.0-1.0

**Checks:**
- Career interests (strong boost/penalty)
- Location preference
- Budget preference
- University size preference
- Course length preference

**Data Structures:**
- `Dict[str, Any]`: Preferences
- `List[str]`: Career interests

#### `_calculate_ranking_score()`

**Signature:**
```python
def _calculate_ranking_score(self, course: Dict[str, Any]) -> float
```

**Returns:** Float 0.0-1.0

**Algorithm:**
```python
rank_to_use = subject_rank if subject_rank > 0 else overall_rank

if rank_to_use <= 10:
    return 1.0 - (rank_to_use - 1) * 0.01
elif rank_to_use <= 50:
    return 0.9 - (rank_to_use - 10) * 0.01
else:
    return max(0.1, 0.5 - (rank_to_use - 50) * 0.008)
```

#### `_calculate_employability_score()`

**Signature:**
```python
def _calculate_employability_score(self, course: Dict[str, Any]) -> float
```

**Returns:** Float 0.0-1.0

**Formula:**
```python
employment_rate = employability.get('employmentRate', 50)
avg_salary = employability.get('averageSalary', 30000)
salary_score = min(1.0, (avg_salary - 20000) / 40000)

return (employment_rate / 100) * 0.7 + salary_score * 0.3
```

#### `_batch_enrich_courses_with_hesa_data()`

**Signature:**
```python
def _batch_enrich_courses_with_hesa_data(
    self,
    courses: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]
```

**Returns:** Dict mapping `course_id -> enriched_course`

**Algorithm:**
1. Extract HESA identifiers (pubukprn, kiscourseid, kismode)
2. Create temporary table for batch lookups
3. Batch fetch from multiple HESA tables:
   - `employment`: Employment outcomes
   - `gosalary`: Salary data
   - `leo3`: 3-year earnings
   - `joblist`: Job types
   - `entry`: Entry statistics
4. Enrich each course with fetched data

**Data Structures:**
- `List[Tuple]`: HESA keys (pubukprn, kiscourseid, kismode)
- `Dict[Tuple, Dict]`: Employment data
- `Dict[Tuple, Dict]`: Salary data
- `Dict[Tuple, Dict]`: LEO3 data
- `Dict[Tuple, List[Dict]]`: Job types data
- `Dict[Tuple, Dict]`: Entry statistics

**Performance:** Uses temp tables and batch queries to avoid N+1 problem

#### `_enrich_course_with_hesa_data()`

**Signature:**
```python
def _enrich_course_with_hesa_data(
    self,
    course: Dict[str, Any]
) -> Dict[str, Any]
```

**Returns:** Enriched course dictionary

**Adds:**
- `employmentOutcomes`: Employment rates
- `salaryData`: Salary quartiles
- `earningsData`: 3-year earnings
- `commonJobTypes`: Top job types
- `entryStatistics`: Entry route statistics

#### `_meets_all_grade_requirements()`

**Signature:**
```python
def _meets_all_grade_requirements(
    self,
    course: Dict[str, Any],
    predicted_grades: Dict[str, str]
) -> bool
```

**Returns:** Boolean

**Algorithm:**
```python
for subject, required_grade in required_grades.items():
    if subject in predicted_grades:
        predicted_value = self.grade_values.get(predicted_grade, 0)
        required_value = self.grade_values.get(required_grade, 0)
        
        if predicted_value < required_value:
            return False  # Doesn't meet requirement

return True  # Meets all requirements
```

#### `_get_best_course_for_university()`

**Signature:**
```python
def _get_best_course_for_university(
    self,
    university_name: str
) -> Dict[str, Any]
```

**Returns:** Course dictionary or None

**SQL Query:**
```sql
SELECT c.*, u.*
FROM course c
JOIN university u ON c.university_id = u.university_id
WHERE u.name = %s
  AND c.employability_score IS NOT NULL
ORDER BY c.employability_score DESC
LIMIT 1
```

#### `_get_highest_grade_subject()`

**Signature:**
```python
def _get_highest_grade_subject(
    self,
    predicted_grades: Dict[str, str]
) -> str
```

**Returns:** Subject name (str) or None

**Algorithm:**
```python
highest_grade_value = -1
highest_grade_subject = None

for subject, grade in predicted_grades.items():
    grade_value = self.grade_values.get(grade, 0)
    if grade_value > highest_grade_value:
        highest_grade_value = grade_value
        highest_grade_subject = subject

return highest_grade_subject
```

#### `_has_career_interests()`

**Signature:**
```python
def _has_career_interests(
    self,
    preferences: Dict[str, Any],
    criteria: Dict[str, Any]
) -> bool
```

**Returns:** Boolean

**Checks:**
- `careerInterest`, `careerInterests`, `preferredCareer`, etc. in preferences
- Same fields in criteria
- `preferredSubject` in preferences/criteria

#### `_is_legitimate_match()`

**Signature:**
```python
def _is_legitimate_match(
    self,
    related_term: str,
    student_subject: str
) -> bool
```

**Returns:** Boolean

**Purpose:** Prevents false positives (e.g., "science" matching "Business Studies")

**Algorithm:**
```python
if related_term not in self.generic_terms:
    return True  # Not generic, always legitimate

if related_term in self.legitimate_generic_matches:
    return self.legitimate_generic_matches[related_term](student_subject)

return related_term in student_subject.lower()
```

#### `_load_career_interests_from_db()`

**Signature:**
```python
def _load_career_interests_from_db(self) -> None
```

**Purpose:** Load career interests, keywords, and conflicts from database

**SQL Queries:**
1. Load career interests:
   ```sql
   SELECT interest_id, interest_name, display_name
   FROM career_interest
   WHERE is_active = TRUE
   ```

2. Load keywords:
   ```sql
   SELECT ci.interest_name, cik.keyword, cik.priority
   FROM career_interest_keyword cik
   JOIN career_interest ci ON cik.interest_id = ci.interest_id
   WHERE cik.is_active = TRUE AND ci.is_active = TRUE
   ORDER BY cik.priority DESC
   ```

3. Load conflicts:
   ```sql
   SELECT ci1.interest_name, ci2.interest_name as conflicting_interest_name
   FROM career_interest_conflict cic
   JOIN career_interest ci1 ON cic.interest_id = ci1.interest_id
   JOIN career_interest ci2 ON cic.conflicting_interest_id = ci2.interest_id
   WHERE ci1.is_active = TRUE AND ci2.is_active = TRUE
   ```

**Populates:**
- `self.career_keywords_map`: Dict[str, List[str]]
- `self.conflicting_career_fields`: Dict[str, List[str]]

**Fallback:** Hardcoded values if database fails

#### `_load_feedback_settings()`

**Signature:**
```python
def _load_feedback_settings(self) -> None
```

**Purpose:** Load tunable feedback settings from database

**SQL Query:**
```sql
SELECT setting_key, setting_value
FROM recommendation_settings
```

**Updates:** `self.feedback_settings` dictionary

#### `_get_student_feedback_scores()`

**Signature:**
```python
def _get_student_feedback_scores(
    self,
    student_id: str,
    course_ids: List[str],
    preferences: Dict[str, Any] = None
) -> Dict[str, float]
```

**Returns:** Dict mapping `course_id -> feedback_score` (-1.0 to 1.0)

**Algorithm:**
1. Get feedback from this student
2. Get feedback from similar students (same career interests)
3. Weighted combination: 60% own, 40% similar
4. Calculate net score: `(positive - negative) / total`
5. Apply boost/penalty based on net score

**SQL Queries:**
1. Student feedback:
   ```sql
   SELECT course_id,
          COUNT(*) FILTER (WHERE feedback_type = 'positive') as positive_count,
          COUNT(*) FILTER (WHERE feedback_type = 'negative') as negative_count
   FROM recommendation_feedback
   WHERE student_id = %s AND course_id = ANY(%s)
   GROUP BY course_id
   ```

2. Similar students feedback:
   ```sql
   SELECT rf.course_id, ...
   FROM recommendation_feedback rf
   WHERE rf.course_id = ANY(%s)
     AND rf.student_id != %s
     AND rf.search_criteria::jsonb @> %s::jsonb
   GROUP BY rf.course_id
   ```

**Data Structures:**
- `Dict[str, Dict]`: Student feedback (positive, negative, total)
- `Dict[str, Dict]`: Similar student feedback
- `Dict[str, float]`: Final feedback scores

#### `_get_match_reasons()`

**Signature:**
```python
def _get_match_reasons(
    self,
    course: Dict[str, Any],
    a_level_subjects: List[str],
    predicted_grades: Dict[str, str],
    preferences: Dict[str, Any]
) -> List[str]
```

**Returns:** List of human-readable reason strings

**Generates reasons for:**
- Subject matches
- Grade matches
- Highest-grade subject relevance
- Preference matches (region, budget)
- University ranking
- Employability
- Career interests

#### `_get_all_courses()`

**Signature:**
```python
def _get_all_courses(self) -> List[Dict[str, Any]]
```

**Returns:** List of course dictionaries

**SQL Query:**
```sql
SELECT c.*, u.*
FROM course c
JOIN university u ON c.university_id = u.university_id
LIMIT 1000
```

**Post-processing:**
- Fetches entry requirements for each course
- Formats for recommendation engine
- Adds nested structures (university, fees, employability)

**Data Structures:**
- `List[Dict[str, Any]]`: Courses
- `Dict[str, str]`: Requirements (subject -> grade)
- `List[str]`: Subjects list

## Python Data Structures Used

### Lists
- `List[str]`: A-level subjects, course subjects
- `List[Dict[str, Any]]`: Courses, recommendations
- `List[Tuple]`: Heap items `(-score, index, course)`

### Dictionaries
- `Dict[str, str]`: Grade mappings, subject -> grade
- `Dict[str, int]`: Grade values, counts
- `Dict[str, float]`: Scores, weights, bonuses
- `Dict[str, List[str]]`: Subject mappings, career keywords
- `Dict[str, Any]`: Course data, preferences, criteria
- `Dict[str, Dict[str, Any]]`: Nested structures (university, fees, etc.)

### Sets
- `Set[str]`: Normalized subjects, conflicting courses, generic terms
- `Set[Tuple]`: HESA keys

### Tuples
- `Tuple[float, int, Dict]`: Heap items `(neg_score, index, course)`
- `Tuple[str, str, str]`: HESA identifiers `(pubukprn, kiscourseid, kismode)`

### Specialized
- `heapq`: Min-heap for Top-K selection
- `RealDictCursor`: PostgreSQL cursor returning dicts
- Lambda functions: Generic term validation

## Algorithm Details

### Top-K Heap Selection

**Implementation:**
```python
import heapq

k = 100
heap = []

for idx, course in enumerate(courses):
    score = calculate_score(course)
    if len(heap) < k:
        heapq.heappush(heap, (-score, idx, course))
    elif score > -heap[0][0]:
        heapq.heapreplace(heap, (-score, idx, course))
```

**Why negative scores?** Min-heap stores smallest first. Negating makes largest positive = smallest negative.

**Why index?** Breaks ties and prevents dict comparison errors.

### Career Interest Filtering

**Multi-layer approach:**

1. **Early Check** (Line 354-389):
   ```python
   if has_business_finance:
       if any(term in course_name for term in conflicting_terms):
           continue  # Filter out immediately
   ```

2. **Conflicting Courses Set** (Line 230, 338-357):
   ```python
   conflicting_courses = set()
   # Mark courses during initial scoring
   ```

3. **Career Match Check** (Line 397-427):
   ```python
   if not course_matches_career:
       continue  # Filter out non-matching courses
   ```

4. **Final Gate** (Line 456-520):
   ```python
   if has_career_interests and course_id not in career_interest_bonus:
       continue  # Absolute filter
   ```

### Subject Matching Logic

**Two-stage matching:**

1. **Exact Match**:
   ```python
   matching_required = student_subjects_normalized & required_subjects_normalized
   ```

2. **Related Match**:
   ```python
   for stud_subj in student_subjects_normalized:
       if stud_subj in self.subject_mappings:
           for related_term in self.subject_mappings[stud_subj]:
               if related_term in course_name:
                   if self._is_legitimate_match(related_term, stud_subj):
                       matching_student_subjects.add(stud_subj)
   ```

**False Positive Prevention:**
- Uses `_is_legitimate_match()` for generic terms
- Checks if generic term is part of compound subject name
- Prevents "science" matching "Business Studies"

## Performance Optimizations

1. **Batch Processing**: HESA data fetched in batches using temp tables
2. **Caching**: Career interest data cached after initial load
3. **Heap Selection**: O(N log K) instead of O(N log N)
4. **Early Filtering**: Filters non-matching courses before expensive operations
5. **Set Operations**: Fast set intersections for subject matching

## Error Handling

- **Database Failures**: Falls back to hardcoded values
- **Missing Data**: Gracefully handles missing HESA data
- **Invalid Input**: Validates and returns appropriate errors
- **Connection Errors**: Prints warnings, continues with fallback

## Example Usage

```python
from recommendation_engine import RecommendationEngine

# Initialize
engine = RecommendationEngine()

# Generate recommendations
recommendations = engine.get_recommendations(
    a_level_subjects=['Mathematics', 'Economics', 'English Literature'],
    predicted_grades={
        'Mathematics': 'B',
        'Economics': 'A*',
        'English Literature': 'A'
    },
    preferences={
        'careerInterests': ['Business & Finance'],
        'preferredRegion': 'London',
        'maxBudget': 9250
    },
    criteria={
        'student_id': 'STU123456',
        'limit': 20
    }
)

# Process results
for rec in recommendations[:5]:
    print(f"{rec['course']['name']}: {rec['matchScore']:.2%}")
    print(f"  Reasons: {', '.join(rec['reasons'])}")
    print(f"  Meets requirements: {rec['meetsRequirements']}")
```

## Related Modules

- `scoring_components.py`: Individual scorer components
- `database_helper.py`: Database connection utilities
- `models/course.py`: Course data model
- `models/student.py`: Student data model

## Testing

Test suite: `server/tests/test_recommendation_engine.py`

Run tests:
```bash
cd server
pytest tests/test_recommendation_engine.py -v
```

## Configuration

Career interests and conflicts can be managed via:
- Database tables (recommended): `career_interest`, `career_interest_keyword`, `career_interest_conflict`
- See [docs/guides/career_interests.md](../guides/career_interests.md) for management guide
