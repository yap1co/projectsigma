# Running the Feedback System Migration

The feedback system requires database tables to be created. Run the migration using one of these methods:

## Option 1: Using the Python Script (Recommended)

```bash
cd server/database
python run_feedback_migration.py
```

## Option 2: Using init_db.py (Runs all migrations)

```bash
cd server/database
python init_db.py
```

This will run all migrations including the feedback migration.

## Option 3: Manual SQL Execution

```bash
psql -d university_recommender -f server/database/migrations/004_recommendation_feedback.sql
```

## What Gets Created

1. **recommendation_feedback** table - Stores thumbs up/down feedback
2. **recommendation_settings** table - Stores tunable parameters
3. Default settings are automatically inserted

## Verification

After running the migration, you should see:
- ✓ Tables created successfully
- No more "relation does not exist" errors in server logs

## Troubleshooting

If you see "relation already exists" errors:
- The tables are already created, you can ignore the warnings
- Or drop and recreate: `DROP TABLE IF EXISTS recommendation_feedback, recommendation_settings CASCADE;`
