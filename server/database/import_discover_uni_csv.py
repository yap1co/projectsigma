"""
Imports  HESA CSV files used by the recommendation engine
Based on HESA C25061 file structure
"""

import os
import sys
import csv
import psycopg2
from psycopg2.extras import execute_values, execute_batch
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Add parent directory to path to import database_helper
sys.path.insert(0, str(Path(__file__).parent.parent))

from database_helper import get_db_connection as get_db_connection_helper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create database connection using database_helper"""
    return get_db_connection_helper()

def normalize_value(value: str) -> Optional[str]:
    """Normalize CSV values - handle empty strings, whitespace"""
    if value is None:
        return None
    value = str(value).strip()
    return value if value else None

def normalize_int(value: str) -> Optional[int]:
    """Convert string to integer, handling empty strings"""
    if not value or value.strip() == '':
        return None
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return None

def read_csv_file(file_path: Path) -> List[Dict]:
    """Read CSV file and return list of dictionaries"""
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return []
    
    rows = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        logger.info(f"  → Read {len(rows)} rows from {file_path.name}")
    except Exception as e:
        logger.error(f"  Error reading {file_path.name}: {e}")
        return []
    
    return rows

def read_sbj_csv_file(file_path: Path) -> List[Dict]:
    """Read SBJ.csv file with proper UTF-16 encoding to handle null bytes"""
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return []
    
    rows = []
    try:
        with open(file_path, 'r', encoding='utf-16', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        logger.info(f"  → Read {len(rows)} rows from {file_path.name} (UTF-16 encoding)")
    except Exception as e:
        logger.error(f"  Error reading {file_path.name} with UTF-16: {e}")
        return []
    
    return rows

def import_core_entities(cursor, data_dir: Path):
    """Import core HESA entities (institution and course)"""
    logger.info("\n" + "="*70)
    logger.info("IMPORTING CORE HESA TABLES")
    
    logger.info("\nImporting INSTITUTION.csv...")
    rows = read_csv_file(data_dir / 'INSTITUTION.csv')
    if rows:
        raw_data = [
            (
                normalize_value(row.get('PUBUKPRN')),
                normalize_value(row.get('FIRST_TRADING_NAME')),
                normalize_value(row.get('LEGAL_NAME')),
                normalize_value(row.get('COUNTRY')),
                normalize_value(row.get('PROVURL')),
                normalize_value(row.get('PROVADDRESS')),
                normalize_value(row.get('PROVTEL')),
                normalize_value(row.get('PUBUKPRNCOUNTRY'))
            )
            for row in rows
            if normalize_value(row.get('PUBUKPRN'))
        ]
        
        # Deduplicate by PUBUKPRN (keep last/most recent occurrence for mergers/takeovers)
        data_dict = {}
        duplicates = 0
        for item in raw_data:
            pubukprn = item[0]
            if pubukprn in data_dict:
                duplicates += 1
            data_dict[pubukprn] = item
        
        data = list(data_dict.values())
        
        if data:
            execute_values(
                cursor,
                """
                INSERT INTO hesa_institution (pubukprn, first_trading_name, legal_name, country, provurl, provaddress, provtel, pubukprncountry)
                VALUES %s
                ON CONFLICT (pubukprn) DO UPDATE
                SET first_trading_name = EXCLUDED.first_trading_name,
                    legal_name = EXCLUDED.legal_name,
                    provurl = EXCLUDED.provurl,
                    provaddress = EXCLUDED.provaddress,
                    provtel = EXCLUDED.provtel,
                    pubukprncountry = EXCLUDED.pubukprncountry
                """,
                data,
                page_size=1000
            )
            logger.info(f"  Imported {len(data)} Institution records (kept most recent of {duplicates} duplicate PUBUKPRNs)")
    
    # 2. KISCOURSE
    logger.info("\n[2/2] Importing KISCOURSE.csv...")
    rows = read_csv_file(data_dir / 'KISCOURSE.csv')
    if rows:
        data = []
        for row in rows:
            pubukprn = normalize_value(row.get('PUBUKPRN'))
            kiscourseid = normalize_value(row.get('KISCOURSEID'))
            kismode = normalize_value(row.get('KISMODE'))
            
            if pubukprn and kiscourseid and kismode:
                data.append((
                    pubukprn,
                    normalize_value(row.get('UKPRN')),
                    kiscourseid,
                    normalize_value(row.get('TITLE')),
                    normalize_value(row.get('TITLEW')),
                    kismode,
                    normalize_value(row.get('LENGTH')),
                    normalize_value(row.get('LEVELCODE')),
                    normalize_value(row.get('LOCID')),
                    normalize_value(row.get('DISTANCE')),
                    normalize_value(row.get('OWNCOHORT')),
                    normalize_value(row.get('AVGCOURSECOST')),
                    normalize_value(row.get('AVGCOURSECOSTW')),
                    normalize_value(row.get('AVCOSTID')),
                    normalize_int(row.get('FEEUK')),
                    normalize_int(row.get('FEEENG')),
                    normalize_int(row.get('FEENI')),
                    normalize_int(row.get('FEESCT')),
                    normalize_int(row.get('FEEWALES')),
                    normalize_value(row.get('HONOURS')),
                    normalize_value(row.get('SANDWICH')),
                    normalize_value(row.get('YEARABROAD')),
                    normalize_value(row.get('FOUNDATIONYEAR')),
                    normalize_value(row.get('JACS3')),
                    normalize_value(row.get('SUBJECTCODENAME')),
                    normalize_value(row.get('SUBJECTCODENAMEW')),
                    normalize_value(row.get('COURSELOCATION')),
                    normalize_value(row.get('COURSELOCATIONW')),
                    normalize_value(row.get('COURSEPAGEURL')),
                    normalize_value(row.get('COURSEPAGEURLW')),
                    normalize_value(row.get('COURSEPAGEURLID')),
                    normalize_value(row.get('SUPPORTURL')),
                    normalize_value(row.get('SUPPORTURLW')),
                    normalize_value(row.get('SUPPORTURLID')),
                    normalize_value(row.get('EMPLOYABILITYURL')),
                    normalize_value(row.get('EMPLOYABILITYURLW')),
                    normalize_value(row.get('EMPLOYABILITYURLID')),
                    normalize_value(row.get('FINANCIALURL')),
                    normalize_value(row.get('FINANCIALURLW')),
                    normalize_value(row.get('FINANCIALURLID'))
                ))
        
        if data:
            # Process in smaller batches to avoid memory issues
            batch_size = 100  # Reduced from 1000 to avoid memory issues
            total_batches = (len(data) - 1) // batch_size + 1
            
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                batch_num = i//batch_size + 1
                
                try:
                    execute_batch(
                        cursor,
                        """
                        INSERT INTO hesa_kiscourse (
                            pubukprn, ukprn, kiscourseid, title, titlew, kismode, length,
                            levelcode, locid, distance, owncohort, avgcoursecost, avgcoursecostw,
                            avcostid, feeuk, feeeng, feeni, feesct, feewales, honours,
                            sandwich, yearabroad, foundationyear, jacs3code, subjectcodename,
                            subjectcodenamew, courselocation, courselocationw, coursepageurl,
                            coursepageurlw, coursepageurlid, supporturl, supporturlw, supporturlid,
                            employabilityurl, employabilityurlw, employabilityurlid,
                            financialurl, financialurlw, financialurlid
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                 %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                 %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (pubukprn, kiscourseid, kismode) DO UPDATE
                        SET title = EXCLUDED.title,
                            jacs3code = EXCLUDED.jacs3code,
                            feeuk = EXCLUDED.feeuk
                        """,
                        batch,
                        page_size=100  # Reduced page size
                    )
                    logger.info(f"  → Processed batch {batch_num}/{total_batches}")
                except Exception as e:
                    logger.error(f"  → Error in batch {batch_num}: {e}")
                    # Continue with next batch instead of failing completely
                    continue
            
            logger.info(f"  Imported {len(data)} KIS Course records")

    # 3. UCASCOURSEID - Special handling for UTF-16 encoding
    logger.info("\n[3/4] Importing UCASCOURSEID.csv...")
    rows = read_sbj_csv_file(data_dir / 'UCASCOURSEID.csv')
    if rows:
        data = []
        for row in rows:
            pubukprn = row.get('PUBUKPRN', '').strip() if row.get('PUBUKPRN') else None
            ukprn = row.get('UKPRN', '').strip() if row.get('UKPRN') else None
            kiscourseid = row.get('KISCOURSEID', '').strip() if row.get('KISCOURSEID') else None
            kismode = row.get('KISMODE', '').strip() if row.get('KISMODE') else None
            locid = row.get('LOCID', '').strip() if row.get('LOCID') else None
            ucascourseid = row.get('UCASCOURSEID', '').strip() if row.get('UCASCOURSEID') else None
            
            if pubukprn and ucascourseid:
                data.append((pubukprn, ukprn, kiscourseid, kismode, locid, ucascourseid))
        
        if data:
            execute_values(
                cursor,
                """
                INSERT INTO hesa_ucascourseid (pubukprn, ukprn, kiscourseid, kismode, locid, ucascourseid)
                VALUES %s
                ON CONFLICT DO NOTHING
                """,
                data,
                page_size=100
            )
            logger.info(f"  Imported {len(data)} UCAS Course ID records")
    
    # 4. SBJ (Subject codes) - Special handling for UTF-16 encoding
    logger.info("\n[4/4] Importing SBJ.csv...")
    rows = read_sbj_csv_file(data_dir / 'SBJ.csv')
    if rows:
        data = []
        for row in rows:
            pubukprn = row.get('PUBUKPRN', '').strip() if row.get('PUBUKPRN') else None
            ukprn = row.get('UKPRN', '').strip() if row.get('UKPRN') else None
            kiscourseid = row.get('KISCOURSEID', '').strip() if row.get('KISCOURSEID') else None
            kismode = row.get('KISMODE', '').strip() if row.get('KISMODE') else None
            sbj = row.get('SBJ', '').strip() if row.get('SBJ') else None
            
            if pubukprn and sbj:
                data.append((pubukprn, ukprn, kiscourseid, kismode, sbj))
        
        if data:
            execute_values(
                cursor,
                """
                INSERT INTO hesa_sbj (pubukprn, ukprn, kiscourseid, kismode, sbj)
                VALUES %s
                ON CONFLICT DO NOTHING
                """,
                data,
                page_size=100
            )
            logger.info(f"  Imported {len(data)} Subject records")

def import_outcome_tables(cursor, data_dir: Path):
    """Import employment and outcomes data"""
    logger.info("\n" + "="*70)
    logger.info("IMPORTING OUTCOME DATA TABLES")
    logger.info("="*70)
    
    # 1. ENTRY
    logger.info("\n[1/6] Importing ENTRY.csv...")
    rows = read_csv_file(data_dir / 'ENTRY.csv')
    if rows:
        data = [
            (
                normalize_value(row.get('PUBUKPRN')),
                normalize_value(row.get('UKPRN')),
                normalize_value(row.get('KISCOURSEID')),
                normalize_value(row.get('KISMODE')),
                normalize_value(row.get('ENTRYLEVEL')),
                normalize_value(row.get('ENTUNAVAILREASON')),
                normalize_int(row.get('ENTPOP')),
                normalize_value(row.get('ENTAGG')),
                normalize_value(row.get('ENTAGGYEAR')),
                normalize_value(row.get('ENTYEAR1')),
                normalize_value(row.get('ENTYEAR2')),
                normalize_value(row.get('ENTSBJ')),
                normalize_int(row.get('ALEVEL')),
                normalize_int(row.get('ACCESS')),
                normalize_int(row.get('ALEVELTCE')),
                normalize_int(row.get('BACC')),
                normalize_int(row.get('DEGREE')),
                normalize_int(row.get('FOUNDATION')),
                normalize_int(row.get('NOQUALS')),
                normalize_int(row.get('OTHER')),
                normalize_int(row.get('OTHERHE'))
            )
            for row in rows
            if (normalize_value(row.get('PUBUKPRN')) and 
                normalize_value(row.get('KISCOURSEID')) and 
                normalize_value(row.get('KISMODE')))
        ]
        if data:
            execute_batch(
                cursor,
                """
                INSERT INTO hesa_entry (pubukprn, ukprn, kiscourseid, kismode, entrylevel,
                                 entunavailreason, entpop, entagg, entaggyear, entyear1,
                                 entyear2, entsbj, alevel, access, aleveltce, bacc,
                                 degree, foundation, noquals, "other", otherhe)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                       %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pubukprn, kiscourseid, kismode) DO UPDATE
                SET entpop = EXCLUDED.entpop,
                    alevel = EXCLUDED.alevel
                """,
                data,
                page_size=1000
            )
            logger.info(f"  Imported {len(data)} Entry records")
    
    # 2. TARIFF (tariff point distributions)
    # 2. TARIFF - Special handling for UTF-16 encoding
    logger.info("\n[2/6] Importing TARIFF.csv...")
    rows = read_sbj_csv_file(data_dir / 'TARIFF.csv')
    if rows:
        data = []
        for row in rows:
            pubukprn = row.get('PUBUKPRN', '').strip() if row.get('PUBUKPRN') else None
            ukprn = row.get('UKPRN', '').strip() if row.get('UKPRN') else None
            kiscourseid = row.get('KISCOURSEID', '').strip() if row.get('KISCOURSEID') else None
            kismode = row.get('KISMODE', '').strip() if row.get('KISMODE') else None
            
            if pubukprn and kiscourseid:
                data.append((
                    pubukprn,
                    ukprn,
                    kiscourseid,
                    kismode,
                    row.get('TARUNAVAILREASON', '').strip() if row.get('TARUNAVAILREASON') else None,
                    int(row.get('TARPOP', 0)) if row.get('TARPOP', '').strip() else None,
                    row.get('TARAGG', '').strip() if row.get('TARAGG') else None,
                    row.get('TARAGGYEAR', '').strip() if row.get('TARAGGYEAR') else None,
                    row.get('TARYEAR1', '').strip() if row.get('TARYEAR1') else None,
                    row.get('TARYEAR2', '').strip() if row.get('TARYEAR2') else None,
                    row.get('TARSBJ', '').strip() if row.get('TARSBJ') else None,
                    int(row.get('T001', 0)) if row.get('T001', '').strip() else None,
                    int(row.get('T048', 0)) if row.get('T048', '').strip() else None,
                    int(row.get('T064', 0)) if row.get('T064', '').strip() else None,
                    int(row.get('T080', 0)) if row.get('T080', '').strip() else None,
                    int(row.get('T096', 0)) if row.get('T096', '').strip() else None,
                    int(row.get('T112', 0)) if row.get('T112', '').strip() else None,
                    int(row.get('T128', 0)) if row.get('T128', '').strip() else None,
                    int(row.get('T144', 0)) if row.get('T144', '').strip() else None,
                    int(row.get('T160', 0)) if row.get('T160', '').strip() else None,
                    int(row.get('T176', 0)) if row.get('T176', '').strip() else None,
                    int(row.get('T192', 0)) if row.get('T192', '').strip() else None,
                    int(row.get('T208', 0)) if row.get('T208', '').strip() else None,
                    int(row.get('T224', 0)) if row.get('T224', '').strip() else None,
                    int(row.get('T240', 0)) if row.get('T240', '').strip() else None
                ))

        if data:
            execute_values(
                cursor,
                """
                INSERT INTO hesa_tariff (
                    pubukprn, ukprn, kiscourseid, kismode, tarunavailreason, tarpop,
                    taragg, taraggyear, taryear1, taryear2, tarsbj,
                    t001, t048, t064, t080, t096, t112, t128, t144,
                    t160, t176, t192, t208, t224, t240
                ) VALUES %s
                ON CONFLICT DO NOTHING
                """,
                data,
                page_size=100
            )
            logger.info(f"  Imported {len(data)} Tariff records")

    # 3. EMPLOYMENT
    logger.info("\n[3/6] Importing EMPLOYMENT.csv...")
    rows = read_csv_file(data_dir / 'EMPLOYMENT.csv')
    if rows:
        data = [
            (
                normalize_value(row.get('PUBUKPRN')),
                normalize_value(row.get('UKPRN')),
                normalize_value(row.get('KISCOURSEID')),
                normalize_value(row.get('KISMODE')),
                normalize_value(row.get('EMPUNAVAILREASON')),
                normalize_int(row.get('EMPPOP')),
                normalize_value(row.get('EMPAGG')),
                normalize_value(row.get('EMPAGGYEAR')),
                normalize_value(row.get('EMPYEAR1')),
                normalize_value(row.get('EMPYEAR2')),
                normalize_value(row.get('EMPSBJ')),
                normalize_int(row.get('WORKSTUDY')),
                normalize_int(row.get('WORK')),
                normalize_int(row.get('STUDY')),
                normalize_int(row.get('UNEMP')),
                normalize_int(row.get('OTHER'))
            )
            for row in rows
            if (normalize_value(row.get('PUBUKPRN')) and 
                normalize_value(row.get('KISCOURSEID')) and 
                normalize_value(row.get('KISMODE')))
        ]
        if data:
            # Process employment data in smaller batches
            batch_size = 100
            total_batches = (len(data) - 1) // batch_size + 1
            
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                try:
                    execute_batch(
                        cursor,
                        """
                        INSERT INTO hesa_employment (pubukprn, ukprn, kiscourseid, kismode,
                                              empunavailreason, emppop, empagg, empaggyear,
                                              empyear1, empyear2, empsbj, workstudy, work,
                                              study, unemp, "other")
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (pubukprn, kiscourseid, kismode) DO UPDATE
                        SET emppop = EXCLUDED.emppop,
                            work = EXCLUDED.work
                        """,
                        batch,
                        page_size=100
                    )
                    logger.info(f"  → Employment batch {batch_num}/{total_batches}")
                except Exception as e:
                    logger.error(f"  → Error in employment batch {batch_num}: {e}")
                    continue
            
            logger.info(f"  Imported {len(data)} Employment records")
    
    # 4. JOBLIST
    logger.info("\n[4/6] Importing JOBLIST.csv...")
    rows = read_csv_file(data_dir / 'JOBLIST.csv')
    if rows:
        data = [
            (
                normalize_value(row.get('PUBUKPRN')),
                normalize_value(row.get('UKPRN')),
                normalize_value(row.get('KISCOURSEID')),
                normalize_value(row.get('KISMODE')),
                normalize_value(row.get('JOBUNAVAILREASON')),
                normalize_int(row.get('JOBPOP')),
                normalize_int(row.get('JOBRESPONSE')),
                normalize_int(row.get('JOBSAMPLE')),
                normalize_int(row.get('JOBRESP_RATE')),
                normalize_value(row.get('JOBAGG')),
                normalize_value(row.get('JOBAGGYEAR')),
                normalize_value(row.get('JOBYEAR1')),
                normalize_value(row.get('JOBYEAR2')),
                normalize_value(row.get('JOBSBJ')),
                normalize_int(row.get('EDUC')),
                normalize_int(row.get('HEALTH')),
                normalize_int(row.get('CAREHOME')),
                normalize_int(row.get('HEALTHSOC')),
                normalize_int(row.get('RETAIL')),
                normalize_int(row.get('MAN')),
                normalize_int(row.get('INFO')),
                normalize_int(row.get('FIN')),
                normalize_int(row.get('PRO')),
                normalize_int(row.get('ADMIN')),
                normalize_int(row.get('OTHER')),
                normalize_int(row.get('UNKWN'))
            )
            for row in rows
            if (normalize_value(row.get('PUBUKPRN')) and 
                normalize_value(row.get('KISCOURSEID')) and 
                normalize_value(row.get('KISMODE')))
        ]
        if data:
            execute_batch(
                cursor,
                """
                INSERT INTO hesa_joblist (pubukprn, ukprn, kiscourseid, kismode,
                                    jobunavailreason, jobpop, jobresponse, jobsample,
                                    jobresp_rate, jobagg, jobaggyear, jobyear1,
                                    jobyear2, jobsbj, educ, health, carehome, healthsoc,
                                    retail, man, info, fin, pro, admin, "other", unkwn)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                       %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pubukprn, kiscourseid, kismode) DO UPDATE
                SET jobpop = EXCLUDED.jobpop
                """,
                data,
                page_size=1000
            )
            logger.info(f"  Imported {len(data)} Job List records")
    
    # 5. GOSALARY
    logger.info("\n[5/6] Importing GOSALARY.csv...")
    rows = read_csv_file(data_dir / 'GOSALARY.csv')
    if rows:
        data = [
            (
                normalize_value(row.get('PUBUKPRN')),
                normalize_value(row.get('UKPRN')),
                normalize_value(row.get('KISCOURSEID')),
                normalize_value(row.get('KISMODE')),
                normalize_value(row.get('GOSUNAVAILREASON')),
                normalize_int(row.get('GOSPOP')),
                normalize_int(row.get('GOSRESPONSE')),
                normalize_int(row.get('GOSSAMPLE')),
                normalize_int(row.get('GOSRESP_RATE')),
                normalize_value(row.get('GOSALAGG')),
                normalize_value(row.get('GOSAGGYEAR')),
                normalize_value(row.get('GOSYEAR1')),
                normalize_value(row.get('GOSYEAR2')),
                normalize_value(row.get('GOSSBJ')),
                normalize_int(row.get('LDLWR')),
                normalize_int(row.get('LDMED')),
                normalize_int(row.get('LDUPR')),
                normalize_int(row.get('LDPOP')),
                normalize_int(row.get('INSTLWR')),
                normalize_int(row.get('INSTMED')),
                normalize_int(row.get('INSTUPR')),
                normalize_int(row.get('INSTPOP'))
            )
            for row in rows
            if (normalize_value(row.get('PUBUKPRN')) and 
                normalize_value(row.get('KISCOURSEID')) and 
                normalize_value(row.get('KISMODE')))
        ]
        if data:
            execute_batch(
                cursor,
                """
                INSERT INTO hesa_gosalary (pubukprn, ukprn, kiscourseid, kismode,
                                    gosunavailreason, gospop, gosresponse, gossample,
                                    gosresp_rate, gosalagg, gosaggyear, gosyear1,
                                    gosyear2, gossbj, ldlwr, ldmed, ldupr, ldpop,
                                    instlwr, instmed, instupr, instpop)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                       %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pubukprn, kiscourseid, kismode) DO UPDATE
                SET gospop = EXCLUDED.gospop
                """,
                data,
                page_size=1000
            )
            logger.info(f"  Imported {len(data)} Graduate Salary records")
    
    # 6. LEO3
    logger.info("\n[6/6] Importing LEO3.csv...")
    rows = read_csv_file(data_dir / 'LEO3.csv')
    if rows:
        data = [
            (
                normalize_value(row.get('PUBUKPRN')),
                normalize_value(row.get('UKPRN')),
                normalize_value(row.get('KISCOURSEID')),
                normalize_value(row.get('KISMODE')),
                normalize_value(row.get('LEO3UNAVAILREASON')),
                normalize_int(row.get('LEO3POP')),
                normalize_value(row.get('LEO3AGG')),
                normalize_value(row.get('LEO3AGGYEAR')),
                normalize_value(row.get('LEO3YEAR1')),
                normalize_value(row.get('LEO3YEAR2')),
                normalize_value(row.get('LEO3SBJ')),
                normalize_int(row.get('LEO3INSTLQ')),
                normalize_int(row.get('LEO3INSTMED')),
                normalize_int(row.get('LEO3INSTUQ')),
                normalize_int(row.get('LEO3INSTPOP')),
                normalize_int(row.get('LEO3SECLQ')),
                normalize_int(row.get('LEO3SECMED')),
                normalize_int(row.get('LEO3SECUQ')),
                normalize_int(row.get('LEO3SECPOP')),
                normalize_value(row.get('LEO3SECTOR'))
            )
            for row in rows
            if (normalize_value(row.get('PUBUKPRN')) and 
                normalize_value(row.get('KISCOURSEID')) and 
                normalize_value(row.get('KISMODE')))
        ]
        if data:
            execute_batch(
                cursor,
                """
                INSERT INTO hesa_leo3 (pubukprn, ukprn, kiscourseid, kismode,
                                leo3unavailreason, leo3pop, leo3agg, leo3aggyear,
                                leo3year1, leo3year2, leo3sbj, leo3instlq, leo3instmed,
                                leo3instuq, leo3instpop, leo3seclq, leo3secmed,
                                leo3secuq, leo3secpop, leo3sector)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                       %s, %s, %s, %s, %s)
                ON CONFLICT (pubukprn, kiscourseid, kismode) DO UPDATE
                SET leo3pop = EXCLUDED.leo3pop
                """,
                data,
                page_size=1000
            )
            logger.info(f"  Imported {len(data)} LEO3 records")

def main():
    """Main import function"""
    # Get data directory from project root
    data_dir = Path(__file__).parent.parent.parent / 'data'
    
    logger.info("="*70)
    logger.info(f" HESA CSV DATA IMPORT from : {data_dir}\n )")

    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Import in order
        import_core_entities(cursor, data_dir)
        import_outcome_tables(cursor, data_dir)
        
        # Commit all changes
        conn.commit()
        
        logger.info("\n" + "="*70)
        logger.info("Import completed successfully!")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"\nError during import: {e}")
        if 'conn' in locals():
            conn.rollback()
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
