"""
Import hardcoded recommendation engine mappings into database tables
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database_helper import get_db_connection
from psycopg2.extras import execute_batch

def import_grade_values():
    """Import grade values"""
    grade_values = [
        ('A*', 8, 'Highest grade'),
        ('A', 7, 'Excellent grade'),
        ('B', 6, 'Good grade'),
        ('C', 5, 'Average grade'),
        ('D', 4, 'Below average grade'),
        ('E', 3, 'Low grade'),
        ('U', 0, 'Ungraded')
    ]
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_batch(
                cur,
                """
                INSERT INTO grade_value (grade, numeric_value, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (grade) DO UPDATE
                SET numeric_value = EXCLUDED.numeric_value,
                    description = EXCLUDED.description
                """,
                grade_values
            )
            conn.commit()
            print(f"  OK Imported {len(grade_values)} grade values")

def import_regions():
    """Regions are now loaded directly from university table (HESA data) - no import needed"""
    print("  OK Regions are loaded from university.region column (HESA data)")

def import_subject_mappings():
    """Import subject related term mappings"""
    subject_mappings = [
        ('english language', 'english', 'related'),
        ('english language', 'literature', 'related'),
        ('english language', 'language', 'related'),
        ('english language', 'writing', 'related'),
        ('english language', 'linguistics', 'related'),
        ('english language', 'humanities', 'category'),
        ('english literature', 'english', 'related'),
        ('english literature', 'literature', 'related'),
        ('english literature', 'language', 'related'),
        ('english literature', 'writing', 'related'),
        ('english literature', 'humanities', 'category'),
        ('philosophy', 'philosophy', 'synonym'),
        ('philosophy', 'ethics', 'related'),
        ('philosophy', 'theology', 'related'),
        ('philosophy', 'religious studies', 'related'),
        ('philosophy', 'politics', 'related'),
        ('philosophy', 'humanities', 'category'),
        ('philosophy', 'philosophical', 'synonym'),
        ('mathematics', 'mathematics', 'synonym'),
        ('mathematics', 'maths', 'synonym'),
        ('mathematics', 'math', 'synonym'),
        ('mathematics', 'statistics', 'related'),
        ('mathematics', 'computing', 'related'),
        ('mathematics', 'computer science', 'related'),
        ('further mathematics', 'mathematics', 'related'),
        ('further mathematics', 'maths', 'synonym'),
        ('further mathematics', 'math', 'synonym'),
        ('further mathematics', 'statistics', 'related'),
        ('further mathematics', 'computing', 'related'),
        ('further mathematics', 'computer science', 'related'),
        ('physics', 'physics', 'synonym'),
        ('physics', 'engineering', 'related'),
        ('physics', 'mathematics', 'related'),
        ('physics', 'computing', 'related'),
        ('physics', 'computer science', 'related'),
        ('chemistry', 'chemistry', 'synonym'),
        ('chemistry', 'biology', 'related'),
        ('chemistry', 'medicine', 'related'),
        ('chemistry', 'pharmacy', 'related'),
        ('biology', 'biology', 'synonym'),
        ('biology', 'medicine', 'related'),
        ('biology', 'pharmacy', 'related'),
        ('biology', 'chemistry', 'related'),
        ('biology', 'biochemistry', 'related'),
        ('history', 'history', 'synonym'),
        ('history', 'politics', 'related'),
        ('history', 'archaeology', 'related'),
        ('history', 'humanities', 'category'),
        ('geography', 'geography', 'synonym'),
        ('geography', 'environmental', 'related'),
        ('geography', 'geology', 'related'),
        ('geography', 'urban planning', 'related'),
        ('economics', 'economics', 'synonym'),
        ('economics', 'business', 'related'),
        ('economics', 'finance', 'related'),
        ('economics', 'accounting', 'related'),
        ('economics', 'politics', 'related'),
        ('business studies', 'business', 'synonym'),
        ('business studies', 'economics', 'related'),
        ('business studies', 'finance', 'related'),
        ('business studies', 'accounting', 'related'),
        ('business studies', 'management', 'related'),
        ('psychology', 'psychology', 'synonym'),
        ('psychology', 'sociology', 'related'),
        ('psychology', 'neuroscience', 'related'),
        ('psychology', 'criminology', 'related'),
        ('sociology', 'sociology', 'synonym'),
        ('sociology', 'psychology', 'related'),
        ('sociology', 'politics', 'related'),
        ('sociology', 'criminology', 'related'),
        ('sociology', 'social work', 'related'),
        ('politics', 'politics', 'synonym'),
        ('politics', 'international relations', 'related'),
        ('politics', 'history', 'related'),
        ('politics', 'philosophy', 'related'),
        ('politics', 'economics', 'related'),
        ('art', 'art', 'synonym'),
        ('art', 'design', 'related'),
        ('art', 'fine art', 'related'),
        ('art', 'creative', 'related'),
        ('art', 'visual arts', 'related'),
        ('design technology', 'design', 'synonym'),
        ('design technology', 'engineering', 'related'),
        ('design technology', 'technology', 'synonym'),
        ('design technology', 'product design', 'related'),
        ('computer science', 'computer science', 'synonym'),
        ('computer science', 'computing', 'synonym'),
        ('computer science', 'software', 'related'),
        ('computer science', 'it', 'related'),
        ('computer science', 'mathematics', 'related'),
        ('computer science', 'physics', 'related')
    ]
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_batch(
                cur,
                """
                INSERT INTO subject_related_term (subject_name, related_term, match_type)
                VALUES (%s, %s, %s)
                ON CONFLICT (subject_name, related_term) DO UPDATE
                SET match_type = EXCLUDED.match_type
                """,
                subject_mappings
            )
            conn.commit()
            print(f"  OK Imported {len(subject_mappings)} subject mappings")

def import_generic_terms():
    """Import generic terms"""
    generic_terms = [
        ('science', 'Generic term for scientific subjects', 3),
        ('studies', 'Generic term for study-based subjects', 3),
        ('business', 'Generic term for business-related subjects', 3),
        ('management', 'Generic term for management subjects', 3),
        ('technology', 'Generic term for technology subjects', 3),
        ('design', 'Generic term for design subjects', 3),
        ('art', 'Generic term for art subjects', 3)
    ]
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_batch(
                cur,
                """
                INSERT INTO generic_term (term, description, min_length)
                VALUES (%s, %s, %s)
                ON CONFLICT (term) DO UPDATE
                SET description = EXCLUDED.description,
                    min_length = EXCLUDED.min_length
                """,
                generic_terms
            )
            conn.commit()
            print(f"  OK Imported {len(generic_terms)} generic terms")

def import_generic_term_rules():
    """Import generic term matching rules"""
    # Rules for when generic terms can legitimately match
    # Format: (generic_term, rule_type, rule_value, description)
    rules = [
        ('science', 'contains', 'science', 'Subject contains "science"'),
        ('science', 'in_list', 'physics,chemistry,biology', 'Subject is physics, chemistry, or biology'),
        ('studies', 'contains', 'studies', 'Subject contains "studies"'),
        ('business', 'contains', 'business', 'Subject contains "business"'),
        ('business', 'contains', 'economics', 'Subject contains "economics"'),
        ('management', 'contains', 'business', 'Subject contains "business"'),
        ('management', 'contains', 'management', 'Subject contains "management"'),
        ('technology', 'contains', 'technology', 'Subject contains "technology"'),
        ('technology', 'contains', 'engineering', 'Subject contains "engineering"'),
        ('design', 'contains', 'design', 'Subject contains "design"'),
        ('design', 'contains', 'art', 'Subject contains "art"'),
        ('art', 'contains', 'art', 'Subject contains "art"'),
        ('art', 'contains', 'design', 'Subject contains "design"')
    ]
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_batch(
                cur,
                """
                INSERT INTO generic_term_rule (generic_term, rule_type, rule_value, description)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                rules
            )
            conn.commit()
            print(f"  OK Imported {len(rules)} generic term rules")

def import_feedback_settings():
    """Import feedback settings"""
    settings = [
        ('feedback_weight', 0.15, 'Weight of feedback in final score (0-1)'),
        ('feedback_decay_days', 90, 'Feedback relevance decays after this many days'),
        ('min_feedback_count', 3, 'Minimum feedback count to apply feedback boost'),
        ('positive_feedback_boost', 0.2, 'Score boost for positive feedback'),
        ('negative_feedback_penalty', -0.3, 'Score penalty for negative feedback')
    ]
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_batch(
                cur,
                """
                INSERT INTO feedback_setting (setting_key, setting_value, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (setting_key) DO UPDATE
                SET setting_value = EXCLUDED.setting_value,
                    description = EXCLUDED.description,
                    updated_at = CURRENT_TIMESTAMP
                """,
                settings
            )
            conn.commit()
            print(f"  OK Imported {len(settings)} feedback settings")

def import_recommendation_weights():
    """Import recommendation engine weights"""
    weights = [
        ('subject_match', 0.35, 'A-level subject alignment'),
        ('grade_match', 0.25, 'Predicted grades vs requirements'),
        ('preference_match', 0.15, 'Student preferences (location, budget, etc.)'),
        ('university_ranking', 0.15, 'University prestige/ranking'),
        ('employability', 0.10, 'Graduate employment prospects')
    ]
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_batch(
                cur,
                """
                INSERT INTO recommendation_weight (weight_key, weight_value, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (weight_key) DO UPDATE
                SET weight_value = EXCLUDED.weight_value,
                    description = EXCLUDED.description,
                    updated_at = CURRENT_TIMESTAMP
                """,
                weights
            )
            conn.commit()
            print(f"  OK Imported {len(weights)} recommendation weights")

if __name__ == '__main__':
    print("="*70)
    print("IMPORTING RECOMMENDATION ENGINE CONFIGURATION")
    print("="*70)
    
    print("\n[1/7] Importing grade values...")
    import_grade_values()
    
    print("\n[2/7] Region mappings (skipped - using university.region from HESA data)...")
    import_regions()
    
    print("\n[3/7] Subject mappings (skipped - using CAH codes from subject_course_mapping)...")
    print("  OK Subject matching now uses CAH codes instead of related terms")
    
    print("\n[4/7] Generic terms (skipped - using CAH codes from subject_course_mapping)...")
    print("  OK Subject matching now uses CAH codes instead of generic terms")
    
    print("\n[5/7] Generic term rules (skipped - using CAH codes from subject_course_mapping)...")
    print("  OK Subject matching now uses CAH codes instead of generic term rules")
    
    print("\n[6/7] Importing feedback settings...")
    import_feedback_settings()
    
    print("\n[7/7] Importing recommendation weights...")
    import_recommendation_weights()
    
    print("\n" + "="*70)
    print("IMPORT COMPLETE")
    print("="*70)

