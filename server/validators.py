"""
Input validation utilities
Demonstrates defensive programming
"""
import re
from typing import Dict, Any, List, Optional
from werkzeug.exceptions import BadRequest


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, None


def validate_grade(grade: str) -> bool:
    """Validate A-level grade format"""
    valid_grades = ['A*', 'A', 'B', 'C', 'D', 'E', 'U']
    return grade in valid_grades


def validate_student_registration(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Validate student registration data"""
    required_fields = ['email', 'password', 'firstName', 'lastName']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
        if not data[field] or not isinstance(data[field], str):
            return False, f"Invalid {field}: must be a non-empty string"
    
    # Validate email
    if not validate_email(data['email']):
        return False, "Invalid email format"
    
    # Validate password
    is_valid, error = validate_password(data['password'])
    if not is_valid:
        return False, error
    
    # Validate names
    if len(data['firstName']) < 1 or len(data['firstName']) > 100:
        return False, "First name must be between 1 and 100 characters"
    if len(data['lastName']) < 1 or len(data['lastName']) > 100:
        return False, "Last name must be between 1 and 100 characters"
    
    # Validate optional fields
    if 'yearGroup' in data and data['yearGroup']:
        valid_years = ['Year 11', 'Year 12', 'Year 13']
        if data['yearGroup'] not in valid_years:
            return False, f"Invalid year group. Must be one of: {', '.join(valid_years)}"
    
    # Validate predicted grades if provided
    if 'predictedGrades' in data and data['predictedGrades']:
        if not isinstance(data['predictedGrades'], dict):
            return False, "predictedGrades must be a dictionary"
        for subject, grade in data['predictedGrades'].items():
            if not validate_grade(grade):
                return False, f"Invalid grade '{grade}' for subject '{subject}'. Valid grades: A*, A, B, C, D, E, U"
    
    return True, None


def validate_preferences(preferences: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Validate student preferences"""
    if not isinstance(preferences, dict):
        return False, "Preferences must be a dictionary"
    
    # Validate budget
    if 'maxBudget' in preferences:
        budget = preferences['maxBudget']
        if not isinstance(budget, (int, float)):
            return False, "maxBudget must be a number"
        if budget < 0 or budget > 100000:
            return False, "maxBudget must be between 0 and 100,000"
    
    # Validate region
    if 'preferredRegion' in preferences and preferences['preferredRegion']:
        valid_regions = [
            'London', 'South East', 'South West', 'Midlands',
            'North West', 'North East', 'Scotland', 'Wales', 'Any'
        ]
        if preferences['preferredRegion'] not in valid_regions:
            return False, f"Invalid region. Must be one of: {', '.join(valid_regions)}"
    
    return True, None


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        return ""
    # Remove leading/trailing whitespace
    value = value.strip()
    # Truncate if too long
    if len(value) > max_length:
        value = value[:max_length]
    return value


def validate_limit(limit: Any, max_limit: int = 100) -> int:
    """Validate and sanitize limit parameter"""
    try:
        limit = int(limit)
        if limit < 1:
            return 1
        if limit > max_limit:
            return max_limit
        return limit
    except (ValueError, TypeError):
        return 10  # Default
