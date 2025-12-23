"""
Base model class with common functionality for all models
Demonstrates OOP inheritance and polymorphism
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseModel(ABC):
    """
    Abstract base class for all data models
    Demonstrates inheritance and polymorphism
    """
    
    def __init__(self, created_at: Optional[datetime] = None):
        """Initialize base model with common attributes"""
        self.created_at = created_at or datetime.now()
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary for database storage
        Must be implemented by subclasses (polymorphism)
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """
        Create model instance from dictionary
        Must be implemented by subclasses (polymorphism)
        """
        pass
    
    def get_created_at(self) -> datetime:
        """Get creation timestamp (common method for all models)"""
        return self.created_at
    
    def is_recent(self, days: int = 30) -> bool:
        """Check if model was created recently (common utility method)"""
        delta = datetime.now() - self.created_at
        return delta.days <= days
    
    def __repr__(self) -> str:
        """String representation (can be overridden by subclasses)"""
        return f"<{self.__class__.__name__} created_at={self.created_at}>"
    
    def __eq__(self, other: Any) -> bool:
        """Equality comparison (can be overridden by subclasses)"""
        if not isinstance(other, self.__class__):
            return False
        return self.to_dict() == other.to_dict()
