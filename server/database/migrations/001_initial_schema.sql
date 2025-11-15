-- University Course Recommender System - Initial Schema
-- PostgreSQL Migration Script
-- This script creates all tables, constraints, and indexes

-- ============================================
-- 1. CORE TABLES
-- ============================================

-- Student table
CREATE TABLE student (
    student_id VARCHAR(50) PRIMARY KEY,
    display_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATE DEFAULT CURRENT_DATE,
    region VARCHAR(100),
    tuition_budget INTEGER,
    preferred_exams TEXT[]
);

-- Subject table
CREATE TABLE subject (
    subject_id VARCHAR(50) PRIMARY KEY,
    subject_name VARCHAR(255) NOT NULL UNIQUE
);

-- StudentGrade table (composite PK)
CREATE TABLE student_grade (
    student_id VARCHAR(50) REFERENCES student(student_id) ON DELETE CASCADE,
    subject_id VARCHAR(50) REFERENCES subject(subject_id) ON DELETE RESTRICT,
    predicted_grade VARCHAR(5) NOT NULL CHECK (predicted_grade IN ('A*', 'A', 'B', 'C', 'D', 'E', 'U')),
    PRIMARY KEY (student_id, subject_id)
);

-- University table
CREATE TABLE university (
    university_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    region VARCHAR(100),
    rank_overall INTEGER,
    employability_score INTEGER CHECK (employability_score BETWEEN 0 AND 100),
    website_url VARCHAR(500)
);

-- Course table
CREATE TABLE course (
    course_id VARCHAR(50) PRIMARY KEY,
    university_id VARCHAR(50) REFERENCES university(university_id) ON DELETE CASCADE,
    ucas_code VARCHAR(20) UNIQUE,
    name VARCHAR(255) NOT NULL,
    annual_fee INTEGER CHECK (annual_fee >= 0),
    subject_rank INTEGER,
    employability_score INTEGER CHECK (employability_score BETWEEN 0 AND 100),
    course_url VARCHAR(500),
    typical_offer_text VARCHAR(255),
    typical_offer_tariff INTEGER
);

-- CourseRequirement table
CREATE TABLE course_requirement (
    req_id VARCHAR(50) PRIMARY KEY,
    course_id VARCHAR(50) REFERENCES course(course_id) ON DELETE CASCADE,
    subject_id VARCHAR(50) REFERENCES subject(subject_id) ON DELETE RESTRICT,
    grade_req VARCHAR(5) NOT NULL CHECK (grade_req IN ('A*', 'A', 'B', 'C', 'D', 'E'))
);

-- EntranceExam table
CREATE TABLE entrance_exam (
    exam_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- CourseRequiredExam junction table (composite PK)
CREATE TABLE course_required_exam (
    course_id VARCHAR(50) REFERENCES course(course_id) ON DELETE CASCADE,
    exam_id VARCHAR(50) REFERENCES entrance_exam(exam_id) ON DELETE RESTRICT,
    PRIMARY KEY (course_id, exam_id)
);

-- RecommendationRun table
CREATE TABLE recommendation_run (
    run_id VARCHAR(50) PRIMARY KEY,
    student_id VARCHAR(50) REFERENCES student(student_id) ON DELETE CASCADE,
    run_at DATE DEFAULT CURRENT_DATE,
    weights JSONB,
    prefs_snapshot JSONB
);

-- RecommendationResult table
CREATE TABLE recommendation_result (
    result_id VARCHAR(50) PRIMARY KEY,
    run_id VARCHAR(50) REFERENCES recommendation_run(run_id) ON DELETE CASCADE,
    items JSONB NOT NULL CHECK (jsonb_typeof(items) = 'array')
);

-- ============================================
-- 2. FOREIGN KEY CONSTRAINTS
-- ============================================

-- Course → University
ALTER TABLE course
  ADD CONSTRAINT fk_course_university
  FOREIGN KEY (university_id) REFERENCES university(university_id) ON DELETE CASCADE;

-- CourseRequirement → Course
ALTER TABLE course_requirement
  ADD CONSTRAINT fk_req_course
  FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE;

-- CourseRequirement → Subject
ALTER TABLE course_requirement
  ADD CONSTRAINT fk_req_subject
  FOREIGN KEY (subject_id) REFERENCES subject(subject_id) ON DELETE RESTRICT;

-- RecommendationRun → Student
ALTER TABLE recommendation_run
  ADD CONSTRAINT fk_run_student
  FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE;

-- RecommendationResult → RecommendationRun
ALTER TABLE recommendation_result
  ADD CONSTRAINT fk_result_run
  FOREIGN KEY (run_id) REFERENCES recommendation_run(run_id) ON DELETE CASCADE;

-- CourseRequiredExam → Course
ALTER TABLE course_required_exam
  ADD CONSTRAINT fk_cre_course 
  FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE;

-- CourseRequiredExam → EntranceExam
ALTER TABLE course_required_exam
  ADD CONSTRAINT fk_cre_exam
  FOREIGN KEY (exam_id) REFERENCES entrance_exam(exam_id) ON DELETE RESTRICT;

-- ============================================
-- 3. CHECK CONSTRAINTS
-- ============================================

-- University employability score
ALTER TABLE university
  ADD CONSTRAINT ck_employability_0_100 CHECK (employability_score BETWEEN 0 AND 100);

-- Course annual fee non-negative
ALTER TABLE course
  ADD CONSTRAINT ck_fee_nonneg CHECK (annual_fee >= 0);

-- RecommendationResult items must be array
ALTER TABLE recommendation_result
  ADD CONSTRAINT ck_items_is_array CHECK (jsonb_typeof(items) = 'array');

-- ============================================
-- 4. INDEXES - Join and Filter (BTREE)
-- ============================================

CREATE INDEX ix_course_university ON course(university_id);
CREATE INDEX ix_req_course ON course_requirement(course_id);
CREATE INDEX ix_req_subject ON course_requirement(subject_id);
CREATE INDEX ix_grade_student ON student_grade(student_id);
CREATE INDEX ix_grade_subject ON student_grade(subject_id);
CREATE INDEX ix_result_run ON recommendation_result(run_id);
CREATE INDEX ix_run_student_created ON recommendation_run(student_id, run_at);

-- ============================================
-- 5. INDEXES - UI Filters
-- ============================================

CREATE INDEX ix_university_region_rank ON university(region, rank_overall);
CREATE INDEX ix_course_fee ON course(annual_fee);
CREATE INDEX ix_course_ucas ON course(ucas_code);
CREATE INDEX ix_course_name_ci ON course(lower(name));
CREATE INDEX ix_university_name_ci ON university(lower(name));

-- Partial index for UK fee cap
CREATE INDEX ix_course_fee_cap ON course(annual_fee) WHERE annual_fee <= 9250;

-- ============================================
-- 6. INDEXES - Arrays and JSONB (GIN)
-- ============================================

CREATE INDEX ix_student_pref_exams_gin ON student USING GIN (preferred_exams);
CREATE INDEX ix_rr_items_gin ON recommendation_result USING GIN (items);

