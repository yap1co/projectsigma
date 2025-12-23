"""
Check if HESA data has been imported and what tables exist
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database_helper import get_db_connection
from psycopg2.extras import RealDictCursor

def check_database():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("="*70)
    print("DATABASE STATUS CHECK")
    print("="*70)
    
    # Check what tables exist
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('institution', 'kiscourse', 'university', 'course', 'entry', 'sbj', 'employment')
        ORDER BY table_name
    """)
    tables = cur.fetchall()
    table_names = [t['table_name'] for t in tables]
    
    print("\nTables found:")
    for name in table_names:
        print(f"  - {name}")
    
    # Check counts
    print("\nData counts:")
    
    if 'institution' in table_names:
        cur.execute("SELECT COUNT(*) as count FROM institution")
        count = cur.fetchone()['count']
        print(f"  Institutions (HESA): {count}")
    
    if 'kiscourse' in table_names:
        cur.execute("SELECT COUNT(*) as count FROM kiscourse")
        count = cur.fetchone()['count']
        print(f"  KIS Courses (HESA): {count}")
    
    if 'university' in table_names:
        cur.execute("SELECT COUNT(*) as count FROM university")
        count = cur.fetchone()['count']
        print(f"  Universities (main): {count}")
    
    if 'course' in table_names:
        cur.execute("SELECT COUNT(*) as count FROM course")
        count = cur.fetchone()['count']
        print(f"  Courses (main): {count}")
    
    if 'course_requirement' in table_names:
        cur.execute("SELECT COUNT(*) as count FROM course_requirement")
        count = cur.fetchone()['count']
        print(f"  Course Requirements: {count}")
    
    cur.close()
    conn.close()
    
    print("\n" + "="*70)
    if 'institution' in table_names and 'kiscourse' in table_names:
        print("HESA data tables found! Run map_hesa_to_main_tables.py to populate main tables.")
    elif 'university' in table_names and 'course' in table_names:
        print("Main tables exist. If you have HESA CSV files, import them first.")
    else:
        print("No data found. Please import HESA data first.")
    print("="*70)

if __name__ == '__main__':
    check_database()
