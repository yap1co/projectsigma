# Flask API (app.py) - Technical Documentation

## Overview

The Flask API (`app.py`) is the backend REST API server for the University Course Recommender system. It handles authentication, student profiles, course recommendations, and feedback management.

**Location**: `server/app.py`  
**Framework**: Flask 2.x  
**Lines**: ~1093 lines  
**Dependencies**: Flask, Flask-JWT-Extended, Flask-CORS, psycopg2, werkzeug

## Architecture

### Application Structure

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
```

### Initialization

```python
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

jwt = JWTManager(app)
CORS(app)
recommendation_engine = RecommendationEngine()
```

**Configuration:**
- `JWT_SECRET_KEY`: Secret key for JWT token signing (from environment)
- `JWT_ACCESS_TOKEN_EXPIRES`: Token expiration (7 days)
- `CORS`: Cross-Origin Resource Sharing enabled for frontend

## Data Structures

### Request Data Structures

#### Student Registration
```python
{
    'email': str,              # Required, validated format
    'password': str,           # Required, min 8 chars, alphanumeric
    'firstName': str,          # Required, 1-100 chars
    'lastName': str,           # Required, 1-100 chars
    'yearGroup': str,          # Optional: 'Year 11', 'Year 12', 'Year 13'
    'predictedGrades': {       # Optional
        'subject_id': 'grade'  # e.g., {'Mathematics': 'A', 'Economics': 'B'}
    },
    'aLevelSubjects': [str],  # Optional: ['Mathematics', 'Economics', ...]
    'preferences': {           # Optional
        'preferredRegion': str,
        'maxBudget': int,
        'preferredExams': [str]
    }
}
```

#### Student Login
```python
{
    'email': str,      # Required
    'password': str    # Required
}
```

#### Profile Update
```python
{
    'preferences': {
        'preferredRegion': str,
        'maxBudget': int,
        'preferredExams': [str]
    },
    'aLevelSubjects': [str],
    'predictedGrades': {
        'subject_id': 'grade'
    }
}
```

#### Password Change
```python
{
    'currentPassword': str,  # Required
    'newPassword': str       # Required, validated
}
```

#### Recommendation Request
```python
{
    'limit': int,           # Optional, default 50
    'filters': {...}        # Optional, additional filters
}
```

#### Feedback Submission
```python
{
    'courseId': str,        # Required
    'feedbackType': str,    # Required: 'positive' or 'negative'
    'matchScore': float,    # Optional
    'searchCriteria': {},   # Optional
    'notes': str           # Optional, max 500 chars
}
```

#### Setting Update
```python
{
    'value': Any  # Required, type depends on setting_key
}
```

### Response Data Structures

#### Success Response
```python
{
    'message': str,         # Success message
    'data': {...}          # Optional, response data
}
```

#### Error Response
```python
{
    'message': str  # Error message
}
```

#### Student Profile Response
```python
{
    'student': {
        'student_id': str,
        'display_name': str,
        'email': str,
        'firstName': str,
        'lastName': str,
        'yearGroup': str,
        'aLevelSubjects': [str],
        'predictedGrades': {
            'subject_id': 'grade'
        },
        'preferences': {
            'preferredRegion': str,
            'maxBudget': int,
            'preferredExams': [str]
        },
        'created_at': str  # ISO format
    }
}
```

#### Recommendations Response
```python
{
    'recommendations': [
        {
            'course': {
                'course_id': str,
                'name': str,
                'university': {...},
                'entryRequirements': {...},
                'fees': {...},
                'employability': {...}
            },
            'matchScore': float,      # 0.0-1.0
            'meetsRequirements': bool,
            'reasons': [str]
        }
    ],
    'total': int,
    'studentId': str
}
```

#### Feedback History Response
```python
{
    'courseId': str,
    'feedbackHistory': [
        {
            'feedback_id': str,
            'feedback_type': str,    # 'positive' or 'negative'
            'feedback_at': str,      # ISO timestamp
            'match_score': float,
            'notes': str
        }
    ],
    'summary': {
        'positive': int,
        'negative': int,
        'total': int
    }
}
```

## API Endpoints

### Public Endpoints

#### `GET /`
**Purpose**: API information and endpoint listing

**Response:**
```python
{
    'name': 'University Course Recommender API',
    'version': '1.0.0',
    'status': 'running',
    'endpoints': {...},
    'documentation': 'See README.md for API documentation'
}
```

#### `GET /api/health`
**Purpose**: Health check endpoint

**Response:**
```python
{
    'status': 'OK',
    'timestamp': str,      # ISO format
    'environment': str     # 'development' or 'production'
}
```

### Authentication Endpoints

#### `POST /api/auth/register`
**Purpose**: Register a new student

**Request Body**: Student registration data (see above)

**Response (201):**
```python
{
    'message': 'Registration successful',
    'access_token': str,   # JWT token
    'student_id': str
}
```

**Errors:**
- `400`: Missing/invalid fields, user already exists
- `500`: Registration failed

**Data Flow:**
1. Validate input using `validate_student_registration()`
2. Sanitize inputs using `sanitize_string()`
3. Check if user exists via `get_student_by_email()`
4. Generate student ID using `generate_id('STU')`
5. Hash password using `generate_password_hash()`
6. Insert into `student` table
7. Insert grades into `student_grade` table
8. Create JWT token using `create_access_token()`
9. Return token and student ID

**SQL Operations:**
```sql
-- Insert student
INSERT INTO student (student_id, display_name, email, password_hash, ...)
VALUES (%s, %s, %s, %s, ...)

-- Insert grades
INSERT INTO student_grade (student_id, subject_id, predicted_grade)
VALUES (%s, %s, %s)
```

#### `POST /api/auth/login`
**Purpose**: Login student

**Request Body**: Login data (email, password)

**Response (200):**
```python
{
    'message': 'Login successful',
    'access_token': str,   # JWT token
    'student_id': str
}
```

**Errors:**
- `400`: Missing fields, invalid email format
- `401`: Invalid credentials
- `500`: Login failed

**Data Flow:**
1. Validate email format
2. Sanitize email
3. Fetch student via `get_student_by_email()`
4. Verify password using `check_password_hash()`
5. Create JWT token
6. Return token and student ID

### Protected Endpoints (Require JWT)

All protected endpoints use `@jwt_required()` decorator and get student ID via `get_jwt_identity()`.

#### `GET /api/student/profile`
**Purpose**: Get student profile

**Headers**: `Authorization: Bearer <token>`

**Response (200):**
```python
{
    'student': {
        # Full student profile (see above)
    }
}
```

**Errors:**
- `404`: Student not found
- `500`: Failed to get profile

**SQL Query:**
```sql
SELECT s.*, sg.subject_id, sg.predicted_grade
FROM student s
LEFT JOIN student_grade sg ON s.student_id = sg.student_id
WHERE s.student_id = %s
```

#### `PUT /api/student/profile`
**Purpose**: Update student profile

**Headers**: `Authorization: Bearer <token>`

**Request Body**: Profile update data

**Response (200):**
```python
{
    'message': 'Profile updated successfully'
}
```

**Errors:**
- `400`: Invalid preferences
- `500`: Failed to update

**SQL Operations:**
```sql
-- Update preferences
UPDATE student
SET region = %s, tuition_budget = %s, preferred_exams = %s
WHERE student_id = %s

-- Delete old grades
DELETE FROM student_grade WHERE student_id = %s

-- Insert new grades
INSERT INTO student_grade (student_id, subject_id, predicted_grade)
VALUES (%s, %s, %s)
```

#### `PUT /api/student/password`
**Purpose**: Change password

**Headers**: `Authorization: Bearer <token>`

**Request Body**: Password change data

**Response (200):**
```python
{
    'message': 'Password updated successfully'
}
```

**Errors:**
- `400`: Missing/invalid fields, invalid new password
- `401`: Current password incorrect
- `404`: Student not found
- `500`: Failed to update

**SQL Operation:**
```sql
UPDATE student
SET password_hash = %s
WHERE student_id = %s
```

### Recommendation Endpoints

#### `POST /api/recommendations`
**Purpose**: Get course recommendations

**Headers**: `Authorization: Bearer <token>`

**Request Body**: Optional criteria

**Response (200):**
```python
{
    'recommendations': [...],  # List of recommendations
    'total': int,
    'studentId': str
}
```

**Data Flow:**
1. Get student ID from JWT
2. Fetch student profile from database
3. Call `recommendation_engine.get_recommendations()`
4. Save recommendation run to database
5. Return recommendations

**SQL Operations:**
```sql
-- Save recommendation run
INSERT INTO recommendation_run (run_id, student_id, run_at, weights, prefs_snapshot)
VALUES (%s, %s, CURRENT_DATE, %s, %s)

-- Save recommendation results
INSERT INTO recommendation_result (result_id, run_id, items)
VALUES (%s, %s, %s)
```

#### `POST /api/recommendations/advanced`
**Purpose**: Advanced recommendations using complex SQL

**Headers**: `Authorization: Bearer <token>`

**Response (200):**
```python
{
    'recommendations': [...],
    'total': int,
    'method': 'advanced_sql',
    'studentId': str
}
```

**SQL Query Structure:**
Uses Common Table Expressions (CTEs) for complex calculations:

```sql
WITH student_profile AS (
    -- Get student's academic profile
    SELECT ...
),
course_subject_matches AS (
    -- Calculate subject matches
    SELECT ...
),
course_grade_matches AS (
    -- Calculate grade matches
    SELECT ...
),
course_scores AS (
    -- Calculate composite scores
    SELECT ...
)
SELECT ... FROM course_scores
ORDER BY total_score DESC
LIMIT 50
```

**Demonstrates:**
- Group A: Cross-table parameterised SQL with CTEs
- Aggregate functions (COUNT, AVG, COALESCE)
- Complex joins and subqueries
- Weighted scoring in SQL

### Course and University Endpoints

#### `GET /api/courses`
**Purpose**: Get all courses with optional filtering

**Query Parameters:**
- `subject`: Filter by subject (string)
- `university`: Filter by university name (string)
- `max_fee`: Filter by maximum fee (int)
- `limit`: Limit results (int, default 50, max 100)

**Response (200):**
```python
{
    'courses': [
        {
            'course_id': str,
            'name': str,
            'university': {...},
            'entryRequirements': {...},
            'fees': {...},
            'employability': {...}
        }
    ],
    'total': int
}
```

**SQL Query:**
```sql
SELECT c.*, u.*
FROM course c
JOIN university u ON c.university_id = u.university_id
WHERE 1=1
  AND (subject filter if provided)
  AND (university filter if provided)
  AND (max_fee filter if provided)
LIMIT %s
```

#### `GET /api/universities`
**Purpose**: Get all universities

**Response (200):**
```python
{
    'universities': [
        {
            'university_id': str,
            'name': str,
            'region': str,
            'ranking': {'overall': int},
            'employability_score': float,
            'website_url': str
        }
    ]
}
```

**SQL Query:**
```sql
SELECT university_id, name, region, rank_overall, 
       employability_score, website_url
FROM university
ORDER BY rank_overall NULLS LAST
```

### Feedback Endpoints

#### `POST /api/recommendations/feedback`
**Purpose**: Submit feedback on a recommendation

**Headers**: `Authorization: Bearer <token>`

**Request Body**: Feedback data

**Response (200):**
```python
{
    'message': 'Feedback submitted successfully',
    'feedbackId': str
}
```

**SQL Operation:**
```sql
INSERT INTO recommendation_feedback 
    (feedback_id, student_id, course_id, feedback_type, 
     match_score, search_criteria, notes)
VALUES (%s, %s, %s, %s, %s, %s, %s)
```

#### `GET /api/recommendations/feedback/<course_id>`
**Purpose**: Get feedback history for a course

**Headers**: `Authorization: Bearer <token>`

**Response (200):**
```python
{
    'courseId': str,
    'feedbackHistory': [...],
    'summary': {
        'positive': int,
        'negative': int,
        'total': int
    }
}
```

**SQL Query:**
```sql
SELECT feedback_id, feedback_type, feedback_at, 
       match_score, notes
FROM recommendation_feedback
WHERE student_id = %s AND course_id = %s
ORDER BY feedback_at DESC
LIMIT 50
```

### Settings Endpoints

#### `GET /api/recommendations/settings`
**Purpose**: Get tunable recommendation settings

**Headers**: `Authorization: Bearer <token>`

**Response (200):**
```python
{
    'settings': {
        'feedback_weight': {
            'value': float,
            'description': str
        },
        ...
    }
}
```

**SQL Query:**
```sql
SELECT setting_key, setting_value, description
FROM recommendation_settings
ORDER BY setting_key
```

#### `PUT /api/recommendations/settings/<setting_key>`
**Purpose**: Update a recommendation setting

**Headers**: `Authorization: Bearer <token>`

**Request Body**: Setting update data

**Response (200):**
```python
{
    'message': 'Setting updated successfully',
    'settingKey': str,
    'newValue': Any
}
```

**Valid Setting Keys:**
- `feedback_weight`: Float 0.0-1.0
- `feedback_decay_days`: Int >= 0
- `min_feedback_count`: Int >= 0
- `positive_feedback_boost`: Float
- `negative_feedback_penalty`: Float

**SQL Operation:**
```sql
UPDATE recommendation_settings
SET setting_value = %s,
    updated_at = CURRENT_TIMESTAMP,
    updated_by = %s
WHERE setting_key = %s
```

### Admin Endpoints

#### `POST /api/admin/courses`
**Purpose**: Add new course (admin only)

**Headers**: `Authorization: Bearer <token>`

**Request Body**: Course data

**Response (201):**
```python
{
    'message': 'Course added successfully',
    'course_id': str
}
```

**SQL Operations:**
```sql
-- Create university if needed
INSERT INTO university (university_id, name, region, ...)
VALUES (%s, %s, %s, ...)
ON CONFLICT (university_id) DO NOTHING

-- Create course
INSERT INTO course (course_id, university_id, name, ...)
VALUES (%s, %s, %s, ...)

-- Add course requirements
INSERT INTO course_requirement (req_id, course_id, subject_id, grade_req)
VALUES (%s, %s, %s, %s)
```

### Export Endpoints

#### `GET /api/export/recommendations/<student_id>?format=csv|pdf`
**Purpose**: Export recommendations as CSV or PDF

**Headers**: `Authorization: Bearer <token>`

**Query Parameters:**
- `format`: 'csv' or 'pdf' (default: 'csv')

**Response:**
- CSV: JSON with CSV string
- PDF: Binary PDF file

**CSV Format:**
```csv
Rank,Course,University,Match Score,Fees,Entry Requirements
1,Business Management,University of London,0.85,9250,{'Mathematics': 'B'}
```

**PDF Format:**
- Uses `reportlab` library
- Formatted table with top 30 recommendations
- Includes summary statistics

## Python Data Structures Used

### Lists
- `List[str]`: Subjects, exam types, reasons
- `List[Dict[str, Any]]`: Courses, recommendations, feedback history

### Dictionaries
- `Dict[str, str]`: Grade mappings, query parameters
- `Dict[str, Any]`: Request/response bodies, course data, student data
- `Dict[str, Dict[str, Any]]`: Nested structures (university, fees, etc.)

### Sets
- `Set[str]`: Used internally for deduplication

### Specialized
- `RealDictCursor`: PostgreSQL cursor returning dicts
- `timedelta`: JWT expiration
- `io.StringIO`: CSV generation
- `io.BytesIO`: PDF generation

## Security Features

### Authentication
- **JWT Tokens**: Stateless authentication
- **Password Hashing**: `werkzeug.security.generate_password_hash()` (PBKDF2)
- **Token Expiration**: 7 days

### Input Validation
- **Email Validation**: Regex pattern matching
- **Password Validation**: Min 8 chars, alphanumeric
- **String Sanitization**: `sanitize_string()` removes whitespace, truncates
- **Limit Validation**: `validate_limit()` prevents excessive queries

### SQL Injection Prevention
- **Parameterized Queries**: All SQL uses `%s` placeholders
- **No String Concatenation**: Never builds SQL from user input directly

### CORS
- **Cross-Origin Resource Sharing**: Enabled for frontend
- **Configurable**: Can restrict to specific origins in production

## Error Handling

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid credentials, missing token)
- `404`: Not Found
- `500`: Internal Server Error

### Error Response Format
```python
{
    'message': str  # Human-readable error message
}
```

### Exception Handling
All endpoints wrapped in try-except blocks:
```python
try:
    # Endpoint logic
    ...
except Exception as e:
    return jsonify({'message': f'Failed: {str(e)}'}), 500
```

## Database Integration

### Connection Management
Uses context managers for automatic connection cleanup:
```python
with get_db_connection() as conn:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Database operations
        conn.commit()
```

### Transaction Management
- Explicit commits: `conn.commit()` after writes
- Automatic rollback on exceptions
- No explicit rollback needed (context manager handles it)

### Cursor Type
- `RealDictCursor`: Returns rows as dictionaries
- Enables `row['column_name']` access instead of `row[0]`

## Helper Functions Used

### From `database_helper.py`
- `get_db_connection()`: Get PostgreSQL connection
- `generate_id(prefix)`: Generate unique ID
- `get_student_by_id(cursor, student_id)`: Fetch student with related data
- `get_student_by_email(cursor, email)`: Fetch student by email

### From `validators.py`
- `validate_student_registration(data)`: Validate registration data
- `validate_preferences(preferences)`: Validate preferences
- `validate_email(email)`: Validate email format
- `validate_password(password)`: Validate password strength
- `sanitize_string(value, max_length)`: Sanitize string input
- `validate_limit(limit, max_limit)`: Validate and sanitize limit

### From `recommendation_engine.py`
- `RecommendationEngine`: Main recommendation engine class
- `get_recommendations()`: Generate recommendations

## Performance Considerations

### Database Queries
- **Indexed Columns**: Queries use indexed columns (student_id, course_id)
- **LIMIT Clauses**: All list endpoints use LIMIT
- **Batch Operations**: Recommendation runs saved in single transaction

### Caching
- **Recommendation Engine**: Initialized once, reused for all requests
- **Career Interests**: Cached in recommendation engine after first load

### Response Size
- **Pagination**: Limit parameter on list endpoints
- **Truncation**: Long text fields truncated (e.g., notes max 500 chars)

## Testing

Test suite: `server/tests/test_api.py`

Run tests:
```bash
cd server
pytest tests/test_api.py -v
```

## Configuration

### Environment Variables
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_HOST`: Database host
- `POSTGRES_PORT`: Database port
- `JWT_SECRET_KEY`: Secret key for JWT signing
- `FLASK_ENV`: Environment ('development' or 'production')

### Configuration File
`.env` file in `server/` directory (not committed to git)

## Related Modules

- `recommendation_engine.py`: Core recommendation logic
- `database_helper.py`: Database utilities
- `validators.py`: Input validation
- `models/student.py`: Student data model
- `models/course.py`: Course data model
