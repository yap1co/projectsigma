"""
Run the feedback migration to create recommendation_feedback and recommendation_settings tables
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
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    parent_env = Path(__file__).parent.parent / '.env'
    if parent_env.exists():
        load_dotenv(parent_env)

# Database configuration
DB_NAME = os.getenv('POSTGRES_DB', 'university_recommender')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

def run_migration():
    """Run the feedback migration"""
    migration_file = Path(__file__).parent / 'migrations' / '004_recommendation_feedback.sql'
    
    if not migration_file.exists():
        print(f"✗ Migration file not found: {migration_file}")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        print(f"→ Running migration: {migration_file.name}")
        
        # Read and execute migration
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        cursor.execute(sql_content)
        conn.commit()
        
        print("✓ Migration applied successfully")
        print("✓ Tables created:")
        print("  - recommendation_feedback")
        print("  - recommendation_settings")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.errors.DuplicateTable:
        print("⚠ Tables already exist, skipping migration")
        conn.rollback()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Error applying migration: {e}")
        if 'conn' in locals():
            conn.rollback()
            cursor.close()
            conn.close()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Running Feedback System Migration")
    print("=" * 60)
    
    if run_migration():
        print("\n" + "=" * 60)
        print("✓ Migration complete!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ Migration failed!")
        print("=" * 60)
        sys.exit(1)
