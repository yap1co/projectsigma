-- Discover Uni Dataset - Database Schema (CLEANED for NEA)
-- PostgreSQL Migration Script
-- This script creates only the HESA tables used by the recommendation engine
-- Based on HESA C25061 file structure: https://www.hesa.ac.uk/collection/C25061/filestructure

-- ============================================
-- CORE HESA TABLES
-- ============================================

-- Institution entity (maps to university table)
-- Contains core information about higher education institutions
CREATE TABLE institution (
    ukprn VARCHAR(10) PRIMARY KEY,
    pubukprn VARCHAR(10) NOT NULL,
    ukprncountry VARCHAR(2),
    name VARCHAR(255) NOT NULL,
    namew VARCHAR(255),  -- Welsh translation
    locid VARCHAR(20),
    suurl VARCHAR(500),  -- Student Union URL
    suurlw VARCHAR(500),  -- Welsh Student Union URL
    suurlid VARCHAR(10),  -- Student Union URL ID
    hepurl VARCHAR(500),  -- HEP URL
    hepurlw VARCHAR(500),  -- Welsh HEP URL
    hepurlid VARCHAR(10),  -- HEP URL ID
    instaccom VARCHAR(255),  -- Institution accommodation
    instaccomw VARCHAR(255),  -- Welsh translation
    region VARCHAR(100)
);

COMMENT ON TABLE institution IS 'Institution entity - higher education institution details';
COMMENT ON COLUMN institution.pubukprn IS 'Published UKPRN (may differ from UKPRN for merged institutions)';
COMMENT ON COLUMN institution.namew IS 'Welsh translation of institution name';

CREATE INDEX idx_institution_name ON institution(name);
CREATE INDEX idx_institution_region ON institution(region);

-- KIS Course entity (maps to course table)
-- Contains core information about courses at institutions
CREATE TABLE kiscourse (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    titlew VARCHAR(255),  -- Welsh translation
    kismode VARCHAR(2) NOT NULL,  -- Mode: 01=Full-time, 02=Part-time, etc.
    length VARCHAR(50),
    levelcode VARCHAR(10),
    locid VARCHAR(20),
    distance VARCHAR(1),  -- Distance learning: 0=No, 1=Distance/Online, 2=Mixed
    owncohort VARCHAR(1),  -- Own cohort: 0=No, 1=Yes
    avgcoursecost VARCHAR(50),
    avgcoursecostw VARCHAR(50),  -- Welsh translation
    avcostid VARCHAR(10),
    feeuk INTEGER,  -- UK student fee
    feeeng INTEGER,  -- England student fee
    feeni INTEGER,  -- Northern Ireland student fee
    feesct INTEGER,  -- Scotland student fee
    feewales INTEGER,  -- Wales student fee
    honours VARCHAR(1),  -- Honours flag: 0=No, 1=Yes
    sandwich VARCHAR(1),  -- Sandwich year: 0=No, 1=Available, 2=Compulsory
    yearabroad VARCHAR(1),  -- Year abroad: 0=No, 1=Available, 2=Compulsory
    foundationyear VARCHAR(1),  -- Foundation year: 0=No, 1=Available, 2=Compulsory
    jacs3code VARCHAR(10),  -- JACS3 subject code
    subjectcodename VARCHAR(255),
    subjectcodenamew VARCHAR(255),  -- Welsh translation
    courselocation VARCHAR(255),
    courselocationw VARCHAR(255),  -- Welsh translation
    coursepageurl VARCHAR(500),
    coursepageurlw VARCHAR(500),  -- Welsh URL
    coursepageurlid VARCHAR(10),
    supporturl VARCHAR(500),
    supporturlw VARCHAR(500),  -- Welsh URL
    supporturlid VARCHAR(10),
    employabilityurl VARCHAR(500),
    employabilityurlw VARCHAR(500),  -- Welsh URL
    employabilityurlid VARCHAR(10),
    financialurl VARCHAR(500),
    financialurlw VARCHAR(500),  -- Welsh URL
    financialurlid VARCHAR(10),
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE kiscourse IS 'KIS Course entity - course information at institutions';
COMMENT ON COLUMN kiscourse.kismode IS 'Mode of study: 01=Full-time, 02=Part-time, 03=Both, 04=Flexible';
COMMENT ON COLUMN kiscourse.distance IS 'Distance learning: 0=No, 1=Distance/Online, 2=Mixed';

CREATE INDEX idx_kiscourse_title ON kiscourse(title);
CREATE INDEX idx_kiscourse_institution ON kiscourse(pubukprn);
CREATE INDEX idx_kiscourse_subject ON kiscourse(jacs3code);
CREATE INDEX idx_kiscourse_ukprn_id ON kiscourse(ukprn, kiscourseid);

-- Foreign key
ALTER TABLE kiscourse 
    ADD CONSTRAINT fk_kiscourse_institution 
    FOREIGN KEY (pubukprn) REFERENCES institution(pubukprn) ON DELETE CASCADE;

-- ============================================
-- STUDENT OUTCOMES TABLES (USED BY ENGINE)
-- ============================================

-- Entry entity
-- Contains entry qualification data for courses
CREATE TABLE entry (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    entrylevel VARCHAR(10),
    entunavailreason VARCHAR(1),
    entpop INTEGER,
    entagg VARCHAR(2),  -- Aggregation indicator
    entaggyear VARCHAR(10),
    entyear1 VARCHAR(10),
    entyear2 VARCHAR(10),
    entsbj VARCHAR(50),
    alevel INTEGER,
    access INTEGER,
    aleveltce INTEGER,
    bacc INTEGER,
    degree INTEGER,
    foundation INTEGER,
    noquals INTEGER,
    other INTEGER,
    otherhe INTEGER,
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE entry IS 'Entry entity - entry qualification data for students';

CREATE INDEX idx_entry_course ON entry(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_entry_sbj ON entry(entsbj);

-- Foreign key
ALTER TABLE entry 
    ADD CONSTRAINT fk_entry_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- Employment entity
-- Contains employment data for course graduates
CREATE TABLE employment (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    empunavailreason VARCHAR(1),
    emppop INTEGER,
    empagg VARCHAR(2),  -- Aggregation indicator
    empaggyear VARCHAR(10),
    empyear1 VARCHAR(10),
    empyear2 VARCHAR(10),
    empsbj VARCHAR(50),
    workstudy INTEGER,
    work INTEGER,
    study INTEGER,
    unemp INTEGER,
    other INTEGER,
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE employment IS 'Employment entity - employment outcomes for graduates';

CREATE INDEX idx_employment_course ON employment(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_employment_sbj ON employment(empsbj);

-- Foreign key
ALTER TABLE employment 
    ADD CONSTRAINT fk_employment_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- Job List entity
-- Contains job type destinations for graduates
CREATE TABLE joblist (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    jobunavailreason VARCHAR(1),
    jobpop INTEGER,
    jobresponse INTEGER,
    jobsample INTEGER,
    jobresp_rate INTEGER,
    jobagg VARCHAR(2),  -- Aggregation indicator
    jobaggyear VARCHAR(10),
    jobyear1 VARCHAR(10),
    jobyear2 VARCHAR(10),
    jobsbj VARCHAR(50),
    educ INTEGER,
    health INTEGER,
    carehome INTEGER,
    healthsoc INTEGER,
    retail INTEGER,
    man INTEGER,
    info INTEGER,
    fin INTEGER,
    pro INTEGER,
    admin INTEGER,
    other INTEGER,
    unkwn INTEGER,
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE joblist IS 'Job List entity - types of jobs graduates enter';

CREATE INDEX idx_joblist_course ON joblist(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_joblist_sbj ON joblist(jobsbj);

-- Foreign key
ALTER TABLE joblist 
    ADD CONSTRAINT fk_joblist_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- Graduate Salary entity
-- Contains salary information for graduates in employment
CREATE TABLE gosalary (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    gosunavailreason VARCHAR(1),
    gospop INTEGER,
    gosresponse INTEGER,
    gossample INTEGER,
    gosresp_rate INTEGER,
    gosalagg VARCHAR(2),  -- Aggregation indicator
    gosaggyear VARCHAR(10),
    gosyear1 VARCHAR(10),
    gosyear2 VARCHAR(10),
    gossbj VARCHAR(50),
    ldlwr INTEGER,
    ldmed INTEGER,
    ldupr INTEGER,
    ldpop INTEGER,
    instlwr INTEGER,
    instmed INTEGER,
    instupr INTEGER,
    instpop INTEGER,
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE gosalary IS 'Graduate Salary entity - salary information for graduates';

CREATE INDEX idx_gosalary_course ON gosalary(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_gosalary_sbj ON gosalary(gossbj);

-- Foreign key
ALTER TABLE gosalary 
    ADD CONSTRAINT fk_gosalary_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- LEO3 entity
-- Contains Longitudinal Education Outcomes data (3 years after graduation)
CREATE TABLE leo3 (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    leo3unavailreason VARCHAR(1),
    leo3pop INTEGER,
    leo3agg VARCHAR(2),  -- Aggregation indicator
    leo3aggyear VARCHAR(10),
    leo3year1 VARCHAR(10),
    leo3year2 VARCHAR(10),
    leo3sbj VARCHAR(50),
    leo3instlq INTEGER,
    leo3instmed INTEGER,
    leo3instuq INTEGER,
    leo3instpop INTEGER,
    leo3seclq INTEGER,
    leo3secmed INTEGER,
    leo3secuq INTEGER,
    leo3secpop INTEGER,
    leo3sector VARCHAR(50),
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE leo3 IS 'LEO3 entity - Longitudinal Education Outcomes (3 years)';

CREATE INDEX idx_leo3_course ON leo3(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_leo3_sbj ON leo3(leo3sbj);

-- Foreign key
ALTER TABLE leo3 
    ADD CONSTRAINT fk_leo3_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;
