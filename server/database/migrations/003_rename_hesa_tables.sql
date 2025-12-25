-- Migration 003: Rename HESA tables with hesa_ prefix
-- This clarifies the data lineage: HESA raw data → processing → application tables
-- For NEA documentation: Shows understanding of data pipeline architecture

BEGIN;

-- Rename HESA tables to have hesa_ prefix
ALTER TABLE IF EXISTS institution RENAME TO hesa_institution;
ALTER TABLE IF EXISTS kiscourse RENAME TO hesa_kiscourse;
ALTER TABLE IF EXISTS employment RENAME TO hesa_employment;
ALTER TABLE IF EXISTS entry RENAME TO hesa_entry;
ALTER TABLE IF EXISTS gosalary RENAME TO hesa_gosalary;
ALTER TABLE IF EXISTS joblist RENAME TO hesa_joblist;
ALTER TABLE IF EXISTS leo3 RENAME TO hesa_leo3;

-- Update schema_migrations table
INSERT INTO schema_migrations (version, applied_at)
VALUES ('003', CURRENT_TIMESTAMP)
ON CONFLICT (version) DO NOTHING;

COMMIT;

-- Rollback script (if needed):
-- ALTER TABLE hesa_institution RENAME TO institution;
-- ALTER TABLE hesa_kiscourse RENAME TO kiscourse;
-- ALTER TABLE hesa_employment RENAME TO employment;
-- ALTER TABLE hesa_entry RENAME TO entry;
-- ALTER TABLE hesa_gosalary RENAME TO gosalary;
-- ALTER TABLE hesa_joblist RENAME TO joblist;
-- ALTER TABLE hesa_leo3 RENAME TO leo3;
