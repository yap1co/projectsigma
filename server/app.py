from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
from recommendation_engine import RecommendationEngine
from models.student import Student
from models.course import Course
from database_helper import get_db_connection, generate_id, get_student_by_id, get_student_by_email
from validators import (
    validate_student_registration, validate_preferences,
    validate_email, validate_password, sanitize_string, validate_limit
)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# Initialize extensions
jwt = JWTManager(app)
CORS(app)

# Initialize recommendation engine
recommendation_engine = RecommendationEngine()

@app.route('/', methods=['GET'])
def root():
    """Root endpoint - API information"""
    return jsonify({
        'name': 'University Course Recommender API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'register': '/api/auth/register',
            'login': '/api/auth/login',
            'profile': '/api/student/profile',
            'recommendations': '/api/recommendations',
            'courses': '/api/courses',
            'universities': '/api/universities'
        },
        'documentation': 'See README.md for API documentation'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.now().isoformat(),
        'environment': os.getenv('FLASK_ENV', 'development')
    })

# Authentication routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new student"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Request body is required'}), 400
        
        # Input validation (defensive programming)
        is_valid, error = validate_student_registration(data)
        if not is_valid:
            return jsonify({'message': error}), 400
        
        # Sanitize inputs
        data['email'] = sanitize_string(data['email'], 255).lower()
        data['firstName'] = sanitize_string(data['firstName'], 100)
        data['lastName'] = sanitize_string(data['lastName'], 100)
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if user already exists
                if get_student_by_email(cur, data['email']):
                    return jsonify({'message': 'User already exists'}), 400
                
                # Generate student ID
                student_id = generate_id('STU')
                display_name = f"{data['firstName']} {data['lastName']}"
                password_hash = generate_password_hash(data['password'])
                
                # Get preferences
                preferences = data.get('preferences', {})
                
                # Insert student
                cur.execute("""
                    INSERT INTO student (student_id, display_name, email, password_hash, 
                                      region, tuition_budget, preferred_exams, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_DATE)
                    RETURNING student_id
                """, (
                    student_id,
                    display_name,
                    data['email'],
                    password_hash,
                    preferences.get('preferredRegion'),
                    preferences.get('maxBudget'),
                    preferences.get('preferredExams', [])
                ))
                
                student_id = cur.fetchone()['student_id']
                
                # Insert student grades if provided
                predicted_grades = data.get('predictedGrades', {})
                a_level_subjects = data.get('aLevelSubjects', [])
                
                for subject_id in a_level_subjects:
                    if subject_id in predicted_grades:
                        # Check if subject exists, if not create it
                        cur.execute("SELECT subject_id FROM subject WHERE subject_id = %s", (subject_id,))
                        if not cur.fetchone():
                            cur.execute("""
                                INSERT INTO subject (subject_id, subject_name)
                                VALUES (%s, %s)
                                ON CONFLICT (subject_id) DO NOTHING
                            """, (subject_id, subject_id))
                        
                        cur.execute("""
                            INSERT INTO student_grade (student_id, subject_id, predicted_grade)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (student_id, subject_id) 
                            DO UPDATE SET predicted_grade = EXCLUDED.predicted_grade
                        """, (student_id, subject_id, predicted_grades[subject_id]))
                
                conn.commit()
        
        # Create access token
        access_token = create_access_token(identity=student_id)
        
        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token,
            'student_id': student_id
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login student"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Request body is required'}), 400
        
        # Validate required fields
        if 'email' not in data or 'password' not in data:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Sanitize email
        data['email'] = sanitize_string(data['email'], 255).lower()
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                student = get_student_by_email(cur, data['email'])
                
                if not student or not check_password_hash(student['password_hash'], data['password']):
                    return jsonify({'message': 'Invalid credentials'}), 401
                
                student_id = student['student_id']
        
        # Create access token
        access_token = create_access_token(identity=student_id)
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'student_id': student_id
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Login error: {str(e)}")
        print(f"Traceback: {error_details}")
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

# Student profile routes
@app.route('/api/student/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get student profile"""
    try:
        student_id = get_jwt_identity()
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                student = get_student_by_id(cur, student_id)
                
                if not student:
                    return jsonify({'message': 'Student not found'}), 404
                
                # Remove password from response
                del student['password_hash']
                student['yearGroup'] = 'Year 12'  # Default, can be stored if needed
                
                return jsonify({'student': student})
        
    except Exception as e:
        return jsonify({'message': f'Failed to get profile: {str(e)}'}), 500

@app.route('/api/student/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update student profile"""
    try:
        student_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Request body is required'}), 400
        
        # Validate preferences if provided
        if 'preferences' in data:
            is_valid, error = validate_preferences(data['preferences'])
            if not is_valid:
                return jsonify({'message': error}), 400
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Update preferences
                if 'preferences' in data:
                    prefs = data['preferences']
                    cur.execute("""
                        UPDATE student
                        SET region = %s, tuition_budget = %s, preferred_exams = %s
                        WHERE student_id = %s
                    """, (
                        prefs.get('preferredRegion'),
                        prefs.get('maxBudget'),
                        prefs.get('preferredExams', []),
                        student_id
                    ))
                
                # Update student grades
                if 'aLevelSubjects' in data and 'predictedGrades' in data:
                    # Delete existing grades
                    cur.execute("DELETE FROM student_grade WHERE student_id = %s", (student_id,))
                    
                    # Insert new grades
                    for subject_id in data['aLevelSubjects']:
                        if subject_id in data['predictedGrades']:
                            # Ensure subject exists
                            cur.execute("SELECT subject_id FROM subject WHERE subject_id = %s", (subject_id,))
                            if not cur.fetchone():
                                cur.execute("""
                                    INSERT INTO subject (subject_id, subject_name)
                                    VALUES (%s, %s)
                                    ON CONFLICT (subject_id) DO NOTHING
                                """, (subject_id, subject_id))
                            
                            cur.execute("""
                                INSERT INTO student_grade (student_id, subject_id, predicted_grade)
                                VALUES (%s, %s, %s)
                            """, (student_id, subject_id, data['predictedGrades'][subject_id]))
                
                conn.commit()
        
        return jsonify({'message': 'Profile updated successfully'})
        
    except Exception as e:
        return jsonify({'message': f'Failed to update profile: {str(e)}'}), 500

@app.route('/api/student/password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change student password"""
    try:
        student_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Request body is required'}), 400
        
        if 'currentPassword' not in data or 'newPassword' not in data:
            return jsonify({'message': 'Current password and new password are required'}), 400
        
        # Validate new password
        is_valid, error = validate_password(data['newPassword'])
        if not is_valid:
            return jsonify({'message': error}), 400
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get current student
                student = get_student_by_id(cur, student_id)
                
                if not student:
                    return jsonify({'message': 'Student not found'}), 404
                
                # Verify current password
                if not check_password_hash(student['password_hash'], data['currentPassword']):
                    return jsonify({'message': 'Current password is incorrect'}), 401
                
                # Update password
                new_password_hash = generate_password_hash(data['newPassword'])
                cur.execute("""
                    UPDATE student
                    SET password_hash = %s
                    WHERE student_id = %s
                """, (new_password_hash, student_id))
                
                conn.commit()
        
        return jsonify({'message': 'Password updated successfully'})
        
    except Exception as e:
        return jsonify({'message': f'Failed to change password: {str(e)}'}), 500

# Recommendation routes
@app.route('/api/recommendations', methods=['POST'])
@jwt_required()
def get_recommendations():
    """Get course recommendations for student"""
    try:
        student_id = get_jwt_identity()
        criteria = request.get_json() or {}
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                student = get_student_by_id(cur, student_id)
                
                if not student:
                    return jsonify({'message': 'Student not found'}), 404
                
                # Add student_id to criteria for feedback lookup
                criteria_with_student = {**criteria, 'student_id': student_id}
                
                # Generate recommendations
                recommendations = recommendation_engine.get_recommendations(
                    student.get('aLevelSubjects', []),
                    student.get('predictedGrades', {}),
                    student.get('preferences', {}),
                    criteria_with_student
                )
                
                # Save recommendations to database
                run_id = generate_id('RUN')
                cur.execute("""
                    INSERT INTO recommendation_run (run_id, student_id, run_at, weights, prefs_snapshot)
                    VALUES (%s, %s, CURRENT_DATE, %s, %s)
                    RETURNING run_id
                """, (
                    run_id,
                    student_id,
                    json.dumps(recommendation_engine.weights),
                    json.dumps(student.get('preferences', {}))
                ))
                
                result_id = generate_id('RES')
                cur.execute("""
                    INSERT INTO recommendation_result (result_id, run_id, items)
                    VALUES (%s, %s, %s)
                """, (result_id, run_id, json.dumps(recommendations)))
                
                conn.commit()
        
        return jsonify({
            'recommendations': recommendations,
            'total': len(recommendations),
            'studentId': student_id
        })
        
    except Exception as e:
        return jsonify({'message': f'Failed to get recommendations: {str(e)}'}), 500

@app.route('/api/recommendations/advanced', methods=['POST'])
@jwt_required()
def get_advanced_recommendations():
    """
    Advanced recommendations using complex SQL with CTEs and aggregate functions
    Demonstrates Group A: Cross-table parameterised SQL with CTEs
    """
    try:
        student_id = get_jwt_identity()
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Complex SQL query with CTEs (Common Table Expressions)
                # This demonstrates advanced SQL skills required for Group A
                query = """
                WITH student_profile AS (
                    -- Get student's academic profile
                    SELECT 
                        s.student_id,
                        s.region as preferred_region,
                        s.tuition_budget,
                        sg.subject_id,
                        sg.predicted_grade
                    FROM student s
                    LEFT JOIN student_grade sg ON s.student_id = sg.student_id
                    WHERE s.student_id = %s
                ),
                course_subject_matches AS (
                    -- Calculate subject matches for each course
                    SELECT 
                        c.course_id,
                        c.name as course_name,
                        COUNT(DISTINCT CASE 
                            WHEN cr.subject_id IN (SELECT subject_id FROM student_profile) 
                            THEN cr.subject_id 
                        END) as matched_subjects_count,
                        COUNT(DISTINCT cr.subject_id) as total_required_subjects
                    FROM course c
                    LEFT JOIN course_requirement cr ON c.course_id = cr.course_id
                    GROUP BY c.course_id, c.name
                ),
                course_grade_matches AS (
                    -- Calculate grade matches for each course
                    SELECT 
                        c.course_id,
                        AVG(CASE 
                            WHEN sg.predicted_grade >= cr.grade_req THEN 1.0 
                            ELSE 0.0 
                        END) as grade_match_ratio,
                        COUNT(DISTINCT cr.subject_id) as graded_requirements_count
                    FROM course c
                    JOIN course_requirement cr ON c.course_id = cr.course_id
                    LEFT JOIN student_profile sg ON cr.subject_id = sg.subject_id
                    WHERE sg.student_id IS NOT NULL
                    GROUP BY c.course_id
                ),
                course_scores AS (
                    -- Calculate composite scores
                    SELECT 
                        c.course_id,
                        c.name,
                        u.name as university_name,
                        u.rank_overall,
                        u.region,
                        c.annual_fee,
                        c.employability_score,
                        COALESCE(csm.matched_subjects_count, 0)::float / 
                            NULLIF(COALESCE(csm.total_required_subjects, 1), 0) as subject_match_score,
                        COALESCE(cgm.grade_match_ratio, 0.5) as grade_match_score,
                        CASE WHEN u.region = (SELECT preferred_region FROM student_profile LIMIT 1) 
                             THEN 1.0 ELSE 0.0 END as region_match_score,
                        CASE WHEN c.annual_fee <= (SELECT tuition_budget FROM student_profile LIMIT 1) 
                             THEN 1.0 ELSE 0.0 END as budget_match_score,
                        CASE WHEN u.rank_overall IS NOT NULL AND u.rank_overall > 0
                             THEN 1.0 / (1.0 + u.rank_overall::float / 100.0)
                             ELSE 0.5 END as ranking_score
                    FROM course c
                    JOIN university u ON c.university_id = u.university_id
                    LEFT JOIN course_subject_matches csm ON c.course_id = csm.course_id
                    LEFT JOIN course_grade_matches cgm ON c.course_id = cgm.course_id
                    CROSS JOIN (SELECT preferred_region, tuition_budget FROM student_profile LIMIT 1) sp
                )
                SELECT 
                    course_id,
                    name as course_name,
                    university_name,
                    rank_overall,
                    region,
                    annual_fee,
                    employability_score,
                    -- Weighted total score calculation
                    (
                        subject_match_score * 0.30 +
                        grade_match_score * 0.25 +
                        region_match_score * 0.20 +
                        budget_match_score * 0.15 +
                        ranking_score * 0.10
                    ) as total_score,
                    subject_match_score,
                    grade_match_score,
                    region_match_score,
                    budget_match_score,
                    ranking_score
                FROM course_scores
                WHERE total_score > 0
                ORDER BY total_score DESC
                LIMIT 50;
                """
                
                cur.execute(query, (student_id,))
                results = [dict(row) for row in cur.fetchall()]
                
                # Format results for API response
                recommendations = []
                for row in results:
                    recommendations.append({
                        'course': {
                            'course_id': row['course_id'],
                            'name': row['course_name'],
                            'university': {
                                'name': row['university_name'],
                                'region': row['region'],
                                'ranking': {'overall': row['rank_overall']}
                            },
                            'fees': {'uk': row['annual_fee']},
                            'employability': {'employmentRate': row['employability_score'] or 50}
                        },
                        'matchScore': float(row['total_score']),
                        'scoreBreakdown': {
                            'subject': float(row['subject_match_score']),
                            'grade': float(row['grade_match_score']),
                            'region': float(row['region_match_score']),
                            'budget': float(row['budget_match_score']),
                            'ranking': float(row['ranking_score'])
                        }
                    })
        
        return jsonify({
            'recommendations': recommendations,
            'total': len(recommendations),
            'method': 'advanced_sql',
            'studentId': student_id
        })
        
    except Exception as e:
        return jsonify({'message': f'Failed to get advanced recommendations: {str(e)}'}), 500

# Course and university data routes
@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses with optional filtering"""
    try:
        # Get and validate query parameters
        subject = request.args.get('subject')
        university = request.args.get('university')
        max_fee = request.args.get('max_fee')
        limit = validate_limit(request.args.get('limit', 50), max_limit=100)
        
        # Sanitize string inputs
        if subject:
            subject = sanitize_string(subject, 100)
        if university:
            university = sanitize_string(university, 100)
        
        # Validate max_fee
        if max_fee:
            try:
                max_fee = int(max_fee)
                if max_fee < 0 or max_fee > 100000:
                    return jsonify({'message': 'max_fee must be between 0 and 100,000'}), 400
            except (ValueError, TypeError):
                return jsonify({'message': 'max_fee must be a valid number'}), 400
        
        # Build SQL query
        query = """
            SELECT 
                c.course_id, c.name, c.annual_fee, c.ucas_code,
                c.typical_offer_text, c.typical_offer_tariff,
                u.university_id, u.name as university_name, u.region,
                u.rank_overall, u.employability_score as uni_employability,
                c.employability_score as course_employability
            FROM course c
            JOIN university u ON c.university_id = u.university_id
            WHERE 1=1
        """
        params = []
        
        if subject:
            query += """
                AND c.course_id IN (
                    SELECT DISTINCT cr.course_id 
                    FROM course_requirement cr
                    JOIN subject s ON cr.subject_id = s.subject_id
                    WHERE s.subject_name ILIKE %s OR s.subject_id = %s
                )
            """
            params.extend([f'%{subject}%', subject])
        
        if university:
            query += " AND u.name ILIKE %s"
            params.append(f'%{university}%')
        
        if max_fee:
            query += " AND c.annual_fee <= %s"
            params.append(int(max_fee))
        
        query += " LIMIT %s"
        params.append(limit)
        
        courses = []
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                
                for row in cur.fetchall():
                    course = dict(row)
                    course_id = course['course_id']
                    
                    # Get entry requirements
                    cur.execute("""
                        SELECT s.subject_id, s.subject_name, cr.grade_req
                        FROM course_requirement cr
                        JOIN subject s ON cr.subject_id = s.subject_id
                        WHERE cr.course_id = %s
                    """, (course_id,))
                    
                    requirements = {}
                    subjects = []
                    for req_row in cur.fetchall():
                        req = dict(req_row)
                        subject_id = req['subject_id']
                        requirements[subject_id] = req['grade_req']
                        subjects.append(subject_id)
                    
                    # Format for frontend
                    course['entryRequirements'] = {
                        'subjects': subjects,
                        'grades': requirements
                    }
                    course['fees'] = {
                        'uk': course.get('annual_fee', 0)
                    }
                    course['university'] = {
                        'name': course['university_name'],
                        'region': course['region'],
                        'ranking': {
                            'overall': course.get('rank_overall')
                        }
                    }
                    course['employability'] = {
                        'employmentRate': course.get('course_employability') or course.get('uni_employability', 0)
                    }
                    course['subjects'] = subjects
                    
                    courses.append(course)
        
        return jsonify({
            'courses': courses,
            'total': len(courses)
        })
        
    except Exception as e:
        return jsonify({'message': f'Failed to get courses: {str(e)}'}), 500

@app.route('/api/universities', methods=['GET'])
def get_universities():
    """Get all universities"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT university_id, name, region, rank_overall, 
                           employability_score, website_url
                    FROM university
                    ORDER BY rank_overall NULLS LAST
                """)
                
                universities = []
                for row in cur.fetchall():
                    uni = dict(row)
                    uni['ranking'] = {
                        'overall': uni.get('rank_overall')
                    }
                    universities.append(uni)
        
        return jsonify({'universities': universities})
        
    except Exception as e:
        return jsonify({'message': f'Failed to get universities: {str(e)}'}), 500

# Recommendation Feedback routes
@app.route('/api/recommendations/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    """Submit feedback (thumbs up/down) on a recommendation"""
    try:
        student_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'message': 'Request body is required'}), 400
        
        course_id = data.get('courseId') or data.get('course_id')
        feedback_type = data.get('feedbackType') or data.get('feedback_type')
        match_score = data.get('matchScore') or data.get('match_score')
        search_criteria = data.get('searchCriteria') or data.get('search_criteria', {})
        notes = data.get('notes', '')
        
        if not course_id:
            return jsonify({'message': 'courseId is required'}), 400
        
        if feedback_type not in ['positive', 'negative']:
            return jsonify({'message': 'feedbackType must be "positive" or "negative"'}), 400
        
        # Validate course exists
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT course_id FROM course WHERE course_id = %s", (course_id,))
                if not cur.fetchone():
                    return jsonify({'message': 'Course not found'}), 404
                
                # Insert feedback
                feedback_id = generate_id('FB')
                cur.execute("""
                    INSERT INTO recommendation_feedback 
                        (feedback_id, student_id, course_id, feedback_type, match_score, search_criteria, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    feedback_id,
                    student_id,
                    course_id,
                    feedback_type,
                    match_score,
                    json.dumps(search_criteria),
                    notes[:500] if notes else None  # Limit notes length
                ))
                
                conn.commit()
        
        return jsonify({
            'message': 'Feedback submitted successfully',
            'feedbackId': feedback_id
        })
        
    except Exception as e:
        return jsonify({'message': f'Failed to submit feedback: {str(e)}'}), 500

@app.route('/api/recommendations/feedback/<course_id>', methods=['GET'])
@jwt_required()
def get_course_feedback(course_id):
    """Get feedback history for a specific course"""
    try:
        student_id = get_jwt_identity()
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        feedback_id,
                        feedback_type,
                        feedback_at,
                        match_score,
                        notes
                    FROM recommendation_feedback
                    WHERE student_id = %s AND course_id = %s
                    ORDER BY feedback_at DESC
                    LIMIT 50
                """, (student_id, course_id))
                
                feedback_history = [dict(row) for row in cur.fetchall()]
                
                # Calculate summary
                positive_count = sum(1 for f in feedback_history if f['feedback_type'] == 'positive')
                negative_count = sum(1 for f in feedback_history if f['feedback_type'] == 'negative')
                
        return jsonify({
            'courseId': course_id,
            'feedbackHistory': feedback_history,
            'summary': {
                'positive': positive_count,
                'negative': negative_count,
                'total': len(feedback_history)
            }
        })
        
    except Exception as e:
        return jsonify({'message': f'Failed to get feedback: {str(e)}'}), 500

@app.route('/api/recommendations/settings', methods=['GET'])
@jwt_required()
def get_recommendation_settings():
    """Get tunable recommendation settings"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT setting_key, setting_value, description
                    FROM recommendation_settings
                    ORDER BY setting_key
                """)
                
                settings = {}
                for row in cur.fetchall():
                    settings[row['setting_key']] = {
                        'value': row['setting_value'],
                        'description': row['description']
                    }
        
        return jsonify({'settings': settings})
        
    except Exception as e:
        return jsonify({'message': f'Failed to get settings: {str(e)}'}), 500

@app.route('/api/recommendations/settings/<setting_key>', methods=['PUT'])
@jwt_required()
def update_recommendation_setting(setting_key):
    """Update a tunable recommendation setting (admin or student preference)"""
    try:
        student_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'value' not in data:
            return jsonify({'message': 'value is required'}), 400
        
        new_value = data['value']
        
        # Validate setting key
        valid_keys = ['feedback_weight', 'feedback_decay_days', 'min_feedback_count', 
                     'positive_feedback_boost', 'negative_feedback_penalty']
        if setting_key not in valid_keys:
            return jsonify({'message': f'Invalid setting key. Valid keys: {", ".join(valid_keys)}'}), 400
        
        # Validate value based on key
        try:
            if setting_key in ['feedback_decay_days', 'min_feedback_count']:
                new_value = int(new_value)
                if new_value < 0:
                    return jsonify({'message': 'Value must be non-negative'}), 400
            else:
                new_value = float(new_value)
                if setting_key == 'feedback_weight' and not (0 <= new_value <= 1):
                    return jsonify({'message': 'feedback_weight must be between 0 and 1'}), 400
        except (ValueError, TypeError):
            return jsonify({'message': 'Invalid value type'}), 400
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Update setting
                cur.execute("""
                    UPDATE recommendation_settings
                    SET setting_value = %s,
                        updated_at = CURRENT_TIMESTAMP,
                        updated_by = %s
                    WHERE setting_key = %s
                    RETURNING setting_id
                """, (new_value, student_id, setting_key))
                
                if not cur.fetchone():
                    return jsonify({'message': 'Setting not found'}), 404
                
                conn.commit()
        
        return jsonify({
            'message': 'Setting updated successfully',
            'settingKey': setting_key,
            'newValue': new_value
        })
        
    except Exception as e:
        return jsonify({'message': f'Failed to update setting: {str(e)}'}), 500

# Admin routes
@app.route('/api/admin/courses', methods=['POST'])
@jwt_required()
def add_course():
    """Add new course (admin only)"""
    try:
        # TODO: Check if user is admin (implement proper admin check)
        data = request.get_json()
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get or create university
                university_id = data.get('university_id')
                if not university_id:
                    # Create university if needed
                    university_id = generate_id('UNI')
                    cur.execute("""
                        INSERT INTO university (university_id, name, region, rank_overall, employability_score)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (university_id) DO NOTHING
                    """, (
                        university_id,
                        data.get('university', {}).get('name', 'Unknown'),
                        data.get('university', {}).get('region'),
                        data.get('university', {}).get('ranking', {}).get('overall'),
                        data.get('university', {}).get('employability', {}).get('employmentRate')
                    ))
                
                # Create course
                course_id = generate_id('CRS')
                cur.execute("""
                    INSERT INTO course (course_id, university_id, name, annual_fee, 
                                      employability_score, typical_offer_text)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING course_id
                """, (
                    course_id,
                    university_id,
                    data['name'],
                    data.get('fees', {}).get('uk', 9250),
                    data.get('employability', {}).get('employmentRate', 50),
                    data.get('description', '')
                ))
                
                # Add course requirements
                entry_req = data.get('entryRequirements', {})
                subjects = entry_req.get('subjects', [])
                grades = entry_req.get('grades', {})
                
                for subject_id in subjects:
                    # Ensure subject exists
                    cur.execute("SELECT subject_id FROM subject WHERE subject_id = %s", (subject_id,))
                    if not cur.fetchone():
                        cur.execute("""
                            INSERT INTO subject (subject_id, subject_name)
                            VALUES (%s, %s)
                            ON CONFLICT (subject_id) DO NOTHING
                        """, (subject_id, subject_id))
                    
                    # Add requirement
                    req_id = generate_id('REQ')
                    grade_req = grades.get(subject_id, 'C')
                    cur.execute("""
                        INSERT INTO course_requirement (req_id, course_id, subject_id, grade_req)
                        VALUES (%s, %s, %s, %s)
                    """, (req_id, course_id, subject_id, grade_req))
                
                conn.commit()
        
        return jsonify({
            'message': 'Course added successfully',
            'course_id': course_id
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Failed to add course: {str(e)}'}), 500

# Export routes
@app.route('/api/export/recommendations/<student_id>', methods=['GET'])
@jwt_required()
def export_recommendations(student_id):
    """Export recommendations as PDF or CSV"""
    try:
        format_type = request.args.get('format', 'csv')
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get latest recommendations
                cur.execute("""
                    SELECT rr.items, rr.run_id
                    FROM recommendation_result rr
                    JOIN recommendation_run rrun ON rr.run_id = rrun.run_id
                    WHERE rrun.student_id = %s
                    ORDER BY rrun.run_at DESC
                    LIMIT 1
                """, (student_id,))
                
                row = cur.fetchone()
                if not row:
                    return jsonify({'message': 'No recommendations found'}), 404
                
                recommendations = json.loads(row['items'])
        
        if format_type == 'csv':
            # Generate CSV
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Rank', 'Course', 'University', 'Match Score', 'Fees', 'Entry Requirements'])
            
            # Write data
            for i, rec in enumerate(recommendations, 1):
                course = rec.get('course', {})
                writer.writerow([
                    i,
                    course.get('name', ''),
                    course.get('university', {}).get('name', ''),
                    rec.get('matchScore', 0),
                    course.get('fees', {}).get('uk', 0),
                    str(course.get('entryRequirements', {}).get('grades', {}))
                ])
            
            return jsonify({
                'data': output.getvalue(),
                'format': 'csv'
            })
        
        elif format_type == 'pdf':
            # Generate PDF using reportlab
            try:
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.lib import colors
                from reportlab.lib.units import inch
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.enums import TA_CENTER, TA_LEFT
                import io
                from datetime import datetime
                
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
                elements = []
                styles = getSampleStyleSheet()
                
                # Title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=18,
                    textColor=colors.HexColor('#1a365d'),
                    spaceAfter=30,
                    alignment=TA_CENTER
                )
                elements.append(Paragraph("University Course Recommendations", title_style))
                elements.append(Spacer(1, 0.2*inch))
                
                # Date
                date_style = ParagraphStyle(
                    'DateStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=colors.grey,
                    alignment=TA_CENTER
                )
                elements.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y')}", date_style))
                elements.append(Spacer(1, 0.3*inch))
                
                # Table data
                table_data = [['Rank', 'Course', 'University', 'Match Score', 'Fees (£)']]
                
                for i, rec in enumerate(recommendations[:30], 1):  # Top 30 for PDF
                    course = rec.get('course', {})
                    match_score = rec.get('matchScore', 0)
                    
                    table_data.append([
                        str(i),
                        course.get('name', 'N/A')[:40],  # Truncate long names
                        course.get('university', {}).get('name', 'N/A')[:30],
                        f"{match_score:.2f}",
                        f"£{course.get('fees', {}).get('uk', 0):,}"
                    ])
                
                # Create table
                table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 2*inch, 1*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 0.3*inch))
                
                # Summary
                summary_style = ParagraphStyle(
                    'SummaryStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    alignment=TA_LEFT
                )
                elements.append(Paragraph(f"<b>Total Recommendations:</b> {len(recommendations)}", summary_style))
                elements.append(Spacer(1, 0.1*inch))
                elements.append(Paragraph(f"<b>Showing top 30 matches</b>", summary_style))
                
                # Build PDF
                doc.build(elements)
                buffer.seek(0)
                
                from flask import Response
                return Response(
                    buffer.getvalue(),
                    mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment; filename=course-recommendations.pdf'}
                )
            except ImportError:
                return jsonify({'message': 'PDF export requires reportlab library. Install with: pip install reportlab'}), 501
            except Exception as e:
                return jsonify({'message': f'PDF generation failed: {str(e)}'}), 500
        
        return jsonify({'message': 'Invalid format'}), 400
        
    except Exception as e:
        return jsonify({'message': f'Export failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
