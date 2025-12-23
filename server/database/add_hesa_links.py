"""Add HESA link columns to course table"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database_helper import get_db_connection

def add_hesa_links():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Add HESA link columns
        cur.execute("""
            ALTER TABLE course
            ADD COLUMN IF NOT EXISTS pubukprn VARCHAR(10),
            ADD COLUMN IF NOT EXISTS kiscourseid VARCHAR(50),
            ADD COLUMN IF NOT EXISTS kismode VARCHAR(2)
        """)
        
        # Create index
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_course_hesa_link 
            ON course(pubukprn, kiscourseid, kismode)
        """)
        
        conn.commit()
        print("OK: Added HESA link columns to course table")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        raise

if __name__ == '__main__':
    add_hesa_links()
