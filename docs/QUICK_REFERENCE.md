# Quick Reference Guide

## Core Modules

### RecommendationEngine
**Location**: `server/recommendation_engine.py`  
**Documentation**: [modules/recommendation_engine.md](./modules/recommendation_engine.md)

**Key Methods**:
- `get_recommendations()` - Generate course recommendations
- `_load_career_interests_from_db()` - Load career interests from database

**Usage**:
```python
from recommendation_engine import RecommendationEngine
engine = RecommendationEngine()
recommendations = engine.get_recommendations(subjects, grades, preferences, criteria)
```

### Flask API (app.py)
**Location**: `server/app.py`  
**Documentation**: [modules/app.md](./modules/app.md)

**Key Endpoints**:
- `POST /api/auth/register` - Register new student
- `POST /api/auth/login` - Authenticate student
- `GET /api/student/profile` - Get student profile
- `POST /api/recommendations` - Get recommendations
- `POST /api/recommendations/feedback` - Submit feedback

### Data Models
**Location**: `server/models/`  
**Documentation**: [modules/models.md](./modules/models.md)

**Key Models**:
- `Student` - Student user model
- `Course` - Course model
- `BaseModel` - Base model class

## Common Tasks

### Setup
1. **Database**: [database/QUICK_START_LOCAL.md](./database/QUICK_START_LOCAL.md)
2. **Backend**: [setup/COMPLETE_BEGINNER_SETUP_GUIDE.md](./setup/COMPLETE_BEGINNER_SETUP_GUIDE.md)
3. **Frontend**: [setup/frontend_setup.md](./setup/frontend_setup.md)

### Database Migrations
1. **Career Interests**: [database/run_feedback_migration.md](./database/run_feedback_migration.md)
2. **Feedback System**: [database/run_feedback_migration.md](./database/run_feedback_migration.md)
3. **HESA Data**: [guides/hesa_data.md](./guides/hesa_data.md)

### Management
1. **Career Interests**: [guides/career_interests.md](./guides/career_interests.md)
2. **Student Profiles**: [guides/profile_management.md](./guides/profile_management.md)
3. **Feedback**: [guides/feedback_system.md](./guides/feedback_system.md)

## Troubleshooting

### Login Issues
- [Login Errors](./troubleshooting/login_errors.md)
- [Quick Fix Login](./troubleshooting/quick_fix_login.md)
- [Password Setup](./troubleshooting/password_setup.md)

### Frontend Issues
- [Frontend Errors](./troubleshooting/frontend_errors.md)

### Python Issues
- [Python Compatibility](./troubleshooting/python_compatibility.md)

## File Locations

### Backend
- Main API: `server/app.py`
- Recommendation Engine: `server/recommendation_engine.py`
- Models: `server/models/`
- Database Helper: `server/database_helper.py`
- Validators: `server/validators.py`

### Frontend
- Main App: `client/app/`
- Components: `client/components/`
- Configuration: `client/next.config.js`

### Database
- Migrations: `server/database/migrations/`
- Import Scripts: `server/database/`
- Data: `server/database/data/`

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost/university_recommender
JWT_SECRET_KEY=your-secret-key
FLASK_ENV=development
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## Common Commands

### Backend
```bash
cd server
python app.py                    # Run Flask server
pytest tests/                    # Run tests
python -m pytest tests/ -v      # Verbose tests
```

### Frontend
```bash
cd client
npm install                      # Install dependencies
npm run dev                      # Development server
npm run build                    # Production build
```

### Database
```bash
cd server/database
python init_db.py                # Initialize database
python run_career_interests_migration.py  # Run career interests migration
python run_feedback_migration.py # Run feedback migration
```

## API Quick Reference

### Authentication
```bash
# Register
POST /api/auth/register
Body: { email, password, firstName, lastName, preferences }

# Login
POST /api/auth/login
Body: { email, password }
Response: { access_token, student_id }
```

### Recommendations
```bash
POST /api/recommendations
Headers: Authorization: Bearer <token>
Body: { a_level_subjects, predicted_grades, preferences, limit }
Response: { recommendations: [...], total: 50 }
```

### Profile
```bash
GET /api/student/profile
Headers: Authorization: Bearer <token>
Response: { student_id, display_name, email, preferences, ... }

PUT /api/student/profile
Headers: Authorization: Bearer <token>
Body: { display_name, preferences, ... }
```

## Testing

### Run All Tests
```bash
cd server
pytest tests/ -v
```

### Run Specific Test Suite
```bash
pytest tests/test_recommendation_engine.py -v
pytest tests/test_api.py -v
pytest tests/test_models.py -v
```

## Database Queries

### Check Career Interests
```sql
SELECT * FROM career_interest WHERE is_active = TRUE;
SELECT * FROM career_interest_keyword WHERE interest_id = 'CI001';
```

### Check Feedback
```sql
SELECT * FROM recommendation_feedback ORDER BY feedback_at DESC LIMIT 10;
```

### Check Students
```sql
SELECT student_id, display_name, email, created_at FROM student ORDER BY created_at DESC;
```
