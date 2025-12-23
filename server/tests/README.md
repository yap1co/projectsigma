# Test Suite

## Running Tests

### Run all tests:
```bash
cd server
pytest tests/
```

### Run specific test file:
```bash
pytest tests/test_recommendation_engine.py
pytest tests/test_api.py
pytest tests/test_models.py
```

### Run with verbose output:
```bash
pytest tests/ -v
```

### Run with coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

## Test Structure

- `test_recommendation_engine.py` - Unit tests for recommendation algorithm
- `test_api.py` - Integration tests for API endpoints
- `test_models.py` - Unit tests for data models
- `conftest.py` - Pytest configuration and fixtures

## Test Coverage

### Recommendation Engine Tests
- Engine initialization
- Weight validation
- Subject matching
- Grade matching
- Preference matching
- Ranking scoring
- Weighted score calculation

### API Tests
- Health check endpoint
- Authentication (register/login)
- Course endpoints
- Protected endpoints (auth required)
- Database connectivity

### Model Tests
- Student model creation and validation
- Course model creation and validation
- Model methods (matching, affordability, etc.)

## Notes

- Tests may require database connection for some integration tests
- Set environment variables for database connection if needed
- Some tests may skip if database is not available (graceful degradation)
