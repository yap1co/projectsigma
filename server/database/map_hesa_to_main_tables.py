"""
Map HESA Discotablesver Uni data to main university and course tables
This script reads from the HESA tables (hesa_institution, hesa_kiscourse) and 
populates the main tables (university, course) used by the recommendation engine
"""

import sys
from pathlib import Path

# Add parent directory to path to import database_helper
sys.path.insert(0, str(Path(__file__).parent.parent))

from database_helper import get_db_connection, generate_id
from psycopg2.extras import RealDictCursor
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def map_hesa_to_main_tables():
    """Map HESA data from institution/kiscourse to university/course tables"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        logger.info("="*70)
        logger.info("MAPPING HESA DATA TO MAIN TABLES")
        
        # Step 1: Map institutions to universities
        logger.info("\n[1/3] Mapping institutions to universities...")
        cur.execute("""
            SELECT DISTINCT 
                i.pubukprn,
                COALESCE(i.first_trading_name, i.legal_name, 'Unknown University') as name,
                CASE 
                    WHEN i.country = 'XI' THEN 'Wales'
                    WHEN i.country = 'XH' THEN 'Scotland'
                    WHEN i.country = 'XG' THEN 'Northern Ireland'
                    WHEN i.country = 'XF' THEN 'England'
                    ELSE 'Unknown'
                END as region,                NULL::INTEGER as rank_overall,
                75 as employability_score,  -- Default, can be updated from other HESA tables
                i.provurl as website_url  -- Include PROVURL from hesa_institution table
            FROM hesa_institution i
            WHERE i.pubukprn IS NOT NULL
        """)
        
        institutions = cur.fetchall()
        university_map = {}  # pubukprn -> university_id
        
        for inst in institutions:
            uni_id = generate_id('UNIV_')
            pubukprn = inst['pubukprn']
            
            # Normalize URL - ensure it starts with http:// or https://
            website_url = inst.get('website_url')
            if website_url and not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url.lstrip('/')
            
            cur.execute("""
                INSERT INTO university (university_id, pubukprn, name, region, rank_overall, employability_score, website_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pubukprn) DO UPDATE
                SET name = EXCLUDED.name,
                    region = EXCLUDED.region,
                    rank_overall = EXCLUDED.rank_overall,
                    employability_score = EXCLUDED.employability_score,
                    website_url = EXCLUDED.website_url
            """, (uni_id, pubukprn, inst['name'], inst['region'], inst['rank_overall'], inst['employability_score'], website_url))
            
            university_map[pubukprn] = uni_id
        
        conn.commit()
        logger.info(f"  OK: Mapped {len(university_map)} institutions to universities")
        
        # Step 2: Map KIS courses to courses
        logger.info("\n[2/3] Mapping KIS courses to courses...")
        cur.execute("""
            SELECT DISTINCT
                kc.pubukprn,
                kc.kiscourseid,
                kc.kismode,
                kc.title,
                kc.ucasprogid,
                kc.hecos,
                kc.length,
                kc.coursepageurl,
                uc.ucascourseid
            FROM hesa_kiscourse kc
            LEFT JOIN hesa_ucascourseid uc ON 
                kc.pubukprn = uc.pubukprn AND
                kc.kiscourseid = uc.kiscourseid AND
                kc.kismode = uc.kismode
            WHERE kc.pubukprn IS NOT NULL 
              AND kc.kiscourseid IS NOT NULL
              AND kc.title IS NOT NULL
              AND kc.kismode IN ('1', '2')  -- Full-time (1) and part-time (2)
        """)
        
        courses_data = cur.fetchall()
        course_count = 0
        
        for kc in courses_data:
            pubukprn = kc['pubukprn']
            
            # Look up university_id from database using pubukprn
            cur.execute("SELECT university_id FROM university WHERE pubukprn = %s", (pubukprn,))
            uni_result = cur.fetchone()
            if not uni_result:
                continue  # Skip if university doesn't exist
            
            uni_id = uni_result['university_id']
            course_id = generate_id('COURSE_')
            course_name = kc['title']
            ucas_code = kc.get('ucascourseid') or kc.get('ucasprogid')
            
            # Get employability score from hesa_employment data if available
            # Calculate based on work/(work+study+unemp) ratio, scaled to 0-100
            cur.execute("""
                SELECT work, study, unemp
                FROM hesa_employment
                WHERE pubukprn = %s AND kiscourseid = %s AND kismode = %s
                LIMIT 1
            """, (pubukprn, kc['kiscourseid'], kc['kismode']))
            emp_result = cur.fetchone()
            if emp_result and emp_result.get('work') and emp_result.get('study') and emp_result.get('unemp'):
                total = emp_result['work'] + emp_result['study'] + emp_result['unemp']
                if total > 0:
                    # Calculate percentage employed, scale to 0-100
                    work_ratio = emp_result['work'] / total
                    employability = int(work_ratio * 100)
                else:
                    employability = 75
            else:
                employability = 75  # Default if no employment data

            # Get typical tariff points from hesa_tariff (median bin)
            typical_tariff = None
            cur.execute("""
                SELECT t001, t048, t064, t080, t096, t112, t128, t144, t160, t176, t192, t208, t224, t240
                FROM hesa_tariff
                WHERE pubukprn = %s AND kiscourseid = %s AND kismode = %s
                LIMIT 1
            """, (pubukprn, kc['kiscourseid'], kc['kismode']))
            tariff_row = cur.fetchone()
            if tariff_row:
                bins = [
                    ('t001', 1), ('t048', 48), ('t064', 64), ('t080', 80), ('t096', 96),
                    ('t112', 112), ('t128', 128), ('t144', 144), ('t160', 160), ('t176', 176),
                    ('t192', 192), ('t208', 208), ('t224', 224), ('t240', 240)
                ]
                total = sum((tariff_row.get(col) or 0) for col, _ in bins)
                if total and total > 0:
                    half = total / 2
                    cumulative = 0
                    for col, val in bins:
                        cumulative += (tariff_row.get(col) or 0)
                        if cumulative >= half:
                            typical_tariff = val
                            break
            
            # Handle UCAS code duplicates by making it NULL if it would conflict
            # or by appending a suffix
            if ucas_code:
                cur.execute("SELECT course_id FROM course WHERE ucas_code = %s LIMIT 1", (ucas_code,))
                if cur.fetchone():
                    # UCAS code already exists, set to NULL to avoid conflict
                    ucas_code = None
            
            cur.execute("""
                INSERT INTO course (
                    course_id, university_id, name, ucas_code, ucasprogid,
                    hecos, length, annual_fee, employability_score, course_url,
                    typical_offer_text, typical_offer_tariff,
                    pubukprn, kiscourseid, kismode
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pubukprn, kiscourseid, kismode) DO UPDATE
                SET name = EXCLUDED.name,
                    ucasprogid = EXCLUDED.ucasprogid,
                    hecos = EXCLUDED.hecos,
                    length = EXCLUDED.length,
                    employability_score = EXCLUDED.employability_score,
                    course_url = EXCLUDED.course_url,
                    typical_offer_tariff = EXCLUDED.typical_offer_tariff
            """, (
                course_id, uni_id, course_name, ucas_code,
                kc.get('ucasprogid'),  # UCAS Programme ID
                kc.get('hecos'),  # First HECOS subject code
                kc.get('length'),  # Course length (from NUMSTAGE)
                9250,  # Default UK fee
                employability,
                kc.get('coursepageurl'),  # Course URL from CRSEURL
                None,  # typical_offer_text (not available in HESA)
                typical_tariff,
                pubukprn,  # Store HESA identifiers for linking back
                kc['kiscourseid'],
                kc['kismode']
            ))
            
            # Verify course exists (get actual course_id if conflict occurred)
            cur.execute("""
                SELECT course_id FROM course 
                WHERE pubukprn = %s AND kiscourseid = %s AND kismode = %s
            """, (pubukprn, kc['kiscourseid'], kc['kismode']))
            
            existing_course = cur.fetchone()
            if not existing_course:
                # Course insertion failed for some reason, skip
                continue
            
            # Use the actual course_id from database (might be different if duplicate)
            actual_course_id = existing_course['course_id']
            
            # Step 3: Add entry requirements from hesa_entry and SBJ tables
            # Get entry qualifications (A-level requirements)
            cur.execute("""
                SELECT entsbj, alevel
                FROM hesa_entry
                WHERE pubukprn = %s AND kiscourseid = %s AND kismode = %s
                LIMIT 1
            """, (pubukprn, kc['kiscourseid'], kc['kismode']))
            
            entry_data = cur.fetchone()
            
            # Note: Course requirements will be created by enhance_subject_mapping.py
            # based on CAH codes, which provides more accurate subject-to-course mappings
            
            course_count += 1
            if course_count % 100 == 0:
                conn.commit()
                logger.info(f"  -> Processed {course_count} courses...")
        
        conn.commit()
        logger.info(f"  OK: Mapped {course_count} courses")
        
        # Step 4: Update university rankings from external data or keep NULL
        # (Rankings would need to come from a separate source like Times/Sunday Times rankings)
        
        # Verify final counts
        cur.execute("SELECT COUNT(*) as count FROM university")
        uni_count = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) as count FROM course")
        final_course_count = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) as count FROM course_subject_requirement")
        req_count = cur.fetchone()['count']
        
        logger.info("\n" + "="*70)
        logger.info("MAPPING COMPLETE - Database Summary:")
        logger.info(f"  Universities: {uni_count}")
        logger.info(f"  Courses: {final_course_count}")
        logger.info(f"  Course Requirements: {req_count}")
        logger.info("="*70)
        
        cur.close()
        conn.close()
        
        logger.info("\nOK: HESA data successfully mapped to main tables!")
        logger.info("The recommendation engine can now use this data.")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"\nERROR: Error mapping HESA data: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    map_hesa_to_main_tables()
