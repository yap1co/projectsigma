"""
Sample Data Import Script - Traditional Approach
Imports just a few rows from each CSV to understand relationships
"""

import os
import sys
import csv
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path

# Database configuration
DB_NAME = os.getenv('POSTGRES_DB', 'discover_uni_db')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

# Number of sample rows to import from each CSV
SAMPLE_ROWS = 5


def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def normalize_value(value):
    """Normalize CSV values"""
    if value is None:
        return None
    value = str(value).strip()
    return value if value else None


def normalize_int(value):
    """Convert to integer"""
    if not value or value.strip() == '':
        return None
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return None


def normalize_numeric(value):
    """Convert to numeric"""
    if not value or value.strip() == '':
        return None
    try:
        return float(value.strip())
    except (ValueError, AttributeError):
        return None


def read_sample_csv(file_path, num_rows=SAMPLE_ROWS):
    """Read first N rows from CSV file"""
    if not file_path.exists():
        print(f"  ✗ File not found: {file_path}")
        return []
    
    rows = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= num_rows:
                    break
                rows.append(row)
        print(f"  → Read {len(rows)} sample rows from {file_path.name}")
    except Exception as e:
        print(f"  ✗ Error reading {file_path.name}: {e}")
        return []
    
    return rows


def import_sample_lookup_tables(cursor, data_dir):
    """Import sample lookup tables"""
    print("\n" + "="*70)
    print("STEP 1: IMPORTING SAMPLE LOOKUP TABLES")
    print("="*70)
    
    # KIS Aim
    print("\n[1/3] Importing sample KISAIM.csv...")
    rows = read_sample_csv(data_dir / 'KISAIM.csv', SAMPLE_ROWS)
    if rows:
        data = [
            (normalize_value(row.get('KISAIMCODE')), normalize_value(row.get('KISAIMLABEL')))
            for row in rows
            if normalize_value(row.get('KISAIMCODE'))
        ]
        if data:
            execute_values(
                cursor,
                """
                INSERT INTO discover_uni.kis_aim (kisaimcode, kisaimlabel)
                VALUES %s
                ON CONFLICT (kisaimcode) DO UPDATE
                SET kisaimlabel = EXCLUDED.kisaimlabel
                """,
                data
            )
            print(f"  ✓ Imported {len(data)} KIS Aim records")
    
    # Accreditation Table
    print("\n[2/3] Importing sample ACCREDITATIONTABLE.csv...")
    rows = read_sample_csv(data_dir / 'ACCREDITATIONTABLE.csv', SAMPLE_ROWS)
    if rows:
        data = [
            (
                normalize_value(row.get('ACCTYPE')),
                normalize_value(row.get('ACCURL')),
                normalize_value(row.get('ACCTEXT')),
                normalize_value(row.get('ACCTEXTW'))
            )
            for row in rows
            if normalize_value(row.get('ACCTYPE'))
        ]
        if data:
            execute_values(
                cursor,
                """
                INSERT INTO discover_uni.accreditation_table (acctype, accurl, acctext, acctextw)
                VALUES %s
                ON CONFLICT (acctype) DO UPDATE
                SET accurl = EXCLUDED.accurl,
                    acctext = EXCLUDED.acctext,
                    acctextw = EXCLUDED.acctextw
                """,
                data
            )
            print(f"  ✓ Imported {len(data)} Accreditation Table records")
    
    # Location
    print("\n[3/3] Importing sample LOCATION.csv...")
    rows = read_sample_csv(data_dir / 'LOCATION.csv', SAMPLE_ROWS)
    if rows:
        data = [
            (
                normalize_value(row.get('UKPRN')),
                normalize_value(row.get('LOCID')),
                normalize_value(row.get('LOCNAME')),
                normalize_value(row.get('LOCNAMEW')),
                normalize_numeric(row.get('LATITUDE')),
                normalize_numeric(row.get('LONGITUDE')),
                normalize_value(row.get('ACCOMURL')),
                normalize_value(row.get('ACCOMURLW')),
                normalize_value(row.get('LOCUKPRN')),
                normalize_value(row.get('LOCCOUNTRY')),
                normalize_value(row.get('SUURL')),
                normalize_value(row.get('SUURLW'))
            )
            for row in rows
            if normalize_value(row.get('UKPRN')) and normalize_value(row.get('LOCID'))
        ]
        if data:
            execute_values(
                cursor,
                """
                INSERT INTO discover_uni.location (ukprn, locid, locname, locnamew, latitude, longitude,
                                                 accomurl, accomurlw, locukprn, loccountry, suurl, suurlw)
                VALUES %s
                ON CONFLICT (ukprn, locid) DO UPDATE
                SET locname = EXCLUDED.locname,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude
                """,
                data
            )
            print(f"  ✓ Imported {len(data)} Location records")


def import_sample_core_entities(cursor, data_dir):
    """Import sample core entities"""
    print("\n" + "="*70)
    print("STEP 2: IMPORTING SAMPLE CORE ENTITIES")
    print("="*70)
    
    # Institution
    print("\n[1/2] Importing sample INSTITUTION.csv...")
    rows = read_sample_csv(data_dir / 'INSTITUTION.csv', SAMPLE_ROWS)
    if rows:
        data = [
            (
                normalize_value(row.get('PUBUKPRN')),
                normalize_value(row.get('UKPRN')),
                normalize_value(row.get('LEGAL_NAME')),
                normalize_value(row.get('FIRST_TRADING_NAME')),
                normalize_value(row.get('OTHER_NAMES')),
                normalize_value(row.get('PROVADDRESS')),
                normalize_value(row.get('PROVTEL')),
                normalize_value(row.get('PROVURL')),
                normalize_value(row.get('COUNTRY')),
                normalize_value(row.get('PUBUKPRNCOUNTRY')),
                normalize_value(row.get('QAA_Report_Type')),
                normalize_value(row.get('QAA_URL')),
                normalize_value(row.get('SUURL')),
                normalize_value(row.get('SUURLW'))
            )
            for row in rows
            if normalize_value(row.get('PUBUKPRN'))
        ]
        if data:
            execute_values(
                cursor,
                """
                INSERT INTO discover_uni.institution (pubukprn, ukprn, legal_name, first_trading_name, other_names,
                                                      provaddress, provtel, provurl, country, pubukprncountry,
                                                      qaa_report_type, qaa_url, suurl, suurlw)
                VALUES %s
                ON CONFLICT (pubukprn) DO UPDATE
                SET legal_name = EXCLUDED.legal_name
                """,
                data
            )
            print(f"  ✓ Imported {len(data)} Institution records")
    
    # KIS Course
    print("\n[2/2] Importing sample KISCOURSE.csv...")
    rows = read_sample_csv(data_dir / 'KISCOURSE.csv', SAMPLE_ROWS)
    if rows:
        data = []
        for row in rows:
            pubukprn = normalize_value(row.get('PUBUKPRN'))
            kiscourseid = normalize_value(row.get('KISCOURSEID'))
            kismode = normalize_value(row.get('KISMODE'))
            
            if pubukprn and kiscourseid and kismode:
                data.append((
                    pubukprn,
                    normalize_value(row.get('UKPRN')),
                    kiscourseid,
                    kismode,
                    normalize_value(row.get('TITLE')),
                    normalize_value(row.get('TITLEW')),
                    normalize_value(row.get('ASSURL')),
                    normalize_value(row.get('ASSURLW')),
                    normalize_value(row.get('CRSECSTURL')),
                    normalize_value(row.get('CRSECSTURLW')),
                    normalize_value(row.get('CRSEURL')),
                    normalize_value(row.get('CRSEURLW')),
                    normalize_value(row.get('DISTANCE')),
                    normalize_value(row.get('EMPLOYURL')),
                    normalize_value(row.get('EMPLOYURLW')),
                    normalize_value(row.get('FOUNDATION')),
                    normalize_value(row.get('HONOURS')),
                    normalize_value(row.get('HECOS')),
                    normalize_value(row.get('HECOS2')) if 'HECOS2' in row else None,
                    normalize_value(row.get('HECOS3')) if 'HECOS3' in row else None,
                    normalize_value(row.get('HECOS4')) if 'HECOS4' in row else None,
                    normalize_value(row.get('HECOS5')) if 'HECOS5' in row else None,
                    normalize_value(row.get('LOCCHNGE')),
                    normalize_value(row.get('LTURL')),
                    normalize_value(row.get('LTURLW')),
                    normalize_value(row.get('NHS')),
                    normalize_int(row.get('NUMSTAGE')),
                    normalize_value(row.get('SANDWICH')),
                    normalize_value(row.get('SUPPORTURL')),
                    normalize_value(row.get('SUPPORTURLW')),
                    normalize_value(row.get('UCASPROGID')),
                    normalize_value(row.get('UKPRNAPPLY')),
                    normalize_value(row.get('YEARABROAD')),
                    normalize_value(row.get('KISAIMCODE')),
                    normalize_value(row.get('KISLEVEL'))
                ))
        
        if data:
            execute_values(
                cursor,
                """
                INSERT INTO discover_uni.kiscourse (pubukprn, ukprn, kiscourseid, kismode, title, titlew,
                                                   assurl, assurlw, crsecsturl, crsecsturlw, crseurl, crseurlw,
                                                   distance, employurl, employurlw, foundation, honours,
                                                   hecos, hecos2, hecos3, hecos4, hecos5,
                                                   locchnge, lturl, lturlw, nhs, numstage, sandwich,
                                                   supporturl, supporturlw, ucasprogid, ukprnapply,
                                                   yearabroad, kisaimcode, kislevel)
                VALUES %s
                ON CONFLICT (pubukprn, kiscourseid, kismode) DO UPDATE
                SET title = EXCLUDED.title
                """,
                data
            )
            print(f"  ✓ Imported {len(data)} KIS Course records")


def import_sample_related_entities(cursor, data_dir):
    """Import sample related entities"""
    print("\n" + "="*70)
    print("STEP 3: IMPORTING SAMPLE RELATED ENTITIES")
    print("="*70)
    
    # Accreditation
    print("\n[1/3] Importing sample ACCREDITATION.csv...")
    rows = read_sample_csv(data_dir / 'ACCREDITATION.csv', SAMPLE_ROWS)
    if rows:
        data = [
            (
                normalize_value(row.get('PUBUKPRN')),
                normalize_value(row.get('UKPRN')),
                normalize_value(row.get('KISCOURSEID')),
                normalize_value(row.get('KISMODE')),
                normalize_value(row.get('ACCTYPE')),
                normalize_value(row.get('ACCDEPEND')),
                normalize_value(row.get('ACCDEPENDURL')),
                normalize_value(row.get('ACCDEPENDURLW'))
            )
            for row in rows
            if (normalize_value(row.get('PUBUKPRN')) and 
                normalize_value(row.get('KISCOURSEID')) and 
                normalize_value(row.get('KISMODE')))
        ]
        if data:
            execute_values(
                cursor,
                """
                INSERT INTO discover_uni.accreditation (pubukprn, ukprn, kiscourseid, kismode, acctype,
                                                       accdepend, accdependurl, accdependurlw)
                VALUES %s
                ON CONFLICT DO NOTHING
                """,
                data
            )
            print(f"  ✓ Imported {len(data)} Accreditation records")
    
    # Course Location
    print("\n[2/3] Importing sample COURSELOCATION.csv...")
    rows = read_sample_csv(data_dir / 'COURSELOCATION.csv', SAMPLE_ROWS)
    if rows:
        data = []
        for row in rows:
            pubukprn = normalize_value(row.get('PUBUKPRN'))
            kiscourseid = normalize_value(row.get('KISCOURSEID'))
            kismode = normalize_value(row.get('KISMODE'))
            locid = normalize_value(row.get('LOCID'))
            
            if pubukprn and kiscourseid and kismode:
                data.append((
                    pubukprn,
                    normalize_value(row.get('UKPRN')),
                    kiscourseid,
                    kismode,
                    locid
                ))
        
        if data:
            execute_values(
                cursor,
                """
                INSERT INTO discover_uni.courselocation (pubukprn, ukprn, kiscourseid, kismode, locid)
                VALUES %s
                ON CONFLICT DO NOTHING
                """,
                data
            )
            print(f"  ✓ Imported {len(data)} Course Location records")
    
    # Subject (SBJ)
    print("\n[3/3] Importing sample SBJ.csv...")
    rows = read_sample_csv(data_dir / 'SBJ.csv', SAMPLE_ROWS)
    if rows:
        data = [
            (
                normalize_value(row.get('PUBUKPRN')),
                normalize_value(row.get('UKPRN')),
                normalize_value(row.get('KISCOURSEID')),
                normalize_value(row.get('KISMODE')),
                normalize_value(row.get('SBJ'))
            )
            for row in rows
            if (normalize_value(row.get('PUBUKPRN')) and 
                normalize_value(row.get('KISCOURSEID')) and 
                normalize_value(row.get('KISMODE')) and
                normalize_value(row.get('SBJ')))
        ]
        if data:
            execute_values(
                cursor,
                """
                INSERT INTO discover_uni.sbj (pubukprn, ukprn, kiscourseid, kismode, sbj)
                VALUES %s
                ON CONFLICT DO NOTHING
                """,
                data
            )
            print(f"  ✓ Imported {len(data)} Subject records")


def import_sample_outcomes(cursor, data_dir):
    """Import sample student outcomes"""
    print("\n" + "="*70)
    print("STEP 4: IMPORTING SAMPLE STUDENT OUTCOMES")
    print("="*70)
    
    # Entry
    print("\n[1/2] Importing sample ENTRY.csv...")
    rows = read_sample_csv(data_dir / 'ENTRY.csv', SAMPLE_ROWS)
    if rows:
        data = [
            (
                normalize_value(row.get('PUBUKPRN')),
                normalize_value(row.get('UKPRN')),
                normalize_value(row.get('KISCOURSEID')),
                normalize_value(row.get('KISMODE')),
                normalize_value(row.get('ENTUNAVAILREASON')),
                normalize_int(row.get('ENTPOP')),
                normalize_value(row.get('ENTAGG')),
                normalize_value(row.get('ENTAGGYEAR')),
                normalize_value(row.get('ENTYEAR1')),
                normalize_value(row.get('ENTYEAR2')),
                normalize_value(row.get('ENTSBJ')),
                normalize_int(row.get('ACCESS')),
                normalize_int(row.get('ALEVEL')),
                normalize_int(row.get('BACC')),
                normalize_int(row.get('DEGREE')),
                normalize_int(row.get('FOUNDTN')),
                normalize_int(row.get('NOQUALS')),
                normalize_int(row.get('OTHER')),
                normalize_int(row.get('OTHERHE'))
            )
            for row in rows
            if (normalize_value(row.get('PUBUKPRN')) and 
                normalize_value(row.get('KISCOURSEID')) and 
                normalize_value(row.get('KISMODE')))
        ]
        if data:
            execute_values(
                cursor,
                """
                INSERT INTO discover_uni.entry (pubukprn, ukprn, kiscourseid, kismode, entunavailreason,
                                               entpop, entagg, entaggyear, entyear1, entyear2, entsbj,
                                               access, alevel, bacc, degree, foundtn, noquals, other, otherhe)
                VALUES %s
                ON CONFLICT DO NOTHING
                """,
                data
            )
            print(f"  ✓ Imported {len(data)} Entry records")
    
    # Employment
    print("\n[2/2] Importing sample EMPLOYMENT.csv...")
    rows = read_sample_csv(data_dir / 'EMPLOYMENT.csv', SAMPLE_ROWS)
    if rows:
        data = [
            (
                normalize_value(row.get('PUBUKPRN')),
                normalize_value(row.get('UKPRN')),
                normalize_value(row.get('KISCOURSEID')),
                normalize_value(row.get('KISMODE')),
                normalize_value(row.get('EMPUNAVAILREASON')),
                normalize_int(row.get('EMPPOP')),
                normalize_int(row.get('EMPRESPONSE')),
                normalize_int(row.get('EMPSAMPLE')),
                normalize_int(row.get('EMPRESP_RATE')),
                normalize_value(row.get('EMPAGG')),
                normalize_value(row.get('EMPAGGYEAR')),
                normalize_value(row.get('EMPYEAR1')),
                normalize_value(row.get('EMPYEAR2')),
                normalize_value(row.get('EMPSBJ')),
                normalize_int(row.get('WORKSTUDY')),
                normalize_int(row.get('STUDY')),
                normalize_int(row.get('UNEMP')),
                normalize_int(row.get('PREVWORKSTUD')),
                normalize_int(row.get('BOTH')),
                normalize_int(row.get('NOAVAIL')),
                normalize_int(row.get('WORK'))
            )
            for row in rows
            if (normalize_value(row.get('PUBUKPRN')) and 
                normalize_value(row.get('KISCOURSEID')) and 
                normalize_value(row.get('KISMODE')))
        ]
        if data:
            execute_values(
                cursor,
                """
                INSERT INTO discover_uni.employment (pubukprn, ukprn, kiscourseid, kismode, empunavailreason,
                                                    emppop, empresponse, empsample, empresp_rate, empagg,
                                                    empaggyear, empyear1, empyear2, empsbj,
                                                    workstudy, study, unemp, prevworkstud, both, noavail, work)
                VALUES %s
                ON CONFLICT DO NOTHING
                """,
                data
            )
            print(f"  ✓ Imported {len(data)} Employment records")


def verify_relationships(cursor):
    """Verify relationships with sample queries"""
    print("\n" + "="*70)
    print("STEP 5: VERIFYING RELATIONSHIPS")
    print("="*70)
    
    queries = [
        ("Institutions", "SELECT COUNT(*) FROM discover_uni.institution"),
        ("KIS Courses", "SELECT COUNT(*) FROM discover_uni.kiscourse"),
        ("Courses with Institutions", """
            SELECT i.legal_name, COUNT(k.kiscourseid) as course_count
            FROM discover_uni.institution i
            LEFT JOIN discover_uni.kiscourse k ON i.pubukprn = k.pubukprn
            GROUP BY i.legal_name
            LIMIT 5
        """),
        ("Courses with KIS Aims", """
            SELECT k.title, ka.kisaimlabel
            FROM discover_uni.kiscourse k
            LEFT JOIN discover_uni.kis_aim ka ON k.kisaimcode = ka.kisaimcode
            LIMIT 5
        """),
        ("Courses with Accreditations", """
            SELECT k.title, at.acctext
            FROM discover_uni.kiscourse k
            JOIN discover_uni.accreditation a ON k.pubukprn = a.pubukprn 
                AND k.kiscourseid = a.kiscourseid 
                AND k.kismode = a.kismode
            JOIN discover_uni.accreditation_table at ON a.acctype = at.acctype
            LIMIT 5
        """),
        ("Courses with Locations", """
            SELECT k.title, l.locname
            FROM discover_uni.kiscourse k
            JOIN discover_uni.courselocation cl ON k.pubukprn = cl.pubukprn 
                AND k.kiscourseid = cl.kiscourseid 
                AND k.kismode = cl.kismode
            LEFT JOIN discover_uni.location l ON cl.ukprn = l.ukprn AND cl.locid = l.locid
            LIMIT 5
        """),
        ("Courses with Employment Data", """
            SELECT k.title, e.work, e.study, e.unemp
            FROM discover_uni.kiscourse k
            LEFT JOIN discover_uni.employment e ON k.pubukprn = e.pubukprn 
                AND k.kiscourseid = e.kiscourseid 
                AND k.kismode = e.kismode
            WHERE e.work IS NOT NULL
            LIMIT 5
        """)
    ]
    
    for name, query in queries:
        try:
            cursor.execute(query)
            if "COUNT" in query:
                result = cursor.fetchone()[0]
                print(f"\n✓ {name}: {result} records")
            else:
                results = cursor.fetchall()
                print(f"\n✓ {name}:")
                for row in results[:3]:  # Show first 3 rows
                    print(f"    {row}")
        except Exception as e:
            print(f"\n✗ Error querying {name}: {e}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import sample data from Discover Uni CSV files')
    parser.add_argument('--data-dir', type=str, default='./data',
                       help='Directory containing CSV files')
    parser.add_argument('--sample-size', type=int, default=5,
                       help='Number of sample rows to import from each CSV')
    
    args = parser.parse_args()
    
    global SAMPLE_ROWS
    SAMPLE_ROWS = args.sample_size
    
    data_dir = Path(args.data_dir)
    
    if not data_dir.exists():
        print(f"✗ Data directory not found: {data_dir}")
        sys.exit(1)
    
    print("="*70)
    print("DISCOVER UNI - SAMPLE DATA IMPORT")
    print("="*70)
    print(f"Data directory: {data_dir.absolute()}")
    print(f"Sample size: {SAMPLE_ROWS} rows per CSV")
    print(f"Database: {DB_NAME} @ {DB_HOST}:{DB_PORT}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Set schema
        cursor.execute("SET search_path TO discover_uni, public;")
        
        # Import in order
        import_sample_lookup_tables(cursor, data_dir)
        conn.commit()
        
        import_sample_core_entities(cursor, data_dir)
        conn.commit()
        
        import_sample_related_entities(cursor, data_dir)
        conn.commit()
        
        import_sample_outcomes(cursor, data_dir)
        conn.commit()
        
        # Verify relationships
        verify_relationships(cursor)
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*70)
        print("✓ Sample data import completed successfully!")
        print("="*70)
        print("\nNext steps:")
        print("1. Explore the data with SQL queries")
        print("2. Verify relationships are working correctly")
        print("3. When ready, import full datasets")
        
    except Exception as e:
        print(f"\n✗ Error during import: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

