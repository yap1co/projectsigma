# Test Cases Catalog

## Overview

This document catalogs all test cases in the University Course Recommender system, organized by test suite and functionality.

**Total Tests**: 43  
**Status**: 100% Passing (43/43) ✅

---

## Test Suite 1: Recommendation Engine Tests (13 tests)

### RE-001: Engine Initialization
- **Test ID**: `test_engine_initialization`
- **Purpose**: Verify RecommendationEngine initializes correctly
- **What it tests**: Engine object creation, attribute existence
- **How it tests**: Creates engine instance, checks for `weights` and `grade_values` attributes
- **Expected**: Engine created, attributes present
- **Status**: ✅ PASS

### RE-002: Weight Validation
- **Test ID**: `test_weights_sum_to_one`
- **Purpose**: Ensure recommendation weights sum to 1.0
- **What it tests**: Weight configuration correctness
- **How it tests**: Sums all weight values, checks if equals 1.0 (within 0.01 tolerance)
- **Expected**: Total weight = 1.0
- **Status**: ✅ PASS

### RE-003: Subject Match - Perfect Match
- **Test ID**: `test_calculate_subject_match_perfect`
- **Purpose**: Test subject matching when all required subjects match
- **What it tests**: Perfect subject alignment scoring
- **How it tests**: Course requires ['Mathematics', 'Physics'], student has ['Mathematics', 'Physics', 'Chemistry']
- **Expected**: Score > 0.8
- **Status**: ✅ PASS

### RE-004: Subject Match - Partial Match
- **Test ID**: `test_calculate_subject_match_partial`
- **Purpose**: Test subject matching when some required subjects match
- **What it tests**: Partial subject alignment scoring
- **How it tests**: Course requires ['Mathematics', 'Physics', 'Chemistry'], student has ['Mathematics', 'Physics']
- **Expected**: Score between 0.3-0.9
- **Status**: ✅ PASS

### RE-005: Subject Match - No Requirements
- **Test ID**: `test_calculate_subject_match_no_requirements`
- **Purpose**: Test subject matching when course has no requirements
- **What it tests**: Default scoring for courses without requirements
- **How it tests**: Course has empty subjects list, student has subjects
- **Expected**: Score = 0.5 (neutral)
- **Status**: ✅ PASS

### RE-006: Grade Match - Exceeds Requirements
- **Test ID**: `test_calculate_grade_match_exceeds`
- **Purpose**: Test grade matching when student grades exceed requirements
- **What it tests**: Bonus scoring for exceeding requirements
- **How it tests**: Course requires {'Mathematics': 'A', 'Physics': 'B'}, student has {'Mathematics': 'A*', 'Physics': 'A'}
- **Expected**: Score >= 0.5
- **Status**: ✅ PASS

### RE-007: Grade Match - Meets Requirements
- **Test ID**: `test_calculate_grade_match_meets`
- **Purpose**: Test grade matching when student grades meet requirements exactly
- **What it tests**: Exact match scoring
- **How it tests**: Course requires {'Mathematics': 'A', 'Physics': 'B'}, student has {'Mathematics': 'A', 'Physics': 'B'}
- **Expected**: Score >= 0.5
- **Status**: ✅ PASS

### RE-008: Grade Match - Below Requirements
- **Test ID**: `test_calculate_grade_match_below`
- **Purpose**: Test grade matching when student grades are below requirements
- **What it tests**: Penalty scoring for unmet requirements
- **How it tests**: Course requires {'Mathematics': 'A', 'Physics': 'B'}, student has {'Mathematics': 'B', 'Physics': 'C'}
- **Expected**: Score < 1.0 (penalized)
- **Status**: ✅ PASS

### RE-009: Preference Match - Region
- **Test ID**: `test_calculate_preference_match_region`
- **Purpose**: Test preference matching for region preference
- **What it tests**: Location-based scoring
- **How it tests**: Course in 'South East', student prefers 'South East'
- **Expected**: Score 0-1.0
- **Status**: ✅ PASS

### RE-010: Preference Match - Budget
- **Test ID**: `test_calculate_preference_match_budget`
- **Purpose**: Test preference matching for budget preference
- **What it tests**: Budget constraint scoring
- **How it tests**: Course fee £9000, student max budget £10000
- **Expected**: Score 0-1.0
- **Status**: ✅ PASS

### RE-011: Ranking Score - Top Ranked
- **Test ID**: `test_calculate_ranking_score_top_ranked`
- **Purpose**: Test ranking score for top-ranked university
- **What it tests**: High ranking bonus scoring
- **How it tests**: University ranked #1
- **Expected**: Score > 0.9
- **Status**: ✅ PASS

### RE-012: Ranking Score - No Ranking
- **Test ID**: `test_calculate_ranking_score_no_ranking`
- **Purpose**: Test ranking score when no ranking data available
- **What it tests**: Default scoring for missing data
- **How it tests**: Course with no ranking information
- **Expected**: Score = 0.5 (neutral)
- **Status**: ✅ PASS

### RE-013: Weighted Match Score
- **Test ID**: `test_calculate_match_score_weighted`
- **Purpose**: Test composite weighted score calculation
- **What it tests**: Overall match score combining all factors
- **How it tests**: Complete course and student profile, calculates weighted score
- **Expected**: Score 0-1.0, positive value
- **Status**: ✅ PASS

---

## Test Suite 2: Model Tests (8 tests)

### M-001: Student Creation
- **Test ID**: `test_student_creation`
- **Purpose**: Verify Student model can be created
- **What it tests**: Student object instantiation
- **How it tests**: Creates Student with email, password, firstName, lastName
- **Expected**: Student created with correct attributes
- **Status**: ✅ PASS

### M-002: Student Defaults
- **Test ID**: `test_student_defaults`
- **Purpose**: Verify Student model default values
- **What it tests**: Default attribute values
- **How it tests**: Creates Student, checks default values for yearGroup, aLevelSubjects, etc.
- **Expected**: Defaults match specification
- **Status**: ✅ PASS

### M-003: Student to Dictionary
- **Test ID**: `test_student_to_dict`
- **Purpose**: Test Student serialization to dictionary
- **What it tests**: `to_dict()` method
- **How it tests**: Creates Student, calls `to_dict()`, verifies structure
- **Expected**: Returns dict with all attributes
- **Status**: ✅ PASS

### M-004: Student from Dictionary
- **Test ID**: `test_student_from_dict`
- **Purpose**: Test Student deserialization from dictionary
- **What it tests**: `from_dict()` class method
- **How it tests**: Creates dict, calls `Student.from_dict()`, verifies object
- **Expected**: Student object created with correct data
- **Status**: ✅ PASS

### M-005: Student Profile Completeness
- **Test ID**: `test_student_is_complete_profile`
- **Purpose**: Test profile completeness check
- **What it tests**: `is_complete_profile()` method
- **How it tests**: Creates incomplete profile, then adds subjects/grades/preferences
- **Expected**: Returns False initially, True when complete
- **Status**: ✅ PASS

### M-006: Student Full Name
- **Test ID**: `test_student_get_full_name`
- **Purpose**: Test full name retrieval
- **What it tests**: `get_full_name()` method
- **How it tests**: Creates Student with firstName and lastName, calls method
- **Expected**: Returns "FirstName LastName"
- **Status**: ✅ PASS

### M-007: Course Creation
- **Test ID**: `test_course_creation`
- **Purpose**: Verify Course model can be created
- **What it tests**: Course object instantiation with nested objects
- **How it tests**: Creates Course with EntryRequirements, Fees, Ranking, Employability
- **Expected**: Course created with all nested objects
- **Status**: ✅ PASS

### M-008: Course Subject Matching
- **Test ID**: `test_course_matches_subjects`
- **Purpose**: Test course subject matching logic
- **What it tests**: `matches_subjects()` method
- **How it tests**: Course requires ['Mathematics', 'Physics'], tests various student subject combinations
- **Expected**: Returns True for matching subjects, False otherwise
- **Status**: ✅ PASS

### M-009: Course Grade Requirements
- **Test ID**: `test_course_meets_grade_requirements`
- **Purpose**: Test grade requirement checking
- **What it tests**: `meets_grade_requirements()` method
- **How it tests**: Course requires {'Mathematics': 'A'}, tests with A*, A, B grades
- **Expected**: True for A* and A, False for B
- **Status**: ✅ PASS

### M-010: Course Affordability
- **Test ID**: `test_course_is_affordable`
- **Purpose**: Test budget affordability check
- **What it tests**: `is_affordable()` method
- **How it tests**: Course fee £9000, tests with budgets £10000, £9000, £8000
- **Expected**: True for >= £9000, False for < £9000
- **Status**: ✅ PASS

---

## Test Suite 3: OOP Features Tests (8 tests)

### OOP-001: Student Inheritance
- **Test ID**: `test_student_inherits_from_base_model`
- **Purpose**: Verify Student inherits from BaseModel
- **What it tests**: Inheritance pattern
- **How it tests**: Creates Student, checks `isinstance(student, BaseModel)`, verifies inherited attributes
- **Expected**: Student is instance of BaseModel, has inherited methods
- **Status**: ✅ PASS

### OOP-002: Course Inheritance
- **Test ID**: `test_course_inherits_from_base_model`
- **Purpose**: Verify Course inherits from BaseModel
- **What it tests**: Inheritance pattern
- **How it tests**: Creates Course, checks `isinstance(course, BaseModel)`, verifies inherited attributes
- **Expected**: Course is instance of BaseModel, has inherited methods
- **Status**: ✅ PASS

### OOP-003: BaseModel Common Methods
- **Test ID**: `test_base_model_common_methods`
- **Purpose**: Test common methods inherited from BaseModel
- **What it tests**: `get_created_at()`, `is_recent()`, `__repr__()`
- **How it tests**: Creates Student, calls inherited methods
- **Expected**: Methods work correctly
- **Status**: ✅ PASS

### OOP-004: Recommendation Engine Composition
- **Test ID**: `test_recommendation_engine_uses_composition`
- **Purpose**: Verify RecommendationEngine uses composition pattern
- **What it tests**: Composition with scorer components
- **How it tests**: Creates engine, checks for scorer attributes or fallback methods
- **Expected**: Engine uses composition (scorers) or has fallback methods
- **Status**: ✅ PASS

### OOP-005: Scorer Components
- **Test ID**: `test_scorer_components`
- **Purpose**: Test individual scorer components
- **What it tests**: SubjectMatchScorer functionality
- **How it tests**: Creates scorer, calls `calculate_score()` with test data
- **Expected**: Returns score 0-1.0
- **Status**: ✅ PASS

### OOP-006: Grade Scorer Component
- **Test ID**: `test_grade_scorer_component`
- **Purpose**: Test GradeMatchScorer component
- **What it tests**: Grade matching scorer functionality
- **How it tests**: Creates scorer, calls `calculate_score()` with grade data
- **Expected**: Returns score 0-1.0
- **Status**: ✅ PASS

### OOP-007: to_dict Polymorphism
- **Test ID**: `test_to_dict_polymorphism`
- **Purpose**: Test polymorphic behavior of to_dict method
- **What it tests**: Polymorphism pattern
- **How it tests**: Creates Student, calls `to_dict()`, verifies it works for different model types
- **Expected**: Method works polymorphically across models
- **Status**: ✅ PASS

### OOP-008: from_dict Polymorphism
- **Test ID**: `test_from_dict_polymorphism`
- **Purpose**: Test polymorphic behavior of from_dict method
- **What it tests**: Polymorphism pattern
- **How it tests**: Creates dict, calls `Student.from_dict()`, verifies object type
- **Expected**: Method works polymorphically, returns correct type
- **Status**: ✅ PASS

---

## Test Suite 4: API Integration Tests (12 tests)

### API-001: Health Check
- **Test ID**: `test_health_check`
- **Purpose**: Test API health check endpoint
- **What it tests**: `/api/health` endpoint
- **How it tests**: Sends GET request, verifies response status and structure
- **Expected**: Status 200, returns {'status': 'OK', 'timestamp': ...}
- **Status**: ✅ PASS

### API-002: Registration - Missing Fields
- **Test ID**: `test_register_missing_fields`
- **Purpose**: Test registration validation for missing fields
- **What it tests**: Input validation
- **How it tests**: Sends POST to `/api/auth/register` with only email (missing password, firstName, lastName)
- **Expected**: Status 400 or 500 (validation error)
- **Status**: ✅ PASS

### API-003: Registration - Valid Data
- **Test ID**: `test_register_valid_data`
- **Purpose**: Test successful student registration
- **What it tests**: Registration endpoint with valid data
- **How it tests**: Sends POST with complete valid data, unique email
- **Expected**: Status 201 (created) or 400 (if user exists), returns access_token and student_id
- **Status**: ✅ PASS

### API-004: Login - Invalid Credentials
- **Test ID**: `test_login_invalid_credentials`
- **Purpose**: Test login with wrong credentials
- **What it tests**: Authentication failure handling
- **How it tests**: Sends POST to `/api/auth/login` with non-existent email and wrong password
- **Expected**: Status 401 (Unauthorized)
- **Status**: ✅ PASS

### API-005: Login - Missing Fields
- **Test ID**: `test_login_missing_fields`
- **Purpose**: Test login validation for missing fields
- **What it tests**: Input validation
- **How it tests**: Sends POST with only email (missing password)
- **Expected**: Status 400, 401, or 500 (validation error)
- **Status**: ✅ PASS

### API-006: Get Courses
- **Test ID**: `test_get_courses`
- **Purpose**: Test courses list endpoint
- **What it tests**: `/api/courses` GET endpoint
- **How it tests**: Sends GET request, verifies response structure
- **Expected**: Status 200, returns {'courses': [...], 'total': int}
- **Status**: ✅ PASS

### API-007: Get Courses with Limit
- **Test ID**: `test_get_courses_with_limit`
- **Purpose**: Test courses endpoint with limit parameter
- **What it tests**: Query parameter handling
- **How it tests**: Sends GET to `/api/courses?limit=10`
- **Expected**: Status 200, returns <= 10 courses
- **Status**: ✅ PASS

### API-008: Get Universities
- **Test ID**: `test_get_universities`
- **Purpose**: Test universities list endpoint
- **What it tests**: `/api/universities` GET endpoint
- **How it tests**: Sends GET request, verifies response structure
- **Expected**: Status 200, returns {'universities': [...]}
- **Status**: ✅ PASS

### API-009: Get Profile Without Auth
- **Test ID**: `test_get_profile_without_auth`
- **Purpose**: Test that profile endpoint requires authentication
- **What it tests**: JWT authentication requirement
- **How it tests**: Sends GET to `/api/student/profile` without Authorization header
- **Expected**: Status 401 (Unauthorized)
- **Status**: ✅ PASS

### API-010: Get Recommendations Without Auth
- **Test ID**: `test_get_recommendations_without_auth`
- **Purpose**: Test that recommendations endpoint requires authentication
- **What it tests**: JWT authentication requirement
- **How it tests**: Sends POST to `/api/recommendations` without Authorization header
- **Expected**: Status 401 (Unauthorized)
- **Status**: ✅ PASS

### API-011: Database Helper Import
- **Test ID**: `test_database_helper_import`
- **Purpose**: Test database helper module can be imported
- **What it tests**: Module availability
- **How it tests**: Imports `database_helper`, checks functions are callable
- **Expected**: Module imports, functions are callable
- **Status**: ✅ PASS

### API-012: Generate ID
- **Test ID**: `test_generate_id`
- **Purpose**: Test ID generation function
- **What it tests**: `generate_id()` function
- **How it tests**: Calls `generate_id('TEST')` twice, verifies format and uniqueness
- **Expected**: IDs start with prefix, are unique, have additional characters
- **Status**: ✅ PASS

---

## Test Execution Summary

### Test Statistics
- **Total Tests**: 43
- **Passing**: 43 (100%)
- **Failing**: 0
- **Skipped**: 0

### Test Categories
- **Unit Tests**: 31 tests (72%)
- **Integration Tests**: 12 tests (28%)

### Test Suites
- **Recommendation Engine**: 13 tests
- **Models**: 8 tests
- **OOP Features**: 8 tests
- **API Integration**: 12 tests

---

## Test Coverage Areas

### ✅ Fully Covered
- Recommendation algorithm logic
- Subject matching
- Grade matching
- Preference matching
- Ranking scoring
- Model creation and validation
- OOP patterns (inheritance, composition, polymorphism)
- API endpoints
- Authentication
- Input validation

### ⚠️ Partially Covered
- Career interest filtering (tested indirectly)
- Feedback system (tested via API)
- HESA data enrichment (tested indirectly)

### ❌ Not Covered (Future)
- Performance benchmarks
- Load testing
- Security penetration testing
- Browser-based UI testing

---

## Test Maintenance

### Regular Updates
- Update tests when requirements change
- Add tests for new features
- Refactor tests for maintainability

### Test Review
- Quarterly test review
- Coverage analysis
- Performance benchmarking

---

## Notes

- All tests are automated using pytest
- Integration tests require database connection
- Tests are designed to be independent and idempotent
- Test data is isolated from production data
