"""Check if university URLs are in database"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database_helper import get_db_connection
from psycopg2.extras import RealDictCursor

conn = get_db_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)

cur.execute("SELECT COUNT(*) as total FROM university WHERE website_url IS NOT NULL AND website_url != ''")
total = cur.fetchone()['total']
print(f"Universities with URLs: {total}")

cur.execute("SELECT name, website_url FROM university WHERE website_url IS NOT NULL LIMIT 10")
for row in cur.fetchall():
    print(f"  {row['name']}: {row['website_url']}")

cur.close()
conn.close()
