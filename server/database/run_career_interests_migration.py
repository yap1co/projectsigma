"""
Run the career interests migration (005_career_interests.sql)
This creates tables for managing career interests, keywords, and conflicts in the database
"""

import os
import sys
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB', 'university_recommender')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')

def read_sql_file(file_path: Path) -> str:
    """Read SQL file content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def run_migration():
    """Run the career interests migration"""
    migration_file = Path(__file__).parent / 'migrations' / '005_career_interests.sql'
    
    if not migration_file.exists():
        print(f"✗ Migration file not found: {migration_file}")
        return False
    
    try:
        print(f"→ Running migration: {migration_file.name}")
        sql_content = read_sql_file(migration_file)
        
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_content)
            conn.commit()
            print("✓ Migration applied successfully")
            return True
        except psycopg2.errors.DuplicateTable:
            conn.rollback()
            print("⊙ Tables already exist, skipping")
            return True
        except Exception as e:
            conn.rollback()
            print(f"✗ Error applying migration: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"✗ Error running migration: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Career Interests Migration")
    print("=" * 60)
    success = run_migration()
    if success:
        print("=" * 60)
        print("✓ Migration completed")
        print("=" * 60)
    else:
        print("=" * 60)
        print("✗ Migration failed")
        print("=" * 60)
        sys.exit(1)
