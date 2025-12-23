# Career Interests Database Management

This document explains the database-driven career interests system that replaces hardcoded values in the recommendation engine.

## Overview

Instead of hardcoding career interest keywords and conflicts in the Python code, the system now stores this data in the database. This allows:

- **Easy Updates**: Modify keywords and conflicts without code changes
- **Admin Management**: Non-developers can update career interest data
- **Version Control**: Database migrations track changes
- **Flexibility**: Add new career interests or modify existing ones dynamically

## Database Schema

### Tables

1. **`career_interest`**: Career interest categories
   - `interest_id`: Primary key
   - `interest_name`: Unique identifier (e.g., "Business & Finance")
   - `display_name`: User-facing name
   - `is_active`: Enable/disable career interest
   - `display_order`: Order for UI display

2. **`career_interest_keyword`**: Keywords for matching courses
   - `keyword_id`: Primary key
   - `interest_id`: Foreign key to `career_interest`
   - `keyword`: The keyword to match (e.g., "business", "finance")
   - `priority`: Higher priority keywords are checked first
   - `is_active`: Enable/disable keyword

3. **`career_interest_conflict`**: Conflicting career interests
   - `conflict_id`: Primary key
   - `interest_id`: The career interest
   - `conflicting_interest_id`: The conflicting career interest
   - `conflict_strength`: 'weak', 'medium', or 'strong'

## Running the Migration

### Option 1: Using Python Script

```bash
cd server/database
python run_career_interests_migration.py
```

### Option 2: Using init_db.py

The migration will be automatically run when you run:

```bash
cd server/database
python init_db.py
```

### Option 3: Manual SQL

```bash
psql -d university_recommender -f server/database/migrations/005_career_interests.sql
```

## Managing Career Interests

### Adding a New Career Interest

```sql
-- 1. Add the career interest
INSERT INTO career_interest (interest_id, interest_name, display_name, description, display_order)
VALUES ('CI011', 'Data Science', 'Data Science', 'Data science, analytics, machine learning', 11);

-- 2. Add keywords
INSERT INTO career_interest_keyword (keyword_id, interest_id, keyword, priority)
VALUES 
    ('KW067', 'CI011', 'data science', 10),
    ('KW068', 'CI011', 'analytics', 9),
    ('KW069', 'CI011', 'machine learning', 9),
    ('KW070', 'CI011', 'artificial intelligence', 8);

-- 3. Add conflicts (if any)
INSERT INTO career_interest_conflict (conflict_id, interest_id, conflicting_interest_id, conflict_strength)
VALUES 
    ('CF033', 'CI011', 'CI001', 'weak'),  -- Conflicts with Business & Finance
    ('CF034', 'CI001', 'CI011', 'weak');  -- Reverse conflict
```

### Updating Keywords

```sql
-- Add a new keyword
INSERT INTO career_interest_keyword (keyword_id, interest_id, keyword, priority)
VALUES ('KW071', 'CI001', 'fintech', 7);

-- Disable a keyword
UPDATE career_interest_keyword 
SET is_active = FALSE 
WHERE keyword = 'tech' AND interest_id = 'CI003';

-- Change keyword priority
UPDATE career_interest_keyword 
SET priority = 10 
WHERE keyword = 'business' AND interest_id = 'CI001';
```

### Modifying Conflicts

```sql
-- Add a new conflict
INSERT INTO career_interest_conflict (conflict_id, interest_id, conflicting_interest_id, conflict_strength)
VALUES ('CF035', 'CI001', 'CI008', 'medium');

-- Remove a conflict
DELETE FROM career_interest_conflict 
WHERE interest_id = 'CI001' AND conflicting_interest_id = 'CI008';

-- Change conflict strength
UPDATE career_interest_conflict 
SET conflict_strength = 'strong' 
WHERE interest_id = 'CI001' AND conflicting_interest_id = 'CI003';
```

## How It Works

1. **On Engine Initialization**: The `RecommendationEngine` class loads all career interests, keywords, and conflicts from the database in `_load_career_interests_from_db()`

2. **Caching**: Data is cached in memory (`self.career_keywords_map` and `self.conflicting_career_fields`) for performance

3. **Fallback**: If the database connection fails, the system falls back to hardcoded values (for backward compatibility)

4. **Usage**: The recommendation engine uses the loaded data instead of hardcoded dictionaries

## Benefits

- ✅ **No Code Changes**: Update keywords/conflicts without deploying new code
- ✅ **Admin-Friendly**: Non-developers can manage career interests via SQL or admin UI
- ✅ **Version Control**: Database migrations track all changes
- ✅ **Flexibility**: Easy to add new career interests or modify existing ones
- ✅ **Performance**: Data is cached in memory after initial load

## Troubleshooting

### Career interests not loading

Check the database connection and ensure the migration has been run:

```sql
SELECT COUNT(*) FROM career_interest;
SELECT COUNT(*) FROM career_interest_keyword;
SELECT COUNT(*) FROM career_interest_conflict;
```

### Keywords not matching

Verify keywords are active and properly formatted:

```sql
SELECT * FROM career_interest_keyword 
WHERE interest_id = 'CI001' AND is_active = TRUE
ORDER BY priority DESC;
```

### Conflicts not working

Check conflicts are properly defined:

```sql
SELECT 
    ci1.interest_name,
    ci2.interest_name as conflicting,
    cic.conflict_strength
FROM career_interest_conflict cic
JOIN career_interest ci1 ON cic.interest_id = ci1.interest_id
JOIN career_interest ci2 ON cic.conflicting_interest_id = ci2.interest_id
WHERE ci1.interest_name = 'Business & Finance';
```

## Next Steps

Consider creating an admin UI or API endpoints to manage career interests without writing SQL directly.
