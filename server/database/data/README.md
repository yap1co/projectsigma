# Data Import Guide

This directory should contain CSV files for importing data into the PostgreSQL database.

## Required CSV Files

### 1. `universities.csv`

Required columns:
- `university_id` (or will be auto-generated)
- `name` (required)
- `region` (optional)
- `rank_overall` (optional)
- `employability_score` (optional, 0-100)
- `website_url` (optional)

Example:
```csv
university_id,name,region,rank_overall,employability_score,website_url
UNIV_001,University of Oxford,South East,1,95,https://www.ox.ac.uk
UNIV_002,University of Cambridge,East of England,2,94,https://www.cam.ac.uk
```

### 2. `courses.csv`

Required columns:
- `course_id` (or will be auto-generated)
- `university_id` (required - must match university in universities.csv)
- `name` or `course_name` (required)
- `ucas_code` (optional)
- `annual_fee` or `fee` or `uk_fees` (optional)
- `subject_rank` or `subject_ranking` (optional)
- `employability_score` or `employability` (optional, 0-100)
- `course_url` or `url` (optional)
- `typical_offer_text` or `typical_offer` (optional)
- `typical_offer_tariff` or `tariff` (optional)
- `required_subjects` or `subjects` (optional, comma-separated)
- `required_grades` or `grades` (optional, comma-separated)
- `required_exams` or `entrance_exams` (optional, comma-separated)

Example:
```csv
course_id,university_id,name,ucas_code,annual_fee,required_subjects,required_grades,typical_offer_tariff
COURSE_001,UNIV_001,Computer Science,G400,9250,"Mathematics,Computer Science","A*,A",152
COURSE_002,UNIV_002,Mathematics,G100,9250,"Mathematics,Further Mathematics","A*,A*",168
```

## Optional CSV Files

### 3. `subjects.csv`

If not provided, default A-Level subjects will be created.

Columns:
- `subject_id` (or will be auto-generated)
- `subject_name` or `name` (required)

### 4. `exams.csv`

If not provided, default entrance exams will be created.

Columns:
- `exam_id` (or will be auto-generated)
- `name` or `exam_name` (required)

## Usage

### Option 1: Place files in `server/database/data/` directory

```bash
# Copy your CSV files to the data directory
cp universities.csv server/database/data/
cp courses.csv server/database/data/

# Run import script
cd server/database
python import_csv.py
```

### Option 2: Specify file paths

```bash
python import_csv.py \
  --universities /path/to/universities.csv \
  --courses /path/to/courses.csv \
  --subjects /path/to/subjects.csv \
  --exams /path/to/exams.csv
```

### Option 3: Using Docker

```bash
# Copy CSV files to data directory
cp *.csv server/database/data/

# Run import in Docker container
docker-compose exec backend python /app/database/import_csv.py
```

## CSV Format Tips

1. **Headers**: First row should contain column names
2. **Encoding**: Use UTF-8 encoding
3. **Quotes**: Use double quotes for fields containing commas
4. **Missing Values**: Leave empty or use NULL
5. **IDs**: If not provided, unique IDs will be auto-generated

## Data Validation

The import script will:
- Auto-generate IDs if not provided
- Validate foreign key relationships (university_id must exist)
- Handle duplicate entries (ON CONFLICT DO UPDATE)
- Create default subjects and exams if CSV files not provided
- Report errors for invalid data

## Troubleshooting

### Common Issues

1. **Foreign Key Errors**: Ensure `university_id` in courses.csv exists in universities.csv
2. **Subject Not Found**: Subject names must match exactly (case-insensitive)
3. **Encoding Issues**: Ensure CSV files are UTF-8 encoded
4. **Missing Columns**: Use column aliases (e.g., `fee` instead of `annual_fee`)

### Debug Mode

Add `--verbose` flag for detailed output (if implemented):
```bash
python import_csv.py --universities universities.csv --courses courses.csv --verbose
```

