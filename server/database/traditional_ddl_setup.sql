-- ============================================
-- TRADITIONAL DDL APPROACH - DISCOVER UNI DATABASE
-- Step-by-step database creation with relationships
-- ============================================

-- Step 1: Create Database (run this separately if needed)
-- CREATE DATABASE discover_uni_db;
-- \c discover_uni_db;

-- Step 2: Create Schema (optional, for organization)
CREATE SCHEMA IF NOT EXISTS discover_uni;
SET search_path TO discover_uni, public;

-- ============================================
-- STEP 3: CREATE LOOKUP TABLES (Reference Data)
-- These have no dependencies - create first
-- ============================================

-- 3.1: KIS Aim Lookup Table
-- Stores qualification types (BA, BSc, MEng, etc.)
CREATE TABLE IF NOT EXISTS kis_aim (
    kisaimcode VARCHAR(10) PRIMARY KEY,
    kisaimlabel VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE kis_aim IS 'Lookup table for KIS Aim codes (qualification types)';
COMMENT ON COLUMN kis_aim.kisaimcode IS 'KIS Aim code (e.g., 000=BA, 021=BSc)';
COMMENT ON COLUMN kis_aim.kisaimlabel IS 'KIS Aim label (e.g., BA, BSc, MEng)';

-- 3.2: Accreditation Type Lookup Table
-- Stores accreditation body information
CREATE TABLE IF NOT EXISTS accreditation_table (
    acctype VARCHAR(10) PRIMARY KEY,
    accurl VARCHAR(500),
    acctext TEXT,
    acctextw TEXT,  -- Welsh translation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE accreditation_table IS 'Lookup table for accreditation types';
COMMENT ON COLUMN accreditation_table.acctype IS 'Accreditation type code';

-- 3.3: Location Lookup Table
-- Stores teaching location details
CREATE TABLE IF NOT EXISTS location (
    ukprn VARCHAR(10) NOT NULL,
    locid VARCHAR(20) NOT NULL,
    locname VARCHAR(255),
    locnamew VARCHAR(255),  -- Welsh translation
    latitude NUMERIC(10, 8),
    longitude NUMERIC(11, 8),
    accomurl VARCHAR(500),
    accomurlw VARCHAR(500),
    locukprn VARCHAR(10),
    loccountry VARCHAR(2),
    suurl VARCHAR(500),  -- Student Union URL
    suurlw VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ukprn, locid)
);

COMMENT ON TABLE location IS 'Lookup table for teaching locations';
COMMENT ON COLUMN location.locid IS 'Location identifier';
COMMENT ON COLUMN location.latitude IS 'Latitude coordinate';
COMMENT ON COLUMN location.longitude IS 'Longitude coordinate';

-- ============================================
-- STEP 4: CREATE CORE ENTITIES
-- These depend on lookup tables
-- ============================================

-- 4.1: Institution Table
-- Main table for higher education institutions
CREATE TABLE IF NOT EXISTS institution (
    pubukprn VARCHAR(10) PRIMARY KEY,
    ukprn VARCHAR(10) NOT NULL,
    legal_name VARCHAR(500),
    first_trading_name VARCHAR(500),
    other_names TEXT,
    provaddress TEXT,
    provtel VARCHAR(50),
    provurl VARCHAR(500),
    country VARCHAR(2),
    pubukprncountry VARCHAR(2),
    qaa_report_type VARCHAR(100),
    qaa_url VARCHAR(500),
    suurl VARCHAR(500),
    suurlw VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE institution IS 'Main table for higher education institutions';
COMMENT ON COLUMN institution.pubukprn IS 'Published UK Provider Reference Number (Primary Key)';
COMMENT ON COLUMN institution.ukprn IS 'UK Provider Reference Number';

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_institution_ukprn ON institution(ukprn);

-- 4.2: KIS Course Table
-- Main table for courses (depends on institution and kis_aim)
CREATE TABLE IF NOT EXISTS kiscourse (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    title VARCHAR(500),
    titlew VARCHAR(500),  -- Welsh translation
    assurl VARCHAR(500),  -- Assessment URL
    assurlw VARCHAR(500),
    crsecsturl VARCHAR(500),  -- Course student URL
    crsecsturlw VARCHAR(500),
    crseurl VARCHAR(500),  -- Course URL
    crseurlw VARCHAR(500),
    distance VARCHAR(1),  -- Distance learning indicator
    employurl VARCHAR(500),
    employurlw VARCHAR(500),
    foundation VARCHAR(1),  -- Foundation year indicator
    honours VARCHAR(1),
    hecos VARCHAR(10),  -- HECOS subject code
    hecos2 VARCHAR(10),
    hecos3 VARCHAR(10),
    hecos4 VARCHAR(10),
    hecos5 VARCHAR(10),
    locchnge VARCHAR(1),
    lturl VARCHAR(500),  -- Learning and teaching URL
    lturlw VARCHAR(500),
    nhs VARCHAR(1),
    numstage INTEGER,
    sandwich VARCHAR(1),
    supporturl VARCHAR(500),
    supporturlw VARCHAR(500),
    ucasprogid VARCHAR(50),
    ukprnapply VARCHAR(10),
    yearabroad VARCHAR(1),
    kisaimcode VARCHAR(10),  -- Foreign key to kis_aim
    kislevel VARCHAR(2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE kiscourse IS 'Main table for KIS courses';
COMMENT ON COLUMN kiscourse.kiscourseid IS 'KIS Course identifier';
COMMENT ON COLUMN kiscourse.kismode IS 'KIS Mode (01=Full-time, 02=Part-time)';
COMMENT ON COLUMN kiscourse.kisaimcode IS 'Foreign key to kis_aim table';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_kiscourse_ukprn ON kiscourse(ukprn);
CREATE INDEX IF NOT EXISTS idx_kiscourse_pubukprn ON kiscourse(pubukprn);
CREATE INDEX IF NOT EXISTS idx_kiscourse_kisaimcode ON kiscourse(kisaimcode);

-- ============================================
-- STEP 5: CREATE FOREIGN KEY RELATIONSHIPS
-- Establish relationships between tables
-- ============================================

-- 5.1: KIS Course → Institution (Many-to-One)
-- Each course belongs to one institution
ALTER TABLE kiscourse
    ADD CONSTRAINT fk_kiscourse_institution
    FOREIGN KEY (pubukprn)
    REFERENCES institution(pubukprn)
    ON DELETE CASCADE
    ON UPDATE CASCADE;

-- 5.2: KIS Course → KIS Aim (Many-to-One)
-- Each course has one qualification aim (BA, BSc, etc.)
ALTER TABLE kiscourse
    ADD CONSTRAINT fk_kiscourse_kisaim
    FOREIGN KEY (kisaimcode)
    REFERENCES kis_aim(kisaimcode)
    ON DELETE SET NULL
    ON UPDATE CASCADE;

-- ============================================
-- STEP 6: CREATE COURSE-RELATED TABLES
-- These depend on kiscourse
-- ============================================

-- 6.1: Accreditation Table
-- Links courses to their accreditations (Many-to-Many relationship)
CREATE TABLE IF NOT EXISTS accreditation (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    acctype VARCHAR(10) NOT NULL,  -- Foreign key to accreditation_table
    accdepend VARCHAR(1),
    accdependurl VARCHAR(500),
    accdependurlw VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pubukprn, kiscourseid, kismode, acctype)
);

COMMENT ON TABLE accreditation IS 'Course accreditations - links courses to accreditation types';
COMMENT ON COLUMN accreditation.acctype IS 'Foreign key to accreditation_table';

CREATE INDEX IF NOT EXISTS idx_accreditation_course ON accreditation(pubukprn, kiscourseid, kismode);
CREATE INDEX IF NOT EXISTS idx_accreditation_acctype ON accreditation(acctype);

-- Foreign keys for accreditation
ALTER TABLE accreditation
    ADD CONSTRAINT fk_accreditation_kiscourse
    FOREIGN KEY (pubukprn, kiscourseid, kismode)
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode)
    ON DELETE CASCADE
    ON UPDATE CASCADE;

ALTER TABLE accreditation
    ADD CONSTRAINT fk_accreditation_table
    FOREIGN KEY (acctype)
    REFERENCES accreditation_table(acctype)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- 6.2: Course Location Table
-- Links courses to teaching locations (Many-to-Many relationship)
CREATE TABLE IF NOT EXISTS courselocation (
    courselocation_id SERIAL PRIMARY KEY,
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    locid VARCHAR(20),  -- Can be NULL, foreign key to location
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (pubukprn, kiscourseid, kismode, locid)
);

COMMENT ON TABLE courselocation IS 'Links courses to teaching locations';
COMMENT ON COLUMN courselocation.locid IS 'Foreign key to location table (can be NULL)';

CREATE INDEX IF NOT EXISTS idx_courselocation_course ON courselocation(pubukprn, kiscourseid, kismode);
CREATE INDEX IF NOT EXISTS idx_courselocation_loc ON courselocation(ukprn, locid);

-- Foreign keys for courselocation
ALTER TABLE courselocation
    ADD CONSTRAINT fk_courselocation_kiscourse
    FOREIGN KEY (pubukprn, kiscourseid, kismode)
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode)
    ON DELETE CASCADE
    ON UPDATE CASCADE;

-- Note: Foreign key to location is partial (locid can be NULL)
-- We'll handle this with a conditional foreign key or application logic
ALTER TABLE courselocation
    ADD CONSTRAINT fk_courselocation_location
    FOREIGN KEY (ukprn, locid)
    REFERENCES location(ukprn, locid)
    ON DELETE SET NULL
    ON UPDATE CASCADE;

-- 6.3: Subject Table (SBJ)
-- Links courses to subject codes (Many-to-Many relationship)
CREATE TABLE IF NOT EXISTS sbj (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    sbj VARCHAR(50) NOT NULL,  -- CAH subject code
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pubukprn, kiscourseid, kismode, sbj)
);

COMMENT ON TABLE sbj IS 'Subject codes for courses (CAH codes)';
COMMENT ON COLUMN sbj.sbj IS 'CAH (Common Aggregation Hierarchy) subject code';

CREATE INDEX IF NOT EXISTS idx_sbj_course ON sbj(pubukprn, kiscourseid, kismode);
CREATE INDEX IF NOT EXISTS idx_sbj_code ON sbj(sbj);

-- Foreign key for sbj
ALTER TABLE sbj
    ADD CONSTRAINT fk_sbj_kiscourse
    FOREIGN KEY (pubukprn, kiscourseid, kismode)
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode)
    ON DELETE CASCADE
    ON UPDATE CASCADE;

-- ============================================
-- STEP 7: CREATE STUDENT OUTCOMES TABLES
-- These also depend on kiscourse
-- ============================================

-- 7.1: Entry Qualifications Table
CREATE TABLE IF NOT EXISTS entry (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    entunavailreason VARCHAR(1),
    entpop INTEGER,
    entagg VARCHAR(1),
    entaggyear VARCHAR(10),
    entyear1 VARCHAR(10),
    entyear2 VARCHAR(10),
    entsbj VARCHAR(50),
    access INTEGER,  -- Access qualifications count
    alevel INTEGER,  -- A-Level qualifications count
    bacc INTEGER,  -- Baccalaureate count
    degree INTEGER,
    foundtn INTEGER,
    noquals INTEGER,
    other INTEGER,
    otherhe INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE entry IS 'Entry qualifications data for courses';

CREATE INDEX IF NOT EXISTS idx_entry_course ON entry(pubukprn, kiscourseid, kismode);

-- Foreign key for entry
ALTER TABLE entry
    ADD CONSTRAINT fk_entry_kiscourse
    FOREIGN KEY (pubukprn, kiscourseid, kismode)
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode)
    ON DELETE CASCADE
    ON UPDATE CASCADE;

-- 7.2: Employment Table
CREATE TABLE IF NOT EXISTS employment (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    empunavailreason VARCHAR(1),
    emppop INTEGER,
    empresponse INTEGER,
    empsample INTEGER,
    empresp_rate INTEGER,
    empagg VARCHAR(1),
    empaggyear VARCHAR(10),
    empyear1 VARCHAR(10),
    empyear2 VARCHAR(10),
    empsbj VARCHAR(50),
    workstudy INTEGER,
    study INTEGER,
    unemp INTEGER,
    prevworkstud INTEGER,
    both INTEGER,
    noavail INTEGER,
    work INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE employment IS 'Employment statistics for courses';

CREATE INDEX IF NOT EXISTS idx_employment_course ON employment(pubukprn, kiscourseid, kismode);

-- Foreign key for employment
ALTER TABLE employment
    ADD CONSTRAINT fk_employment_kiscourse
    FOREIGN KEY (pubukprn, kiscourseid, kismode)
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode)
    ON DELETE CASCADE
    ON UPDATE CASCADE;

-- ============================================
-- STEP 8: VERIFY RELATIONSHIPS
-- Run these queries to verify structure
-- ============================================

-- View all tables
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'discover_uni' ORDER BY table_name;

-- View all foreign keys
-- SELECT
--     tc.table_name, 
--     kcu.column_name, 
--     ccu.table_name AS foreign_table_name,
--     ccu.column_name AS foreign_column_name 
-- FROM information_schema.table_constraints AS tc 
-- JOIN information_schema.key_column_usage AS kcu
--   ON tc.constraint_name = kcu.constraint_name
-- JOIN information_schema.constraint_column_usage AS ccu
--   ON ccu.constraint_name = tc.constraint_name
-- WHERE tc.constraint_type = 'FOREIGN KEY'
--   AND tc.table_schema = 'discover_uni';

-- ============================================
-- NOTES:
-- 1. This creates a simplified schema with core relationships
-- 2. Additional tables (TARIFF, CONTINUATION, GOSALARY, etc.) 
--    follow the same pattern - depend on kiscourse
-- 3. All relationships use ON DELETE CASCADE for kiscourse
--    (if course deleted, related data deleted)
-- 4. Lookup tables use ON DELETE RESTRICT/SET NULL
--    (protect reference data)
-- ============================================

