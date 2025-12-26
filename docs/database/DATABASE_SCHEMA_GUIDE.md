# University Recommender Database Schema Guide

This guide documents all tables in the `university_recommender` database. The database uses PostgreSQL and contains tables for student management, course recommendations, and HESA (Higher Education Statistics Agency) data integration.

## Database Overview

**Database Name**: `university_recommender`  
**PostgreSQL Version**: 12+  
**Schema**: `public` (default schema)

The database is organized into several logical groups:

1. **Core Application Tables**: Student profiles, courses, universities, recommendations
2. **HESA Data Tables**: Discover Uni dataset integration (kiscourse, employment, salaries, etc.)
3. **Lookup Tables**: Reference data (subjects, locations, accreditation types)
4. **Feedback & Learning Tables**: Student feedback and recommendation settings
5. **Career Interest Tables**: Career interest matching and keyword management

---

## Table Categories

### 1. Core Application Tables (Initial Schema)

These tables store the core application data for the recommendation system.

#### `student`
**Purpose**: Stores student user accounts and profiles

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `student_id` | VARCHAR(50) | PRIMARY KEY | Unique student identifier |
| `display_name` | VARCHAR(255) | NOT NULL | Student's display name |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Student email address |
| `password_hash` | VARCHAR(255) | NOT NULL | Hashed password for authentication |
| `created_at` | DATE | DEFAULT CURRENT_DATE | Account creation date |
| `region` | VARCHAR(100) | | Preferred region (e.g., "London", "South East") |
| `tuition_budget` | INTEGER | | Maximum tuition budget in £ |
| `preferred_exams` | TEXT[] | | Array of preferred exam types (e.g., ["A-Level"]) |

**Indexes**: 
- GIN index on `preferred_exams` for array queries

**Relationships**:
- One-to-Many with `student_grade`
- One-to-Many with `recommendation_run`

---

#### `subject`
**Purpose**: Reference table for A-level subjects

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `subject_id` | VARCHAR(50) | PRIMARY KEY | Unique subject identifier |
| `subject_name` | VARCHAR(255) | UNIQUE, NOT NULL | Subject name (e.g., "Mathematics", "Economics") |

**Relationships**:
- One-to-Many with `student_grade`
- One-to-Many with `course_requirement`

---

#### `student_grade`
**Purpose**: Stores predicted A-level grades for each student

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `student_id` | VARCHAR(50) | PRIMARY KEY (part 1), FK → student | Student identifier |
| `subject_id` | VARCHAR(50) | PRIMARY KEY (part 2), FK → subject | Subject identifier |
| `predicted_grade` | VARCHAR(5) | NOT NULL, CHECK IN ('A*', 'A', 'B', 'C', 'D', 'E', 'U') | Predicted grade |

**Composite Primary Key**: (`student_id`, `subject_id`)

**Indexes**:
- `ix_grade_student` on `student_id`
- `ix_grade_subject` on `subject_id`

---

#### `university`
**Purpose**: Stores university/institution information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `university_id` | VARCHAR(50) | PRIMARY KEY | Unique university identifier |
| `name` | VARCHAR(255) | NOT NULL | University name |
| `region` | VARCHAR(100) | | Geographic region |
| `rank_overall` | INTEGER | | Overall university ranking |
| `employability_score` | INTEGER | CHECK (0-100) | Employment rate score (0-100) |
| `website_url` | VARCHAR(500) | | University website URL |

**Indexes**:
- `ix_university_region_rank` on (`region`, `rank_overall`)
- `ix_university_name_ci` on `lower(name)` (case-insensitive search)

**Relationships**:
- One-to-Many with `course`

---

#### `course`
**Purpose**: Stores course information (main course table for recommendations)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `course_id` | VARCHAR(50) | PRIMARY KEY | Unique course identifier |
| `university_id` | VARCHAR(50) | FK → university | University offering the course |
| `ucas_code` | VARCHAR(20) | UNIQUE | UCAS course code |
| `name` | VARCHAR(255) | NOT NULL | Course name |
| `annual_fee` | INTEGER | CHECK (>= 0) | Annual tuition fee in £ |
| `subject_rank` | INTEGER | | Subject-specific ranking |
| `employability_score` | INTEGER | CHECK (0-100) | Employment rate score (0-100) |
| `course_url` | VARCHAR(500) | | Course information URL |
| `typical_offer_text` | VARCHAR(255) | | Typical offer description |
| `typical_offer_tariff` | INTEGER | | Typical UCAS tariff points |
| `pubukprn` | VARCHAR(10) | | HESA Published UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | | HESA KIS Course ID (links to kiscourse table) |
| `kismode` | VARCHAR(2) | | HESA KIS Mode (01=Full-time, 02=Part-time) |

**Indexes**:
- `ix_course_university` on `university_id`
- `ix_course_fee` on `annual_fee`
- `ix_course_ucas` on `ucas_code`
- `ix_course_name_ci` on `lower(name)`
- `ix_course_fee_cap` on `annual_fee` WHERE `annual_fee <= 9250` (partial index)
- `idx_course_hesa_link` on (`pubukprn`, `kiscourseid`, `kismode`)

**Relationships**:
- Many-to-One with `university`
- One-to-Many with `course_requirement`
- One-to-Many with `course_required_exam`
- One-to-Many with `recommendation_feedback`

---

#### `course_requirement`
**Purpose**: Stores subject and grade requirements for courses

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `req_id` | VARCHAR(50) | PRIMARY KEY | Unique requirement identifier |
| `course_id` | VARCHAR(50) | FK → course | Course identifier |
| `subject_id` | VARCHAR(50) | FK → subject | Required subject |
| `grade_req` | VARCHAR(5) | NOT NULL, CHECK IN ('A*', 'A', 'B', 'C', 'D', 'E') | Required grade |

**Indexes**:
- `ix_req_course` on `course_id`
- `ix_req_subject` on `subject_id`

---

#### `entrance_exam`
**Purpose**: Reference table for entrance exam types

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `exam_id` | VARCHAR(50) | PRIMARY KEY | Unique exam identifier |
| `name` | VARCHAR(255) | UNIQUE, NOT NULL | Exam name (e.g., "A-Level", "BTEC") |

---

#### `course_required_exam`
**Purpose**: Junction table linking courses to required entrance exams

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `course_id` | VARCHAR(50) | PRIMARY KEY (part 1), FK → course | Course identifier |
| `exam_id` | VARCHAR(50) | PRIMARY KEY (part 2), FK → entrance_exam | Exam identifier |

**Composite Primary Key**: (`course_id`, `exam_id`)

---

#### `recommendation_run`
**Purpose**: Tracks each recommendation generation session

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `run_id` | VARCHAR(50) | PRIMARY KEY | Unique run identifier |
| `student_id` | VARCHAR(50) | FK → student | Student who requested recommendations |
| `run_at` | DATE | DEFAULT CURRENT_DATE | Date of recommendation run |
| `weights` | JSONB | | Snapshot of scoring weights used |
| `prefs_snapshot` | JSONB | | Snapshot of student preferences at time of run |

**Indexes**:
- `ix_run_student_created` on (`student_id`, `run_at`)

**Relationships**:
- Many-to-One with `student`
- One-to-Many with `recommendation_result`

---

#### `recommendation_result`
**Purpose**: Stores the results (top 50 courses) from each recommendation run

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `result_id` | VARCHAR(50) | PRIMARY KEY | Unique result identifier |
| `run_id` | VARCHAR(50) | FK → recommendation_run | Recommendation run identifier |
| `items` | JSONB | NOT NULL, CHECK (jsonb_typeof = 'array') | Array of recommended courses with scores |

**Indexes**:
- `ix_result_run` on `run_id`
- `ix_rr_items_gin` USING GIN on `items` (for JSONB queries)

**Relationships**:
- Many-to-One with `recommendation_run`

---

### 2. Feedback & Learning Tables

#### `recommendation_feedback`
**Purpose**: Stores student feedback (thumbs up/down) on recommendations for learning

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `feedback_id` | VARCHAR(50) | PRIMARY KEY | Unique feedback identifier |
| `student_id` | VARCHAR(50) | FK → student | Student who provided feedback |
| `course_id` | VARCHAR(50) | FK → course | Course being rated |
| `feedback_type` | VARCHAR(10) | NOT NULL, CHECK IN ('positive', 'negative') | Type of feedback |
| `feedback_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp of feedback |
| `search_criteria` | JSONB | | Snapshot of search criteria for learning |
| `match_score` | DECIMAL(5,4) | | Match score at time of feedback |
| `notes` | TEXT | | Optional notes from student |

**Indexes**:
- `ix_feedback_student_course` on (`student_id`, `course_id`, `feedback_at DESC`)
- `ix_feedback_type` on (`feedback_type`, `feedback_at DESC`)
- `ix_feedback_course` on (`course_id`, `feedback_type`, `feedback_at DESC`)
- `ix_feedback_criteria_gin` USING GIN on `search_criteria`

**Unique Constraint**: (`student_id`, `course_id`, `feedback_at`) - prevents duplicate feedback

---

#### `recommendation_settings`
**Purpose**: Stores tunable parameters for recommendation engine behavior

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `setting_id` | VARCHAR(50) | PRIMARY KEY | Unique setting identifier |
| `setting_key` | VARCHAR(100) | UNIQUE, NOT NULL | Setting key (e.g., "feedback_weight") |
| `setting_value` | JSONB | NOT NULL | Setting value |
| `description` | TEXT | | Description of the setting |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |
| `updated_by` | VARCHAR(50) | FK → student | Who updated the setting |

**Indexes**:
- `ix_settings_key` on `setting_key`

**Default Settings**:
- `feedback_weight`: 0.15 (Weight of feedback in final score)
- `feedback_decay_days`: 90 (Days before feedback relevance decays)
- `min_feedback_count`: 3 (Minimum feedback count to apply boost)
- `positive_feedback_boost`: 0.2 (Score boost for positive feedback)
- `negative_feedback_penalty`: -0.3 (Score penalty for negative feedback)

---

### 3. Career Interest Tables

#### `career_interest`
**Purpose**: Defines career interest categories (e.g., "Business & Finance", "Medicine & Healthcare")

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `interest_id` | VARCHAR(50) | PRIMARY KEY | Unique interest identifier |
| `interest_name` | VARCHAR(255) | UNIQUE, NOT NULL | Interest name (internal key) |
| `display_name` | VARCHAR(255) | NOT NULL | Display name for UI |
| `description` | TEXT | | Description of the career interest |
| `is_active` | BOOLEAN | DEFAULT TRUE | Whether interest is active |
| `display_order` | INTEGER | DEFAULT 0 | Display order for UI |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Update timestamp |

**Indexes**:
- Partial index on `is_active` WHERE `is_active = TRUE`

**Default Interests** (10 categories):
1. Business & Finance
2. Medicine & Healthcare
3. Engineering & Technology
4. Law
5. Education
6. Arts & Humanities
7. Sciences
8. Social Sciences
9. Creative Arts
10. Sports & Fitness

---

#### `career_interest_keyword`
**Purpose**: Stores keywords used to match courses to career interests

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `keyword_id` | VARCHAR(50) | PRIMARY KEY | Unique keyword identifier |
| `interest_id` | VARCHAR(50) | FK → career_interest | Career interest identifier |
| `keyword` | VARCHAR(100) | NOT NULL | Keyword to match (e.g., "business", "finance") |
| `match_type` | VARCHAR(20) | DEFAULT 'contains', CHECK IN ('contains', 'exact', 'starts_with', 'ends_with') | How to match the keyword |
| `priority` | INTEGER | DEFAULT 0 | Higher priority keywords checked first |
| `is_active` | BOOLEAN | DEFAULT TRUE | Whether keyword is active |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Indexes**:
- `idx_career_interest_keyword_interest` on `interest_id`
- `idx_career_interest_keyword_keyword` on `keyword`
- Partial index on (`interest_id`, `is_active`) WHERE `is_active = TRUE`

**Unique Constraint**: (`interest_id`, `keyword`)

**Example Keywords**:
- Business & Finance: "business", "finance", "accounting", "economics", "management", "banking"
- Medicine & Healthcare: "medicine", "health", "nursing", "pharmacy", "dentistry"
- Engineering & Technology: "engineering", "technology", "computer", "software", "electrical"

---

#### `career_interest_conflict`
**Purpose**: Defines conflicting career interests (e.g., Business conflicts with Sciences)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `conflict_id` | VARCHAR(50) | PRIMARY KEY | Unique conflict identifier |
| `interest_id` | VARCHAR(50) | FK → career_interest | First career interest |
| `conflicting_interest_id` | VARCHAR(50) | FK → career_interest | Conflicting career interest |
| `conflict_strength` | VARCHAR(20) | DEFAULT 'strong', CHECK IN ('weak', 'medium', 'strong') | Strength of conflict |
| `description` | TEXT | | Description of why they conflict |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Indexes**:
- `idx_career_interest_conflict_interest` on `interest_id`
- `idx_career_interest_conflict_conflicting` on `conflicting_interest_id`

**Unique Constraint**: (`interest_id`, `conflicting_interest_id`)  
**Check Constraint**: `interest_id != conflicting_interest_id` (can't conflict with itself)

**Example Conflicts**:
- Business & Finance ↔ Engineering & Technology (strong)
- Business & Finance ↔ Sciences (strong)
- Business & Finance ↔ Medicine & Healthcare (strong)

---

### 4. HESA Data Tables (Discover Uni Dataset)

These tables store data imported from the HESA Discover Uni dataset. They use composite primary keys based on (`pubukprn`, `kiscourseid`, `kismode`) to uniquely identify courses.

---

#### Lookup Tables

##### `accreditation_table`
**Purpose**: Reference table for accreditation types

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `acctype` | VARCHAR(10) | PRIMARY KEY | Accreditation type code |
| `accurl` | VARCHAR(500) | | Accreditation URL |
| `acctext` | TEXT | | Accreditation text (English) |
| `acctextw` | TEXT | | Accreditation text (Welsh) |

---

##### `kis_aim`
**Purpose**: Reference table for qualification types (e.g., BA, BSc, MEng)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `kisaimcode` | VARCHAR(10) | PRIMARY KEY | KIS Aim code (e.g., "000"=BA, "021"=BSc) |
| `kisaimlabel` | VARCHAR(100) | NOT NULL | Qualification label (e.g., "BA", "BSc") |

---

##### `location`
**Purpose**: Reference table for teaching locations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `ukprn` | VARCHAR(10) | PRIMARY KEY (part 1) | UK Provider Reference Number |
| `locid` | VARCHAR(20) | PRIMARY KEY (part 2) | Location identifier |
| `locname` | VARCHAR(255) | | Location name |
| `locnamew` | VARCHAR(255) | | Location name (Welsh) |
| `latitude` | NUMERIC(10,8) | | Latitude coordinate |
| `longitude` | NUMERIC(11,8) | | Longitude coordinate |
| `accomurl` | VARCHAR(500) | | Accommodation URL |
| `accomurlw` | VARCHAR(500) | | Accommodation URL (Welsh) |
| `locukprn` | VARCHAR(10) | | Location UKPRN |
| `loccountry` | VARCHAR(2) | | Country code |
| `suurl` | VARCHAR(500) | | Student Union URL |
| `suurlw` | VARCHAR(500) | | Student Union URL (Welsh) |

**Composite Primary Key**: (`ukprn`, `locid`)

---

#### Core HESA Entities

##### `institution`
**Purpose**: Describes the reporting institution (university/HE provider)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `pubukprn` | VARCHAR(10) | PRIMARY KEY | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `legal_name` | VARCHAR(500) | | Legal name of institution |
| `first_trading_name` | VARCHAR(500) | | Primary trading name |
| `other_names` | TEXT | | Other names for the institution |
| `provaddress` | TEXT | | Provider address |
| `provtel` | VARCHAR(50) | | Provider telephone |
| `provurl` | VARCHAR(500) | | Provider website URL |
| `country` | VARCHAR(2) | | Country code |
| `pubukprncountry` | VARCHAR(2) | | Published UKPRN country |
| `qaa_report_type` | VARCHAR(100) | | QAA report type |
| `qaa_url` | VARCHAR(500) | | QAA report URL |
| `suurl` | VARCHAR(500) | | Student Union URL |
| `suurlw` | VARCHAR(500) | | Student Union URL (Welsh) |

**Indexes**:
- `idx_institution_ukprn` on `ukprn`

**Relationships**:
- One-to-Many with `kiscourse`
- One-to-Many with `tefoutcome`

---

##### `kiscourse`
**Purpose**: Main HESA course entity (records details of KIS courses)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `pubukprn` | VARCHAR(10) | PRIMARY KEY (part 1), FK → institution | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | PRIMARY KEY (part 2) | KIS Course identifier |
| `kismode` | VARCHAR(2) | PRIMARY KEY (part 3) | KIS Mode (01=Full-time, 02=Part-time) |
| `title` | VARCHAR(500) | | Course title |
| `titlew` | VARCHAR(500) | | Course title (Welsh) |
| `assurl` | VARCHAR(500) | | Assessment URL |
| `assurlw` | VARCHAR(500) | | Assessment URL (Welsh) |
| `crsecsturl` | VARCHAR(500) | | Course student URL |
| `crsecsturlw` | VARCHAR(500) | | Course student URL (Welsh) |
| `crseurl` | VARCHAR(500) | | Course URL |
| `crseurlw` | VARCHAR(500) | | Course URL (Welsh) |
| `distance` | VARCHAR(1) | | Distance learning indicator (Y/N) |
| `employurl` | VARCHAR(500) | | Employment URL |
| `employurlw` | VARCHAR(500) | | Employment URL (Welsh) |
| `foundation` | VARCHAR(1) | | Foundation year indicator (Y/N) |
| `honours` | VARCHAR(1) | | Honours indicator (Y/N) |
| `hecos` | VARCHAR(10) | | HECOS subject code (first) |
| `hecos2` | VARCHAR(10) | | HECOS subject code (second) |
| `hecos3` | VARCHAR(10) | | HECOS subject code (third) |
| `hecos4` | VARCHAR(10) | | HECOS subject code (fourth) |
| `hecos5` | VARCHAR(10) | | HECOS subject code (fifth) |
| `locchnge` | VARCHAR(1) | | Location change indicator |
| `lturl` | VARCHAR(500) | | Learning and teaching URL |
| `lturlw` | VARCHAR(500) | | Learning and teaching URL (Welsh) |
| `nhs` | VARCHAR(1) | | NHS indicator (Y/N) |
| `numstage` | INTEGER | | Number of stages |
| `sandwich` | VARCHAR(1) | | Sandwich course indicator (Y/N) |
| `supporturl` | VARCHAR(500) | | Support URL |
| `supporturlw` | VARCHAR(500) | | Support URL (Welsh) |
| `ucasprogid` | VARCHAR(50) | | UCAS Programme ID |
| `ukprnapply` | VARCHAR(10) | | UKPRN for application |
| `yearabroad` | VARCHAR(1) | | Year abroad indicator (Y/N) |
| `kisaimcode` | VARCHAR(10) | FK → kis_aim | KIS Aim code (qualification type) |
| `kislevel` | VARCHAR(2) | | KIS Level (e.g., 03=Undergraduate) |

**Composite Primary Key**: (`pubukprn`, `kiscourseid`, `kismode`)

**Indexes**:
- `idx_kiscourse_ukprn` on `ukprn`
- `idx_kiscourse_pubukprn` on `pubukprn`
- `idx_kiscourse_kisaimcode` on `kisaimcode`

**Relationships**:
- Many-to-One with `institution`
- Many-to-One with `kis_aim`
- One-to-Many with multiple HESA data tables (accreditation, courselocation, entry, employment, etc.)

---

#### Course-Related HESA Tables

##### `accreditation`
**Purpose**: Links courses to accreditation types

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `pubukprn` | VARCHAR(10) | PRIMARY KEY (part 1), FK → kiscourse | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | PRIMARY KEY (part 2), FK → kiscourse | KIS Course identifier |
| `kismode` | VARCHAR(2) | PRIMARY KEY (part 3), FK → kiscourse | KIS Mode |
| `acctype` | VARCHAR(10) | PRIMARY KEY (part 4), FK → accreditation_table | Accreditation type code |
| `accdepend` | VARCHAR(1) | | Accreditation dependency indicator |
| `accdependurl` | VARCHAR(500) | | Accreditation dependency URL |
| `accdependurlw` | VARCHAR(500) | | Accreditation dependency URL (Welsh) |

**Composite Primary Key**: (`pubukprn`, `kiscourseid`, `kismode`, `acctype`)

**Indexes**:
- `idx_accreditation_course` on (`pubukprn`, `kiscourseid`, `kismode`)
- `idx_accreditation_acctype` on `acctype`

---

##### `courselocation`
**Purpose**: Links courses to teaching locations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `courselocation_id` | SERIAL | PRIMARY KEY | Surrogate primary key |
| `pubukprn` | VARCHAR(10) | NOT NULL, FK → kiscourse | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | NOT NULL, FK → kiscourse | KIS Course identifier |
| `kismode` | VARCHAR(2) | NOT NULL, FK → kiscourse | KIS Mode |
| `locid` | VARCHAR(20) | FK → location | Location identifier (may be NULL) |

**Indexes**:
- `idx_courselocation_course` on (`pubukprn`, `kiscourseid`, `kismode`)
- `idx_courselocation_loc` on (`ukprn`, `locid`)

**Unique Constraint**: (`pubukprn`, `kiscourseid`, `kismode`, `locid`)

---

##### `ucascourseid`
**Purpose**: Stores UCAS course identifiers for each course location

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `ucascourseid_id` | SERIAL | PRIMARY KEY | Surrogate primary key |
| `pubukprn` | VARCHAR(10) | NOT NULL | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | NOT NULL | KIS Course identifier |
| `kismode` | VARCHAR(2) | NOT NULL | KIS Mode |
| `locid` | VARCHAR(20) | | Location identifier (may be NULL) |
| `ucascourseid` | VARCHAR(50) | NOT NULL | UCAS course identifier |

**Indexes**:
- `idx_ucascourseid_courselocation` on (`pubukprn`, `kiscourseid`, `kismode`, `locid`)
- `idx_ucascourseid_ucas` on `ucascourseid`

**Unique Constraint**: (`pubukprn`, `kiscourseid`, `kismode`, `locid`, `ucascourseid`)

**Foreign Key**: References `courselocation` via composite key

---

##### `sbj`
**Purpose**: Links courses to CAH (Common Aggregation Hierarchy) subject codes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `pubukprn` | VARCHAR(10) | PRIMARY KEY (part 1), FK → kiscourse | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | PRIMARY KEY (part 2), FK → kiscourse | KIS Course identifier |
| `kismode` | VARCHAR(2) | PRIMARY KEY (part 3), FK → kiscourse | KIS Mode |
| `sbj` | VARCHAR(50) | PRIMARY KEY (part 4) | CAH subject code |

**Composite Primary Key**: (`pubukprn`, `kiscourseid`, `kismode`, `sbj`)

**Indexes**:
- `idx_sbj_course` on (`pubukprn`, `kiscourseid`, `kismode`)
- `idx_sbj_code` on `sbj`

---

#### Student Outcomes Tables

##### `entry`
**Purpose**: Entry qualifications statistics (A-Levels, BTEC, etc.)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `pubukprn` | VARCHAR(10) | PRIMARY KEY (part 1), FK → kiscourse | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | PRIMARY KEY (part 2), FK → kiscourse | KIS Course identifier |
| `kismode` | VARCHAR(2) | PRIMARY KEY (part 3), FK → kiscourse | KIS Mode |
| `entunavailreason` | VARCHAR(1) | | Unavailability reason code |
| `entpop` | INTEGER | | Population count |
| `entagg` | VARCHAR(1) | | Aggregation indicator |
| `entaggyear` | VARCHAR(10) | | Aggregation year |
| `entyear1` | VARCHAR(10) | | Year 1 |
| `entyear2` | VARCHAR(10) | | Year 2 |
| `entsbj` | VARCHAR(50) | | Subject code |
| `access` | INTEGER | | Access qualifications count |
| `alevel` | INTEGER | | A-Level qualifications count |
| `bacc` | INTEGER | | Baccalaureate count |
| `degree` | INTEGER | | Degree count |
| `foundtn` | INTEGER | | Foundation count |
| `noquals` | INTEGER | | No qualifications count |
| `other` | INTEGER | | Other qualifications count |
| `otherhe` | INTEGER | | Other HE qualifications count |

**Composite Primary Key**: (`pubukprn`, `kiscourseid`, `kismode`)

**Indexes**:
- `idx_entry_course` on (`pubukprn`, `kiscourseid`, `kismode`)
- `idx_entry_sbj` on `entsbj`

---

##### `tariff`
**Purpose**: Entry tariff points statistics (UCAS points distribution)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `pubukprn` | VARCHAR(10) | PRIMARY KEY (part 1), FK → kiscourse | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | PRIMARY KEY (part 2), FK → kiscourse | KIS Course identifier |
| `kismode` | VARCHAR(2) | PRIMARY KEY (part 3), FK → kiscourse | KIS Mode |
| `tarunavailreason` | VARCHAR(1) | | Unavailability reason code |
| `tarpop` | INTEGER | | Population count |
| `taragg` | VARCHAR(1) | | Aggregation indicator |
| `taraggyear` | VARCHAR(10) | | Aggregation year |
| `taryear1` | VARCHAR(10) | | Year 1 |
| `taryear2` | VARCHAR(10) | | Year 2 |
| `tarsbj` | VARCHAR(50) | | Subject code |
| `t001` | INTEGER | | Students with 0-16 tariff points |
| `t048` | INTEGER | | Students with 48 tariff points |
| `t064` | INTEGER | | Students with 64 tariff points |
| `t080` | INTEGER | | Students with 80 tariff points |
| `t096` | INTEGER | | Students with 96 tariff points |
| `t112` | INTEGER | | Students with 112 tariff points |
| `t128` | INTEGER | | Students with 128 tariff points |
| `t144` | INTEGER | | Students with 144 tariff points |
| `t160` | INTEGER | | Students with 160 tariff points |
| `t176` | INTEGER | | Students with 176 tariff points |
| `t192` | INTEGER | | Students with 192 tariff points |
| `t208` | INTEGER | | Students with 208 tariff points |
| `t224` | INTEGER | | Students with 224 tariff points |
| `t240` | INTEGER | | Students with 240+ tariff points |

**Composite Primary Key**: (`pubukprn`, `kiscourseid`, `kismode`)

**Indexes**:
- `idx_tariff_course` on (`pubukprn`, `kiscourseid`, `kismode`)
- `idx_tariff_sbj` on `tarsbj`

---

##### `continuation`
**Purpose**: Continuation statistics (retention rates)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `pubukprn` | VARCHAR(10) | PRIMARY KEY (part 1), FK → kiscourse | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | PRIMARY KEY (part 2), FK → kiscourse | KIS Course identifier |
| `kismode` | VARCHAR(2) | PRIMARY KEY (part 3), FK → kiscourse | KIS Mode |
| `contunavailreason` | VARCHAR(1) | | Unavailability reason code |
| `contpop` | INTEGER | | Population count |
| `contagg` | VARCHAR(1) | | Aggregation indicator |
| `contaggyear` | VARCHAR(10) | | Aggregation year |
| `contyear1` | VARCHAR(10) | | Year 1 |
| `contyear2` | VARCHAR(10) | | Year 2 |
| `contsbj` | VARCHAR(50) | | Subject code |
| `ucont` | INTEGER | | Continued count |
| `udormant` | INTEGER | | Dormant count |
| `ugained` | INTEGER | | Gained count |
| `uleft` | INTEGER | | Left count |
| `ulower` | INTEGER | | Lower level count |

**Composite Primary Key**: (`pubukprn`, `kiscourseid`, `kismode`)

**Indexes**:
- `idx_continuation_course` on (`pubukprn`, `kiscourseid`, `kismode`)
- `idx_continuation_sbj` on `contsbj`

---

#### Employment & Salary Tables

##### `employment`
**Purpose**: Employment outcomes statistics (15 months after graduation)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `pubukprn` | VARCHAR(10) | PRIMARY KEY (part 1), FK → kiscourse | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | PRIMARY KEY (part 2), FK → kiscourse | KIS Course identifier |
| `kismode` | VARCHAR(2) | PRIMARY KEY (part 3), FK → kiscourse | KIS Mode |
| `empunavailreason` | VARCHAR(1) | | Unavailability reason code |
| `emppop` | INTEGER | | Population count |
| `empresponse` | INTEGER | | Response count |
| `empsample` | INTEGER | | Sample size |
| `empresp_rate` | INTEGER | | Response rate percentage |
| `empagg` | VARCHAR(1) | | Aggregation indicator |
| `empaggyear` | VARCHAR(10) | | Aggregation year |
| `empyear1` | VARCHAR(10) | | Year 1 |
| `empyear2` | VARCHAR(10) | | Year 2 |
| `empsbj` | VARCHAR(50) | | Subject code |
| `workstudy` | INTEGER | | Working and studying count |
| `study` | INTEGER | | Studying count |
| `unemp` | INTEGER | | Unemployed count |
| `prevworkstud` | INTEGER | | Previously working/studying count |
| `both` | INTEGER | | Both working and studying count |
| `noavail` | INTEGER | | Not available count |
| `work` | INTEGER | | Working count |

**Composite Primary Key**: (`pubukprn`, `kiscourseid`, `kismode`)

**Indexes**:
- `idx_employment_course` on (`pubukprn`, `kiscourseid`, `kismode`)
- `idx_employment_sbj` on `empsbj`

---

##### `jobtype`
**Purpose**: Job type statistics (professional/managerial vs other)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `pubukprn` | VARCHAR(10) | PRIMARY KEY (part 1), FK → kiscourse | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | PRIMARY KEY (part 2), FK → kiscourse | KIS Course identifier |
| `kismode` | VARCHAR(2) | PRIMARY KEY (part 3), FK → kiscourse | KIS Mode |
| `jobunavailreason` | VARCHAR(1) | | Unavailability reason code |
| `jobpop` | INTEGER | | Population count |
| `jobresponse` | INTEGER | | Response count |
| `jobsample` | INTEGER | | Sample size |
| `jobresp_rate` | INTEGER | | Response rate percentage |
| `jobagg` | VARCHAR(1) | | Aggregation indicator |
| `jobaggyear` | VARCHAR(10) | | Aggregation year |
| `jobyear1` | VARCHAR(10) | | Year 1 |
| `jobyear2` | VARCHAR(10) | | Year 2 |
| `jobsbj` | VARCHAR(50) | | Subject code |
| `profman` | INTEGER | | Professional/Managerial count |
| `otherjob` | INTEGER | | Other job count |
| `unkwn` | INTEGER | | Unknown count |

**Composite Primary Key**: (`pubukprn`, `kiscourseid`, `kismode`)

**Indexes**:
- `idx_jobtype_course` on (`pubukprn`, `kiscourseid`, `kismode`)
- `idx_jobtype_sbj` on `jobsbj`

---

##### `common`
**Purpose**: Common job types grouping (parent table for joblist)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `common_id` | SERIAL | PRIMARY KEY | Surrogate primary key |
| `pubukprn` | VARCHAR(10) | NOT NULL, FK → kiscourse | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | NOT NULL, FK → kiscourse | KIS Course identifier |
| `kismode` | VARCHAR(2) | NOT NULL, FK → kiscourse | KIS Mode |
| `comunavailreason` | VARCHAR(1) | | Unavailability reason code |
| `compop` | INTEGER | | Population count |
| `comresponse` | INTEGER | | Response count |
| `comsample` | INTEGER | | Sample size |
| `compesp_rate` | INTEGER | | Response rate percentage |
| `comagg` | VARCHAR(1) | | Aggregation indicator |
| `comaggyear` | VARCHAR(10) | | Aggregation year |
| `comyear1` | VARCHAR(10) | | Year 1 |
| `comyear2` | VARCHAR(10) | | Year 2 |
| `comsbj` | VARCHAR(50) | | Subject code (may be NULL) |

**Indexes**:
- `idx_common_course` on (`pubukprn`, `kiscourseid`, `kismode`)
- `idx_common_sbj` on `comsbj`

**Unique Constraint**: (`pubukprn`, `kiscourseid`, `kismode`, `comsbj`)

---

##### `joblist`
**Purpose**: Specific job titles obtained by graduates (e.g., "Marketing Manager", "Software Developer")

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `joblist_id` | SERIAL | PRIMARY KEY | Surrogate primary key |
| `pubukprn` | VARCHAR(10) | NOT NULL | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | NOT NULL | KIS Course identifier |
| `kismode` | VARCHAR(2) | NOT NULL | KIS Mode |
| `comsbj` | VARCHAR(50) | | Subject code (may be NULL) |
| `job` | VARCHAR(500) | | Job title |
| `perc` | INTEGER | | Percentage of graduates |
| `order` | INTEGER | | Display order |
| `hs` | INTEGER | | High skill indicator |

**Indexes**:
- `idx_joblist_common` on (`pubukprn`, `kiscourseid`, `kismode`, `comsbj`)
- `idx_joblist_sbj` on `comsbj`

**Unique Constraint**: (`pubukprn`, `kiscourseid`, `kismode`, `comsbj`, `job`)

**Foreign Key**: References `common` via composite key

---

##### `gosalary`
**Purpose**: Graduate salary data (15 months after graduation) - institution level

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `pubukprn` | VARCHAR(10) | PRIMARY KEY (part 1), FK → kiscourse | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | PRIMARY KEY (part 2), FK → kiscourse | KIS Course identifier |
| `kismode` | VARCHAR(2) | PRIMARY KEY (part 3), FK → kiscourse | KIS Mode |
| `gosalunavailreason` | VARCHAR(1) | | Unavailability reason code |
| `gosalpop` | INTEGER | | Population count |
| `gosalresponse` | INTEGER | | Response count |
| `gosalsample` | INTEGER | | Sample size |
| `gosalresp_rate` | INTEGER | | Response rate percentage |
| `gosalagg` | VARCHAR(1) | | Aggregation indicator |
| `gosalaggyear` | VARCHAR(10) | | Aggregation year |
| `gosalyear1` | VARCHAR(10) | | Year 1 |
| `gosalyear2` | VARCHAR(10) | | Year 2 |
| `gosalsbj` | VARCHAR(50) | | Subject code |
| `goinstlq` | INTEGER | | Institution Lower Quartile salary (£) |
| `goinstmed` | INTEGER | | Institution Median salary (£) |
| `goinstuq` | INTEGER | | Institution Upper Quartile salary (£) |
| `goprov_pc_uk` | INTEGER | | Provider percentage UK |
| `goprov_pc_e` | INTEGER | | Provider percentage England |
| `goprov_pc_ni` | INTEGER | | Provider percentage Northern Ireland |
| `goprov_pc_s` | INTEGER | | Provider percentage Scotland |
| `goprov_pc_w` | INTEGER | | Provider percentage Wales |

**Composite Primary Key**: (`pubukprn`, `kiscourseid`, `kismode`)

**Indexes**:
- `idx_gosalary_course` on (`pubukprn`, `kiscourseid`, `kismode`)
- `idx_gosalary_sbj` on `gosalsbj`

---

##### `gosecsal`
**Purpose**: Sector salary data (benchmark salaries by subject area and mode)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `gosecsbj` | VARCHAR(50) | PRIMARY KEY (part 1) | Sector subject code (CAH code) |
| `kismode` | VARCHAR(2) | PRIMARY KEY (part 2) | KIS Mode |
| `kislevel` | VARCHAR(2) | PRIMARY KEY (part 3) | KIS Level (03=Undergraduate, 04=Postgraduate) |
| `goseclq_uk` | INTEGER | | Lower Quartile UK |
| `gosecmed_uk` | INTEGER | | Median UK |
| `gosecuq_uk` | INTEGER | | Upper Quartile UK |
| `gosecpop_uk` | INTEGER | | Population UK |
| `goseclq_e` | INTEGER | | Lower Quartile England |
| `gosecmed_e` | INTEGER | | Median England |
| `gosecuq_e` | INTEGER | | Upper Quartile England |
| `gosecpop_e` | INTEGER | | Population England |
| ... (similar columns for NI, Scotland, Wales) | | | |

**Composite Primary Key**: (`gosecsbj`, `kismode`, `kislevel`)

**Indexes**:
- `idx_gosecsal_sbj` on `gosecsbj`
- `idx_gosecsal_mode_level` on (`kismode`, `kislevel`)

---

##### `govoicework`
**Purpose**: Graduate voice/work satisfaction scores

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `pubukprn` | VARCHAR(10) | PRIMARY KEY (part 1), FK → kiscourse | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | PRIMARY KEY (part 2), FK → kiscourse | KIS Course identifier |
| `kismode` | VARCHAR(2) | PRIMARY KEY (part 3), FK → kiscourse | KIS Mode |
| `goworkunavailreason` | VARCHAR(1) | | Unavailability reason code |
| `goworkpop` | INTEGER | | Population count |
| `goworkresponse` | INTEGER | | Response count |
| `goworksample` | INTEGER | | Sample size |
| `goworkresp_rate` | INTEGER | | Response rate percentage |
| `goworkagg` | VARCHAR(1) | | Aggregation indicator |
| `goworkaggyear` | VARCHAR(10) | | Aggregation year |
| `goworkyear1` | VARCHAR(10) | | Year 1 |
| `goworkyear2` | VARCHAR(10) | | Year 2 |
| `goworksbj` | VARCHAR(50) | | Subject code |
| `goworkmean` | INTEGER | | Mean score (0-100) |
| `goworkontrack` | INTEGER | | On track score (0-100) |
| `goworkskills` | INTEGER | | Skills score (0-100) |

**Composite Primary Key**: (`pubukprn`, `kiscourseid`, `kismode`)

**Indexes**:
- `idx_govoicework_course` on (`pubukprn`, `kiscourseid`, `kismode`)
- `idx_govoicework_sbj` on `goworksbj`

---

#### LEO (Longitudinal Education Outcomes) Tables

##### `leo3`
**Purpose**: Earnings data 3 years after graduation - institution level

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `pubukprn` | VARCHAR(10) | PRIMARY KEY (part 1), FK → kiscourse | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | PRIMARY KEY (part 2), FK → kiscourse | KIS Course identifier |
| `kismode` | VARCHAR(2) | PRIMARY KEY (part 3), FK → kiscourse | KIS Mode |
| `leo3unavailreason` | VARCHAR(1) | | Unavailability reason code |
| `leo3pop` | INTEGER | | Population count |
| `leo3agg` | VARCHAR(1) | | Aggregation indicator |
| `leo3aggyear` | VARCHAR(10) | | Aggregation year |
| `leo3sbj` | VARCHAR(50) | | Subject code |
| `leo3instlq` | INTEGER | | Institution Lower Quartile earnings (£) |
| `leo3instmed` | INTEGER | | Institution Median earnings (£) |
| `leo3instuq` | INTEGER | | Institution Upper Quartile earnings (£) |
| `leo3prov_pc_uk` | INTEGER | | Provider percentage UK |
| `leo3prov_pc_e` | INTEGER | | Provider percentage England |
| ... (similar columns for regions: nw, ne, em, wm, ee, se, sw, yh, ln, ni, s, ed, gl, w, cf) | | | |

**Composite Primary Key**: (`pubukprn`, `kiscourseid`, `kismode`)

**Indexes**:
- `idx_leo3_course` on (`pubukprn`, `kiscourseid`, `kismode`)
- `idx_leo3_sbj` on `leo3sbj`

---

##### `leo3sec`
**Purpose**: Sector earnings data 3 years after graduation

Similar structure to `leo3` but aggregated at sector level (by subject code, mode, level).

**Composite Primary Key**: (`leo3secsbj`, `kismode`, `kislevel`)

---

##### `leo5`
**Purpose**: Earnings data 5 years after graduation - institution level

Similar structure to `leo3` but for 5-year timepoint.

**Composite Primary Key**: (`pubukprn`, `kiscourseid`, `kismode`)

---

##### `leo5sec`
**Purpose**: Sector earnings data 5 years after graduation

Similar structure to `leo3sec` but for 5-year timepoint.

**Composite Primary Key**: (`leo5secsbj`, `kismode`, `kislevel`)

---

#### NSS (National Student Survey) Tables

##### `nss`
**Purpose**: National Student Survey results (student satisfaction scores)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `pubukprn` | VARCHAR(10) | PRIMARY KEY (part 1), FK → kiscourse | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | PRIMARY KEY (part 2), FK → kiscourse | KIS Course identifier |
| `kismode` | VARCHAR(2) | PRIMARY KEY (part 3), FK → kiscourse | KIS Mode |
| `nssunavailreason` | VARCHAR(1) | | Unavailability reason code |
| `nsspop` | INTEGER | | Population count |
| `nssresp_rate` | INTEGER | | Response rate percentage |
| `nssagg` | VARCHAR(1) | | Aggregation indicator |
| `nssaggyear` | VARCHAR(10) | | Aggregation year |
| `nssyear1` | VARCHAR(10) | | Year 1 |
| `nssyear2` | VARCHAR(10) | | Year 2 |
| `nsssbj` | VARCHAR(50) | | Subject code |
| `q1` through `q26` | INTEGER | | Question scores (0-100) |
| `t1` through `t7` | INTEGER | | Theme scores (0-100) |

**Composite Primary Key**: (`pubukprn`, `kiscourseid`, `kismode`)

**Indexes**:
- `idx_nss_course` on (`pubukprn`, `kiscourseid`, `kismode`)
- `idx_nss_sbj` on `nsssbj`

---

##### `nsscountry`
**Purpose**: Country-specific NSS results (additional questions for England/Wales/Scotland)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `pubukprn` | VARCHAR(10) | PRIMARY KEY (part 1), FK → kiscourse | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | NOT NULL | UK Provider Reference Number |
| `kiscourseid` | VARCHAR(50) | PRIMARY KEY (part 2), FK → kiscourse | KIS Course identifier |
| `kismode` | VARCHAR(2) | PRIMARY KEY (part 3), FK → kiscourse | KIS Mode |
| `nsscountryunavailreason` | VARCHAR(1) | | Unavailability reason code |
| `nsscountrypop` | INTEGER | | Population count |
| `nsscountryresp_rate` | INTEGER | | Response rate percentage |
| `nsscountryagg` | VARCHAR(1) | | Aggregation indicator |
| `nsscountryaggyear` | VARCHAR(10) | | Aggregation year |
| `nsscountryyear1` | VARCHAR(10) | | Year 1 |
| `nsscountryyear2` | VARCHAR(10) | | Year 2 |
| `nsscountrysbj` | VARCHAR(50) | | Subject code |
| `q27` | INTEGER | | Question 27 - Freedom of expression (England only) |
| `q28` | INTEGER | | Question 28 - Mental wellbeing services |

**Composite Primary Key**: (`pubukprn`, `kiscourseid`, `kismode`)

**Indexes**:
- `idx_nsscountry_course` on (`pubukprn`, `kiscourseid`, `kismode`)
- `idx_nsscountry_sbj` on `nsscountrysbj`

---

#### TEF (Teaching Excellence Framework) Table

##### `tefoutcome`
**Purpose**: Teaching Excellence Framework ratings (Gold, Silver, Bronze)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `pubukprn` | VARCHAR(10) | PRIMARY KEY (part 1), FK → institution | Published UK Provider Reference Number |
| `ukprn` | VARCHAR(10) | PRIMARY KEY (part 2) | UK Provider Reference Number |
| `report_ukprn` | VARCHAR(10) | NOT NULL | Report UKPRN |
| `overall_rating` | VARCHAR(20) | | Overall TEF rating (Gold, Silver, Bronze, Provisional) |
| `student_experience_rating` | VARCHAR(20) | | Student experience rating |
| `student_outcomes_rating` | VARCHAR(20) | | Student outcomes rating |
| `outcome_url` | VARCHAR(500) | | URL to TEF outcome details |

**Composite Primary Key**: (`pubukprn`, `ukprn`)

**Indexes**:
- `idx_tefoutcome_pubukprn` on `pubukprn`
- `idx_tefoutcome_ukprn` on `ukprn`
- `idx_tefoutcome_rating` on `overall_rating`

---

#### Additional Table

##### `accreditation_by_hep`
**Purpose**: Additional accreditation information by Higher Education Provider

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `accrediting_body_name` | VARCHAR(500) | PRIMARY KEY (part 1) | Accrediting body name |
| `hep` | VARCHAR(500) | PRIMARY KEY (part 2) | Higher Education Provider name |
| `kiscourseid` | VARCHAR(50) | PRIMARY KEY (part 3) | KIS Course identifier |
| `accredition_type` | TEXT | | Accreditation type |
| `kiscourse_title` | VARCHAR(500) | | KIS Course title |

**Composite Primary Key**: (`accrediting_body_name`, `hep`, `kiscourseid`)

**Indexes**:
- `idx_accreditation_by_hep_kiscourseid` on `kiscourseid`
- `idx_accreditation_by_hep_hep` on `hep`

---

## Key Relationships Summary

### One-to-Many Relationships
- `student` → `student_grade`
- `student` → `recommendation_run`
- `student` → `recommendation_feedback`
- `university` → `course`
- `course` → `course_requirement`
- `course` → `course_required_exam`
- `course` → `recommendation_feedback`
- `subject` → `student_grade`
- `subject` → `course_requirement`
- `entrance_exam` → `course_required_exam`
- `recommendation_run` → `recommendation_result`
- `institution` → `kiscourse`
- `institution` → `tefoutcome`
- `kis_aim` → `kiscourse`
- `kiscourse` → (multiple HESA tables)
- `career_interest` → `career_interest_keyword`
- `career_interest` → `career_interest_conflict` (both directions)

### Many-to-Many Relationships (via Junction Tables)
- `course` ↔ `subject` (via `course_requirement`)
- `course` ↔ `entrance_exam` (via `course_required_exam`)
- `kiscourse` ↔ `location` (via `courselocation`)
- `kiscourse` ↔ `accreditation_table` (via `accreditation`)
- `kiscourse` ↔ `sbj` (subject codes, via direct table)
- `common` ↔ `joblist` (job types)

### Composite Primary Keys
Many HESA tables use composite primary keys based on (`pubukprn`, `kiscourseid`, `kismode`) to uniquely identify courses. This allows:
- Same course offered full-time and part-time
- Same course at different institutions
- Historical data tracking

---

## Data Import Order

When importing data, follow this order to respect foreign key constraints:

1. **Lookup Tables**: `subject`, `entrance_exam`, `accreditation_table`, `kis_aim`, `location`
2. **Core Entities**: `student`, `university`, `institution`
3. **HESA Core**: `kiscourse`
4. **Courses**: `course` (with HESA links)
5. **Requirements**: `course_requirement`, `course_required_exam`
6. **HESA Related**: `accreditation`, `courselocation`, `ucascourseid`, `sbj`
7. **HESA Outcomes**: `entry`, `tariff`, `continuation`, `employment`, `jobtype`, `common`, `joblist`, `gosalary`, `gosecsal`, `govoicework`, `leo3`, `leo3sec`, `leo5`, `leo5sec`, `nss`, `nsscountry`
8. **TEF**: `tefoutcome`
9. **Career Interests**: `career_interest`, `career_interest_keyword`, `career_interest_conflict`
10. **Feedback**: `recommendation_feedback`, `recommendation_settings`

---

## Indexing Strategy

### B-Tree Indexes
- Foreign keys: Automatically indexed for join performance
- Frequently filtered columns: `region`, `rank_overall`, `annual_fee`, `ucas_code`
- Case-insensitive search: `lower(name)` on `course` and `university`

### GIN Indexes (Generalized Inverted Index)
- JSONB columns: `recommendation_result.items`, `recommendation_feedback.search_criteria`
- Array columns: `student.preferred_exams`

### Partial Indexes
- `ix_course_fee_cap`: Only indexes courses with fee ≤ £9,250 (UK fee cap)
- Career interest active filters: Only indexes active records

---

## Notes

1. **HESA Data Linking**: The `course` table links to HESA data via (`pubukprn`, `kiscourseid`, `kismode`). This allows the recommendation engine to enrich course recommendations with employment, salary, and student satisfaction data.

2. **Welsh Translations**: Many HESA tables include Welsh translations (`*w` columns) for bilingual support.

3. **Unavailability Reasons**: Many HESA tables include `*unavailreason` columns to indicate why data might not be available.

4. **Subject Codes**: HESA uses CAH (Common Aggregation Hierarchy) subject codes in the `sbj` table, while the application uses custom subject identifiers in the `subject` table.

5. **Composite Keys**: HESA tables use composite primary keys because the same course can exist in multiple modes (full-time, part-time) and at multiple institutions.

6. **Feedback Learning**: The `recommendation_feedback` table enables the recommendation engine to learn from student feedback and improve recommendations over time.

7. **Career Interest Matching**: The career interest tables allow dynamic matching of courses to student career interests without hardcoding keywords in application code.

---

## Migration History

The database schema is managed through migration files:

1. **001_initial_schema.sql**: Core application tables
2. **002_discover_uni_data_schema.sql**: HESA data tables
3. **003_add_hesa_links.sql**: Adds HESA linking columns to `course` table
4. **004_recommendation_feedback.sql**: Feedback and learning system
5. **005_career_interests.sql**: Career interest matching system

To apply migrations, use:
```bash
python server/database/init_db.py
```

This script tracks applied migrations in the `schema_migrations` table (if implemented) to prevent duplicate execution.

