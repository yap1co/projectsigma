# Discover Uni Dataset Schema

This migration (`002_discover_uni_data_schema.sql`) creates the database schema for the Discover Uni dataset CSV files.

## Overview

The Discover Uni dataset contains comprehensive information about UK higher education courses, including:
- Course details and locations
- Entry requirements and tariff points
- Student outcomes (employment, salaries, continuation)
- National Student Survey (NSS) results
- Teaching Excellence Framework (TEF) ratings
- Longitudinal Education Outcomes (LEO) data

## Tables Created

### Lookup Tables (Reference Data)

1. **accreditation_table** - Accreditation types and descriptions
2. **kis_aim** - KIS Aim codes (BA, BSc, MEng, etc.)
3. **location** - Teaching location details

### Core Entities

4. **institution** - Higher education institutions
5. **kiscourse** - Main course table (KIS courses)

### Course-Related Entities

6. **accreditation** - Course accreditation information
7. **courselocation** - Course teaching locations
8. **ucascourseid** - UCAS course identifiers
9. **sbj** - Subject codes (CAH codes) for courses

### Student Outcomes Entities

10. **entry** - Entry qualifications data
11. **tariff** - Entry tariff points data
12. **continuation** - Student continuation rates

### Employment & Salary Entities

13. **employment** - Employment statistics
14. **jobtype** - Types of professions entered
15. **common** - Common job types
16. **joblist** - Detailed job lists
17. **gosalary** - Graduate salary information
18. **gosecsal** - Sector salary data
19. **govoicework** - Graduate voice/work satisfaction

### LEO (Longitudinal Education Outcomes) Entities

20. **leo3** - Earnings data at 3 years
21. **leo3sec** - Sector earnings data at 3 years
22. **leo5** - Earnings data at 5 years
23. **leo5sec** - Sector earnings data at 5 years

### NSS (National Student Survey) Entities

24. **nss** - NSS survey results
25. **nsscountry** - Country-specific NSS results

### TEF (Teaching Excellence Framework) Entity

26. **tefoutcome** - TEF ratings

### Additional Tables

27. **accreditation_by_hep** - Accreditation by Higher Education Provider

## Key Relationships

### Primary Relationships

- **kiscourse** → **institution** (via `pubukprn`)
- **kiscourse** → **kis_aim** (via `kisaimcode`)
- All course-related entities → **kiscourse** (via `pubukprn`, `kiscourseid`, `kismode`)

### Foreign Key Relationships

```
institution (pubukprn)
  └── kiscourse (pubukprn, kiscourseid, kismode)
      ├── accreditation
      ├── courselocation
      │   └── ucascourseid
      ├── sbj
      ├── entry
      ├── tariff
      ├── continuation
      ├── employment
      ├── jobtype
      ├── common
      │   └── joblist
      ├── gosalary
      ├── govoicework
      ├── leo3
      ├── leo5
      ├── nss
      └── nsscountry

kiscourse (kisaimcode) → kis_aim
accreditation (acctype) → accreditation_table
courselocation (ukprn, locid) → location
tefoutcome (pubukprn) → institution
```

## Important Notes

### Nullable Columns in Keys

Some tables have nullable columns that are part of unique constraints:
- **courselocation.locid** - May be null
- **common.comsbj** - May be null

These tables use surrogate primary keys (`SERIAL`) with `UNIQUE` constraints on the business keys to handle nullable values properly.

### Data Types

- **VARCHAR** - Used for codes, IDs, and short text fields
- **TEXT** - Used for longer text fields
- **INTEGER** - Used for counts, percentages, and numeric values
- **NUMERIC** - Used for coordinates (latitude/longitude)
- **SERIAL** - Used for surrogate primary keys

### Indexes

Indexes are created on:
- Foreign key columns
- Frequently queried columns (subject codes, UKPRN, etc.)
- Composite indexes for common join patterns

## CSV File Mapping

| CSV File | Table Name | Primary Key |
|----------|------------|-------------|
| ACCREDITATION.csv | accreditation | (pubukprn, kiscourseid, kismode, acctype) |
| ACCREDITATIONTABLE.csv | accreditation_table | acctype |
| COMMON.csv | common | common_id (SERIAL) |
| CONTINUATION.csv | continuation | (pubukprn, kiscourseid, kismode) |
| COURSELOCATION.csv | courselocation | courselocation_id (SERIAL) |
| EMPLOYMENT.csv | employment | (pubukprn, kiscourseid, kismode) |
| ENTRY.csv | entry | (pubukprn, kiscourseid, kismode) |
| GOSALARY.csv | gosalary | (pubukprn, kiscourseid, kismode) |
| GOSECSAL.csv | gosecsal | (gosecsbj, kismode, kislevel) |
| GOVOICEWORK.csv | govoicework | (pubukprn, kiscourseid, kismode) |
| INSTITUTION.csv | institution | pubukprn |
| JOBLIST.csv | joblist | joblist_id (SERIAL) |
| JOBTYPE.csv | jobtype | (pubukprn, kiscourseid, kismode) |
| KISAIM.csv | kis_aim | kisaimcode |
| KISCOURSE.csv | kiscourse | (pubukprn, kiscourseid, kismode) |
| LEO3.csv | leo3 | (pubukprn, kiscourseid, kismode) |
| LEO3SEC.csv | leo3sec | (leo3secsbj, kismode, kislevel) |
| LEO5.csv | leo5 | (pubukprn, kiscourseid, kismode) |
| LEO5SEC.csv | leo5sec | (leo5secsbj, kismode, kislevel) |
| LOCATION.csv | location | (ukprn, locid) |
| NSS.csv | nss | (pubukprn, kiscourseid, kismode) |
| NSSCOUNTRY.csv | nsscountry | (pubukprn, kiscourseid, kismode) |
| SBJ.csv | sbj | (pubukprn, kiscourseid, kismode, sbj) |
| TARIFF.csv | tariff | (pubukprn, kiscourseid, kismode) |
| TEFOutcome.csv | tefoutcome | (pubukprn, ukprn) |
| UCASCOURSEID.csv | ucascourseid | ucascourseid_id (SERIAL) |
| AccreditationByHep.csv | accreditation_by_hep | (accrediting_body_name, hep, kiscourseid) |

## Usage

### Running the Migration

```bash
# Using the init script
cd server/database
python init_db.py

# Or manually
psql -h localhost -U postgres -d university_recommender -f migrations/002_discover_uni_data_schema.sql
```

### Importing CSV Data

After creating the schema, you can import CSV files using PostgreSQL's `COPY` command or a data import script.

Example:
```sql
COPY institution FROM '/path/to/INSTITUTION.csv' WITH (FORMAT csv, HEADER true);
```

## References

- HESA C25061 File Structure: https://www.hesa.ac.uk/collection/C25061/filestructure
- Discover Uni Dataset Documentation: See `data/readme.txt`

