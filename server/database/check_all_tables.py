#!/usr/bin/env python3
"""
Comprehensive database table checker for Project Sigma
Checks row counts in all HESA import tables and application tables
"""

import psycopg2
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from database_helper import get_db_connection

def check_all_tables():
    """Check row counts in all database tables"""
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        print("=" * 80)
        print("COMPREHENSIVE DATABASE TABLE CHECK - Project Sigma")
        print("=" * 80)
        
        # Get all table names from the database
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        all_tables = [row[0] for row in cur.fetchall()]
        print(f"Found {len(all_tables)} tables in database\n")
        
        # Define table categories explicitly
        hesa_tables = [
            'hesa_institution', 'hesa_kiscourse', 'hesa_sbj', 'hesa_entry', 
            'hesa_tariff', 'hesa_employment', 'hesa_joblist', 'hesa_gosalary', 
            'hesa_leo3', 'hesa_ucascourseid'
        ]
        
        app_tables = [
            'university', 'course', 'subject', 'course_subject_requirement', 
            'career_interest', 'entrance_exam', 'student', 'student_grade',
            'student_career_interest', 'student_preferred_exam', 'course_required_exam',
            'recommendation_run', 'recommendation_result', 'subject_to_career'
        ]
        
        system_tables = ['schema_migrations']
        
        # Filter to only tables that actually exist
        existing_hesa = [t for t in hesa_tables if t in all_tables]
        existing_app = [t for t in app_tables if t in all_tables]  
        existing_system = [t for t in system_tables if t in all_tables]
        other_tables = [t for t in all_tables if t not in hesa_tables + app_tables + system_tables]
        
        # Build comprehensive SQL query
        sql_parts = []
        
        # HESA Tables section
        print("HESA IMPORT TABLES")
        print("-" * 40)
        for table in sorted(existing_hesa):
            table_display = table.replace('hesa_', '').upper()
            sql_parts.append(f"SELECT 'HESA_{table_display}' as table_name, COUNT(*) as count, 'hesa' as category FROM {table}")
        
        # Application Tables section  
        print(f"\nAPPLICATION TABLES")
        print("-" * 40)
        for table in sorted(existing_app):
            table_display = table.replace('_', ' ').title()
            sql_parts.append(f"SELECT '{table_display}' as table_name, COUNT(*) as count, 'app' as category FROM {table}")
        
        # System Tables section
        if existing_system:
            print(f"\nSYSTEM TABLES")
            print("-" * 40)
            for table in sorted(existing_system):
                table_display = table.replace('_', ' ').title()
                sql_parts.append(f"SELECT '{table_display}' as table_name, COUNT(*) as count, 'system' as category FROM {table}")
        
        # Other Tables
        if other_tables:
            print(f"\n❓ OTHER TABLES")
            print("-" * 40)
            for table in sorted(other_tables):
                table_display = table.replace('_', ' ').title()
                sql_parts.append(f"SELECT '{table_display}' as table_name, COUNT(*) as count, 'other' as category FROM {table}")
        
        # Execute the comprehensive query
        if sql_parts:
            full_query = "\nUNION ALL\n".join(sql_parts) + "\nORDER BY category, table_name"
            
            cur.execute(full_query)
            results = cur.fetchall()
            
            current_category = None
            total_hesa = 0
            total_app = 0
            total_system = 0
            
            for table_name, count, category in results:
                # Print category header
                if category != current_category:
                    if category == 'hesa':
                        print("HESA IMPORT TABLES")
                        print("-" * 40)
                    elif category == 'app':
                        print("\nAPPLICATION TABLES") 
                        print("-" * 40)
                    elif category == 'system':
                        print("\nSYSTEM TABLES")
                        print("-" * 40)
                    elif category == 'other':
                        print("\n❓ OTHER TABLES")
                        print("-" * 40)
                    current_category = category
                
                # Format the output nicely
                if count == 0 and 'migration' not in table_name.lower():
                    status = "EMPTY"
                elif count < 100 and 'migration' not in table_name.lower():
                    status = "LOW"
                else:
                    status = "OK"
                
                print(f"{table_name:<25} {count:>10,} {status:>8}")
                
                # Track totals
                if category == 'hesa':
                    total_hesa += count
                elif category == 'app':
                    total_app += count
                elif category == 'system':
                    total_system += count
            
            print("\n" + "=" * 60)
            print("SUMMARY STATISTICS")
            print("=" * 60)
            print(f"{'HESA Records Total:':<25} {total_hesa:>15,}")
            print(f"{'Application Records:':<25} {total_app:>15,}")
            print(f"{'System Records:':<25} {total_system:>15,}")
            print(f"{'Total Database Records:':<25} {total_hesa + total_app + total_system:>15,}")
            print(f"{'Number of Tables:':<25} {len(all_tables):>15}")
            
            # Additional insights
            print("\nKEY METRICS")
            print("-" * 30)
            
            # Check specific important relationships
            cur.execute("SELECT COUNT(*) FROM course")
            course_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM course_subject_requirement") 
            req_count = cur.fetchone()[0]
            
            if course_count > 0:
                coverage = (req_count / course_count) * 100
                print(f"Course Requirement Coverage: {coverage:.1f}%")
            
            cur.execute("SELECT COUNT(DISTINCT sbj) FROM hesa_sbj")
            cah_codes = cur.fetchone()[0]
            print(f"Unique CAH Codes: {cah_codes}")
            
            cur.execute("SELECT COUNT(*) FROM university")
            uni_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM hesa_institution")
            hesa_uni_count = cur.fetchone()[0]
            
            if hesa_uni_count > 0:
                uni_mapping = (uni_count / hesa_uni_count) * 100
                print(f"University Mapping Rate: {uni_mapping:.1f}%")
            
        else:
            print("No tables found in database")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error checking tables: {e}")
        return False
        
    return True

if __name__ == "__main__":
    success = check_all_tables()
    if not success:
        sys.exit(1)
    
    print("\nDatabase check completed successfully!")
    print("=" * 80)