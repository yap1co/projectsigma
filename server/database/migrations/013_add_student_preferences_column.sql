-- Migration 013: Add preferences JSONB column to student table
-- This allows storing career interests and other preferences as JSON

-- ============================================
-- 1. Add preferences column to student table
-- ============================================

ALTER TABLE uni_recomm_student
    ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}'::jsonb;

-- ============================================
-- 2. Create GIN index for JSONB queries
-- ============================================

CREATE INDEX IF NOT EXISTS ix_student_preferences_gin 
    ON uni_recomm_student USING GIN (preferences);

-- ============================================
-- 3. Add comments
-- ============================================

COMMENT ON COLUMN uni_recomm_student.preferences IS 'JSONB field storing student preferences including careerInterests, preferredRegion, maxBudget, etc.';

