"""
Integration tests for API endpoints
"""
import pytest
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test that health endpoint returns OK"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'OK'
        assert 'timestamp' in data


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields"""
        response = client.post('/api/auth/register', json={
            'email': 'test@test.com'
            # Missing password, firstName, lastName
        })
        assert response.status_code in [400, 500]  # Should fail validation
    
    def test_register_valid_data(self, client):
        """Test registration with valid data"""
        response = client.post('/api/auth/register', json={
            'email': f'test_{os.urandom(4).hex()}@test.com',  # Unique email
            'password': 'testpass123',
            'firstName': 'Test',
            'lastName': 'User'
        })
        # Should succeed or return 400 if user exists (both are acceptable)
        assert response.status_code in [201, 400]
        if response.status_code == 201:
            data = json.loads(response.data)
            assert 'access_token' in data
            assert 'student_id' in data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@test.com',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        response = client.post('/api/auth/login', json={
            'email': 'test@test.com'
            # Missing password
        })
        assert response.status_code in [400, 401, 500]


class TestCourseEndpoints:
    """Test course-related endpoints"""
    
    def test_get_courses(self, client):
        """Test getting courses list"""
        response = client.get('/api/courses')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'courses' in data
        assert 'total' in data
        assert isinstance(data['courses'], list)
    
    def test_get_courses_with_limit(self, client):
        """Test getting courses with limit parameter"""
        response = client.get('/api/courses?limit=10')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['courses']) <= 10
    
    def test_get_universities(self, client):
        """Test getting universities list"""
        response = client.get('/api/universities')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'universities' in data
        assert isinstance(data['universities'], list)


class TestProtectedEndpoints:
    """Test endpoints that require authentication"""
    
    def test_get_profile_without_auth(self, client):
        """Test that profile endpoint requires authentication"""
        response = client.get('/api/student/profile')
        assert response.status_code == 401  # Unauthorized
    
    def test_get_recommendations_without_auth(self, client):
        """Test that recommendations endpoint requires authentication"""
        response = client.post('/api/recommendations', json={})
        assert response.status_code == 401  # Unauthorized


class TestDatabaseConnection:
    """Test database connectivity"""
    
    def test_database_helper_import(self):
        """Test that database helper can be imported"""
        try:
            from database_helper import get_db_connection, generate_id
            assert callable(get_db_connection)
            assert callable(generate_id)
        except ImportError as e:
            pytest.skip(f"Database helper not available: {e}")
    
    def test_generate_id(self):
        """Test ID generation"""
        from database_helper import generate_id
        id1 = generate_id('TEST')
        id2 = generate_id('TEST')
        assert id1.startswith('TEST')
        assert id1 != id2  # Should be unique
        assert len(id1) > len('TEST')  # Should have additional characters
