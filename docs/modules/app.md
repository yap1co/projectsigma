# Flask API (app.py) Module

## Overview

The Flask API (`app.py`) is the main backend server that handles HTTP requests, authentication, and coordinates between the frontend and the recommendation engine.

**Location**: `server/app.py`

## Architecture

### Framework Stack

- **Flask**: Lightweight web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-JWT-Extended**: JWT-based authentication
- **PostgreSQL**: Database via `psycopg2`
- **Werkzeug**: Password hashing utilities

### Key Components

```python
app = Flask(__name__)
jwt = JWTManager(app)
CORS(app)
recommendation_engine = RecommendationEngine()
```

## API Endpoints

### Health & Information

#### `GET /`
Root endpoint providing API information.

**Response**:
```json
{
  "name": "University Course Recommender API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": { ... }
}
```

#### `GET /api/health`
Health check endpoint.

**Response**:
```json
{
  "status": "OK",
  "timestamp": "2024-01-01T00:00:00",
  "environment": "development"
}
```

### Authentication Endpoints

#### `POST /api/auth/register`
Register a new student account.

**Request Body**:
```json
{
  "email": "student@example.com",
  "password": "securePassword123",
  "firstName": "John",
  "lastName": "Doe",
  "preferences": {
    "region": "London",
    "tuitionBudget": 9250
  }
}
```

**Response** (Success):
```json
{
  "message": "User registered successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "student_id": "STU123456"
}
```

**Response** (Error):
```json
{
  "message": "User already exists"
}
```

**Validation**:
- Email format validation
- Password strength requirements
- Input sanitization
- Duplicate email check

#### `POST /api/auth/login`
Authenticate and get access token.

**Request Body**:
```json
{
  "email": "student@example.com",
  "password": "securePassword123"
}
```

**Response** (Success):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "student_id": "STU123456"
}
```

**Response** (Error):
```json
{
  "message": "Invalid credentials"
}
```

### Student Profile Endpoints

#### `GET /api/student/profile`
Get current student's profile (requires authentication).

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "student_id": "STU123456",
  "display_name": "John Doe",
  "email": "student@example.com",
  "region": "London",
  "tuition_budget": 9250,
  "preferred_exams": ["A-Level"],
  "preferences": { ... }
}
```

#### `PUT /api/student/profile`
Update student profile (requires authentication).

**Request Body**:
```json
{
  "display_name": "John Smith",
  "region": "South East",
  "preferences": {
    "careerInterests": ["Business & Finance"],
    "preferredRegion": "London"
  }
}
```

### Recommendation Endpoints

#### `POST /api/recommendations`
Get personalized course recommendations (requires authentication).

**Request Body**:
```json
{
  "a_level_subjects": ["Mathematics", "Economics", "English Literature"],
  "predicted_grades": {
    "Mathematics": "B",
    "Economics": "A*",
    "English Literature": "A"
  },
  "preferences": {
    "careerInterests": ["Business & Finance"],
    "preferredRegion": "London"
  },
  "limit": 20
}
```

**Response**:
```json
{
  "recommendations": [
    {
      "course": {
        "name": "Business Management",
        "university": { "name": "University of London" },
        ...
      },
      "matchScore": 0.85,
      "meetsRequirements": true,
      "reasons": [
        "Matches your A-level subjects: Economics",
        "Matches your career interests: Business & Finance"
      ]
    },
    ...
  ],
  "total": 50
}
```

**Features**:
- Uses `RecommendationEngine` for matching
- Applies career interest filtering
- Enriches with HESA data
- Returns top matches sorted by score

#### `POST /api/recommendations/feedback`
Submit feedback on a recommendation (requires authentication).

**Request Body**:
```json
{
  "course_id": "COU123456",
  "feedback_type": "positive",
  "search_criteria": { ... }
}
```

**Response**:
```json
{
  "message": "Feedback recorded successfully"
}
```

### Course & University Endpoints

#### `GET /api/courses`
Get course information.

**Query Parameters**:
- `course_id`: Specific course ID
- `university_id`: Filter by university
- `limit`: Maximum results (default: 100)

#### `GET /api/universities`
Get university information.

**Query Parameters**:
- `university_id`: Specific university ID
- `region`: Filter by region
- `limit`: Maximum results (default: 100)

## Security Features

### Authentication

- **JWT Tokens**: 7-day expiration
- **Password Hashing**: Uses `werkzeug.security.generate_password_hash()`
- **Token Validation**: `@jwt_required` decorator on protected routes

### Input Validation

Uses `validators.py` module:
- `validate_student_registration()`: Registration data validation
- `validate_email()`: Email format validation
- `validate_password()`: Password strength validation
- `sanitize_string()`: Input sanitization
- `validate_preferences()`: Preferences validation

### Error Handling

- **400 Bad Request**: Invalid input, validation errors
- **401 Unauthorized**: Missing or invalid JWT token
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side errors

## Database Integration

### Connection Management

Uses `database_helper.py`:
- `get_db_connection()`: Context manager for database connections
- `get_student_by_id()`: Fetch student by ID
- `get_student_by_email()`: Fetch student by email
- `generate_id()`: Generate unique IDs (STU, COU, etc.)

### Transaction Management

Uses PostgreSQL transactions:
```python
with get_db_connection() as conn:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Database operations
        conn.commit()  # or conn.rollback()
```

## Error Handling Pattern

```python
try:
    # Operation
    return jsonify({'result': data}), 200
except Exception as e:
    print(f"Error: {e}")  # Log error
    return jsonify({'message': 'Internal server error'}), 500
```

## CORS Configuration

Enabled for all routes to allow frontend access:
```python
CORS(app)
```

## Environment Variables

Required environment variables (via `.env`):
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_ENV`: Environment (development/production)

## Request Flow Example

1. **Client Request** → Flask receives HTTP request
2. **Authentication** → JWT validation (if protected route)
3. **Input Validation** → Validate and sanitize inputs
4. **Database Query** → Execute database operations
5. **Business Logic** → Call RecommendationEngine or other services
6. **Response** → Return JSON response

## Example: Recommendation Request Flow

```
POST /api/recommendations
  ↓
@jwt_required decorator validates token
  ↓
Extract student_id from token
  ↓
Validate request body (subjects, grades, preferences)
  ↓
Call recommendation_engine.get_recommendations()
  ↓
Engine calculates scores and filters courses
  ↓
Return JSON response with recommendations
```

## Testing

Test suite: `server/tests/test_api.py`

Run tests:
```bash
cd server
pytest tests/test_api.py -v
```

## Related Modules

- `recommendation_engine.py`: Core recommendation logic
- `models/student.py`: Student data model
- `models/course.py`: Course data model
- `database_helper.py`: Database utilities
- `validators.py`: Input validation functions

## Deployment

### Development
```bash
cd server
python app.py
```

### Production
- Use WSGI server (e.g., Gunicorn)
- Set `FLASK_ENV=production`
- Configure proper CORS origins
- Use secure JWT secret key
