-- Migration: Move recommendation engine hardcoded mappings to database
-- This migration creates tables to store all configuration data for the recommendation engine

-- ============================================
-- 1. Grade Values Table
-- ============================================
CREATE TABLE IF NOT EXISTS grade_value (
    grade VARCHAR(10) PRIMARY KEY,
    numeric_value INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE grade_value IS 'Grade to numeric value mapping for recommendation engine';
COMMENT ON COLUMN grade_value.grade IS 'Grade letter (A*, A, B, C, D, E, U)';
COMMENT ON COLUMN grade_value.numeric_value IS 'Numeric value for comparison (higher is better)';

-- ============================================
-- 2. Region Mapping Table
-- ============================================
CREATE TABLE IF NOT EXISTS region_mapping (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL,
    city_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (region_name, city_name)
);

COMMENT ON TABLE region_mapping IS 'Mapping of regions to cities for location matching';
COMMENT ON COLUMN region_mapping.region_name IS 'Region name (e.g., London, South East)';
COMMENT ON COLUMN region_mapping.city_name IS 'City name within the region';

CREATE INDEX idx_region_mapping_region ON region_mapping(region_name);

-- ============================================
-- 3. Subject Mapping Table
-- ============================================
CREATE TABLE IF NOT EXISTS subject_related_term (
    mapping_id SERIAL PRIMARY KEY,
    subject_name VARCHAR(255) NOT NULL,
    related_term VARCHAR(255) NOT NULL,
    match_type VARCHAR(50) DEFAULT 'related',  -- 'related', 'synonym', 'category'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (subject_name, related_term)
);

COMMENT ON TABLE subject_related_term IS 'Mapping of A-Level subjects to related terms for course matching';
COMMENT ON COLUMN subject_related_term.subject_name IS 'A-Level subject name (normalized, lowercase)';
COMMENT ON COLUMN subject_related_term.related_term IS 'Related term that can appear in course names';
COMMENT ON COLUMN subject_related_term.match_type IS 'Type of relationship: related, synonym, category';

CREATE INDEX idx_subject_related_term_subject ON subject_related_term(subject_name);
CREATE INDEX idx_subject_related_term_term ON subject_related_term(related_term);

-- ============================================
-- 4. Generic Terms Table
-- ============================================
CREATE TABLE IF NOT EXISTS generic_term (
    term_id SERIAL PRIMARY KEY,
    term VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    min_length INTEGER DEFAULT 3,  -- Minimum length for matching
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE generic_term IS 'Generic terms that are too generic to match alone (need context)';
COMMENT ON COLUMN generic_term.term IS 'Generic term (e.g., science, studies, business)';
COMMENT ON COLUMN generic_term.min_length IS 'Minimum length of related term to allow matching';

-- ============================================
-- 5. Generic Term Matching Rules Table
-- ============================================
CREATE TABLE IF NOT EXISTS generic_term_rule (
    rule_id SERIAL PRIMARY KEY,
    generic_term VARCHAR(100) NOT NULL,
    rule_type VARCHAR(50) NOT NULL,  -- 'contains', 'equals', 'in_list'
    rule_value TEXT NOT NULL,  -- JSON or comma-separated values
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (generic_term) REFERENCES generic_term(term) ON DELETE CASCADE
);

COMMENT ON TABLE generic_term_rule IS 'Rules for when generic terms can legitimately match subjects';
COMMENT ON COLUMN generic_term_rule.generic_term IS 'The generic term this rule applies to';
COMMENT ON COLUMN generic_term_rule.rule_type IS 'Type of rule: contains, equals, in_list';
COMMENT ON COLUMN generic_term_rule.rule_value IS 'Rule value (subject name, list of subjects, etc.)';

CREATE INDEX idx_generic_term_rule_term ON generic_term_rule(generic_term);

-- ============================================
-- 6. Feedback Settings Table
-- ============================================
CREATE TABLE IF NOT EXISTS feedback_setting (
    setting_key VARCHAR(100) PRIMARY KEY,
    setting_value NUMERIC NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE feedback_setting IS 'Tunable settings for feedback-based learning in recommendation engine';
COMMENT ON COLUMN feedback_setting.setting_key IS 'Setting name (e.g., feedback_weight, feedback_decay_days)';
COMMENT ON COLUMN feedback_setting.setting_value IS 'Setting value (numeric)';

-- ============================================
-- 7. Recommendation Engine Weights Table
-- ============================================
CREATE TABLE IF NOT EXISTS recommendation_weight (
    weight_key VARCHAR(100) PRIMARY KEY,
    weight_value NUMERIC(5, 3) NOT NULL CHECK (weight_value >= 0 AND weight_value <= 1),
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE recommendation_weight IS 'Weights for different scoring criteria in recommendation engine';
COMMENT ON COLUMN recommendation_weight.weight_key IS 'Weight name (e.g., subject_match, grade_match)';
COMMENT ON COLUMN recommendation_weight.weight_value IS 'Weight value (0.0 to 1.0)';

