# Design

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         React/Next.js Frontend (Port 3000)             │ │
│  │  - Dashboard, ProfileSetup, RecommendationResults     │ │
│  │  - TypeScript, Tailwind CSS                           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                         HTTP/REST API
                              │
┌─────────────────────────────────────────────────────────────┐
│                   FLASK SERVER (Port 5000)                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Python Backend API                        │ │
│  │  - recommendation_engine.py (weighted scoring)         │ │
│  │  - scoring_components.py (individual scores)           │ │
│  │  - routes/ (API endpoints)                             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                         SQL Queries
                              │
┌─────────────────────────────────────────────────────────────┐
│               POSTGRESQL DATABASE (Port 5432)                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Application Tables:                                   │ │
│  │  - university, course, user, user_preference           │ │
│  │  - course_requirement, user_feedback                   │ │
│  │                                                        │ │
│  │  HESA Tables:                                          │ │
│  │  - hesa_institution, hesa_kiscourse                   │ │
│  │  - hesa_employment, hesa_entry, hesa_gosalary         │ │
│  │  - hesa_joblist, hesa_leo3                            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Justification:**
- **Three-tier architecture:** Separates presentation (React), logic (Flask), data (PostgreSQL)
- **RESTful API:** Stateless, scalable, follows industry standards
- **Client-side rendering:** Fast, interactive UI with Next.js
- **Relational database:** Appropriate for structured HESA data with complex relationships

### 1.2 Data Flow Diagram

[Create a DFD showing:
- User inputs (grades, interests, preferences)
- Processing (recommendation engine, scoring components)
- Data stores (database tables)
- Outputs (recommended courses, details)]

---

## 2. Database Design

### 2.1 Entity-Relationship Diagram

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   UNIVERSITY │─────────│    COURSE    │─────────│  COURSE_REQ  │
│              │ 1     * │              │ 1     * │              │
│ university_id│         │ course_id    │         │ requirement_ │
│ name         │         │ university_id│         │ course_id    │
│ region       │         │ name         │         │ subject      │
│ rank         │         │ ucas_code    │         │ grade        │
│ employability│         │ annual_fee   │         └──────────────┘
│ website_url  │         │ employability│
└──────────────┘         │ pubukprn *   │
                         │ kiscourseid *│
                         │ kismode *    │
                         └──────────────┘
                               │
                               │ FK: (pubukprn, kiscourseid, kismode)
                               │
         ┌─────────────────────┴────────────────────────┐
         │                                               │
         ▼                                               ▼
┌──────────────────┐                           ┌──────────────────┐
│ HESA_KISCOURSE   │                           │ HESA_EMPLOYMENT  │
│                  │                           │                  │
│ pubukprn (PK)    │                           │ pubukprn (PK)    │
│ kiscourseid (PK) │                           │ kiscourseid (PK) │
│ kismode (PK)     │                           │ kismode (PK)     │
│ title            │                           │ work             │
│ hecos            │                           │ study            │
│ numstage         │                           │ unemp            │
└──────────────────┘                           │ workstudy        │
                                               └──────────────────┘

┌──────────────────┐
│ HESA_INSTITUTION │
│                  │
│ pubukprn (PK)    │
│ first_trading_   │
│ legal_name       │
│ country          │
│ provurl          │
└──────────────────┘
```

### 2.2 Table Schemas

#### Application Tables

**university**
```sql
CREATE TABLE university (
    university_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    region VARCHAR(100),
    rank_overall INTEGER,
    employability_score INTEGER,
    website_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**course**
```sql
CREATE TABLE course (
    course_id VARCHAR(255) PRIMARY KEY,
    university_id VARCHAR(255) REFERENCES university(university_id),
    name TEXT NOT NULL,
    ucas_code VARCHAR(10) UNIQUE,
    annual_fee INTEGER,
    employability_score INTEGER,
    course_url TEXT,
    pubukprn VARCHAR(8),    -- HESA link
    kiscourseid VARCHAR(20), -- HESA link
    kismode VARCHAR(2),      -- HESA link
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**user**
```sql
CREATE TABLE "user" (
    user_id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**user_preference**
```sql
CREATE TABLE user_preference (
    preference_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES "user"(user_id),
    preferred_regions TEXT[],
    career_interests TEXT[],
    subject_1 VARCHAR(100),
    subject_1_grade VARCHAR(2),
    subject_2 VARCHAR(100),
    subject_2_grade VARCHAR(2),
    subject_3 VARCHAR(100),
    subject_3_grade VARCHAR(2),
    ucas_points INTEGER,
    max_fee INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### HESA Tables (7 tables - reduced scope)

**hesa_institution**
```sql
CREATE TABLE hesa_institution (
    pubukprn VARCHAR(8) PRIMARY KEY,
    first_trading_name VARCHAR(255),
    legal_name VARCHAR(255),
    country VARCHAR(10),
    provurl TEXT
);
```

**hesa_kiscourse**
```sql
CREATE TABLE hesa_kiscourse (
    pubukprn VARCHAR(8),
    kiscourseid VARCHAR(20),
    kismode VARCHAR(2),
    title TEXT,
    ucasprogid VARCHAR(10),
    hecos VARCHAR(100),
    numstage INTEGER,
    crseurl TEXT,
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);
```

**hesa_employment**
```sql
CREATE TABLE hesa_employment (
    pubukprn VARCHAR(8),
    kiscourseid VARCHAR(20),
    kismode VARCHAR(2),
    empagg VARCHAR(2),
    work INTEGER,
    study INTEGER,
    unemp INTEGER,
    workstudy INTEGER,
    emppop INTEGER,
    empresponse INTEGER,
    empresp_rate INTEGER,
    empsample INTEGER,
    PRIMARY KEY (pubukprn, kiscourseid, kismode, empagg)
);
```

[Continue with hesa_entry, hesa_gosalary, hesa_joblist, hesa_leo3...]

### 2.3 Data Dictionary

[For each important field, document:
- Field name
- Data type
- Description
- Validation rules
- Source (if HESA data)]

---

## 3. Algorithm Design

### 3.1 Recommendation Algorithm (Weighted Scoring)

**Purpose:** Calculate a personalized score for each course based on user preferences and course attributes.

**Inputs:**
- User profile: predicted grades, career interests, location preferences
- Course data: employability, fees, entry requirements, location
- HESA data: employment outcomes, salaries, graduate destinations

**Algorithm Pseudocode:**

```
FUNCTION calculate_recommendation_score(user, course):
    // Initialize weights (sum to 1.0)
    weights = {
        'location': 0.15,
        'employability': 0.25,
        'career_alignment': 0.20,
        'entry_requirements': 0.20,
        'fees': 0.10,
        'graduate_salary': 0.10
    }
    
    // Calculate individual component scores (0-100)
    location_score = score_location(user.preferred_regions, course.region)
    employability_score = course.employability_score
    career_score = score_career_alignment(user.career_interests, course.job_types)
    entry_score = score_entry_requirements(user.grades, course.requirements)
    fee_score = score_fees(user.max_fee, course.annual_fee)
    salary_score = normalize_salary(course.leo3_median)
    
    // Calculate weighted sum
    total_score = (
        weights['location'] * location_score +
        weights['employability'] * employability_score +
        weights['career_alignment'] * career_score +
        weights['entry_requirements'] * entry_score +
        weights['fees'] * fee_score +
        weights['graduate_salary'] * salary_score
    )
    
    RETURN total_score (0-100)
END FUNCTION
```

**Justification:**
- Weighted scoring allows balancing multiple criteria
- Transparent and explainable (vs. black-box ML)
- Weights can be tuned based on user feedback
- Efficient: O(n) complexity for n courses

### 3.2 Scoring Component Algorithms

#### 3.2.1 Location Scoring

```
FUNCTION score_location(preferred_regions, course_region):
    IF course_region IN preferred_regions:
        RETURN 100
    ELSE:
        RETURN 50  // Neutral score for non-preferred regions
    END IF
END FUNCTION
```

#### 3.2.2 Career Alignment Scoring

```
FUNCTION score_career_alignment(user_interests, course_job_types):
    // user_interests: ['Software Developer', 'Data Analyst']
    // course_job_types: [{'job': 'Programmer', 'percentage': 35}, ...]
    
    total_alignment = 0
    
    FOR EACH interest IN user_interests:
        FOR EACH job_type IN course_job_types:
            IF interest SIMILAR TO job_type.job:  // Fuzzy matching
                total_alignment += job_type.percentage
            END IF
        END FOR
    END FOR
    
    // Normalize to 0-100
    RETURN MIN(total_alignment, 100)
END FUNCTION
```

#### 3.2.3 Entry Requirements Scoring

```
FUNCTION score_entry_requirements(user_grades, course_requirements):
    user_points = calculate_ucas_points(user_grades)
    course_points = course_requirements.typical_ucas_points
    
    IF user_points >= course_points:
        // Exceed requirements: perfect score
        RETURN 100
    ELSE IF user_points >= course_points * 0.9:
        // Close to requirements: high score
        RETURN 80
    ELSE IF user_points >= course_points * 0.8:
        // Slightly below: medium score
        RETURN 60
    ELSE:
        // Significantly below: low score
        RETURN 30
    END IF
END FUNCTION
```

### 3.3 Data Mapping Algorithm

**Purpose:** Map HESA raw data (institution, kiscourse) to application tables (university, course)

**Process:**
1. Read `hesa_institution` table
2. For each institution:
   - Generate university_id
   - Extract name, region, website URL
   - Insert into `university` table
3. Read `hesa_kiscourse` table (5000 courses)
4. For each course:
   - Find matching university (via pubukprn)
   - Lookup employment data from `hesa_employment`
   - Calculate employability score
   - Extract entry requirements from `hesa_entry`
   - Insert into `course` and `course_requirement` tables

[See implementation in `server/database/map_hesa_to_main_tables.py`]

---

## 4. User Interface Design

### 4.1 Wireframes

#### 4.1.1 Landing Page

```
┌─────────────────────────────────────────────────────────┐
│  [Logo] Project Sigma       [Login] [Sign Up]          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│           Find Your Perfect University Course            │
│                                                         │
│     [Personalized recommendations based on your         │
│      grades, interests, and career goals]               │
│                                                         │
│              [Get Started →]                            │
│                                                         │
│  Features:                                              │
│  ✓ 5000+ UK university courses                         │
│  ✓ Real employment outcomes                            │
│  ✓ Graduate salary data                                │
│  ✓ Personalized matching                               │
└─────────────────────────────────────────────────────────┘
```

#### 4.1.2 Profile Setup Page

```
┌─────────────────────────────────────────────────────────┐
│  [Back] Profile Setup                           [Save]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Step 1: Your Predicted A-Level Grades                 │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Subject 1: [Mathematics    ▼] Grade: [A*▼]       │ │
│  │ Subject 2: [Computer Sci   ▼] Grade: [A ▼]       │ │
│  │ Subject 3: [Physics        ▼] Grade: [A ▼]       │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  Step 2: Career Interests (select up to 3)             │
│  ┌───────────────────────────────────────────────────┐ │
│  │ [x] Software Developer                            │ │
│  │ [ ] Data Analyst                                  │ │
│  │ [ ] Cybersecurity Specialist                      │ │
│  │ [x] AI/Machine Learning Engineer                  │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  Step 3: Location Preferences                          │
│  ┌───────────────────────────────────────────────────┐ │
│  │ [x] England  [x] Scotland  [ ] Wales  [ ] NI      │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  Step 4: Financial Considerations                      │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Maximum annual fee: £[9250] ───────────────────   │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│                    [Get Recommendations →]             │
└─────────────────────────────────────────────────────────┘
```

#### 4.1.3 Recommendations Dashboard

```
┌───────────────────────────────────────────────────────────┐
│ [Home] Your Recommendations                  [Profile] [⚙] │
├───────────────────────────────────────────────────────────┤
│ Filters: [Location▼] [Fees▼] [Entry▼]     [Sort: Match▼] │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 1. BSc Computer Science - University of Example    │  │
│  │    Match: 92%  ████████████░                       │  │
│  │    📍 England  💰 £9,250/year  📊 Employability: 95% │  │
│  │    Entry: AAA   Median Salary: £35,000             │  │
│  │    [View Details] [Compare] [Save]                 │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 2. BSc Software Engineering - Example Tech Uni     │  │
│  │    Match: 89%  ███████████░░                       │  │
│  │    📍 Scotland  💰 £9,250/year  📊 Employability: 92% │  │
│  │    Entry: AAB   Median Salary: £33,500             │  │
│  │    [View Details] [Compare] [Save]                 │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  [Load More Results...]                                   │
└───────────────────────────────────────────────────────────┘
```

### 4.2 UI Component Breakdown

[List React components and their responsibilities:
- Header.tsx: Navigation, user menu
- Dashboard.tsx: Main recommendations view
- ProfileSetup.tsx: Multi-step form
- CourseDetailsModal.tsx: Detailed course information
- ProjectCard.tsx: Individual course card
- RecommendationResults.tsx: Results list]

### 4.3 User Journey Map

1. User arrives → Landing page
2. Click "Get Started" → Profile setup
3. Enter grades, interests, preferences → Submit
4. Algorithm runs → Dashboard shows recommendations
5. Browse results → Click course card
6. View detailed outcomes → Modal with employment data
7. Save preferred courses → User profile updated

---

## 5. Test Plan

### 5.1 Unit Tests

| Test ID | Component | Test Description | Expected Result |
|---------|-----------|------------------|-----------------|
| UT1 | score_location() | Test scoring with preferred region | Return 100 |
| UT2 | score_location() | Test scoring with non-preferred region | Return 50 |
| UT3 | calculate_ucas_points() | Test A*AA grades | Return 144 |
| UT4 | score_entry_requirements() | User points >= course points | Return 100 |
| UT5 | score_career_alignment() | Exact career match | Return ≥ 80 |
| UT6 | normalize_salary() | £35,000 median salary | Return normalized 0-100 |
| UT7 | generate_id() | Generate unique ID | Return 'UNIV_' prefix ID |

### 5.2 Integration Tests

| Test ID | Integration | Test Description | Expected Result |
|---------|-------------|------------------|-----------------|
| IT1 | Database → Backend | Query courses by UCAS code | Return correct course object |
| IT2 | Backend → Frontend | GET /api/recommendations | Return JSON array of courses |
| IT3 | HESA Mapping | Map institution to university | University row created in DB |
| IT4 | Scoring → Results | Generate scores for 100 courses | All courses have valid scores |
| IT5 | User Input → Profile | Save user preferences | Preferences stored in DB |

### 5.3 System Tests

| Test ID | Feature | Test Description | Expected Result |
|---------|---------|------------------|-----------------|
| ST1 | End-to-end flow | Complete user journey (landing → profile → results) | Success |
| ST2 | Performance | Load 5000 courses and generate recommendations | < 3 seconds |
| ST3 | Filtering | Apply region filter (England only) | Show only England courses |
| ST4 | Sorting | Sort by match score descending | Highest match first |
| ST5 | Course Details | Click course card → open modal | Modal displays HESA data |

### 5.4 User Acceptance Tests

| Test ID | User Story | Test Description | Acceptance Criteria |
|---------|-----------|------------------|---------------------|
| UAT1 | As a student, I want to see courses matching my grades | Enter A*AA, view recommendations | See only courses with AAA or lower entry |
| UAT2 | As a student, I want to see employment outcomes | View course details | Display employment %, salary, job types |
| UAT3 | As a student, I want to save my preferences | Set up profile, log out, log back in | Preferences persisted |
| UAT4 | As a student, I want to filter by location | Select "Scotland" filter | Show only Scottish universities |

### 5.5 Test Data

[Specify test data sets:
- Sample user profiles (various grade combinations)
- Mock HESA data for controlled testing
- Edge cases (missing data, extreme values)]

---

## 6. Security and Error Handling

### 6.1 Security Measures

- Password hashing (bcrypt)
- SQL injection prevention (parameterized queries)
- CORS configuration
- Input validation on all API endpoints

### 6.2 Error Handling Strategy

- Try-catch blocks in Python backend
- Database connection error handling
- Frontend error boundaries (React)
- User-friendly error messages

---

## 7. Summary

[Conclude Design section with:
- Architecture decisions justified
- Database schema complete and normalized
- Algorithms designed with pseudocode
- UI wireframes address user needs
- Comprehensive test plan covering all components]

**Next Steps:** Proceed to Development phase with designs as blueprint.
