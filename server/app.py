from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
from recommendation_engine import RecommendationEngine
from models.student import Student
from models.course import Course
from models.university import University

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# Initialize extensions
jwt = JWTManager(app)
CORS(app)

# Database connection
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client.university_recommender

# Initialize recommendation engine
recommendation_engine = RecommendationEngine()

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
        
        # Check if user already exists
        if db.students.find_one({'email': data['email']}):
            return jsonify({'message': 'User already exists'}), 400
        
        # Create new student
        student_data = {
            'email': data['email'],
            'password': generate_password_hash(data['password']),
            'firstName': data['firstName'],
            'lastName': data['lastName'],
            'yearGroup': data.get('yearGroup', 'Year 12'),
            'aLevelSubjects': data.get('aLevelSubjects', []),
            'predictedGrades': data.get('predictedGrades', {}),
            'preferences': data.get('preferences', {}),
            'createdAt': datetime.now(),
            'lastLogin': None
        }
        
        result = db.students.insert_one(student_data)
        student_id = str(result.inserted_id)
        
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
        student = db.students.find_one({'email': data['email']})
        
        if not student or not check_password_hash(student['password'], data['password']):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Update last login
        db.students.update_one(
            {'_id': student['_id']},
            {'$set': {'lastLogin': datetime.now()}}
        )
        
        # Create access token
        access_token = create_access_token(identity=str(student['_id']))
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'student_id': str(student['_id'])
        })
        
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

# Student profile routes
@app.route('/api/student/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get student profile"""
    try:
        student_id = get_jwt_identity()
        student = db.students.find_one({'_id': ObjectId(student_id)})
        
        if not student:
            return jsonify({'message': 'Student not found'}), 404
        
        # Remove password from response
        del student['password']
        student['_id'] = str(student['_id'])
        
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
        
        # Update student data
        update_data = {}
        if 'aLevelSubjects' in data:
            update_data['aLevelSubjects'] = data['aLevelSubjects']
        if 'predictedGrades' in data:
            update_data['predictedGrades'] = data['predictedGrades']
        if 'preferences' in data:
            update_data['preferences'] = data['preferences']
        
        update_data['updatedAt'] = datetime.now()
        
        result = db.students.update_one(
            {'_id': ObjectId(student_id)},
            {'$set': update_data}
        )
        
        if result.modified_count == 0:
            return jsonify({'message': 'No changes made'}), 400
        
        return jsonify({'message': 'Profile updated successfully'})
        
    except Exception as e:
        return jsonify({'message': f'Failed to update profile: {str(e)}'}), 500

# Recommendation routes
@app.route('/api/recommendations', methods=['POST'])
@jwt_required()
def get_recommendations():
    """Get course recommendations for student"""
    try:
        student_id = get_jwt_identity()
        student = db.students.find_one({'_id': ObjectId(student_id)})
        
        if not student:
            return jsonify({'message': 'Student not found'}), 404
        
        # Get recommendation criteria from request
        criteria = request.get_json()
        
        # Generate recommendations
        recommendations = recommendation_engine.get_recommendations(
            student['aLevelSubjects'],
            student['predictedGrades'],
            student.get('preferences', {}),
            criteria
        )
        
        # Save recommendations to database
        recommendation_data = {
            'studentId': ObjectId(student_id),
            'criteria': criteria,
            'recommendations': recommendations,
            'createdAt': datetime.now()
        }
        
        db.recommendations.insert_one(recommendation_data)
        
        return jsonify({
            'recommendations': recommendations,
            'total': len(recommendations)
        })
        
    except Exception as e:
        return jsonify({'message': f'Failed to get recommendations: {str(e)}'}), 500

# Course and university data routes
@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses with optional filtering"""
    try:
        # Get query parameters
        subject = request.args.get('subject')
        university = request.args.get('university')
        min_grade = request.args.get('min_grade')
        max_fee = request.args.get('max_fee')
        limit = int(request.args.get('limit', 50))
        
        # Build query
        query = {}
        if subject:
            query['subjects'] = {'$in': [subject]}
        if university:
            query['university.name'] = {'$regex': university, '$options': 'i'}
        if min_grade:
            query['entryRequirements.grades'] = {'$lte': min_grade}
        if max_fee:
            query['fees.uk'] = {'$lte': int(max_fee)}
        
        courses = list(db.courses.find(query).limit(limit))
        
        # Convert ObjectId to string
        for course in courses:
            course['_id'] = str(course['_id'])
        
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
        universities = list(db.universities.find())
        
        # Convert ObjectId to string
        for university in universities:
            university['_id'] = str(university['_id'])
        
        return jsonify({'universities': universities})
        
    except Exception as e:
        return jsonify({'message': f'Failed to get universities: {str(e)}'}), 500

# Admin routes
@app.route('/api/admin/courses', methods=['POST'])
@jwt_required()
def add_course():
    """Add new course (admin only)"""
    try:
        # Check if user is admin (implement proper admin check)
        data = request.get_json()
        
        course_data = {
            'name': data['name'],
            'university': data['university'],
            'subjects': data['subjects'],
            'entryRequirements': data['entryRequirements'],
            'fees': data['fees'],
            'ranking': data.get('ranking', {}),
            'employability': data.get('employability', {}),
            'description': data.get('description', ''),
            'createdAt': datetime.now(),
            'updatedAt': datetime.now()
        }
        
        result = db.courses.insert_one(course_data)
        
        return jsonify({
            'message': 'Course added successfully',
            'course_id': str(result.inserted_id)
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
        
        # Get student's latest recommendations
        recommendations = db.recommendations.find_one(
            {'studentId': ObjectId(student_id)},
            sort=[('createdAt', -1)]
        )
        
        if not recommendations:
            return jsonify({'message': 'No recommendations found'}), 404
        
        if format_type == 'csv':
            # Generate CSV
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Rank', 'Course', 'University', 'Match Score', 'Fees', 'Entry Requirements'])
            
            # Write data
            for i, rec in enumerate(recommendations['recommendations'], 1):
                writer.writerow([
                    i,
                    rec['course']['name'],
                    rec['course']['university']['name'],
                    rec['matchScore'],
                    rec['course']['fees']['uk'],
                    str(rec['course']['entryRequirements']['grades'])
                ])
            
            return jsonify({
                'data': output.getvalue(),
                'format': 'csv'
            })
        
        elif format_type == 'pdf':
            # Generate PDF (implement PDF generation)
            return jsonify({'message': 'PDF export not yet implemented'}), 501
        
        return jsonify({'message': 'Invalid format'}), 400
        
    except Exception as e:
        return jsonify({'message': f'Export failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
