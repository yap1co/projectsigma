import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Require password to be set explicitly
db_password = os.getenv('POSTGRES_PASSWORD')
if not db_password:
    raise RuntimeError(
        "POSTGRES_PASSWORD environment variable is not set. "
        "Please create server/.env file with database credentials."
    )

conn = psycopg2.connect(
    dbname='university_recommender',
    user=os.getenv('POSTGRES_USER', 'postgres'),
    password=db_password,
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    port=os.getenv('POSTGRES_PORT', '5432')
)
cur = conn.cursor()
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
tables = cur.fetchall()

print(f"\nTotal tables: {len(tables)}\n")
for table in tables:
    print(f"  - {table[0]}")

cur.close()
conn.close()
