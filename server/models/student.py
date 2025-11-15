"""
Student model for the university recommendation system
"""

from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Student:
    """
    Student model representing a user of the recommendation system
    """
    email: str
    password: str
    firstName: str
    lastName: str
    yearGroup: str = "Year 12"
    aLevelSubjects: List[str] = None
    predictedGrades: Dict[str, str] = None
    preferences: Dict[str, any] = None
    createdAt: datetime = None
    lastLogin: Optional[datetime] = None
    
    def __post_init__(self):
        if self.aLevelSubjects is None:
            self.aLevelSubjects = []
        if self.predictedGrades is None:
            self.predictedGrades = {}
        if self.preferences is None:
            self.preferences = {}
        if self.createdAt is None:
            self.createdAt = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert student to dictionary for database storage"""
        return {
            'email': self.email,
            'password': self.password,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'yearGroup': self.yearGroup,
            'aLevelSubjects': self.aLevelSubjects,
            'predictedGrades': self.predictedGrades,
            'preferences': self.preferences,
            'createdAt': self.createdAt,
            'lastLogin': self.lastLogin
        }
    
    @classmethod
    
    def from_dict(cls, data: Dict) -> 'Student':
        """Create student from dictionary"""
        return cls(
            email=data['email'],
            password=data['password'],
            firstName=data['firstName'],
            lastName=data['lastName'],
            yearGroup=data.get('yearGroup', 'Year 12'),
            aLevelSubjects=data.get('aLevelSubjects', []),
            predictedGrades=data.get('predictedGrades', {}),
            preferences=data.get('preferences', {}),
            createdAt=data.get('createdAt', datetime.now()),
            lastLogin=data.get('lastLogin')
        )
    
    def update_academic_profile(self, subjects: List[str], grades: Dict[str, str]):
        """Update student's academic information"""
        self.aLevelSubjects = subjects
        self.predictedGrades = grades
    
    def update_preferences(self, preferences: Dict[str, any]):
        """Update student's preferences"""
        self.preferences.update(preferences)
    
    def get_full_name(self) -> str:
        """Get student's full name"""
        return f"{self.firstName} {self.lastName}"
    
    def is_complete_profile(self) -> bool:
        """Check if student has complete profile for recommendations"""
        return (
            len(self.aLevelSubjects) > 0 and
            len(self.predictedGrades) > 0 and
            len(self.preferences) > 0
        )
