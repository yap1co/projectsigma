"""
Pytest configuration and fixtures
"""
import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def test_config():
    """Test configuration"""
    return {
        'TESTING': True,
        'JWT_SECRET_KEY': 'test-secret-key-for-testing-only'
    }
