# Project Sigma - Scope Reduction Plan (Option 2.5)

## CSV Files to KEEP (7 files):
1. `INSTITUTION.csv` → university table
2. `KISCOURSE.csv` → course table
3. `EMPLOYMENT.csv` → employment outcomes
4. `GOSALARY.csv` → graduate salaries
5. `LEO3.csv` → 3-year earnings
6. `JOBLIST.csv` → job destinations
7. `ENTRY.csv` → entry statistics

## CSV Files to DELETE (26 files):
- AccreditationByHep.csv
- ACCREDITATIONTABLE.csv
- ACCREDITATION.csv
- COMMON.csv
- CONTINUATION.csv
- COURSELOCATION.csv
- GOSECSAL.csv
- GOVOICEWORK.csv
- JOBTYPE.csv
- KISAIM.csv
- LEO3SEC.csv
- LEO5.csv
- LEO5SEC.csv
- LOCATION.csv
- NSS.csv
- NSSCOUNTRY.csv
- SBJ.csv
- TARIFF.csv
- TEFOutcome.csv
- UCASCOURSEID.csv
- log_details.csv
- log_summary.csv
- log_updates.csv
- Exclusions.csv
- Exclusions.xlsx
- C25061.xsd

## Tables to KEEP (21 total):

### Core Application (15):
1. student
2. student_grade
3. subject
4. university
5. course
6. course_requirement
7. course_required_exam
8. entrance_exam
9. career_interest
10. career_interest_keyword
11. career_interest_conflict
12. recommendation_run
13. recommendation_result
14. recommendation_feedback
15. recommendation_settings

### HESA Data Used by Engine (4):
16. employment
17. gosalary
18. leo3
19. joblist

### HESA Mapping Tables (2):
20. institution (maps to university)
21. kiscourse (maps to course)
22. entry (used for enrichment)

## Tables to DROP (20):
- kis_aim
- accreditation_table
- location
- accreditation
- accreditation_by_hep
- courselocation
- ucascourseid
- sbj
- continuation
- tariff
- gosecsal
- govoicework
- leo3sec
- leo5
- leo5sec
- jobtype
- nss
- nsscountry
- tefoutcome
- common

## Code Changes Required:
**NONE!** ✅ 
- recommendation_engine.py already uses employment, gosalary, leo3, joblist, entry
- No other files reference removed tables

## Files to Modify:

### 1. Delete unused CSVs
Location: `data/`

### 2. Update schema migration
File: `server/database/migrations/002_discover_uni_data_schema.sql`
Action: Remove CREATE TABLE statements for dropped tables

### 3. Update import script
File: `server/database/import_discover_uni_csv.py`
Action: Remove import logic for deleted tables

## Result:
- **Before**: 42 tables, 33 CSV files, ~14K lines
- **After**: 22 tables, 7 CSV files, same ~14K lines
- **Scope reduction**: ~48% fewer tables, 79% fewer data files
