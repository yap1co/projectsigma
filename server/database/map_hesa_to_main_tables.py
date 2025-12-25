"""
Map HESA Discover Uni data to main university and course tables
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
        logger.info("="*70)
        
        # Step 1: Map institutions to universities
        logger.info("\n[1/3] Mapping institutions to universities...")
        cur.execute("""
            SELECT DISTINCT 
                i.pubukprn,
                COALESCE(i.first_trading_name, i.legal_name, 'Unknown University') as name,
                CASE 
                    WHEN i.country = 'W92000024' THEN 'Wales'
                    WHEN i.country = 'S92000003' THEN 'Scotland'
                    WHEN i.country = 'N92000002' THEN 'Northern Ireland'
                    ELSE 'England'
                END as region,
                NULL::INTEGER as rank_overall,
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
                INSERT INTO university (university_id, name, region, rank_overall, employability_score, website_url)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (university_id) DO UPDATE
                SET name = EXCLUDED.name,
                    region = EXCLUDED.region,
                    rank_overall = EXCLUDED.rank_overall,
                    employability_score = EXCLUDED.employability_score,
                    website_url = EXCLUDED.website_url
            """, (uni_id, inst['name'], inst['region'], inst['rank_overall'], inst['employability_score'], website_url))
            
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
                kc.numstage,
                uc.ucascourseid
            FROM hesa_kiscourse kc
            LEFT JOIN ucascourseid uc ON 
                kc.pubukprn = uc.pubukprn AND
                kc.kiscourseid = uc.kiscourseid AND
                kc.kismode = uc.kismode
            WHERE kc.pubukprn IS NOT NULL 
              AND kc.kiscourseid IS NOT NULL
              AND kc.title IS NOT NULL
              AND kc.kismode = '01'  -- Full-time only for now
            LIMIT 5000 -- Limit to avoid overwhelming the system
        """)
        
        courses_data = cur.fetchall()
        course_count = 0
        
        for kc in courses_data:
            pubukprn = kc['pubukprn']
            if pubukprn not in university_map:
                continue
            
            uni_id = university_map[pubukprn]
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
            
            # Handle UCAS code duplicates by making it NULL if it would conflict
            # or by appending a suffix
            if ucas_code:
                cur.execute("SELECT course_id FROM course WHERE ucas_code = %s LIMIT 1", (ucas_code,))
                if cur.fetchone():
                    # UCAS code already exists, set to NULL to avoid conflict
                    ucas_code = None
            
            cur.execute("""
                INSERT INTO course (
                    course_id, university_id, name, ucas_code, 
                    annual_fee, employability_score, course_url,
                    pubukprn, kiscourseid, kismode
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (course_id) DO UPDATE
                SET name = EXCLUDED.name,
                    ucas_code = EXCLUDED.ucas_code,
                    employability_score = EXCLUDED.employability_score,
                    pubukprn = EXCLUDED.pubukprn,
                    kiscourseid = EXCLUDED.kiscourseid,
                    kismode = EXCLUDED.kismode
            """, (
                course_id, uni_id, course_name, ucas_code,
                9250,  # Default UK fee
                employability,
                kc.get('crseurl'),  # Course URL from KIS data
                pubukprn,  # Store HESA identifiers for linking back
                kc['kiscourseid'],
                kc['kismode']
            ))
            
            # Step 3: Add entry requirements from hesa_entry and SBJ tables
            # Get entry qualifications (A-level requirements)
            cur.execute("""
                SELECT entsbj, alevel
                FROM hesa_entry
                WHERE pubukprn = %s AND kiscourseid = %s AND kismode = %s
                LIMIT 1
            """, (pubukprn, kc['kiscourseid'], kc['kismode']))
            
            entry_data = cur.fetchone()
            
            # Get subjects from SBJ table
            cur.execute("""
                SELECT DISTINCT sbj
                FROM sbj
                WHERE pubukprn = %s AND kiscourseid = %s AND kismode = %s
            """, (pubukprn, kc['kiscourseid'], kc['kismode']))
            
            subjects = [row['sbj'] for row in cur.fetchall() if row['sbj']]
            
            # Add course requirements
            # Note: HESA data doesn't have explicit grade requirements, so we'll infer from typical offers
            # For now, we'll add subject requirements without grades, or use default grades
            for subject_name in subjects[:3]:  # Limit to 3 subjects
                if subject_name:
                    # Ensure subject exists
                    subject_id = subject_name.replace(" ", "_").replace("&", "and")[:50]
                    cur.execute("""
                        SELECT subject_id FROM subject WHERE subject_name = %s OR subject_id = %s
                        LIMIT 1
                    """, (subject_name, subject_id))
                    existing_subj = cur.fetchone()
                    
                    if existing_subj:
                        subject_id = existing_subj['subject_id']
                    else:
                        # Create subject if it doesn't exist
                        cur.execute("""
                            INSERT INTO subject (subject_id, subject_name)
                            VALUES (%s, %s)
                            ON CONFLICT (subject_id) DO NOTHING
                        """, (subject_id, subject_name))
                    
                    # Add requirement with default grade (can be refined later)
                    # If entry data shows A-levels, use A; otherwise use B
                    alevel_value = entry_data.get('alevel', 0) if entry_data else 0
                    alevel_value = alevel_value if alevel_value is not None else 0
                    default_grade = 'A' if alevel_value > 0 else 'B'
                    
                    req_id = generate_id('REQ_')
                    cur.execute("""
                        INSERT INTO course_requirement (req_id, course_id, subject_id, grade_req)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (req_id) DO NOTHING
                    """, (req_id, course_id, subject_id, default_grade))
            
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
        cur.execute("SELECT COUNT(*) as count FROM course_requirement")
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
