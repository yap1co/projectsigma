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
    """Normalize CSV values - handle empty strings, whitespace, and numeric codes"""
    if value is None:
        return None
    
    # Handle pandas NaN/None values
    import pandas as pd
    if pd.isna(value):
        return None
    
    # If it's a float that represents an integer (e.g., 101028.0 for HECOS codes),
    # convert to int first to remove the decimal point
    if isinstance(value, float) and value == int(value):
        value = int(value)
    
    value = str(value).strip()
    return value if value else None

def normalize_int(value: str) -> Optional[int]:
    """Convert string/float to integer, handling empty strings and pandas floats"""
    if value is None:
        return None
    
    # Handle pandas NaN
    import pandas as pd
    if pd.isna(value):
        return None
    
    try:
        # If it's already a float, convert directly
        if isinstance(value, float):
            return int(value)
        # Otherwise strip and convert
        value = str(value).strip()
        if not value:
            return None
        return int(float(value))  # Use float as intermediate to handle "101028.0" strings
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
    
    # 2. KISCOURSE - Use pandas to handle duplicate HECOS column names
    logger.info("\n[2/2] Importing KISCOURSE.csv...")
    import pandas as pd
    csv_path = data_dir / 'KISCOURSE.csv'
    if csv_path.exists():
        df = pd.read_csv(csv_path, encoding='utf-8', low_memory=False)
        rows = df.to_dict('records')
    else:
        logger.warning(f"File not found: {csv_path}")
        rows = []
    
    if rows:
        data = []
        for row in rows:
            pubukprn = normalize_value(row.get('PUBUKPRN'))
            kiscourseid = normalize_value(row.get('KISCOURSEID'))
            kismode = normalize_value(row.get('KISMODE'))
            
            if pubukprn and kiscourseid and kismode:
                # HECOS can be in 5 columns - pandas renames duplicates to HECOS, HECOS.1, HECOS.2, etc.
                # Use the first non-null HECOS value from any of the 5 columns
                hecos_value = None
                hecos_columns = ['HECOS', 'HECOS.1', 'HECOS.2', 'HECOS.3', 'HECOS.4']
                for hecos_col in hecos_columns:
                    if hecos_col in row:
                        hecos_val = normalize_int(row.get(hecos_col))
                        if hecos_val is not None:  # Explicitly check for None (not just falsy)
                            hecos_value = hecos_val
                            break
                
                data.append((
                    pubukprn,
                    normalize_value(row.get('UKPRN')),
                    kiscourseid,
                    normalize_value(row.get('TITLE')),
                    kismode,
                    normalize_value(row.get('UCASPROGID')),   # ucasprogid
                    normalize_value(row.get('NUMSTAGE')),     # length
                    normalize_value(row.get('KISLEVEL')),     # levelcode
                    normalize_value(row.get('KISAIMCODE')),   # locid
                    normalize_value(row.get('DISTANCE')),
                    normalize_value(row.get('HONOURS')),
                    normalize_value(row.get('SANDWICH')),
                    normalize_value(row.get('YEARABROAD')),
                    normalize_value(row.get('FOUNDATION')),   # foundationyear
                    hecos_value,                              # hecos (first non-empty from multiple columns)
                    normalize_value(row.get('CRSEURL')),      # coursepageurl
                    normalize_value(row.get('SUPPORTURL')),
                    normalize_value(row.get('EMPLOYURL'))     # employabilityurl
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
                            pubukprn, ukprn, kiscourseid, title, kismode, ucasprogid, length,
                            levelcode, locid, distance, honours, sandwich, yearabroad, 
                            foundationyear, hecos, coursepageurl,
                            supporturl, employabilityurl
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                 %s, %s, %s)
                        ON CONFLICT (pubukprn, kiscourseid, kismode) DO UPDATE
                        SET title = EXCLUDED.title,
                            hecos = EXCLUDED.hecos,
                            ucasprogid = EXCLUDED.ucasprogid
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
                normalize_value(row.get('ENTUNAVAILREASON')),
                normalize_int(row.get('ENTPOP')),
                normalize_value(row.get('ENTAGG')),
                normalize_value(row.get('ENTAGGYEAR')),
                normalize_value(row.get('ENTYEAR1')),
                normalize_value(row.get('ENTYEAR2')),
                normalize_value(row.get('ENTSBJ')),
                normalize_int(row.get('ACCESS')),
                normalize_int(row.get('ALEVEL')),
                normalize_int(row.get('BACC')),
                normalize_int(row.get('DEGREE')),
                normalize_int(row.get('FOUNDTN')),
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
            # Process in smaller batches to isolate errors
            batch_size = 100
            total_batches = (len(data) + batch_size - 1) // batch_size
            imported_count = 0
            
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                try:
                    execute_batch(
                        cursor,
                        'INSERT INTO hesa_entry (pubukprn, ukprn, kiscourseid, kismode, entunavailreason, entpop, entagg, entaggyear, entyear1, entyear2, entsbj, access, alevel, bacc, degree, foundtn, noquals, "other", otherhe) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (pubukprn, kiscourseid, kismode) DO UPDATE SET entpop = EXCLUDED.entpop, alevel = EXCLUDED.alevel',
                        batch,
                        page_size=50
                    )
                    imported_count += len(batch)
                    if batch_num % 50 == 0:
                        logger.info(f"  → Entry batch {batch_num}/{total_batches}")
                except Exception as e:
                    logger.error(f"  → Error in entry batch {batch_num}: {e}")
                    # Try individual records in this batch
                    for j, record in enumerate(batch):
                        try:
                            cursor.execute(
                                'INSERT INTO hesa_entry (pubukprn, ukprn, kiscourseid, kismode, entunavailreason, entpop, entagg, entaggyear, entyear1, entyear2, entsbj, access, alevel, bacc, degree, foundtn, noquals, "other", otherhe) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (pubukprn, kiscourseid, kismode) DO UPDATE SET entpop = EXCLUDED.entpop, alevel = EXCLUDED.alevel',
                                record
                            )
                            imported_count += 1
                        except Exception as record_error:
                            logger.error(f"    → Skipping bad record {j}: {record_error}")
                            logger.error(f"    → Record data: {record}")
                            continue
                            
            logger.info(f"  Imported {imported_count} Entry records")
    
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
    
    # 4. JOBLIST - Simple import matching CSV structure
    logger.info("\n[4/6] Importing JOBLIST.csv...")
    rows = read_csv_file(data_dir / 'JOBLIST.csv')
    if rows:
        data = [
            (
                normalize_value(row.get('PUBUKPRN')),
                normalize_value(row.get('UKPRN')),
                normalize_value(row.get('KISCOURSEID')),
                normalize_value(row.get('KISMODE')),
                normalize_value(row.get('COMSBJ')),
                normalize_value(row.get('JOB')),
                normalize_int(row.get('PERC')),
                normalize_int(row.get('ORDER')),
                normalize_int(row.get('HS'))
            )
            for row in rows
            if (normalize_value(row.get('PUBUKPRN')) and 
                normalize_value(row.get('KISCOURSEID')) and 
                normalize_value(row.get('KISMODE')) and
                normalize_value(row.get('JOB')))
        ]
        if data:
            execute_batch(
                cursor,
                """
                INSERT INTO hesa_joblist (pubukprn, ukprn, kiscourseid, kismode,
                                   comsbj, job, perc, "order", hs)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pubukprn, kiscourseid, kismode, job) DO UPDATE
                SET perc = EXCLUDED.perc
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
                normalize_value(row.get('GOSALUNAVAILREASON')),
                normalize_int(row.get('GOSALPOP')),
                normalize_int(row.get('GOSALRESPONSE')),
                normalize_int(row.get('GOSALSAMPLE')),
                normalize_int(row.get('GOSALRESP_RATE')),
                normalize_value(row.get('GOSALAGG')),
                normalize_value(row.get('GOSALAGGYEAR')),
                normalize_value(row.get('GOSALYEAR1')),
                normalize_value(row.get('GOSALYEAR2')),
                normalize_value(row.get('GOSALSBJ')),
                normalize_int(row.get('GOINSTLQ')),
                normalize_int(row.get('GOINSTMED')),
                normalize_int(row.get('GOINSTUQ')),
                normalize_int(row.get('GOPROV_PC_UK')),
                normalize_int(row.get('GOPROV_PC_E')),
                normalize_int(row.get('GOPROV_PC_NI')),
                normalize_int(row.get('GOPROV_PC_S')),
                normalize_int(row.get('GOPROV_PC_W'))
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
                                    gosalunavailreason, gosalpop, gosalresponse, gosalsample,
                                    gosalresp_rate, gosalagg, gosalaggyear, gosalyear1,
                                    gosalyear2, gosalsbj, goinstlq, goinstmed, goinstuq,
                                    goprov_pc_uk, goprov_pc_e, goprov_pc_ni, goprov_pc_s, goprov_pc_w)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                       %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pubukprn, kiscourseid, kismode) DO UPDATE
                SET gosalpop = EXCLUDED.gosalpop
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
                normalize_value(row.get('LEO3SBJ')),
                normalize_int(row.get('LEO3INSTLQ')),
                normalize_int(row.get('LEO3INSTMED')),
                normalize_int(row.get('LEO3INSTUQ')),
                normalize_int(row.get('LEO3PROV_PC_UK')),
                normalize_int(row.get('LEO3PROV_PC_E')),
                normalize_int(row.get('LEO3PROV_PC_NW')),
                normalize_int(row.get('LEO3PROV_PC_NE')),
                normalize_int(row.get('LEO3PROV_PC_EM')),
                normalize_int(row.get('LEO3PROV_PC_WM')),
                normalize_int(row.get('LEO3PROV_PC_EE')),
                normalize_int(row.get('LEO3PROV_PC_SE')),
                normalize_int(row.get('LEO3PROV_PC_SW')),
                normalize_int(row.get('LEO3PROV_PC_YH')),
                normalize_int(row.get('LEO3PROV_PC_LN')),
                normalize_int(row.get('LEO3PROV_PC_NI')),
                normalize_int(row.get('LEO3PROV_PC_S')),
                normalize_int(row.get('LEO3PROV_PC_ED')),
                normalize_int(row.get('LEO3PROV_PC_GL')),
                normalize_int(row.get('LEO3PROV_PC_W')),
                normalize_int(row.get('LEO3PROV_PC_CF'))
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
                                leo3sbj, leo3instlq, leo3instmed, leo3instuq,
                                leo3prov_pc_uk, leo3prov_pc_e, leo3prov_pc_nw,
                                leo3prov_pc_ne, leo3prov_pc_em, leo3prov_pc_wm,
                                leo3prov_pc_ee, leo3prov_pc_se, leo3prov_pc_sw,
                                leo3prov_pc_yh, leo3prov_pc_ln, leo3prov_pc_ni,
                                leo3prov_pc_s, leo3prov_pc_ed, leo3prov_pc_gl,
                                leo3prov_pc_w, leo3prov_pc_cf)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                       %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
