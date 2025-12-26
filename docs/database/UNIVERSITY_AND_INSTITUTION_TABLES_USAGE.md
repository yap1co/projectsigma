# University and Institution Tables Usage in Recommendation Engine

## Overview

The recommendation engine uses two related but distinct tables for university data:
1. **`university`** - Normalized application table (primary usage)
2. **`institution`** - Raw HESA data table (fallback/lookup usage)

---

## Table Relationship

```
HESA Data (Raw)              Application Data (Normalized)
┌─────────────────┐          ┌──────────────────┐
│  institution    │ ────────>│   university     │
│  (pubukprn)     │  mapped  │  (university_id) │
└─────────────────┘          └──────────────────┘
       │                              │
       │                              │
       └──────────┬───────────────────┘
                  │
                  ▼
          ┌──────────────┐
          │   course     │
          │ (has both)   │
          └──────────────┘
```

**Key Point**: The `university` table is populated from `institution` table via `map_hesa_to_main_tables.py`, creating a normalized, application-friendly version of the HESA data.

---

## 1. University Table (Primary Usage)

### Purpose
The `university` table is the **primary table** used by the recommendation engine for all university-related operations.

### Schema
```sql
CREATE TABLE university (
    university_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    region VARCHAR(100),              -- Used for preference matching
    rank_overall INTEGER,             -- Used for ranking scorer
    employability_score INTEGER,       -- Used for employability scorer
    website_url VARCHAR(500)
);
```

### Usage in Recommendation Engine

#### 1.1 Loading Regions (Initialization)
**Location**: `recommendation_engine.py`, lines 80-82, 122-123

```python
# Load regions directly from university table (HESA data)
cur.execute("SELECT DISTINCT region FROM university WHERE region IS NOT NULL ORDER BY region")
self.regions = [row['region'] for row in cur.fetchall()]
```

**Purpose**: 
- Loads all available regions from the `university` table
- Used by `PreferenceMatchScorer` to match student's preferred region
- Replaces the deprecated `region_mapping` table

**Why**: Regions come directly from HESA data, ensuring accuracy and eliminating the need for a separate mapping table.

---

#### 1.2 Fetching All Courses (Main Query)
**Location**: `recommendation_engine.py`, `_get_all_courses()`, lines 1901-1912

```sql
SELECT 
    c.course_id, c.name, c.annual_fee, c.ucas_code,
    c.typical_offer_text, c.typical_offer_tariff,
    c.course_url,
    u.university_id, u.name as university_name, u.region,
    u.rank_overall, u.employability_score as uni_employability,
    u.website_url,
    c.employability_score as course_employability,
    c.pubukprn, c.kiscourseid, c.kismode
FROM course c
JOIN university u ON c.university_id = u.university_id
LIMIT 1000
```

**Purpose**:
- Primary query to fetch all courses with university information
- Joins `course` with `university` to get:
  - University name
  - **Region** (for preference matching)
  - **Ranking** (for ranking scorer)
  - **Employability score** (for employability scorer)
  - Website URL

**Data Structure Created**:
```python
course_dict['university'] = {
    'name': course_dict['university_name'],
    'region': course_dict.get('region'),          # Used by PreferenceMatchScorer
    'ranking': {
        'overall': course_dict.get('rank_overall')  # Used by RankingScorer
    },
    'websiteUrl': course_dict.get('website_url')
}
```

---

#### 1.3 Getting Best Course for University
**Location**: `recommendation_engine.py`, `_get_best_course_for_university()`, lines 592-605

```sql
SELECT 
    c.course_id, c.name, c.annual_fee, c.ucas_code,
    c.employability_score, c.typical_offer_text,
    c.course_url,
    u.university_id, u.name as university_name, u.region,
    u.rank_overall, u.website_url
FROM course c
JOIN university u ON c.university_id = u.university_id
WHERE u.name = %s
  AND c.employability_score IS NOT NULL
ORDER BY c.employability_score DESC NULLS LAST
LIMIT 1
```

**Purpose**:
- Finds the "best" course (highest employability score) for a given university
- Used to show students the university's flagship course alongside recommendations
- Provides university context (region, ranking) for the best course

---

#### 1.4 Region Matching (PreferenceMatchScorer)
**Location**: `scoring_components.py`, `PreferenceMatchScorer._get_course_region()`, lines 218-229

```python
def _get_course_region(self, course: Dict[str, Any]) -> str:
    """Determine the region of a course's university - get directly from university data"""
    # Get region directly from university data (from HESA)
    region = course.get('university', {}).get('region')
    if region:
        return region
    
    # Fallback: try to match from university name
    university_name = course.get('university', {}).get('name', '').lower()
    for region in self.regions:
        if region.lower() in university_name:
            return region
    
    return 'Unknown'
```

**Purpose**:
- Gets the region directly from the `university` table data
- Used to match against student's `preferredRegion` preference
- Primary source: `university.region` column (from HESA data)

**Scoring Impact**:
- If `course_region == preferredRegion`: +0.3 to preference match score
- This is part of the 15% weight in overall recommendation score

---

#### 1.5 Ranking Score (RankingScorer)
**Location**: `scoring_components.py`, `RankingScorer.calculate_score()`, lines 1370-1385

```python
def calculate_score(self, course: Dict[str, Any], student_data: Dict[str, Any]) -> float:
    """Calculate score based on university ranking"""
    ranking = course.get('university', {}).get('ranking', {})
    
    if not ranking:
        return 0.5  # Neutral score if no ranking data
    
    overall_rank = ranking.get('overall')
    
    if overall_rank is not None and overall_rank > 0:
        # Higher rank (lower number) = higher score
        # Rank 1 = 1.0, Rank 50 = 0.67, Rank 100 = 0.5
        return 1.0 / (1.0 + overall_rank / 50.0)
    
    return 0.5
```

**Purpose**:
- Uses `university.rank_overall` to calculate ranking score
- Higher-ranked universities (lower rank number) get higher scores
- Part of the 15% weight in overall recommendation score

**Formula**:
- Rank 1 → Score: 1.0 / (1.0 + 1/50) = 0.98
- Rank 10 → Score: 1.0 / (1.0 + 10/50) = 0.83
- Rank 50 → Score: 1.0 / (1.0 + 50/50) = 0.50

---

#### 1.6 Advanced Recommendations Endpoint (CTE Query)
**Location**: `app.py`, `/api/recommendations/advanced`, lines 483-504

```sql
course_scores AS (
    SELECT 
        c.course_id,
        c.name,
        u.name as university_name,
        u.rank_overall,
        u.region,                    -- Used for region matching
        c.annual_fee,
        c.employability_score,
        ...
        CASE WHEN u.region = (SELECT preferred_region FROM student_profile LIMIT 1) 
             THEN 1.0 ELSE 0.0 END as region_match_score,
        CASE WHEN u.rank_overall IS NOT NULL AND u.rank_overall > 0
             THEN 1.0 / (1.0 + u.rank_overall::float / 100.0)
             ELSE 0.5 END as ranking_score
    FROM course c
    JOIN university u ON c.university_id = u.university_id
    ...
)
```

**Purpose**:
- Advanced SQL endpoint using CTEs
- Uses `university.region` for region matching
- Uses `university.rank_overall` for ranking score calculation
- Demonstrates Group A: Advanced SQL skills

---

## 2. Institution Table (Fallback/Lookup Usage)

### Purpose
The `institution` table contains **raw HESA data** and is used primarily for:
1. **Fallback lookups** when HESA identifiers are missing
2. **Name matching** to find courses in HESA data
3. **Data mapping** to populate the `university` table

### Schema
```sql
CREATE TABLE institution (
    pubukprn VARCHAR(10) PRIMARY KEY,        -- Links to HESA data
    ukprn VARCHAR(10) NOT NULL,
    legal_name VARCHAR(500),
    first_trading_name VARCHAR(500),         -- Used for name matching
    other_names TEXT,
    provaddress TEXT,
    provtel VARCHAR(50),
    provurl VARCHAR(500),                   -- Used for website_url mapping
    country VARCHAR(2),
    pubukprncountry VARCHAR(2),
    qaa_report_type VARCHAR(100),
    qaa_url VARCHAR(500),
    suurl VARCHAR(500),
    suurlw VARCHAR(500)
);
```

### Usage in Recommendation Engine

#### 2.1 Fallback HESA Identifier Lookup
**Location**: `recommendation_engine.py`, `_enrich_course_with_hesa_data()`, lines 934-942

```python
# Fallback: try to find by name matching
course_name = course.get('name', '')
university_name = course.get('university', {}).get('name', '')
cur.execute("""
    SELECT kc.pubukprn, kc.kiscourseid, kc.kismode
    FROM kiscourse kc
    JOIN institution i ON kc.pubukprn = i.pubukprn
    WHERE kc.title ILIKE %s 
      AND i.first_trading_name ILIKE %s
      AND kc.kismode = '01'
    LIMIT 1
""", (f'%{course_name}%', f'%{university_name}%'))
```

**Purpose**:
- When a course doesn't have `pubukprn`/`kiscourseid` in the `course` table
- Uses fuzzy name matching between:
  - `kiscourse.title` (course name)
  - `institution.first_trading_name` (university name)
- Finds the HESA identifier (`pubukprn`) to enable HESA data enrichment

**When Used**:
- Course missing HESA identifiers in `course` table
- Need to enrich course with employment/salary data from HESA tables
- Fallback mechanism to find HESA data when direct links are missing

---

#### 2.2 Data Mapping (Populating University Table)
**Location**: `server/database/map_hesa_to_main_tables.py`, lines 44-47

```python
cur.execute("""
    SELECT 
        i.pubukprn,
        i.first_trading_name as name,
        i.provurl as website_url
    FROM institution i
    WHERE i.pubukprn IS NOT NULL
""")
```

**Purpose**:
- Maps HESA `institution` data to normalized `university` table
- Extracts:
  - `first_trading_name` → `university.name`
  - `provurl` → `university.website_url`
  - Region is derived from other HESA tables (not directly in `institution`)

**Note**: This is a **one-time mapping** during data import, not used during recommendation generation.

---

## Key Differences

| Aspect | University Table | Institution Table |
|--------|-----------------|-------------------|
| **Purpose** | Application data (normalized) | Raw HESA data |
| **Primary Key** | `university_id` | `pubukprn` |
| **Usage** | Primary - used in all queries | Fallback - used for lookups |
| **Data Source** | Mapped from `institution` + other HESA tables | Direct from HESA CSV |
| **Region** | ✅ Has `region` column | ❌ No region column |
| **Ranking** | ✅ Has `rank_overall` | ❌ No ranking data |
| **Recommendation Engine** | ✅ Used extensively | ⚠️ Used only for fallback lookups |

---

## Data Flow

```
1. HESA CSV Import
   └─> institution table (raw HESA data)

2. Data Mapping (map_hesa_to_main_tables.py)
   └─> university table (normalized, application-friendly)

3. Recommendation Engine
   ├─> Uses university table (primary)
   │   ├─> Region matching
   │   ├─> Ranking scoring
   │   ├─> University context
   │   └─> Best course lookup
   │
   └─> Uses institution table (fallback only)
       └─> HESA identifier lookup when missing
```

---

## Summary

### University Table (Primary)
- **Used for**: All recommendation engine operations
- **Key Fields**: `region`, `rank_overall`, `employability_score`
- **Queries**: 
  - Main course fetching (JOIN with course)
  - Region loading (for PreferenceMatchScorer)
  - Ranking scoring (RankingScorer)
  - Best course lookup

### Institution Table (Fallback)
- **Used for**: HESA identifier lookups when missing
- **Key Fields**: `pubukprn`, `first_trading_name`, `provurl`
- **Queries**: 
  - Fallback name matching to find `pubukprn`
  - Data mapping (one-time import process)

**Recommendation**: The recommendation engine primarily uses the `university` table. The `institution` table is only used as a fallback when HESA identifiers are missing from the `course` table.

