"""
Course model for the university recommendation system
Demonstrates OOP inheritance from BaseModel
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .base_model import BaseModel

@dataclass
class EntryRequirements:
    """Entry requirements for a course"""
    subjects: List[str]
    grades: Dict[str, str]  # subject -> required grade
    additional_requirements: Optional[str] = None
    interview_required: bool = False
    portfolio_required: bool = False
    entrance_exam: Optional[str] = None

@dataclass
class Fees:
    """Course fees structure"""
    uk: int  # UK/EU student fees
    international: Optional[int] = None
    additional_costs: Optional[str] = None

@dataclass
class Ranking:
    """University and course rankings"""
    overall: Optional[int] = None
    subject: Optional[int] = None
    employability: Optional[int] = None

@dataclass
class Employability:
    """Graduate employability data"""
    employment_rate: float  # Percentage
    average_salary: Optional[int] = None
    top_employers: Optional[List[str]] = None
    further_study_rate: Optional[float] = None

@dataclass
class Course(BaseModel):
    """
    Course model representing a university course
    """
    name: str
    university: Dict[str, Any]  # University information
    subjects: List[str]  # Related subjects
    entry_requirements: EntryRequirements
    fees: Fees
    ranking: Ranking
    employability: Employability
    description: str = ""
    duration: int = 3  # Years
    study_mode: str = "Full-time"  # Full-time, Part-time, etc.
    location: Optional[str] = None
    createdAt: datetime = None
    updatedAt: datetime = None
    
    def __post_init__(self):
        # Initialize base class
        super().__init__(self.createdAt)
        
        if self.createdAt is None:
            self.createdAt = datetime.now()
            self.created_at = self.createdAt
        if self.updatedAt is None:
            self.updatedAt = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert course to dictionary for database storage"""
        return {
            'name': self.name,
            'university': self.university,
            'subjects': self.subjects,
            'entryRequirements': {
                'subjects': self.entry_requirements.subjects,
                'grades': self.entry_requirements.grades,
                'additionalRequirements': self.entry_requirements.additional_requirements,
                'interviewRequired': self.entry_requirements.interview_required,
                'portfolioRequired': self.entry_requirements.portfolio_required,
                'entranceExam': self.entry_requirements.entrance_exam
            },
            'fees': {
                'uk': self.fees.uk,
                'international': self.fees.international,
                'additionalCosts': self.fees.additional_costs
            },
            'ranking': {
                'overall': self.ranking.overall,
                'subject': self.ranking.subject,
                'employability': self.ranking.employability
            },
            'employability': {
                'employmentRate': self.employability.employment_rate,
                'averageSalary': self.employability.average_salary,
                'topEmployers': self.employability.top_employers,
                'furtherStudyRate': self.employability.further_study_rate
            },
            'description': self.description,
            'duration': self.duration,
            'studyMode': self.study_mode,
            'location': self.location,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Course':
        """Create course from dictionary"""
        entry_req_data = data.get('entryRequirements', {})
        entry_requirements = EntryRequirements(
            subjects=entry_req_data.get('subjects', []),
            grades=entry_req_data.get('grades', {}),
            additional_requirements=entry_req_data.get('additionalRequirements'),
            interview_required=entry_req_data.get('interviewRequired', False),
            portfolio_required=entry_req_data.get('portfolioRequired', False),
            entrance_exam=entry_req_data.get('entranceExam')
        )
        
        fees_data = data.get('fees', {})
        fees = Fees(
            uk=fees_data.get('uk', 0),
            international=fees_data.get('international'),
            additional_costs=fees_data.get('additionalCosts')
        )
        
        ranking_data = data.get('ranking', {})
        ranking = Ranking(
            overall=ranking_data.get('overall'),
            subject=ranking_data.get('subject'),
            employability=ranking_data.get('employability')
        )
        
        employability_data = data.get('employability', {})
        employability = Employability(
            employment_rate=employability_data.get('employmentRate', 0.0),
            average_salary=employability_data.get('averageSalary'),
            top_employers=employability_data.get('topEmployers'),
            further_study_rate=employability_data.get('furtherStudyRate')
        )
        
        return cls(
            name=data['name'],
            university=data['university'],
            subjects=data.get('subjects', []),
            entry_requirements=entry_requirements,
            fees=fees,
            ranking=ranking,
            employability=employability,
            description=data.get('description', ''),
            duration=data.get('duration', 3),
            study_mode=data.get('studyMode', 'Full-time'),
            location=data.get('location'),
            createdAt=data.get('createdAt', datetime.now()),
            updatedAt=data.get('updatedAt', datetime.now())
        )
    
    def matches_subjects(self, student_subjects: List[str]) -> bool:
        """Check if course matches student's subjects"""
        required_subjects = set(self.entry_requirements.subjects)
        student_subjects_set = set(student_subjects)
        return len(required_subjects & student_subjects_set) > 0
    
    def meets_grade_requirements(self, student_grades: Dict[str, str]) -> bool:
        """Check if student's grades meet course requirements"""
        for subject, required_grade in self.entry_requirements.grades.items():
            if subject in student_grades:
                student_grade = student_grades[subject]
                # Simple grade comparison (A* > A > B > C > D > E > U)
                grade_hierarchy = {'A*': 8, 'A': 7, 'B': 6, 'C': 5, 'D': 4, 'E': 3, 'U': 0}
                if grade_hierarchy.get(student_grade, 0) < grade_hierarchy.get(required_grade, 0):
                    return False
        return True
    
    def get_total_cost(self, student_type: str = 'uk') -> int:
        """Get total cost for the course"""
        if student_type == 'uk':
            return self.fees.uk
        elif student_type == 'international' and self.fees.international:
            return self.fees.international
        return self.fees.uk
    
    def is_affordable(self, max_budget: int, student_type: str = 'uk') -> bool:
        """Check if course is within budget"""
        return self.get_total_cost(student_type) <= max_budget
