"""Update university website_url from institution.provurl"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database_helper import get_db_connection
from psycopg2.extras import RealDictCursor

def update_university_urls():
    """Update university website_url from institution.provurl using pubukprn mapping via courses"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Use course.pubukprn to link universities to institutions
        # This is the most reliable way since courses have pubukprn stored
        cur.execute("""
            UPDATE university u
            SET website_url = CASE 
                WHEN i.provurl IS NOT NULL AND i.provurl != '' THEN
                    CASE 
                        WHEN i.provurl LIKE 'http://%' OR i.provurl LIKE 'https://%' 
                        THEN i.provurl
                        ELSE 'https://' || LTRIM(i.provurl, '/')
                    END
                ELSE u.website_url
            END
            FROM (
                SELECT DISTINCT c.university_id, c.pubukprn
                FROM course c
                WHERE c.pubukprn IS NOT NULL
            ) course_links
            JOIN institution i ON course_links.pubukprn = i.pubukprn
            WHERE course_links.university_id = u.university_id
              AND i.provurl IS NOT NULL 
              AND i.provurl != ''
              AND (u.website_url IS NULL OR u.website_url = '')
        """)
        
        updated = cur.rowcount
        conn.commit()
        
        if updated > 0:
            print(f"OK: Updated {updated} universities with website URLs from PROVURL")
        else:
            print("INFO: No universities needed URL updates (may already be set)")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    update_university_urls()
