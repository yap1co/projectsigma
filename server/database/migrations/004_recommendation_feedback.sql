-- Migration 004: Recommendation Feedback System
-- Adds support for student feedback (thumbs up/down) on recommendations
-- Enables dynamic learning and improvement of recommendation quality

-- ============================================
-- 1. RECOMMENDATION FEEDBACK TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS recommendation_feedback (
    feedback_id VARCHAR(50) PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
    course_id VARCHAR(50) NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    feedback_type VARCHAR(10) NOT NULL CHECK (feedback_type IN ('positive', 'negative')),
    feedback_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    search_criteria JSONB,  -- Store search criteria snapshot for learning
    match_score DECIMAL(5,4),  -- Store the match score at time of feedback
    notes TEXT,  -- Optional notes from student
    
    -- Prevent duplicate feedback from same student for same course in short time
    UNIQUE(student_id, course_id, feedback_at)
);

-- ============================================
-- 2. INDEXES FOR PERFORMANCE
-- ============================================

-- Index for fast lookup of student feedback
CREATE INDEX IF NOT EXISTS ix_feedback_student_course 
    ON recommendation_feedback(student_id, course_id, feedback_at DESC);

-- Index for feedback type queries
CREATE INDEX IF NOT EXISTS ix_feedback_type 
    ON recommendation_feedback(feedback_type, feedback_at DESC);

-- Index for course-based feedback aggregation
CREATE INDEX IF NOT EXISTS ix_feedback_course 
    ON recommendation_feedback(course_id, feedback_type, feedback_at DESC);

-- GIN index for JSONB search criteria queries
CREATE INDEX IF NOT EXISTS ix_feedback_criteria_gin 
    ON recommendation_feedback USING GIN (search_criteria);

-- ============================================
-- 3. FEEDBACK SETTINGS TABLE (Tunable Parameters)
-- ============================================

CREATE TABLE IF NOT EXISTS recommendation_settings (
    setting_id VARCHAR(50) PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(50) REFERENCES student(student_id) ON DELETE SET NULL
);

-- Insert default settings
INSERT INTO recommendation_settings (setting_id, setting_key, setting_value, description)
VALUES 
    ('SET001', 'feedback_weight', '0.15', 'Weight of feedback in final recommendation score (0-1)'),
    ('SET002', 'feedback_decay_days', '90', 'Number of days before feedback relevance decays'),
    ('SET003', 'min_feedback_count', '3', 'Minimum feedback count to apply feedback boost'),
    ('SET004', 'positive_feedback_boost', '0.2', 'Score boost multiplier for positive feedback'),
    ('SET005', 'negative_feedback_penalty', '-0.3', 'Score penalty multiplier for negative feedback')
ON CONFLICT (setting_key) DO NOTHING;

-- Index for settings lookup
CREATE INDEX IF NOT EXISTS ix_settings_key ON recommendation_settings(setting_key);

-- ============================================
-- 4. COMMENTS
-- ============================================

COMMENT ON TABLE recommendation_feedback IS 'Stores student feedback (thumbs up/down) on course recommendations for learning';
COMMENT ON COLUMN recommendation_feedback.search_criteria IS 'JSON snapshot of search criteria used when feedback was given';
COMMENT ON COLUMN recommendation_feedback.match_score IS 'Match score at time of feedback for analysis';
COMMENT ON TABLE recommendation_settings IS 'Tunable settings for recommendation engine behavior';
