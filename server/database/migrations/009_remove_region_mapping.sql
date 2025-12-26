-- Migration: Remove region_mapping table and use regions from university table instead
-- Regions should come directly from HESA data in the university table

-- ============================================
-- 1. Drop region_mapping table (no longer needed)
-- ============================================
DROP TABLE IF EXISTS region_mapping CASCADE;

-- ============================================
-- 2. Update recommendation_weight table comment
-- ============================================
COMMENT ON TABLE recommendation_weight IS 'Weights for different scoring criteria in recommendation engine. Regions are loaded directly from university.region column (HESA data)';

