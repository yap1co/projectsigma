# Data Models

## Overview

The data models represent the core entities in the system: Students, Courses, and Universities. These models provide an object-oriented interface to the database.

**Location**: `server/models/`

## Student Model

**File**: `server/models/student.py`

### Purpose

Represents a student user in the system with their profile, preferences, and academic information.

### Key Attributes

```python
class Student:
    student_id: str          # Unique identifier (STU...)
    display_name: str        # Full name
    email: str              # Email address (unique)
    password_hash: str      # Hashed password
    region: str             # Preferred region
    tuition_budget: int     # Maximum budget
    preferred_exams: str    # Exam type preference
    created_at: date        # Account creation date
    preferences: dict       # JSON preferences (career interests, etc.)
```

### Methods

#### `from_dict(data: dict) -> Student`
Create a Student instance from a dictionary.

#### `to_dict() -> dict`
Convert Student instance to dictionary.

#### `save(cursor)`
Save student to database (INSERT or UPDATE).

#### `delete(cursor)`
Delete student from database.

### Database Schema

```sql
CREATE TABLE student (
    student_id VARCHAR(50) PRIMARY KEY,
    display_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    region VARCHAR(100),
    tuition_budget INTEGER,
    preferred_exams VARCHAR(50),
    created_at DATE DEFAULT CURRENT_DATE,
    preferences JSONB
);
```

### Usage Example

```python
from models.student import Student

# Create from dictionary
student_data = {
    'student_id': 'STU123456',
    'display_name': 'John Doe',
    'email': 'john@example.com',
    'password_hash': 'hashed_password',
    'region': 'London',
    'preferences': {'careerInterests': ['Business & Finance']}
}
student = Student.from_dict(student_data)

# Save to database
with get_db_connection() as conn:
    with conn.cursor() as cur:
        student.save(cur)
        conn.commit()
```

## Course Model

**File**: `server/models/course.py`

### Purpose

Represents a university course with its details, requirements, and metadata.

### Key Attributes

```python
class Course:
    course_id: str              # Unique identifier (COU...)
    name: str                  # Course name
    university_id: str         # Associated university
    annual_fee: int            # Tuition fee
    ucas_code: str             # UCAS course code
    typical_offer_text: str    # Entry requirements text
    typical_offer_tariff: int  # UCAS tariff points
    course_url: str            # Course webpage URL
    employability_score: int   # Employment rate (0-100)
    pubukprn: str             # HESA institution code
    kiscourseid: str          # HESA course identifier
    kismode: str              # HESA mode (full-time/part-time)
```

### Methods

#### `from_dict(data: dict) -> Course`
Create a Course instance from a dictionary.

#### `to_dict() -> dict`
Convert Course instance to dictionary.

#### `get_entry_requirements(cursor) -> dict`
Fetch entry requirements (subjects and grades).

#### `get_university(cursor) -> dict`
Fetch associated university information.

### Database Schema

```sql
CREATE TABLE course (
    course_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    university_id VARCHAR(50) REFERENCES university(university_id),
    annual_fee INTEGER,
    ucas_code VARCHAR(20),
    typical_offer_text TEXT,
    typical_offer_tariff INTEGER,
    course_url TEXT,
    employability_score INTEGER,
    pubukprn VARCHAR(10),
    kiscourseid VARCHAR(50),
    kismode VARCHAR(2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Related Tables

- `course_requirement`: Entry requirements (subjects and grades)
- `university`: University information
- HESA tables: Employment, salary, job outcomes data

## Base Model

**File**: `server/models/base_model.py`

### Purpose

Provides common functionality shared by all models.

### Features

- ID generation utilities
- Common CRUD operations
- Dictionary conversion methods
- Validation helpers

## Database Relationships

```
university (1) ──< (many) course
course (1) ──< (many) course_requirement
course_requirement (many) >── (1) subject
student (1) ──< (many) recommendation_feedback
```

## Usage in API

Models are used in `app.py` for:

1. **Registration**: Create Student from registration data
2. **Profile Management**: Update Student preferences
3. **Recommendations**: Fetch Course data for recommendations
4. **Feedback**: Link feedback to Course and Student

## Testing

Test suite: `server/tests/test_models.py`

Run tests:
```bash
cd server
pytest tests/test_models.py -v
```
