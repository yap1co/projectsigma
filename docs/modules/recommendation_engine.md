# RecommendationEngine Module

## Overview

The `RecommendationEngine` is the core component of the university course recommendation system. It uses advanced algorithms to match students with university courses based on multiple weighted criteria including academic fit, preferences, and compatibility.

**Location**: `server/recommendation_engine.py`

## Architecture

### Design Pattern: Composition

The engine uses the **composition pattern** with separate scorer components:

- `SubjectMatchScorer`: Matches courses based on A-level subjects
- `GradeMatchScorer`: Evaluates predicted grades vs course requirements
- `PreferenceMatchScorer`: Matches student preferences (location, budget, etc.)
- `RankingScorer`: Considers university prestige/ranking
- `EmployabilityScorer`: Evaluates graduate employment prospects

### Algorithm: Top-K Heap Selection

Uses a heap-based algorithm (`heapq`) for efficient recommendation selection, allowing the system to handle large datasets (50,000+ courses) efficiently.

## Key Components

### Initialization

```python
engine = RecommendationEngine()
```

On initialization, the engine:
1. Loads career interests, keywords, and conflicts from the database
2. Sets up scoring weights for different criteria
3. Initializes scorer components
4. Loads feedback settings for dynamic learning

### Weight Configuration

Default weights (configurable):

```python
weights = {
    'subject_match': 0.35,      # A-level subject alignment
    'grade_match': 0.25,        # Predicted grades vs requirements
    'preference_match': 0.15,   # Student preferences
    'university_ranking': 0.15, # University prestige
    'employability': 0.10       # Graduate employment prospects
}
```

## Main Methods

### `get_recommendations()`

**Purpose**: Generate personalized course recommendations for a student.

**Parameters**:
- `a_level_subjects`: List of student's A-level subjects
- `predicted_grades`: Dictionary mapping subjects to predicted grades
- `preferences`: Student preferences (location, budget, career interests, etc.)
- `criteria`: Additional search criteria

**Returns**: List of recommendation dictionaries, each containing:
- `course`: Full course information
- `matchScore`: Composite match score (0.0 to 1.0)
- `meetsRequirements`: Boolean indicating if student meets all requirements
- `reasons`: Human-readable list of match reasons

**Algorithm Flow**:

1. **Initial Scoring Phase**:
   - Calculate base scores for all courses using scorer components
   - Identify courses matching career interests
   - Mark conflicting courses (e.g., Computer Science when Business & Finance is selected)

2. **Filtering Phase**:
   - Apply strict career interest filtering (if specified)
   - Filter out conflicting courses
   - Remove courses that don't match career interests when interests are specified

3. **Scoring Phase**:
   - Apply diversity bonus for courses matching multiple subjects
   - Apply highest-grade subject bonus (if no career interests)
   - Apply career interest bonus (strong priority)
   - Apply feedback-based score adjustment (dynamic learning)

4. **Final Filtering**:
   - Double-check for conflicting keywords
   - Ensure only matching courses are included when career interests are specified

5. **Enrichment**:
   - Batch enrich courses with HESA data (employment, salary, job outcomes)
   - Add university best course information

6. **Sorting & Return**:
   - Sort by final match score
   - Return top 50 recommendations

### Career Interest Filtering

The engine implements **multi-layer filtering** to prevent irrelevant recommendations:

1. **Early Check**: Explicitly filters out conflicting courses (e.g., Computer Science when Business & Finance is selected)
2. **Conflicting Courses Set**: Marks courses that conflict with selected career interests
3. **Career Match Check**: Only includes courses that match career interests when interests are specified
4. **Final Gate**: Double-checks for conflicting keywords even if a course matched

**Example**: When "Business & Finance" is selected:
- ✅ Includes: Business, Finance, Economics, Accounting, Management
- ❌ Excludes: Computer Science, Physics, Chemistry, Engineering

### Database-Driven Configuration

The engine loads career interest data from the database:

- **Tables**: `career_interest`, `career_interest_keyword`, `career_interest_conflict`
- **Method**: `_load_career_interests_from_db()`
- **Fallback**: Hardcoded values if database connection fails

### Feedback-Based Learning

The engine uses feedback from students to improve recommendations:

- **Source**: `recommendation_feedback` table
- **Scope**: Includes feedback from the student AND similar students with similar profiles
- **Weight**: Configurable via `recommendation_settings` table
- **Method**: `_get_student_feedback_scores()`

## Subject Matching Logic

### Generic Matching

The engine uses intelligent subject matching to find related courses:

```python
subject_mappings = {
    'mathematics': ['mathematics', 'maths', 'math', 'statistics', 'computing', 'computer science'],
    'economics': ['economics', 'business', 'finance', 'accounting', 'politics'],
    # ... more mappings
}
```

### False Positive Prevention

Uses `_is_legitimate_match()` to prevent false positives:
- Generic terms (e.g., "science", "studies") require context
- Checks if generic term is part of compound subject name
- Prevents "Business Studies" from matching unrelated "science" courses

## HESA Data Integration

The engine enriches courses with HESA (Higher Education Statistics Agency) data:

- **Employment Outcomes**: Employment rates, unemployment rates
- **Salary Data**: Median salaries, quartiles
- **Earnings Data**: 3-year post-graduation earnings (LEO3)
- **Job Types**: Common job types for graduates
- **Entry Statistics**: A-level vs other entry routes

**Method**: `_batch_enrich_courses_with_hesa_data()`

## Performance Optimizations

1. **Batch Processing**: Fetches HESA data in batches using temp tables
2. **Caching**: Career interest data cached in memory after initial load
3. **Heap Selection**: Uses `heapq` for efficient top-K selection
4. **Early Filtering**: Filters out non-matching courses before expensive operations

## Error Handling

- **Database Failures**: Falls back to hardcoded values
- **Missing Data**: Gracefully handles missing HESA data
- **Invalid Input**: Validates inputs and returns appropriate errors

## Example Usage

```python
from recommendation_engine import RecommendationEngine

engine = RecommendationEngine()

recommendations = engine.get_recommendations(
    a_level_subjects=['Mathematics', 'Economics', 'English Literature'],
    predicted_grades={'Mathematics': 'B', 'Economics': 'A*', 'English Literature': 'A'},
    preferences={
        'careerInterests': ['Business & Finance'],
        'preferredRegion': 'London',
        'tuitionBudget': 9250
    },
    criteria={}
)

for rec in recommendations[:5]:
    print(f"{rec['course']['name']}: {rec['matchScore']:.2%}")
    print(f"  Reasons: {', '.join(rec['reasons'])}")
```

## Related Modules

- `scoring_components.py`: Individual scorer components
- `database_helper.py`: Database connection utilities
- `models/course.py`: Course data model
- `models/student.py`: Student data model

## Configuration

Career interests and conflicts can be managed via:
- Database tables (recommended)
- See `docs/guides/career_interests.md` for management guide

## Testing

Test suite: `server/tests/test_recommendation_engine.py`

Run tests:
```bash
cd server
pytest tests/test_recommendation_engine.py -v
```
