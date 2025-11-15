"""
Database initialization script for PostgreSQL
Creates database and runs migrations
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path

# Fix Windows console encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Database configuration
DB_NAME = os.getenv('POSTGRES_DB', 'university_recommender')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')


def read_sql_file(file_path):
    """Read SQL file content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def create_database():
    """Create database if it doesn't exist"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (DB_NAME,)
        )
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE {DB_NAME}')
            print(f"✓ Database '{DB_NAME}' created successfully")
        else:
            print(f"✓ Database '{DB_NAME}' already exists")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        raise


def run_migrations():
    """Run migration files"""
    migrations_dir = Path(__file__).parent / 'migrations'
    
    if not migrations_dir.exists():
        print(f"✗ Migrations directory not found: {migrations_dir}")
        return
    
    # Get all SQL files sorted by name
    migration_files = sorted(migrations_dir.glob('*.sql'))
    
    if not migration_files:
        print("✗ No migration files found")
        return
    
    try:
        # Connect to target database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        # Create migration tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        for migration_file in migration_files:
            version = migration_file.stem
            
            # Check if migration already applied
            cursor.execute(
                "SELECT version FROM schema_migrations WHERE version = %s",
                (version,)
            )
            if cursor.fetchone():
                print(f"  ⊙ Migration {version} already applied, skipping")
                continue
            
            print(f"  → Running migration: {migration_file.name}")
            sql_content = read_sql_file(migration_file)
            
            try:
                cursor.execute(sql_content)
                cursor.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s)",
                    (version,)
                )
                conn.commit()
                print(f"  ✓ Migration {version} applied successfully")
            except Exception as e:
                conn.rollback()
                print(f"  ✗ Error applying migration {version}: {e}")
                raise
        
        cursor.close()
        conn.close()
        print("✓ All migrations completed successfully")
        
    except Exception as e:
        print(f"✗ Error running migrations: {e}")
        raise


def main():
    """Main initialization function"""
    print("=" * 60)
    print("PostgreSQL Database Initialization")
    print("=" * 60)
    
    try:
        create_database()
        run_migrations()
        print("\n" + "=" * 60)
        print("✓ Database initialization complete!")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ Initialization failed: {e}")
        print("=" * 60)
        exit(1)


if __name__ == '__main__':
    main()

