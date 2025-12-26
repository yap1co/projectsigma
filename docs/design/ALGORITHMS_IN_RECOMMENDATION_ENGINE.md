# Algorithms Used in Recommendation Engine

## Overview
The recommendation engine uses multiple algorithms and data structures to efficiently match students with university courses. This document details all algorithms implemented.

## 1. Top-K Heap Selection Algorithm ⭐ (Group A: Advanced Algorithm)

### Description
Implements a **min-heap-based Top-K selection** algorithm to efficiently find the top K recommendations without sorting all courses.

### Problem Solved
**Problem**: When there are thousands of courses in the database, sorting all courses by match score to find the top 100 recommendations is computationally expensive and memory-intensive.

**Solution**: Use a min-heap to maintain only the top K candidates during iteration, avoiding the need to sort all courses.

### Issues Without This Algorithm
- **Performance Degradation**: Full sorting of all courses would be O(N log N), which becomes slow with large datasets (e.g., 10,000+ courses)
- **Memory Overhead**: Would need to store all courses in memory for sorting, increasing memory usage significantly
- **Scalability Issues**: As the database grows, response times would increase exponentially
- **User Experience**: Slow API responses (potentially 5-10+ seconds) would make the application unusable
- **Server Load**: High CPU usage from sorting operations would impact server performance

### Implementation
- **Location**: `recommendation_engine.py`, lines 189-214
- **Data Structure**: Min-heap using Python's `heapq` module
- **Complexity**: O(N log K) instead of O(N log N) for full sort
  - N = total number of courses
  - K = number of recommendations (100)

### Algorithm Steps
```python
1. Initialize empty min-heap
2. For each course:
   a. Calculate match score
   b. If heap has < K items: push course to heap
   c. Else if score > worst in heap: replace worst with current
3. Convert heap to sorted list (descending by score)
4. Return top 50 recommendations
```

### Key Features
- Uses **negative scores** in heap (min-heap stores smallest, we want largest)
- **Index-based tie-breaking** to avoid dict comparison errors
- **Efficient**: Only maintains K items in memory instead of sorting all N items

### Why This Algorithm?
- **Scalability**: Handles large course databases efficiently
- **Memory Efficient**: Only stores top K candidates
- **Time Efficient**: O(N log K) vs O(N log N) for full sort

---

## 2. Weighted Multi-Criteria Scoring Algorithm

### Description
Combines multiple scoring criteria using weighted linear combination.

### Problem Solved
**Problem**: Students have diverse needs: academic fit (subjects/grades), preferences (location/budget), university reputation, and career prospects. A single-factor scoring system cannot balance all these requirements effectively.

**Solution**: Weighted multi-criteria scoring allows different factors to contribute proportionally to the final recommendation score, ensuring balanced recommendations that consider all student needs.

### Issues Without This Algorithm
- **Unbalanced Recommendations**: Would prioritize only one factor (e.g., only subject match), ignoring other important criteria
- **Poor User Satisfaction**: Students might get courses that match subjects but are in wrong location, too expensive, or have poor employment prospects
- **Rigid System**: Cannot adjust importance of different factors based on student needs or system requirements
- **No Flexibility**: Cannot easily tune the system (e.g., increase weight on employability for career-focused students)
- **Biased Results**: Recommendations would favor one dimension, making the system less useful for diverse student populations

### Implementation
- **Location**: `recommendation_engine.py`, `_calculate_match_score()` method
- **Scoring Components**:
  - Subject Match (35%)
  - Grade Match (25%)
  - Preference Match (15%)
  - University Ranking (15%)
  - Employability (10%)

### Formula
```
Total Score = Σ(component_score × weight)
where weights sum to 1.0
```

### Algorithm
```python
1. Calculate each component score independently
2. Multiply each by its weight
3. Sum all weighted scores
4. Return normalized score (0.0 to 1.0)
```

### Scoring Components (Composition Pattern)
- `SubjectMatchScorer`: Matches A-Level subjects to course requirements via CAH codes
- `GradeMatchScorer`: Compares predicted grades vs required grades
- `PreferenceMatchScorer`: Matches location, budget preferences
- `RankingScorer`: University ranking score
- `EmployabilityScorer`: Graduate employment prospects

---

## 3. Subject Matching Algorithm (CAH Code-Based)

### Description
Matches student A-Level subjects to courses using CAH (Common Aggregation Hierarchy) codes from HESA data.

### Problem Solved
**Problem**: A-Level subject names vary (e.g., "Mathematics", "Maths", "Math"), and courses use standardized HESA CAH codes. Simple string matching fails to connect student subjects to relevant courses, especially when subject names don't exactly match course names.

**Solution**: Use standardized CAH codes as an intermediary mapping layer. A-Level subjects map to CAH codes, which then map to courses, enabling accurate subject-to-course matching regardless of naming variations.

### Issues Without This Algorithm
- **Poor Subject Matching**: String-based matching would miss many valid matches (e.g., "Mathematics" student wouldn't match "Maths" course)
- **False Negatives**: Students with relevant subjects wouldn't see courses they're qualified for
- **Inconsistent Results**: Different naming conventions would cause unpredictable matching
- **Missing HESA Integration**: Cannot leverage official HESA subject classifications
- **Limited Coverage**: Would only match exact name matches, missing related courses
- **No Standardization**: Each university might name subjects differently, breaking matching

### Implementation
- **Location**: `scoring_components.py`, `SubjectMatchScorer.calculate_score()`
- **Data Source**: `subject_course_mapping` table (A-Level → CAH codes)
- **Link**: CAH codes → HESA `sbj` table → courses

### Algorithm Steps
```python
1. Get student's A-Level subjects
2. Map subjects to CAH codes via subject_course_mapping
3. Find courses with matching CAH codes in sbj table
4. Calculate match ratio:
   - Required subjects match ratio
   - Relevance to all student subjects
5. Apply bonuses for multiple matches
```

### Matching Logic
- **Exact Match**: Subject name appears in course name
- **CAH Code Match**: Student's CAH codes match course's CAH codes
- **Required Subject Match**: All required subjects must match
- **Relevance Match**: Course relates to student's subjects (even if not required)

---

## 4. Grade Matching Algorithm

### Description
Compares student's predicted grades against course entry requirements.

### Problem Solved
**Problem**: Courses have specific grade requirements (e.g., "AAB"), and students have predicted grades. Without grade matching, students would see courses they cannot get into (wasting time) or miss courses they're qualified for.

**Solution**: Numeric grade comparison with penalty system ensures students see courses they can realistically achieve while still showing aspirational options with appropriate scoring.

### Issues Without This Algorithm
- **Unrealistic Recommendations**: Students would see courses requiring AAA when they have BBB, leading to disappointment
- **Missed Opportunities**: Students with high grades wouldn't see top-tier courses they're qualified for
- **Poor User Experience**: Students would apply to courses they can't get into, wasting application slots
- **No Aspiration Handling**: Cannot show "reach" courses with lower scores
- **Binary Matching**: Would be all-or-nothing (match or no match), no nuanced scoring
- **Wasted Applications**: Students would waste UCAS application slots on unrealistic choices

### Implementation
- **Location**: `scoring_components.py`, `GradeMatchScorer.calculate_score()`
- **Grade Values**: A*=8, A=7, B=6, C=5, D=4, E=3, U=0

### Algorithm
```python
1. For each required subject:
   a. Get student's predicted grade
   b. Get required grade
   c. Compare numeric values
   d. If predicted >= required: score = 1.0
   e. Else: apply penalty based on gap
2. Average all subject scores
3. Return normalized score
```

### Penalty System
- **1 grade below**: 0.15 (heavy penalty)
- **2 grades below**: 0.05 (very low)
- **3+ grades below**: 0.01 (minimal)

---

## 5. Diversity Bonus Algorithm

### Description
Adds bonuses to courses that match multiple student subjects, ensuring diverse recommendations.

### Problem Solved
**Problem**: Students with diverse subject combinations (e.g., Mathematics, English, History) would only see recommendations matching their "strongest" subject, missing interdisciplinary courses that combine multiple subjects.

**Solution**: Diversity bonus rewards courses that relate to multiple student subjects, ensuring students see interdisciplinary options and varied recommendations rather than all courses from one narrow field.

### Issues Without This Algorithm
- **Narrow Recommendations**: All recommendations would be from the same subject area (e.g., all Mathematics courses)
- **Missed Interdisciplinary Courses**: Students wouldn't see courses like "Mathematics and Philosophy" or "Economics and History"
- **Limited Exploration**: Students wouldn't discover courses that combine their diverse interests
- **Poor Variety**: Top recommendations would be too similar, reducing choice
- **Subject Bias**: System would favor one subject over others, ignoring student's full profile
- **Reduced Discovery**: Students wouldn't find unique courses that match their broader academic profile

### Implementation
- **Location**: `recommendation_engine.py`, lines 242-303
- **Purpose**: Prevents all recommendations from same subject area

### Algorithm
```python
1. For each course:
   a. Count how many student subjects it matches
   b. If matches > 1: add diversity bonus
   c. Bonus = min(0.15, (match_count - 1) × 0.05)
2. Apply bonus to final score
```

### Example
- Student has: Mathematics, English, Physics
- Course matches all 3: +0.15 bonus
- Course matches 2: +0.05 bonus

---

## 6. Career Interest Matching Algorithm

### Description
Matches courses to student's career interests using keyword-based matching with conflict detection.

### Problem Solved
**Problem**: Students have career goals (e.g., "Business & Finance"), but courses don't always have obvious names. A student interested in finance might miss "Economics and Finance" or see irrelevant "Computer Science" courses.

**Solution**: Keyword-based matching with conflict detection ensures career-aligned courses are prioritized while filtering out courses that conflict with stated career interests.

### Issues Without This Algorithm
- **Irrelevant Recommendations**: Students interested in Business would see Computer Science courses
- **Missed Career-Aligned Courses**: Courses matching career goals wouldn't be prioritized
- **Poor Career Fit**: Recommendations wouldn't align with student's professional aspirations
- **Conflicting Courses**: Students would see courses that contradict their career interests
- **No Career Guidance**: System wouldn't help students find courses that lead to their desired careers
- **Wasted Time**: Students would spend time reviewing courses irrelevant to their goals

### Implementation
- **Location**: `recommendation_engine.py`, lines 310-374
- **Data Source**: `career_interest_keyword` table (database-loaded)

### Algorithm Steps
```python
1. Load career interest keywords from database
2. For each course:
   a. Check if course name contains interest keywords
   b. If match: add strong bonus (0.4)
   c. Check for conflicting keywords
   d. If conflict: mark for filtering
3. Filter out conflicting courses
```

### Conflict Detection
- **Business & Finance** conflicts with: Computer Science, Physics, Chemistry, Biology, Engineering
- **Science** conflicts with: Business Studies (special handling)
- Uses database-loaded `career_interest_conflict` table

---

## 7. Highest Grade Subject Bonus Algorithm

### Description
Prioritizes courses related to student's highest-graded subject (assumes they'll excel in that area).

### Problem Solved
**Problem**: Students typically perform best in subjects they're strongest in. Without prioritizing their highest-graded subject, they might miss courses where they're most likely to succeed and excel.

**Solution**: Bonus system prioritizes courses related to the student's strongest subject, increasing the likelihood of academic success and satisfaction.

### Issues Without This Algorithm
- **Missed Strengths**: Students wouldn't see courses in their strongest subject area
- **Lower Success Probability**: Recommendations might favor subjects where student is weaker
- **Reduced Academic Performance**: Students might choose courses in weaker subjects, leading to lower grades
- **No Strength Recognition**: System wouldn't identify and leverage student's academic strengths
- **Poor Fit**: Students might be recommended courses in subjects they struggle with
- **Career Mismatch**: Students might pursue careers in areas where they're not strongest

### Implementation
- **Location**: `recommendation_engine.py`, lines 305-308
- **Bonus**: +0.25 to courses matching highest-graded subject

### Algorithm
```python
1. Identify subject with highest predicted grade
2. For each course:
   a. Check if course relates to highest-grade subject
   b. If yes: add 0.25 bonus
3. Only applies if no career interests specified
```

---

## 8. Feedback-Based Learning Algorithm

### Description
Adjusts scores based on student feedback (likes/dislikes) and similar students' feedback.

### Problem Solved
**Problem**: Static recommendation systems don't learn from user behavior. If many students dislike a course or similar students found a course helpful, the system should adapt to improve future recommendations.

**Solution**: Feedback-based learning incorporates user preferences and collaborative filtering (similar students' feedback) to continuously improve recommendation quality over time.

### Issues Without This Algorithm
- **No Learning**: System wouldn't improve based on user feedback
- **Persistent Bad Recommendations**: Courses that students consistently dislike would keep appearing
- **No Personalization**: Cannot adapt to individual student preferences
- **Missed Collaborative Insights**: Wouldn't leverage feedback from similar students
- **Static System**: Recommendations would never improve, even with accumulated user data
- **Poor User Satisfaction**: Students would see the same poor recommendations repeatedly
- **No Adaptation**: System couldn't learn that certain courses are popular/unpopular

### Implementation
- **Location**: `recommendation_engine.py`, `_get_student_feedback_scores()`
- **Data Source**: `recommendation_feedback` table

### Algorithm
```python
1. Get feedback for courses from:
   a. Current student
   b. Similar students (same subjects/grades)
2. Calculate feedback score:
   - Positive feedback: +0.2 boost
   - Negative feedback: -0.3 penalty
   - Time decay: older feedback has less weight
3. Apply weighted feedback to match score
```

### Time Decay
- Feedback relevance decays after 90 days (configurable)
- Uses exponential decay based on `feedback_decay_days`

---

## 9. Batch Processing Algorithm

### Description
Processes multiple courses in batches to avoid N+1 query problems.

### Problem Solved
**Problem**: When enriching 100 courses with HESA data, making individual database queries for each course (N+1 problem) would result in 100+ database round trips, causing severe performance issues and database load.

**Solution**: Batch processing collects all course IDs, fetches all required data in a few batch queries, then enriches courses in memory, reducing database queries from 100+ to 3-4.

### Issues Without This Algorithm
- **N+1 Query Problem**: Would make 100+ individual database queries for 100 courses
- **Severe Performance Degradation**: Each query adds network latency (10-50ms), totaling 1-5 seconds just for database calls
- **Database Overload**: High number of concurrent queries would overwhelm the database
- **Slow API Responses**: Total response time could be 5-10+ seconds, making the app unusable
- **Poor Scalability**: As recommendations increase, performance would degrade linearly
- **Resource Waste**: Excessive database connections and query overhead
- **Timeout Risks**: Requests might timeout due to slow database operations

### Implementation
- **Location**: `recommendation_engine.py`, `_batch_enrich_courses_with_hesa_data()`
- **Purpose**: Efficient database queries

### Algorithm
```python
1. Collect all course IDs
2. Batch fetch HESA identifiers (pubukprn, kiscourseid, kismode)
3. Batch fetch HESA data (employment, salary, entry stats)
4. Enrich all courses in one pass
```

### Benefits
- **Reduces queries**: From N queries to 3-4 batch queries
- **Faster**: Database can optimize batch operations
- **Scalable**: Handles large numbers of courses efficiently

---

## 10. CTE-Based Advanced SQL Algorithm

### Description
Uses Common Table Expressions (CTEs) for complex multi-step SQL queries.

### Problem Solved
**Problem**: Complex recommendation logic requires multiple steps (student profile → subject matching → grade matching → scoring). Writing this as nested subqueries or multiple separate queries is unreadable, hard to maintain, and inefficient.

**Solution**: CTEs break the complex query into logical, readable steps that can be optimized by the database engine, making the code maintainable and performant.

### Issues Without This Algorithm
- **Unreadable SQL**: Nested subqueries would be extremely difficult to understand and debug
- **Poor Maintainability**: Changes to one part of the logic would require rewriting complex nested queries
- **Inefficient Queries**: Database optimizer might not optimize nested subqueries as well as CTEs
- **Code Duplication**: Would need to repeat complex logic in multiple places
- **Hard to Debug**: Difficult to test individual steps of the recommendation process
- **No Modularity**: Cannot easily modify one step (e.g., subject matching) without affecting others
- **Performance Issues**: Database might execute subqueries multiple times instead of once

### Implementation
- **Location**: `app.py`, `/api/recommendations/advanced` endpoint
- **Purpose**: Demonstrates Group A: Advanced SQL skills

### Algorithm Structure
```sql
WITH student_profile AS (
    -- Step 1: Get student profile
),
course_subject_matches AS (
    -- Step 2: Calculate subject matches
),
course_grade_matches AS (
    -- Step 3: Calculate grade matches
),
course_scores AS (
    -- Step 4: Calculate composite scores
)
SELECT ... FROM course_scores
ORDER BY total_score DESC
```

### Features
- **CTEs**: Break complex query into readable steps
- **Aggregate Functions**: COUNT, AVG, COALESCE
- **Cross-table Joins**: Multiple table relationships
- **Weighted Scoring**: Calculated in SQL

---

## 11. Set-Based Matching Algorithm

### Description
Uses set operations for efficient subject matching.

### Problem Solved
**Problem**: Subject matching requires checking if student subjects match course requirements. Using lists would require nested loops (O(N×M)), making it slow when checking many courses and subjects.

**Solution**: Set-based operations use hash tables internally, providing O(1) lookups and O(min(A,B)) for intersections, dramatically improving performance for subject matching.

### Issues Without This Algorithm
- **Slow Performance**: List-based matching would be O(N×M) with nested loops, becoming slow with many courses
- **Inefficient Lookups**: Linear search through lists for each subject match
- **Poor Scalability**: Performance would degrade quadratically as data grows
- **High CPU Usage**: Excessive iterations would consume CPU resources
- **Slow Response Times**: Subject matching would become a bottleneck
- **Code Complexity**: Would need nested loops and complex logic to avoid duplicates

### Implementation
- **Location**: `scoring_components.py`, `SubjectMatchScorer`
- **Data Structures**: Sets for O(1) lookup

### Algorithm
```python
1. Convert subjects to normalized sets
2. Calculate set intersections:
   - matching_required = student_subjects ∩ required_subjects
   - matching_student = student_subjects ∩ course_related_subjects
3. Calculate ratios using set sizes
4. Combine matches: all_matching = matching_required ∪ matching_student
```

### Complexity
- **Set Operations**: O(min(len(A), len(B)))
- **Lookup**: O(1) average case
- **Overall**: O(N × M) where N=courses, M=subjects per course

---

## 12. Filtering Algorithm (Conflict Detection)

### Description
Filters out courses that conflict with student's career interests.

### Problem Solved
**Problem**: Students with specific career interests (e.g., "Business & Finance") would see conflicting courses (e.g., "Computer Science") that don't align with their goals, wasting their time and reducing recommendation quality.

**Solution**: Pre-filtering removes conflicting courses before scoring, ensuring students only see courses relevant to their career aspirations, improving recommendation relevance and user experience.

### Issues Without This Algorithm
- **Conflicting Recommendations**: Students interested in Business would see Computer Science courses
- **Poor Relevance**: Recommendations would include courses that contradict stated career goals
- **Wasted User Time**: Students would need to manually filter out irrelevant courses
- **Reduced Trust**: Users would lose confidence in the recommendation system
- **Poor User Experience**: Students would see many courses they're not interested in
- **No Career Alignment**: System wouldn't respect student's career preferences
- **Lower Conversion**: Students might abandon the platform due to poor recommendations

### Implementation
- **Location**: `recommendation_engine.py`, lines 382-520
- **Method**: Keyword-based conflict detection

### Algorithm
```python
1. Load conflicting keywords from database
2. For each course:
   a. Check course name for conflicting keywords
   b. If conflict found: mark for removal
3. Filter out conflicting courses BEFORE scoring
```

### Special Cases
- "Business Studies" contains "science" but doesn't conflict
- Explicit conflict lists for each career interest
- Database-driven (no hardcoded conflicts)

---

## Design Patterns Used

### 1. Composition Pattern
- Separate scorer components (`SubjectMatchScorer`, `GradeMatchScorer`, etc.)
- Each scorer implements `Scorer` abstract base class
- Allows independent testing and modification

### 2. Strategy Pattern
- Different scoring strategies for different criteria
- Can swap scorers without changing main algorithm

### 3. Template Method Pattern
- `get_recommendations()` defines algorithm structure
- Delegates scoring to component scorers

---

## Complexity Analysis

| Algorithm | Time Complexity | Space Complexity | Notes |
|-----------|----------------|------------------|-------|
| Top-K Heap Selection | O(N log K) | O(K) | K=100, N=all courses |
| Weighted Scoring | O(N × M) | O(1) | M=scoring components |
| Subject Matching | O(N × S) | O(S) | S=student subjects |
| Batch Enrichment | O(N) | O(N) | Batch queries |
| Career Matching | O(N × I × K) | O(I) | I=interests, K=keywords |
| **Overall** | **O(N log K)** | **O(K)** | Dominated by heap |

Where:
- N = number of courses
- K = top K recommendations (100)
- M = number of scoring components (5)
- S = number of student subjects
- I = number of career interests
- K = keywords per interest

---

## Performance Optimizations

1. **Heap Selection**: O(N log K) instead of O(N log N)
2. **Batch Queries**: Reduces database round trips
3. **Caching**: Career interests loaded once at init
4. **Early Filtering**: Conflicts filtered before scoring
5. **Set Operations**: Fast O(1) lookups for subject matching
6. **Index Usage**: Database indexes on CAH codes, subject IDs

---

## Summary

The recommendation engine uses **11 distinct algorithms** working together:

1. ⭐ **Top-K Heap Selection** (Advanced - Group A)
2. **Weighted Multi-Criteria Scoring**
3. **CAH Code-Based Subject Matching**
4. **Grade Matching with Penalties**
5. **Diversity Bonus**
6. **Career Interest Matching**
7. **Highest Grade Subject Bonus**
8. **Feedback-Based Learning**
9. **Batch Processing**
10. **CTE-Based SQL** (Advanced - Group A)
11. **Set-Based Matching**
12. **Conflict Filtering**

The main algorithm is the **Top-K Heap Selection**, which provides O(N log K) complexity for efficient recommendation generation.

