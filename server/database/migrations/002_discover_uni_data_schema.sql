-- Discover Uni Dataset - Database Schema
-- PostgreSQL Migration Script
-- This script creates all tables for Discover Uni CSV data files
-- Based on HESA C25061 file structure: https://www.hesa.ac.uk/collection/C25061/filestructure

-- ============================================
-- LOOKUP TABLES (Reference Data)
-- ============================================

-- Accreditation lookup table
-- Contains the accrediting body text and accreditation url for each ACCTYPE
CREATE TABLE accreditation_table (
    acctype VARCHAR(10) PRIMARY KEY,
    accurl VARCHAR(500),
    acctext TEXT,
    acctextw TEXT  -- Welsh translation
);

COMMENT ON TABLE accreditation_table IS 'Accreditation lookup table - accrediting body text and URL for each ACCTYPE';
COMMENT ON COLUMN accreditation_table.acctype IS 'Accreditation type code';
COMMENT ON COLUMN accreditation_table.acctextw IS 'Welsh translation of accreditation text';

-- KIS Aim lookup table
-- Contains the code and label for each KISAIM
CREATE TABLE kis_aim (
    kisaimcode VARCHAR(10) PRIMARY KEY,
    kisaimlabel VARCHAR(100) NOT NULL
);

COMMENT ON TABLE kis_aim IS 'KIS Aim lookup table - code and label for each KISAIM';
COMMENT ON COLUMN kis_aim.kisaimcode IS 'KIS Aim code (e.g., 000=BA, 021=BSc)';
COMMENT ON COLUMN kis_aim.kisaimlabel IS 'KIS Aim label (e.g., BA, BSc, MEng)';

-- Location lookup table
-- Contains details for each teaching location
CREATE TABLE location (
    ukprn VARCHAR(10) NOT NULL,
    locid VARCHAR(20) NOT NULL,
    locname VARCHAR(255),
    locnamew VARCHAR(255),  -- Welsh translation
    latitude NUMERIC(10, 8),
    longitude NUMERIC(11, 8),
    accomurl VARCHAR(500),
    accomurlw VARCHAR(500),  -- Welsh translation
    locukprn VARCHAR(10),
    loccountry VARCHAR(2),
    suurl VARCHAR(500),  -- Student Union URL
    suurlw VARCHAR(500),  -- Welsh Student Union URL
    PRIMARY KEY (ukprn, locid)
);

COMMENT ON TABLE location IS 'Location lookup table - details for each teaching location';
COMMENT ON COLUMN location.locid IS 'Location identifier';
COMMENT ON COLUMN location.latitude IS 'Latitude coordinate';
COMMENT ON COLUMN location.longitude IS 'Longitude coordinate';

-- ============================================
-- CORE ENTITIES
-- ============================================

-- Institution table
-- Describes the reporting institution
CREATE TABLE institution (
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
    suurl VARCHAR(500),  -- Student Union URL
    suurlw VARCHAR(500)  -- Welsh Student Union URL
);

COMMENT ON TABLE institution IS 'Institution table - describes the reporting institution';
COMMENT ON COLUMN institution.pubukprn IS 'Published UK Provider Reference Number';
COMMENT ON COLUMN institution.ukprn IS 'UK Provider Reference Number';

CREATE INDEX idx_institution_ukprn ON institution(ukprn);

-- KIS Course entity
-- Records details of KIS courses (main course table)
CREATE TABLE kiscourse (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    title VARCHAR(500),
    titlew VARCHAR(500),  -- Welsh translation
    assurl VARCHAR(500),  -- Assessment URL
    assurlw VARCHAR(500),  -- Welsh Assessment URL
    crsecsturl VARCHAR(500),  -- Course student URL
    crsecsturlw VARCHAR(500),  -- Welsh Course student URL
    crseurl VARCHAR(500),  -- Course URL
    crseurlw VARCHAR(500),  -- Welsh Course URL
    distance VARCHAR(1),  -- Distance learning indicator
    employurl VARCHAR(500),  -- Employment URL
    employurlw VARCHAR(500),  -- Welsh Employment URL
    foundation VARCHAR(1),  -- Foundation year indicator
    honours VARCHAR(1),  -- Honours indicator
    hecos VARCHAR(10),  -- HECOS code (can repeat up to 5 times)
    hecos2 VARCHAR(10),
    hecos3 VARCHAR(10),
    hecos4 VARCHAR(10),
    hecos5 VARCHAR(10),
    locchnge VARCHAR(1),  -- Location change indicator
    lturl VARCHAR(500),  -- Learning and teaching URL
    lturlw VARCHAR(500),  -- Welsh Learning and teaching URL
    nhs VARCHAR(1),  -- NHS indicator
    numstage INTEGER,  -- Number of stages
    sandwich VARCHAR(1),  -- Sandwich course indicator
    supporturl VARCHAR(500),  -- Support URL
    supporturlw VARCHAR(500),  -- Welsh Support URL
    ucasprogid VARCHAR(50),  -- UCAS Programme ID
    ukprnapply VARCHAR(10),  -- UKPRN for application
    yearabroad VARCHAR(1),  -- Year abroad indicator
    kisaimcode VARCHAR(10),  -- KIS Aim code
    kislevel VARCHAR(2),  -- KIS Level
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE kiscourse IS 'KIS Course entity - records details of KIS courses';
COMMENT ON COLUMN kiscourse.kiscourseid IS 'KIS Course identifier';
COMMENT ON COLUMN kiscourse.kismode IS 'KIS Mode (01=Full-time, 02=Part-time, etc.)';
COMMENT ON COLUMN kiscourse.hecos IS 'HECOS subject code (first of up to 5)';

CREATE INDEX idx_kiscourse_ukprn ON kiscourse(ukprn);
CREATE INDEX idx_kiscourse_pubukprn ON kiscourse(pubukprn);
CREATE INDEX idx_kiscourse_kisaimcode ON kiscourse(kisaimcode);

-- Foreign key to institution
ALTER TABLE kiscourse 
    ADD CONSTRAINT fk_kiscourse_institution 
    FOREIGN KEY (pubukprn) REFERENCES institution(pubukprn) ON DELETE CASCADE;

-- Foreign key to kis_aim
ALTER TABLE kiscourse 
    ADD CONSTRAINT fk_kiscourse_kisaim 
    FOREIGN KEY (kisaimcode) REFERENCES kis_aim(kisaimcode) ON DELETE SET NULL;

-- ============================================
-- COURSE-RELATED ENTITIES
-- ============================================

-- Accreditation entity
-- Contains information about course accreditation
CREATE TABLE accreditation (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    acctype VARCHAR(10) NOT NULL,
    accdepend VARCHAR(1),  -- Accreditation dependency indicator
    accdependurl VARCHAR(500),
    accdependurlw VARCHAR(500),  -- Welsh translation
    PRIMARY KEY (pubukprn, kiscourseid, kismode, acctype)
);

COMMENT ON TABLE accreditation IS 'Accreditation entity - information about course accreditation';
COMMENT ON COLUMN accreditation.acctype IS 'Accreditation type code';

CREATE INDEX idx_accreditation_course ON accreditation(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_accreditation_acctype ON accreditation(acctype);

-- Foreign keys
ALTER TABLE accreditation 
    ADD CONSTRAINT fk_accreditation_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) 
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

ALTER TABLE accreditation 
    ADD CONSTRAINT fk_accreditation_table 
    FOREIGN KEY (acctype) REFERENCES accreditation_table(acctype) ON DELETE RESTRICT;

-- Course Location entity
-- Contains details of the KIS course location
CREATE TABLE courselocation (
    courselocation_id SERIAL PRIMARY KEY,
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    locid VARCHAR(20),  -- May be null
    UNIQUE (pubukprn, kiscourseid, kismode, locid)
);

COMMENT ON TABLE courselocation IS 'Course location entity - details of KIS course location';
COMMENT ON COLUMN courselocation.courselocation_id IS 'Surrogate primary key';
COMMENT ON COLUMN courselocation.locid IS 'Location identifier (may be null)';

CREATE INDEX idx_courselocation_course ON courselocation(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_courselocation_loc ON courselocation(ukprn, locid);

-- Foreign keys
ALTER TABLE courselocation 
    ADD CONSTRAINT fk_courselocation_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) 
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

ALTER TABLE courselocation 
    ADD CONSTRAINT fk_courselocation_location 
    FOREIGN KEY (ukprn, locid) REFERENCES location(ukprn, locid) ON DELETE SET NULL;

-- UCAS Course ID entity
-- Contains UCAS course identifiers for each COURSELOCATION
CREATE TABLE ucascourseid (
    ucascourseid_id SERIAL PRIMARY KEY,
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    locid VARCHAR(20),  -- May be null
    ucascourseid VARCHAR(50) NOT NULL,
    UNIQUE (pubukprn, kiscourseid, kismode, locid, ucascourseid)
);

COMMENT ON TABLE ucascourseid IS 'UCAS Course ID entity - UCAS course identifiers for each COURSELOCATION';
COMMENT ON COLUMN ucascourseid.ucascourseid_id IS 'Surrogate primary key';

CREATE INDEX idx_ucascourseid_courselocation ON ucascourseid(pubukprn, kiscourseid, kismode, locid);
CREATE INDEX idx_ucascourseid_ucas ON ucascourseid(ucascourseid);

-- Foreign key (using the unique constraint columns)
ALTER TABLE ucascourseid 
    ADD CONSTRAINT fk_ucascourseid_courselocation 
    FOREIGN KEY (pubukprn, kiscourseid, kismode, locid) 
    REFERENCES courselocation(pubukprn, kiscourseid, kismode, locid) ON DELETE CASCADE;

-- Subject entity (SBJ)
-- Contains CAH level subject codes for each KISCourse
CREATE TABLE sbj (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    sbj VARCHAR(50) NOT NULL,  -- CAH subject code
    PRIMARY KEY (pubukprn, kiscourseid, kismode, sbj)
);

COMMENT ON TABLE sbj IS 'Subject entity - CAH level subject codes for each KISCourse';
COMMENT ON COLUMN sbj.sbj IS 'CAH (Common Aggregation Hierarchy) subject code';

CREATE INDEX idx_sbj_course ON sbj(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_sbj_code ON sbj(sbj);

-- Foreign key
ALTER TABLE sbj 
    ADD CONSTRAINT fk_sbj_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) 
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- ============================================
-- STUDENT OUTCOMES ENTITIES
-- ============================================

-- Entry qualifications entity
-- Contains information relating to the entry qualifications of students
CREATE TABLE entry (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    entunavailreason VARCHAR(1),  -- Unavailability reason code
    entpop INTEGER,  -- Population
    entagg VARCHAR(1),  -- Aggregation indicator
    entaggyear VARCHAR(10),  -- Aggregation year
    entyear1 VARCHAR(10),  -- Year 1
    entyear2 VARCHAR(10),  -- Year 2
    entsbj VARCHAR(50),  -- Subject code
    access INTEGER,  -- Access qualifications count
    alevel INTEGER,  -- A-Level qualifications count
    bacc INTEGER,  -- Baccalaureate count
    degree INTEGER,  -- Degree count
    foundtn INTEGER,  -- Foundation count
    noquals INTEGER,  -- No qualifications count
    other INTEGER,  -- Other qualifications count
    otherhe INTEGER,  -- Other HE qualifications count
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE entry IS 'Entry qualifications entity - entry qualifications of students';

CREATE INDEX idx_entry_course ON entry(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_entry_sbj ON entry(entsbj);

-- Foreign key
ALTER TABLE entry 
    ADD CONSTRAINT fk_entry_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) 
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- Tariff entity
-- Contains information relating to the entry tariff points of students
CREATE TABLE tariff (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    tarunavailreason VARCHAR(1),  -- Unavailability reason code
    tarpop INTEGER,  -- Population
    taragg VARCHAR(1),  -- Aggregation indicator
    taraggyear VARCHAR(10),  -- Aggregation year
    taryear1 VARCHAR(10),  -- Year 1
    taryear2 VARCHAR(10),  -- Year 2
    tarsbj VARCHAR(50),  -- Subject code
    t001 INTEGER,  -- Tariff points 0-16
    t048 INTEGER,  -- Tariff points 48
    t064 INTEGER,  -- Tariff points 64
    t080 INTEGER,  -- Tariff points 80
    t096 INTEGER,  -- Tariff points 96
    t112 INTEGER,  -- Tariff points 112
    t128 INTEGER,  -- Tariff points 128
    t144 INTEGER,  -- Tariff points 144
    t160 INTEGER,  -- Tariff points 160
    t176 INTEGER,  -- Tariff points 176
    t192 INTEGER,  -- Tariff points 192
    t208 INTEGER,  -- Tariff points 208
    t224 INTEGER,  -- Tariff points 224
    t240 INTEGER,  -- Tariff points 240+
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE tariff IS 'Tariff entity - entry tariff points of students';
COMMENT ON COLUMN tariff.t001 IS 'Number of students with 0-16 tariff points';
COMMENT ON COLUMN tariff.t240 IS 'Number of students with 240+ tariff points';

CREATE INDEX idx_tariff_course ON tariff(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_tariff_sbj ON tariff(tarsbj);

-- Foreign key
ALTER TABLE tariff 
    ADD CONSTRAINT fk_tariff_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) 
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- Continuation entity
-- Contains continuation information for students on the course
CREATE TABLE continuation (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    contunavailreason VARCHAR(1),  -- Unavailability reason code
    contpop INTEGER,  -- Population
    contagg VARCHAR(1),  -- Aggregation indicator
    contaggyear VARCHAR(10),  -- Aggregation year
    contyear1 VARCHAR(10),  -- Year 1
    contyear2 VARCHAR(10),  -- Year 2
    contsbj VARCHAR(50),  -- Subject code
    ucont INTEGER,  -- Continued count
    udormant INTEGER,  -- Dormant count
    ugained INTEGER,  -- Gained count
    uleft INTEGER,  -- Left count
    ulower INTEGER,  -- Lower level count
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE continuation IS 'Continuation entity - continuation information for students';

CREATE INDEX idx_continuation_course ON continuation(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_continuation_sbj ON continuation(contsbj);

-- Foreign key
ALTER TABLE continuation 
    ADD CONSTRAINT fk_continuation_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) 
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- ============================================
-- EMPLOYMENT & SALARY ENTITIES
-- ============================================

-- Employment statistics entity
-- Contains information relating to student employment outcomes
CREATE TABLE employment (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    empunavailreason VARCHAR(1),  -- Unavailability reason code
    emppop INTEGER,  -- Population
    empresponse INTEGER,  -- Response count
    empsample INTEGER,  -- Sample size
    empresp_rate INTEGER,  -- Response rate percentage
    empagg VARCHAR(1),  -- Aggregation indicator
    empaggyear VARCHAR(10),  -- Aggregation year
    empyear1 VARCHAR(10),  -- Year 1
    empyear2 VARCHAR(10),  -- Year 2
    empsbj VARCHAR(50),  -- Subject code
    workstudy INTEGER,  -- Working and studying count
    study INTEGER,  -- Studying count
    unemp INTEGER,  -- Unemployed count
    prevworkstud INTEGER,  -- Previously working/studying count
    both INTEGER,  -- Both working and studying count
    noavail INTEGER,  -- Not available count
    work INTEGER,  -- Working count
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE employment IS 'Employment statistics entity - student employment outcomes';

CREATE INDEX idx_employment_course ON employment(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_employment_sbj ON employment(empsbj);

-- Foreign key
ALTER TABLE employment 
    ADD CONSTRAINT fk_employment_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) 
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- Job type entity
-- Contains information relating to the types of profession entered by students
CREATE TABLE jobtype (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    jobunavailreason VARCHAR(1),  -- Unavailability reason code
    jobpop INTEGER,  -- Population
    jobresponse INTEGER,  -- Response count
    jobsample INTEGER,  -- Sample size
    jobresp_rate INTEGER,  -- Response rate percentage
    jobagg VARCHAR(1),  -- Aggregation indicator
    jobaggyear VARCHAR(10),  -- Aggregation year
    jobyear1 VARCHAR(10),  -- Year 1
    jobyear2 VARCHAR(10),  -- Year 2
    jobsbj VARCHAR(50),  -- Subject code
    profman INTEGER,  -- Professional/Managerial count
    otherjob INTEGER,  -- Other job count
    unkwn INTEGER,  -- Unknown count
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE jobtype IS 'Job type entity - types of profession entered by students';

CREATE INDEX idx_jobtype_course ON jobtype(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_jobtype_sbj ON jobtype(jobsbj);

-- Foreign key
ALTER TABLE jobtype 
    ADD CONSTRAINT fk_jobtype_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) 
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- Common job types entity
-- Contains information relating to common job types obtained by students
CREATE TABLE common (
    common_id SERIAL PRIMARY KEY,
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    comunavailreason VARCHAR(1),  -- Unavailability reason code
    compop INTEGER,  -- Population
    comresponse INTEGER,  -- Response count
    comsample INTEGER,  -- Sample size
    compesp_rate INTEGER,  -- Response rate percentage
    comagg VARCHAR(1),  -- Aggregation indicator
    comaggyear VARCHAR(10),  -- Aggregation year
    comyear1 VARCHAR(10),  -- Year 1
    comyear2 VARCHAR(10),  -- Year 2
    comsbj VARCHAR(50),  -- Subject code (may be null)
    UNIQUE (pubukprn, kiscourseid, kismode, comsbj)
);

COMMENT ON TABLE common IS 'Common job types entity - common job types obtained by students';
COMMENT ON COLUMN common.common_id IS 'Surrogate primary key';
COMMENT ON COLUMN common.comsbj IS 'Subject code (may be null)';

CREATE INDEX idx_common_course ON common(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_common_sbj ON common(comsbj);

-- Foreign key
ALTER TABLE common 
    ADD CONSTRAINT fk_common_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) 
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- Job list entity
-- Contains information about common job types obtained by students
CREATE TABLE joblist (
    joblist_id SERIAL PRIMARY KEY,
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    comsbj VARCHAR(50),  -- Subject code (may be null)
    job VARCHAR(500),  -- Job title
    perc INTEGER,  -- Percentage
    "order" INTEGER,  -- Order (order is a reserved word, so quoted)
    hs INTEGER,  -- High skill indicator
    UNIQUE (pubukprn, kiscourseid, kismode, comsbj, job)
);

COMMENT ON TABLE joblist IS 'Job list entity - common job types obtained by students';
COMMENT ON COLUMN joblist.joblist_id IS 'Surrogate primary key';
COMMENT ON COLUMN joblist.comsbj IS 'Subject code (may be null)';
COMMENT ON COLUMN joblist."order" IS 'Display order';

CREATE INDEX idx_joblist_common ON joblist(pubukprn, kiscourseid, kismode, comsbj);
CREATE INDEX idx_joblist_sbj ON joblist(comsbj);

-- Foreign key (using the unique constraint columns)
ALTER TABLE joblist 
    ADD CONSTRAINT fk_joblist_common 
    FOREIGN KEY (pubukprn, kiscourseid, kismode, comsbj) 
    REFERENCES common(pubukprn, kiscourseid, kismode, comsbj) ON DELETE CASCADE;

-- Salary entity (GO Salary)
-- Contains salary information of graduates
CREATE TABLE gosalary (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    gosalunavailreason VARCHAR(1),  -- Unavailability reason code
    gosalpop INTEGER,  -- Population
    gosalresponse INTEGER,  -- Response count
    gosalsample INTEGER,  -- Sample size
    gosalresp_rate INTEGER,  -- Response rate percentage
    gosalagg VARCHAR(1),  -- Aggregation indicator
    gosalaggyear VARCHAR(10),  -- Aggregation year
    gosalyear1 VARCHAR(10),  -- Year 1
    gosalyear2 VARCHAR(10),  -- Year 2
    gosalsbj VARCHAR(50),  -- Subject code
    goinstlq INTEGER,  -- Institution Lower Quartile salary
    goinstmed INTEGER,  -- Institution Median salary
    goinstuq INTEGER,  -- Institution Upper Quartile salary
    goprov_pc_uk INTEGER,  -- Provider percentage UK
    goprov_pc_e INTEGER,  -- Provider percentage England
    goprov_pc_ni INTEGER,  -- Provider percentage Northern Ireland
    goprov_pc_s INTEGER,  -- Provider percentage Scotland
    goprov_pc_w INTEGER,  -- Provider percentage Wales
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE gosalary IS 'Salary entity - salary information of graduates';
COMMENT ON COLUMN gosalary.goinstlq IS 'Institution Lower Quartile salary (£)';
COMMENT ON COLUMN gosalary.goinstmed IS 'Institution Median salary (£)';
COMMENT ON COLUMN gosalary.goinstuq IS 'Institution Upper Quartile salary (£)';

CREATE INDEX idx_gosalary_course ON gosalary(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_gosalary_sbj ON gosalary(gosalsbj);

-- Foreign key
ALTER TABLE gosalary 
    ADD CONSTRAINT fk_gosalary_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) 
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- Sector salary entity (GO Sector Salary)
-- Contains sector salary data
CREATE TABLE gosecsal (
    gosecsbj VARCHAR(50) NOT NULL,  -- Sector subject code
    kismode VARCHAR(2) NOT NULL,
    kislevel VARCHAR(2) NOT NULL,
    goseclq_uk INTEGER,  -- Lower Quartile UK
    gosecmed_uk INTEGER,  -- Median UK
    gosecuq_uk INTEGER,  -- Upper Quartile UK
    gosecpop_uk INTEGER,  -- Population UK
    goseclq_e INTEGER,  -- Lower Quartile England
    gosecmed_e INTEGER,  -- Median England
    gosecuq_e INTEGER,  -- Upper Quartile England
    gosecpop_e INTEGER,  -- Population England
    goseclq_ni INTEGER,  -- Lower Quartile Northern Ireland
    gosecmed_ni INTEGER,  -- Median Northern Ireland
    gosecuq_ni INTEGER,  -- Upper Quartile Northern Ireland
    gosecpop_ni INTEGER,  -- Population Northern Ireland
    goseclq_s INTEGER,  -- Lower Quartile Scotland
    gosecmed_s INTEGER,  -- Median Scotland
    gosecuq_s INTEGER,  -- Upper Quartile Scotland
    gosecpop_s INTEGER,  -- Population Scotland
    goseclq_w INTEGER,  -- Lower Quartile Wales
    gosecmed_w INTEGER,  -- Median Wales
    gosecuq_w INTEGER,  -- Upper Quartile Wales
    gosecpop_w INTEGER,  -- Population Wales
    PRIMARY KEY (gosecsbj, kismode, kislevel)
);

COMMENT ON TABLE gosecsal IS 'Sector salary entity - sector salary data';
COMMENT ON COLUMN gosecsal.gosecsbj IS 'Sector subject code (CAH code)';
COMMENT ON COLUMN gosecsal.kislevel IS 'KIS Level (e.g., 03=Undergraduate, 04=Postgraduate)';

CREATE INDEX idx_gosecsal_sbj ON gosecsal(gosecsbj);
CREATE INDEX idx_gosecsal_mode_level ON gosecsal(kismode, kislevel);

-- Graduate voice entity
-- Contains information on graduate voice in relation to work
CREATE TABLE govoicework (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    goworkunavailreason VARCHAR(1),  -- Unavailability reason code
    goworkpop INTEGER,  -- Population
    goworkresponse INTEGER,  -- Response count
    goworksample INTEGER,  -- Sample size
    goworkresp_rate INTEGER,  -- Response rate percentage
    goworkagg VARCHAR(1),  -- Aggregation indicator
    goworkaggyear VARCHAR(10),  -- Aggregation year
    goworkyear1 VARCHAR(10),  -- Year 1
    goworkyear2 VARCHAR(10),  -- Year 2
    goworksbj VARCHAR(50),  -- Subject code
    goworkmean INTEGER,  -- Mean score
    goworkontrack INTEGER,  -- On track score
    goworkskills INTEGER,  -- Skills score
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE govoicework IS 'Graduate voice entity - graduate voice in relation to work';
COMMENT ON COLUMN govoicework.goworkmean IS 'Mean score (0-100)';
COMMENT ON COLUMN govoicework.goworkontrack IS 'On track score (0-100)';
COMMENT ON COLUMN govoicework.goworkskills IS 'Skills score (0-100)';

CREATE INDEX idx_govoicework_course ON govoicework(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_govoicework_sbj ON govoicework(goworksbj);

-- Foreign key
ALTER TABLE govoicework 
    ADD CONSTRAINT fk_govoicework_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) 
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- ============================================
-- LEO (LONGITUDINAL EDUCATION OUTCOMES) ENTITIES
-- ============================================

-- LEO3 entity
-- Contains Longitudinal Education Outcomes earnings data - 3 year timepoint
CREATE TABLE leo3 (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    leo3unavailreason VARCHAR(1),  -- Unavailability reason code
    leo3pop INTEGER,  -- Population
    leo3agg VARCHAR(1),  -- Aggregation indicator
    leo3aggyear VARCHAR(10),  -- Aggregation year
    leo3sbj VARCHAR(50),  -- Subject code
    leo3instlq INTEGER,  -- Institution Lower Quartile earnings
    leo3instmed INTEGER,  -- Institution Median earnings
    leo3instuq INTEGER,  -- Institution Upper Quartile earnings
    leo3prov_pc_uk INTEGER,  -- Provider percentage UK
    leo3prov_pc_e INTEGER,  -- Provider percentage England
    leo3prov_pc_nw INTEGER,  -- Provider percentage North West
    leo3prov_pc_ne INTEGER,  -- Provider percentage North East
    leo3prov_pc_em INTEGER,  -- Provider percentage East Midlands
    leo3prov_pc_wm INTEGER,  -- Provider percentage West Midlands
    leo3prov_pc_ee INTEGER,  -- Provider percentage East of England
    leo3prov_pc_se INTEGER,  -- Provider percentage South East
    leo3prov_pc_sw INTEGER,  -- Provider percentage South West
    leo3prov_pc_yh INTEGER,  -- Provider percentage Yorkshire and Humber
    leo3prov_pc_ln INTEGER,  -- Provider percentage London
    leo3prov_pc_ni INTEGER,  -- Provider percentage Northern Ireland
    leo3prov_pc_s INTEGER,  -- Provider percentage Scotland
    leo3prov_pc_ed INTEGER,  -- Provider percentage Edinburgh
    leo3prov_pc_gl INTEGER,  -- Provider percentage Glasgow
    leo3prov_pc_w INTEGER,  -- Provider percentage Wales
    leo3prov_pc_cf INTEGER,  -- Provider percentage Cardiff
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE leo3 IS 'LEO3 entity - Longitudinal Education Outcomes earnings data at 3 year timepoint';
COMMENT ON COLUMN leo3.leo3instlq IS 'Institution Lower Quartile earnings (£)';
COMMENT ON COLUMN leo3.leo3instmed IS 'Institution Median earnings (£)';
COMMENT ON COLUMN leo3.leo3instuq IS 'Institution Upper Quartile earnings (£)';

CREATE INDEX idx_leo3_course ON leo3(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_leo3_sbj ON leo3(leo3sbj);

-- Foreign key
ALTER TABLE leo3 
    ADD CONSTRAINT fk_leo3_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) 
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- LEO3 sector entity
-- Contains sector Longitudinal Education Outcomes earnings data - 3 year timepoint
CREATE TABLE leo3sec (
    leo3secsbj VARCHAR(50) NOT NULL,  -- Sector subject code
    kismode VARCHAR(2) NOT NULL,
    kislevel VARCHAR(2) NOT NULL,
    leo3secpop_uk INTEGER,  -- Population UK
    leo3lq_uk INTEGER,  -- Lower Quartile UK
    leo3med_uk INTEGER,  -- Median UK
    leo3uq_uk INTEGER,  -- Upper Quartile UK
    leo3secpop_e INTEGER,  -- Population England
    leo3lq_e INTEGER,  -- Lower Quartile England
    leo3med_e INTEGER,  -- Median England
    leo3uq_e INTEGER,  -- Upper Quartile England
    leo3secpop_nw INTEGER,  -- Population North West
    leo3lq_nw INTEGER,  -- Lower Quartile North West
    leo3med_nw INTEGER,  -- Median North West
    leo3uq_nw INTEGER,  -- Upper Quartile North West
    leo3secpop_ne INTEGER,  -- Population North East
    leo3lq_ne INTEGER,  -- Lower Quartile North East
    leo3med_ne INTEGER,  -- Median North East
    leo3uq_ne INTEGER,  -- Upper Quartile North East
    leo3secpop_em INTEGER,  -- Population East Midlands
    leo3lq_em INTEGER,  -- Lower Quartile East Midlands
    leo3med_em INTEGER,  -- Median East Midlands
    leo3uq_em INTEGER,  -- Upper Quartile East Midlands
    leo3secpop_wm INTEGER,  -- Population West Midlands
    leo3lq_wm INTEGER,  -- Lower Quartile West Midlands
    leo3med_wm INTEGER,  -- Median West Midlands
    leo3uq_wm INTEGER,  -- Upper Quartile West Midlands
    leo3secpop_ee INTEGER,  -- Population East of England
    leo3lq_ee INTEGER,  -- Lower Quartile East of England
    leo3med_ee INTEGER,  -- Median East of England
    leo3uq_ee INTEGER,  -- Upper Quartile East of England
    leo3secpop_se INTEGER,  -- Population South East
    leo3lq_se INTEGER,  -- Lower Quartile South East
    leo3med_se INTEGER,  -- Median South East
    leo3uq_se INTEGER,  -- Upper Quartile South East
    leo3secpop_sw INTEGER,  -- Population South West
    leo3lq_sw INTEGER,  -- Lower Quartile South West
    leo3med_sw INTEGER,  -- Median South West
    leo3uq_sw INTEGER,  -- Upper Quartile South West
    leo3secpop_yh INTEGER,  -- Population Yorkshire and Humber
    leo3lq_yh INTEGER,  -- Lower Quartile Yorkshire and Humber
    leo3med_yh INTEGER,  -- Median Yorkshire and Humber
    leo3uq_yh INTEGER,  -- Upper Quartile Yorkshire and Humber
    leo3secpop_ln INTEGER,  -- Population London
    leo3lq_ln INTEGER,  -- Lower Quartile London
    leo3med_ln INTEGER,  -- Median London
    leo3uq_ln INTEGER,  -- Upper Quartile London
    leo3secpop_w INTEGER,  -- Population Wales
    leo3lq_w INTEGER,  -- Lower Quartile Wales
    leo3med_w INTEGER,  -- Median Wales
    leo3uq_w INTEGER,  -- Upper Quartile Wales
    leo3secpop_cf INTEGER,  -- Population Cardiff
    leo3lq_cf INTEGER,  -- Lower Quartile Cardiff
    leo3med_cf INTEGER,  -- Median Cardiff
    leo3uq_cf INTEGER,  -- Upper Quartile Cardiff
    leo3secpop_s INTEGER,  -- Population Scotland
    leo3lq_s INTEGER,  -- Lower Quartile Scotland
    leo3med_s INTEGER,  -- Median Scotland
    leo3uq_s INTEGER,  -- Upper Quartile Scotland
    leo3secpop_ed INTEGER,  -- Population Edinburgh
    leo3lq_ed INTEGER,  -- Lower Quartile Edinburgh
    leo3med_ed INTEGER,  -- Median Edinburgh
    leo3uq_ed INTEGER,  -- Upper Quartile Edinburgh
    leo3secpop_gl INTEGER,  -- Population Glasgow
    leo3lq_gl INTEGER,  -- Lower Quartile Glasgow
    leo3med_gl INTEGER,  -- Median Glasgow
    leo3uq_gl INTEGER,  -- Upper Quartile Glasgow
    PRIMARY KEY (leo3secsbj, kismode, kislevel)
);

COMMENT ON TABLE leo3sec IS 'LEO3 sector entity - sector Longitudinal Education Outcomes earnings data at 3 year timepoint';
COMMENT ON COLUMN leo3sec.leo3secsbj IS 'Sector subject code (CAH code)';

CREATE INDEX idx_leo3sec_sbj ON leo3sec(leo3secsbj);
CREATE INDEX idx_leo3sec_mode_level ON leo3sec(kismode, kislevel);

-- LEO5 entity
-- Contains Longitudinal Education Outcomes earnings data - 5 year timepoint
CREATE TABLE leo5 (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    leo5unavailreason VARCHAR(1),  -- Unavailability reason code
    leo5pop INTEGER,  -- Population
    leo5agg VARCHAR(1),  -- Aggregation indicator
    leo5aggyear VARCHAR(10),  -- Aggregation year
    leo5sbj VARCHAR(50),  -- Subject code
    leo5instlq INTEGER,  -- Institution Lower Quartile earnings
    leo5instmed INTEGER,  -- Institution Median earnings
    leo5instuq INTEGER,  -- Institution Upper Quartile earnings
    leo5prov_pc_uk INTEGER,  -- Provider percentage UK
    leo5prov_pc_e INTEGER,  -- Provider percentage England
    leo5prov_pc_nw INTEGER,  -- Provider percentage North West
    leo5prov_pc_ne INTEGER,  -- Provider percentage North East
    leo5prov_pc_em INTEGER,  -- Provider percentage East Midlands
    leo5prov_pc_wm INTEGER,  -- Provider percentage West Midlands
    leo5prov_pc_ee INTEGER,  -- Provider percentage East of England
    leo5prov_pc_se INTEGER,  -- Provider percentage South East
    leo5prov_pc_sw INTEGER,  -- Provider percentage South West
    leo5prov_pc_yh INTEGER,  -- Provider percentage Yorkshire and Humber
    leo5prov_pc_ln INTEGER,  -- Provider percentage London
    leo5prov_pc_ni INTEGER,  -- Provider percentage Northern Ireland
    leo5prov_pc_s INTEGER,  -- Provider percentage Scotland
    leo5prov_pc_ed INTEGER,  -- Provider percentage Edinburgh
    leo5prov_pc_gl INTEGER,  -- Provider percentage Glasgow
    leo5prov_pc_w INTEGER,  -- Provider percentage Wales
    leo5prov_pc_cf INTEGER,  -- Provider percentage Cardiff
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE leo5 IS 'LEO5 entity - Longitudinal Education Outcomes earnings data at 5 year timepoint';
COMMENT ON COLUMN leo5.leo5instlq IS 'Institution Lower Quartile earnings (£)';
COMMENT ON COLUMN leo5.leo5instmed IS 'Institution Median earnings (£)';
COMMENT ON COLUMN leo5.leo5instuq IS 'Institution Upper Quartile earnings (£)';

CREATE INDEX idx_leo5_course ON leo5(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_leo5_sbj ON leo5(leo5sbj);

-- Foreign key
ALTER TABLE leo5 
    ADD CONSTRAINT fk_leo5_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) 
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- LEO5 sector entity
-- Contains sector Longitudinal Education Outcomes earnings data - 5 year timepoint
CREATE TABLE leo5sec (
    leo5secsbj VARCHAR(50) NOT NULL,  -- Sector subject code
    kismode VARCHAR(2) NOT NULL,
    kislevel VARCHAR(2) NOT NULL,
    leo5secpop_uk INTEGER,  -- Population UK
    leo5lq_uk INTEGER,  -- Lower Quartile UK
    leo5med_uk INTEGER,  -- Median UK
    leo5uq_uk INTEGER,  -- Upper Quartile UK
    leo5secpop_e INTEGER,  -- Population England
    leo5lq_e INTEGER,  -- Lower Quartile England
    leo5med_e INTEGER,  -- Median England
    leo5uq_e INTEGER,  -- Upper Quartile England
    leo5secpop_nw INTEGER,  -- Population North West
    leo5lq_nw INTEGER,  -- Lower Quartile North West
    leo5med_nw INTEGER,  -- Median North West
    leo5uq_nw INTEGER,  -- Upper Quartile North West
    leo5secpop_ne INTEGER,  -- Population North East
    leo5lq_ne INTEGER,  -- Lower Quartile North East
    leo5med_ne INTEGER,  -- Median North East
    leo5uq_ne INTEGER,  -- Upper Quartile North East
    leo5secpop_em INTEGER,  -- Population East Midlands
    leo5lq_em INTEGER,  -- Lower Quartile East Midlands
    leo5med_em INTEGER,  -- Median East Midlands
    leo5uq_em INTEGER,  -- Upper Quartile East Midlands
    leo5secpop_wm INTEGER,  -- Population West Midlands
    leo5lq_wm INTEGER,  -- Lower Quartile West Midlands
    leo5med_wm INTEGER,  -- Median West Midlands
    leo5uq_wm INTEGER,  -- Upper Quartile West Midlands
    leo5secpop_ee INTEGER,  -- Population East of England
    leo5lq_ee INTEGER,  -- Lower Quartile East of England
    leo5med_ee INTEGER,  -- Median East of England
    leo5uq_ee INTEGER,  -- Upper Quartile East of England
    leo5secpop_se INTEGER,  -- Population South East
    leo5lq_se INTEGER,  -- Lower Quartile South East
    leo5med_se INTEGER,  -- Median South East
    leo5uq_se INTEGER,  -- Upper Quartile South East
    leo5secpop_sw INTEGER,  -- Population South West
    leo5lq_sw INTEGER,  -- Lower Quartile South West
    leo5med_sw INTEGER,  -- Median South West
    leo5uq_sw INTEGER,  -- Upper Quartile South West
    leo5secpop_yh INTEGER,  -- Population Yorkshire and Humber
    leo5lq_yh INTEGER,  -- Lower Quartile Yorkshire and Humber
    leo5med_yh INTEGER,  -- Median Yorkshire and Humber
    leo5uq_yh INTEGER,  -- Upper Quartile Yorkshire and Humber
    leo5secpop_ln INTEGER,  -- Population London
    leo5lq_ln INTEGER,  -- Lower Quartile London
    leo5med_ln INTEGER,  -- Median London
    leo5uq_ln INTEGER,  -- Upper Quartile London
    leo5secpop_w INTEGER,  -- Population Wales
    leo5lq_w INTEGER,  -- Lower Quartile Wales
    leo5med_w INTEGER,  -- Median Wales
    leo5uq_w INTEGER,  -- Upper Quartile Wales
    leo5secpop_cf INTEGER,  -- Population Cardiff
    leo5lq_cf INTEGER,  -- Lower Quartile Cardiff
    leo5med_cf INTEGER,  -- Median Cardiff
    leo5uq_cf INTEGER,  -- Upper Quartile Cardiff
    leo5secpop_s INTEGER,  -- Population Scotland
    leo5lq_s INTEGER,  -- Lower Quartile Scotland
    leo5med_s INTEGER,  -- Median Scotland
    leo5uq_s INTEGER,  -- Upper Quartile Scotland
    leo5secpop_ed INTEGER,  -- Population Edinburgh
    leo5lq_ed INTEGER,  -- Lower Quartile Edinburgh
    leo5med_ed INTEGER,  -- Median Edinburgh
    leo5uq_ed INTEGER,  -- Upper Quartile Edinburgh
    leo5secpop_gl INTEGER,  -- Population Glasgow
    leo5lq_gl INTEGER,  -- Lower Quartile Glasgow
    leo5med_gl INTEGER,  -- Median Glasgow
    leo5uq_gl INTEGER,  -- Upper Quartile Glasgow
    PRIMARY KEY (leo5secsbj, kismode, kislevel)
);

COMMENT ON TABLE leo5sec IS 'LEO5 sector entity - sector Longitudinal Education Outcomes earnings data at 5 year timepoint';
COMMENT ON COLUMN leo5sec.leo5secsbj IS 'Sector subject code (CAH code)';

CREATE INDEX idx_leo5sec_sbj ON leo5sec(leo5secsbj);
CREATE INDEX idx_leo5sec_mode_level ON leo5sec(kismode, kislevel);

-- ============================================
-- NSS (NATIONAL STUDENT SURVEY) ENTITIES
-- ============================================

-- NSS entity
-- Contains the National Student Survey (NSS) results
CREATE TABLE nss (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    nssunavailreason VARCHAR(1),  -- Unavailability reason code
    nsspop INTEGER,  -- Population
    nssresp_rate INTEGER,  -- Response rate percentage
    nssagg VARCHAR(1),  -- Aggregation indicator
    nssaggyear VARCHAR(10),  -- Aggregation year
    nssyear1 VARCHAR(10),  -- Year 1
    nssyear2 VARCHAR(10),  -- Year 2
    nsssbj VARCHAR(50),  -- Subject code
    q1 INTEGER,  -- Question 1 score (0-100)
    q2 INTEGER,  -- Question 2 score (0-100)
    q3 INTEGER,  -- Question 3 score (0-100)
    q4 INTEGER,  -- Question 4 score (0-100)
    q5 INTEGER,  -- Question 5 score (0-100)
    q6 INTEGER,  -- Question 6 score (0-100)
    q7 INTEGER,  -- Question 7 score (0-100)
    q8 INTEGER,  -- Question 8 score (0-100)
    q9 INTEGER,  -- Question 9 score (0-100)
    q10 INTEGER,  -- Question 10 score (0-100)
    q11 INTEGER,  -- Question 11 score (0-100)
    q12 INTEGER,  -- Question 12 score (0-100)
    q13 INTEGER,  -- Question 13 score (0-100)
    q14 INTEGER,  -- Question 14 score (0-100)
    q15 INTEGER,  -- Question 15 score (0-100)
    q16 INTEGER,  -- Question 16 score (0-100)
    q17 INTEGER,  -- Question 17 score (0-100)
    q18 INTEGER,  -- Question 18 score (0-100)
    q19 INTEGER,  -- Question 19 score (0-100)
    q20 INTEGER,  -- Question 20 score (0-100)
    q21 INTEGER,  -- Question 21 score (0-100)
    q22 INTEGER,  -- Question 22 score (0-100)
    q23 INTEGER,  -- Question 23 score (0-100)
    q24 INTEGER,  -- Question 24 score (0-100)
    q25 INTEGER,  -- Question 25 score (0-100)
    q26 INTEGER,  -- Question 26 score (0-100)
    t1 INTEGER,  -- Theme 1 score (0-100)
    t2 INTEGER,  -- Theme 2 score (0-100)
    t3 INTEGER,  -- Theme 3 score (0-100)
    t4 INTEGER,  -- Theme 4 score (0-100)
    t5 INTEGER,  -- Theme 5 score (0-100)
    t6 INTEGER,  -- Theme 6 score (0-100)
    t7 INTEGER,  -- Theme 7 score (0-100)
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE nss IS 'NSS entity - National Student Survey (NSS) results';
COMMENT ON COLUMN nss.q1 IS 'NSS Question 1 score (0-100)';
COMMENT ON COLUMN nss.t1 IS 'NSS Theme 1 score (0-100)';

CREATE INDEX idx_nss_course ON nss(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_nss_sbj ON nss(nsssbj);

-- Foreign key
ALTER TABLE nss 
    ADD CONSTRAINT fk_nss_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) 
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- NSS Country entity
-- Contains the country specific National Student Survey (NSS) results
CREATE TABLE nsscountry (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    kiscourseid VARCHAR(50) NOT NULL,
    kismode VARCHAR(2) NOT NULL,
    nsscountryunavailreason VARCHAR(1),  -- Unavailability reason code
    nsscountrypop INTEGER,  -- Population
    nsscountryresp_rate INTEGER,  -- Response rate percentage
    nsscountryagg VARCHAR(1),  -- Aggregation indicator
    nsscountryaggyear VARCHAR(10),  -- Aggregation year
    nsscountryyear1 VARCHAR(10),  -- Year 1
    nsscountryyear2 VARCHAR(10),  -- Year 2
    nsscountrysbj VARCHAR(50),  -- Subject code
    q27 INTEGER,  -- Question 27 score (0-100) - Freedom of expression (England only)
    q28 INTEGER,  -- Question 28 score (0-100) - Mental wellbeing services
    PRIMARY KEY (pubukprn, kiscourseid, kismode)
);

COMMENT ON TABLE nsscountry IS 'NSS Country entity - country specific National Student Survey (NSS) results';
COMMENT ON COLUMN nsscountry.q27 IS 'Question 27 - Freedom of expression (England only)';
COMMENT ON COLUMN nsscountry.q28 IS 'Question 28 - Mental wellbeing services';

CREATE INDEX idx_nsscountry_course ON nsscountry(pubukprn, kiscourseid, kismode);
CREATE INDEX idx_nsscountry_sbj ON nsscountry(nsscountrysbj);

-- Foreign key
ALTER TABLE nsscountry 
    ADD CONSTRAINT fk_nsscountry_kiscourse 
    FOREIGN KEY (pubukprn, kiscourseid, kismode) 
    REFERENCES kiscourse(pubukprn, kiscourseid, kismode) ON DELETE CASCADE;

-- ============================================
-- TEF (TEACHING EXCELLENCE FRAMEWORK) ENTITY
-- ============================================

-- TEF Outcome entity
-- Contains information relating to the Teaching and Excellence Framework (TEF) ratings
CREATE TABLE tefoutcome (
    pubukprn VARCHAR(10) NOT NULL,
    ukprn VARCHAR(10) NOT NULL,
    report_ukprn VARCHAR(10) NOT NULL,
    overall_rating VARCHAR(20),  -- Overall TEF rating (Gold, Silver, Bronze, Provisional)
    student_experience_rating VARCHAR(20),  -- Student experience rating
    student_outcomes_rating VARCHAR(20),  -- Student outcomes rating
    outcome_url VARCHAR(500),  -- URL to TEF outcome details
    PRIMARY KEY (pubukprn, ukprn)
);

COMMENT ON TABLE tefoutcome IS 'TEF Outcome entity - Teaching and Excellence Framework (TEF) ratings';
COMMENT ON COLUMN tefoutcome.overall_rating IS 'Overall TEF rating: Gold, Silver, Bronze, or Provisional';
COMMENT ON COLUMN tefoutcome.student_experience_rating IS 'Student experience rating';
COMMENT ON COLUMN tefoutcome.student_outcomes_rating IS 'Student outcomes rating';

CREATE INDEX idx_tefoutcome_pubukprn ON tefoutcome(pubukprn);
CREATE INDEX idx_tefoutcome_ukprn ON tefoutcome(ukprn);
CREATE INDEX idx_tefoutcome_rating ON tefoutcome(overall_rating);

-- Foreign key
ALTER TABLE tefoutcome 
    ADD CONSTRAINT fk_tefoutcome_institution 
    FOREIGN KEY (pubukprn) REFERENCES institution(pubukprn) ON DELETE CASCADE;

-- ============================================
-- ADDITIONAL TABLE (AccreditationByHep)
-- ============================================

-- Accreditation by HEP (Higher Education Provider)
-- Additional table for accreditation information by institution
CREATE TABLE accreditation_by_hep (
    accrediting_body_name VARCHAR(500),
    accredition_type TEXT,
    hep VARCHAR(500),  -- Higher Education Provider name
    kiscourse_title VARCHAR(500),
    kiscourseid VARCHAR(50),
    PRIMARY KEY (accrediting_body_name, hep, kiscourseid)
);

COMMENT ON TABLE accreditation_by_hep IS 'Accreditation by HEP - accreditation information by institution';
COMMENT ON COLUMN accreditation_by_hep.hep IS 'Higher Education Provider name';

CREATE INDEX idx_accreditation_by_hep_kiscourseid ON accreditation_by_hep(kiscourseid);
CREATE INDEX idx_accreditation_by_hep_hep ON accreditation_by_hep(hep);

-- ============================================
-- END OF SCHEMA
-- ============================================

