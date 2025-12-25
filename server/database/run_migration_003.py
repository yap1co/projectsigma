"""
Apply migration 003: Rename HESA tables with hesa_ prefix
"""

import sys
from pathlib import Path

# Add parent directory to path to import database_helper
sys.path.insert(0, str(Path(__file__).parent.parent))

from database_helper import get_db_connection
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migration():
    """Apply migration 003: Rename HESA tables"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        logger.info("="*70)
        logger.info("APPLYING MIGRATION 003: Rename HESA tables")
        logger.info("="*70)
        
        # Read migration file
        migration_path = Path(__file__).parent / 'migrations' / '003_rename_hesa_tables.sql'
        logger.info(f"Reading migration file: {migration_path}")
        
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Execute migration
        logger.info("Executing migration SQL...")
        cur.execute(sql)
        conn.commit()
        
        logger.info("✅ Migration 003 applied successfully")
        
        # Verify renamed tables exist
        logger.info("\nVerifying renamed tables...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_name LIKE 'hesa_%'
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        logger.info(f"\n✅ Found {len(tables)} HESA tables:")
        for table in tables:
            logger.info(f"  - {table[0]}")
        
        # Verify old tables are gone
        logger.info("\nVerifying old table names removed...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_name IN ('institution', 'kiscourse', 'employment', 'entry', 'gosalary', 'joblist', 'leo3')
        """)
        
        old_tables = cur.fetchall()
        if old_tables:
            logger.warning(f"⚠️ Old tables still exist: {[t[0] for t in old_tables]}")
        else:
            logger.info("✅ Old table names successfully removed")
        
        # Check schema_migrations table
        logger.info("\nChecking schema_migrations table...")
        cur.execute("SELECT version, applied_at FROM schema_migrations ORDER BY version")
        migrations = cur.fetchall()
        logger.info(f"\n✅ Applied migrations ({len(migrations)}):")
        for version, applied_at in migrations:
            logger.info(f"  - Version {version} (applied {applied_at})")
        
        logger.info("\n" + "="*70)
        logger.info("MIGRATION 003 COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    try:
        run_migration()
    except Exception as e:
        logger.error(f"Failed to apply migration: {e}")
        sys.exit(1)
