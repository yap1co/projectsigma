# Module Documentation

This directory contains detailed documentation for the core system modules.

## Core Modules

### [RecommendationEngine](./recommendation_engine.md)
The heart of the recommendation system. This module implements the advanced matching algorithm that connects students with university courses.

**Key Features**:
- Multi-criteria weighted scoring
- Career interest filtering
- Database-driven configuration
- Feedback-based learning
- HESA data integration

### [Flask API (app.py)](./app.md)
The main backend server handling HTTP requests, authentication, and API endpoints.

**Key Features**:
- JWT-based authentication
- RESTful API design
- Input validation and sanitization
- Database integration
- Error handling

### [Data Models](./models.md)
Object-oriented models representing core entities: Students, Courses, and Universities.

**Key Features**:
- OOP inheritance pattern
- Database abstraction
- Type safety with dataclasses
- CRUD operations

## Module Relationships

```
app.py (Flask API)
  ├── Uses RecommendationEngine for recommendations
  ├── Uses Student model for user management
  ├── Uses Course model for course data
  └── Uses database_helper for DB operations

RecommendationEngine
  ├── Uses scoring_components for individual scorers
  ├── Uses database_helper for DB queries
  └── Uses models for data structures

Models
  ├── BaseModel provides common functionality
  ├── Student extends BaseModel
  └── Course extends BaseModel
```

## Reading Order

1. **Start with [app.md](./app.md)** - Understand the API structure
2. **Then [recommendation_engine.md](./recommendation_engine.md)** - Understand the core algorithm
3. **Finally [models.md](./models.md)** - Understand data structures

## Additional Resources

- [Quick Reference](../QUICK_REFERENCE.md) - Command and API quick reference
- [Troubleshooting](../troubleshooting/) - Common issues with modules
- [Database Guides](../database/) - Database schema and migrations
