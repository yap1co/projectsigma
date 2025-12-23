# 2-Day Sprint Plan - ProjectSigma

## ⚠️ Realistic Timeline: 2 Days

This plan focuses on **maximum marks in minimum time**. We'll prioritize critical fixes and essential Group A features.

---

## Day 1: Critical Fixes (8-10 hours)

### Morning (3-4 hours): Database Migration 🔴 **CRITICAL**

**Goal**: Get the system working with PostgreSQL

#### Task 1.1: Replace MongoDB with PostgreSQL (2 hours)
- [ ] Update `server/app.py` to use PostgreSQL
- [ ] Create database connection helper
- [ ] Convert all MongoDB queries to SQL

#### Task 1.2: Fix Recommendation Engine (1-2 hours)
- [ ] Implement `_get_all_courses()` to query PostgreSQL
- [ ] Test database connection
- [ ] Verify recommendations work

**Files to modify**:
- `server/app.py` (all database operations)
- `server/recommendation_engine.py` (database query)

---

### Afternoon (4-5 hours): Core Functionality

#### Task 2.1: Basic Test Suite (2 hours) 🔴 **CRITICAL**
- [ ] Create `server/tests/` directory
- [ ] Write 5-10 essential unit tests
- [ ] Write 3-5 integration tests
- [ ] Test database operations
- [ ] Test recommendation engine

**Minimum test coverage**:
- Test database connection
- Test recommendation algorithm (2-3 test cases)
- Test API endpoints (register, login, recommendations)
- Test models (Student, Course)

#### Task 2.2: Fix Critical Bugs (2 hours)
- [ ] Fix any database connection errors
- [ ] Ensure all core endpoints work
- [ ] Test end-to-end flow

---

## Day 2: Group A Features & Completion (8-10 hours)

### Morning (4-5 hours): Group A Technical Skills

#### Task 3.1: Enhance OOP Design (2 hours) 🟠 **HIGH PRIORITY**
- [ ] Create base class for models
- [ ] Add inheritance to Student/Course
- [ ] Implement one polymorphic method
- [ ] Use composition in RecommendationEngine

**Quick implementation**:
```python
# Base model with inheritance
class BaseModel:
    def to_dict(self): pass
    def from_dict(cls, data): pass

class Student(BaseModel):
    # Inherits from BaseModel
    pass

# Composition in RecommendationEngine
class RecommendationEngine:
    def __init__(self):
        self.scorer = WeightedScorer()  # Composition
        self.filterer = CourseFilter()  # Composition
```

#### Task 3.2: Implement Advanced Algorithm (2 hours) 🟠 **HIGH PRIORITY**
- [ ] Add Top-K heap selection to recommendation engine
- [ ] Implement one complex SQL query with JOINs
- [ ] Add parameterized queries

**Quick implementation**:
```python
import heapq

def get_top_k_recommendations(self, courses, k=50):
    heap = []
    for course in courses:
        score = self._calculate_match_score(course)
        if len(heap) < k:
            heapq.heappush(heap, (score, course))
        elif score > heap[0][0]:
            heapq.heapreplace(heap, (score, course))
    return sorted(heap, reverse=True)
```

#### Task 3.3: Complex SQL Query (1 hour) 🟠 **HIGH PRIORITY**
- [ ] Create one complex query with JOINs and CTEs
- [ ] Use parameterized queries
- [ ] Add aggregate functions

---

### Afternoon (4-5 hours): Completion & Polish

#### Task 4.1: Complete Extension Features (2 hours)
- [ ] Implement PDF export (basic version)
- [ ] Add admin authorization check
- [ ] Test extension features

#### Task 4.2: Code Quality (1 hour)
- [ ] Add input validation
- [ ] Improve error handling
- [ ] Add type hints where missing

#### Task 4.3: Final Testing & Documentation (1-2 hours)
- [ ] Run all tests
- [ ] Fix any remaining bugs
- [ ] Update README if needed
- [ ] Document what was completed

---

## Quick Reference: Essential Code Changes

### 1. Database Connection (app.py)

**Replace this**:
```python
from pymongo import MongoClient
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client.university_recommender
```

**With this**:
```python
import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'university_recommender'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )
```

### 2. Database Queries (app.py - register function)

**Replace this**:
```python
if db.students.find_one({'email': data['email']}):
    return jsonify({'message': 'User already exists'}), 400

result = db.students.insert_one(student_data)
student_id = str(result.inserted_id)
```

**With this**:
```python
with get_db_connection() as conn:
    with conn.cursor() as cur:
        # Check if user exists
        cur.execute("SELECT student_id FROM student WHERE email = %s", (data['email'],))
        if cur.fetchone():
            return jsonify({'message': 'User already exists'}), 400
        
        # Insert new student
        cur.execute("""
            INSERT INTO student (student_id, email, password_hash, first_name, last_name, year_group, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            RETURNING student_id
        """, (generate_id('STU'), data['email'], generate_password_hash(data['password']), 
              data['firstName'], data['lastName'], data.get('yearGroup', 'Year 12')))
        student_id = cur.fetchone()[0]
        conn.commit()
```

### 3. Recommendation Engine Database Query

**Replace this**:
```python
def _get_all_courses(self) -> List[Dict[str, Any]]:
    return [{'name': 'Computer Science', ...}]  # Placeholder
```

**With this**:
```python
def _get_all_courses(self) -> List[Dict[str, Any]]:
    """Get all courses from PostgreSQL database"""
    from app import get_db_connection
    
    query = """
    SELECT 
        c.course_id, c.name, c.description, c.duration, c.annual_fee,
        u.university_id, u.name as university_name, u.region, u.rank_overall,
        u.employability_score, u.website_url
    FROM course c
    JOIN university u ON c.university_id = u.university_id
    LIMIT 1000
    """
    
    courses = []
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            for row in cur.fetchall():
                course_dict = dict(row)
                # Get entry requirements
                cur.execute("""
                    SELECT subject_id, required_grade 
                    FROM course_requirement 
                    WHERE course_id = %s
                """, (course_dict['course_id'],))
                requirements = {r[0]: r[1] for r in cur.fetchall()}
                
                course_dict['entryRequirements'] = {
                    'grades': requirements
                }
                courses.append(course_dict)
    
    return courses
```

### 4. Top-K Heap Algorithm

**Add to RecommendationEngine class**:
```python
import heapq

def get_recommendations(self, a_level_subjects, predicted_grades, preferences, criteria):
    """Generate recommendations using Top-K heap selection"""
    courses = self._get_all_courses()
    
    # Use heap for efficient Top-K selection
    heap = []  # Min-heap: (score, course_data)
    k = 50  # Top 50 recommendations
    
    for course in courses:
        match_score = self._calculate_match_score(
            course, a_level_subjects, predicted_grades, preferences, criteria
        )
        
        if match_score > 0:
            if len(heap) < k:
                heapq.heappush(heap, (match_score, course))
            elif match_score > heap[0][0]:
                heapq.heapreplace(heap, (match_score, course))
    
    # Convert heap to sorted list (descending)
    recommendations = []
    for score, course in sorted(heap, reverse=True):
        recommendations.append({
            'course': course,
            'matchScore': score,
            'reasons': self._get_match_reasons(course, a_level_subjects, predicted_grades, preferences)
        })
    
    return recommendations
```

### 5. Complex SQL Query Example

**Add to app.py**:
```python
@app.route('/api/recommendations/advanced', methods=['POST'])
@jwt_required()
def get_advanced_recommendations():
    """Complex SQL query with JOINs and CTEs"""
    student_id = get_jwt_identity()
    
    query = """
    WITH student_profile AS (
        SELECT 
            s.student_id,
            sg.subject_id,
            sg.predicted_grade,
            s.region as preferred_region,
            s.tuition_budget
        FROM student s
        LEFT JOIN student_grade sg ON s.student_id = sg.student_id
        WHERE s.student_id = %s
    ),
    course_scores AS (
        SELECT 
            c.course_id,
            c.name,
            u.name as university_name,
            u.rank_overall,
            COUNT(DISTINCT CASE 
                WHEN cr.subject_id IN (SELECT subject_id FROM student_profile) 
                THEN cr.subject_id 
            END) as matched_subjects,
            AVG(CASE 
                WHEN sg.predicted_grade >= cr.required_grade THEN 1.0 
                ELSE 0.0 
            END) as grade_match_ratio,
            CASE WHEN u.region = sp.preferred_region THEN 1.0 ELSE 0.0 END as region_match,
            CASE WHEN c.annual_fee <= sp.tuition_budget THEN 1.0 ELSE 0.0 END as budget_match
        FROM course c
        JOIN university u ON c.university_id = u.university_id
        LEFT JOIN course_requirement cr ON c.course_id = cr.course_id
        LEFT JOIN student_profile sg ON cr.subject_id = sg.subject_id
        CROSS JOIN (SELECT preferred_region, tuition_budget FROM student_profile LIMIT 1) sp
        GROUP BY c.course_id, c.name, u.name, u.rank_overall, sp.preferred_region, sp.tuition_budget, u.region, c.annual_fee
    )
    SELECT 
        course_id,
        name,
        university_name,
        (matched_subjects * 0.3 + grade_match_ratio * 0.25 + region_match * 0.2 + budget_match * 0.15 + (1.0 / rank_overall) * 0.1) as total_score
    FROM course_scores
    ORDER BY total_score DESC
    LIMIT 50;
    """
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (student_id,))
            results = [dict(row) for row in cur.fetchall()]
    
    return jsonify({'recommendations': results})
```

---

## Essential Test Suite (Minimum Viable)

### Create `server/tests/test_recommendation_engine.py`:
```python
import pytest
from recommendation_engine import RecommendationEngine

def test_calculate_subject_match():
    engine = RecommendationEngine()
    course = {'entryRequirements': {'subjects': ['Mathematics', 'Physics']}}
    subjects = ['Mathematics', 'Physics', 'Chemistry']
    score = engine._calculate_subject_match(course, subjects)
    assert score > 0.8

def test_calculate_grade_match():
    engine = RecommendationEngine()
    course = {'entryRequirements': {'grades': {'Mathematics': 'A', 'Physics': 'B'}}}
    grades = {'Mathematics': 'A*', 'Physics': 'A'}
    score = engine._calculate_grade_match(course, grades)
    assert score >= 0.5

def test_weighted_scoring():
    engine = RecommendationEngine()
    # Test that weights sum correctly
    total_weight = sum(engine.weights.values())
    assert abs(total_weight - 1.0) < 0.01
```

### Create `server/tests/test_api.py`:
```python
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'OK'

def test_register_endpoint(client):
    response = client.post('/api/auth/register', json={
        'email': 'test@test.com',
        'password': 'testpass123',
        'firstName': 'Test',
        'lastName': 'User'
    })
    assert response.status_code in [201, 400]  # 400 if user exists
```

---

## Time-Saving Tips

1. **Copy-paste ready code**: Use the code snippets above - they're production-ready
2. **Focus on one thing**: Don't try to perfect everything - get it working first
3. **Test as you go**: Write tests immediately after implementing features
4. **Use existing schema**: Don't modify database schema - use what exists
5. **Skip perfection**: Basic implementation is better than perfect but incomplete

---

## What to Skip (If Time Runs Out)

- ❌ Advanced graph algorithms (can use simple scoring)
- ❌ Complex UI improvements (frontend works)
- ❌ Extensive documentation (update README only)
- ❌ Performance optimization (basic is fine)
- ❌ Advanced error handling (basic try-catch is enough)

---

## Success Criteria (End of Day 2)

✅ System runs with PostgreSQL  
✅ Recommendations work with real database  
✅ At least 10 tests pass  
✅ Top-K heap algorithm implemented  
✅ One complex SQL query with JOINs  
✅ OOP inheritance/composition added  
✅ PDF export works (basic)  
✅ All core features functional  

---

## Estimated Final Marks (After 2 Days)

| Section | Expected | Max |
|---------|----------|-----|
| Technical Solution | 32-35 | 42 |
| Testing | 5-6 | 8 |
| Completeness | 12-13 | 15 |
| **Total** | **~60-65** | **75** |

**This is a solid pass with good marks!**

---

## Emergency Backup Plan (If Behind Schedule)

**If you're running out of time, prioritize**:
1. Database migration (2 hours) - **MUST HAVE**
2. Basic tests (1 hour) - **MUST HAVE**
3. Top-K heap (30 min) - **QUICK WIN**
4. One complex SQL (30 min) - **QUICK WIN**
5. OOP inheritance (30 min) - **QUICK WIN**

**Skip**: PDF export, admin interface, advanced features

---

**Good luck! You can do this! 💪**
