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

# Get all tables
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
tables = [row[0] for row in cur.fetchall()]

print(f"\n{'Table Name':<35} {'Row Count':>15}")
print("=" * 52)

total_rows = 0
for table in tables:
    if table != 'schema_migrations':
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        total_rows += count
        status = "✓" if count > 0 else "⚠ EMPTY"
        print(f"{table:<35} {count:>10,} {status:>10}")

print("=" * 52)
print(f"{'TOTAL':<35} {total_rows:>10,}")

cur.close()
conn.close()
