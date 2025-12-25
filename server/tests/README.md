# Test Suite Documentation

## Overview

This directory contains comprehensive test suites for the University Course Recommender system, including unit tests, integration tests, and BDD-style Gherkin scenarios.

**Test Status**: ✅ **43/43 tests passing (100%)**

## 📚 Documentation

### Comprehensive Test Documentation

- **[TEST_STRATEGY.md](./TEST_STRATEGY.md)** - Complete test strategy, approach, and methodologies
- **[TEST_CASES_CATALOG.md](./TEST_CASES_CATALOG.md)** - Detailed catalog of all 43 test cases
- **[BDD_TEST_GUIDE.md](./BDD_TEST_GUIDE.md)** - Guide to Gherkin/Cucumber BDD scenarios
- **[TEST_RESULTS_SUMMARY.md](./TEST_RESULTS_SUMMARY.md)** - Latest test execution results

### BDD Feature Files (Gherkin)

All feature files are in `features/` directory:

- **[recommendation_engine.feature](./features/recommendation_engine.feature)** - Recommendation algorithm scenarios
- **[authentication.feature](./features/authentication.feature)** - User registration and login scenarios
- **[student_profile.feature](./features/student_profile.feature)** - Profile management scenarios
- **[recommendations.feature](./features/recommendations.feature)** - Recommendation API scenarios
- **[feedback.feature](./features/feedback.feature)** - Feedback system scenarios
- **[courses_and_universities.feature](./features/courses_and_universities.feature)** - Course and university browsing scenarios

## Running Tests

### Run all tests:
```bash
cd server
pytest tests/ -v
```

### Run specific test file:
```bash
pytest tests/test_recommendation_engine.py -v
pytest tests/test_api.py -v
pytest tests/test_models.py -v
pytest tests/test_oop_features.py -v
```

### Run with verbose output:
```bash
pytest tests/ -v
```

### Run with coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run BDD tests (if step definitions implemented):
```bash
# Using pytest-bdd
pytest tests/features/ -v

# Using behave
behave tests/features/
```

## Test Structure

### Test Files

- **`test_recommendation_engine.py`** - Unit tests for recommendation algorithm (13 tests)
- **`test_api.py`** - Integration tests for API endpoints (12 tests)
- **`test_models.py`** - Unit tests for data models (8 tests)
- **`test_oop_features.py`** - Tests for OOP patterns (8 tests)
- **`conftest.py`** - Pytest configuration and fixtures

### Test Categories

#### Unit Tests (31 tests)
- **Recommendation Engine**: 13 tests
  - Engine initialization
  - Weight validation
  - Subject matching (perfect, partial, no requirements)
  - Grade matching (exceeds, meets, below)
  - Preference matching (region, budget)
  - Ranking scoring (top-ranked, no ranking)
  - Weighted score calculation

- **Model Tests**: 8 tests
  - Student creation and validation
  - Course creation and validation
  - Model methods (matching, affordability, serialization)
  - Profile completeness

- **OOP Features**: 8 tests
  - Inheritance (Student, Course from BaseModel)
  - Composition (RecommendationEngine with scorers)
  - Polymorphism (to_dict, from_dict)

#### Integration Tests (12 tests)
- **API Endpoints**: 12 tests
  - Health check
  - Authentication (register, login)
  - Course endpoints
  - University endpoints
  - Protected endpoints (auth required)
  - Database connectivity

## Test Coverage

### Current Coverage
- **Total Tests**: 43
- **Passing**: 43 (100%) ✅
- **Failing**: 0
- **Skipped**: 0

### Coverage Areas

#### ✅ Fully Covered
- Recommendation algorithm logic
- Subject matching
- Grade matching
- Preference matching
- Ranking scoring
- Model creation and validation
- OOP patterns (inheritance, composition, polymorphism)
- API endpoints
- Authentication
- Input validation

#### ⚠️ Partially Covered
- Career interest filtering (tested indirectly)
- Feedback system (tested via API)
- HESA data enrichment (tested indirectly)

#### ❌ Not Covered (Future)
- Performance benchmarks
- Load testing
- Security penetration testing
- Browser-based UI testing

## Test Strategy

See **[TEST_STRATEGY.md](./TEST_STRATEGY.md)** for:
- Test objectives and approach
- Test levels and types
- Test execution strategy
- Coverage goals
- Tools and frameworks
- Risk-based testing

## Test Cases Catalog

See **[TEST_CASES_CATALOG.md](./TEST_CASES_CATALOG.md)** for:
- Complete list of all 43 test cases
- Test IDs and descriptions
- What each test validates
- How each test works
- Expected results
- Current status

## BDD/Gherkin Scenarios

See **[BDD_TEST_GUIDE.md](./BDD_TEST_GUIDE.md)** for:
- Gherkin syntax explanation
- Feature file structure
- Step definition examples
- How to run BDD tests
- Mapping to existing tests

### Feature Files

All Gherkin feature files are in `features/` directory:

1. **recommendation_engine.feature** - 10 scenarios
2. **authentication.feature** - 13 scenarios
3. **student_profile.feature** - 9 scenarios
4. **recommendations.feature** - 10 scenarios
5. **feedback.feature** - 10 scenarios
6. **courses_and_universities.feature** - 10 scenarios

**Total Gherkin Scenarios**: 62 scenarios

## Test Execution

### Prerequisites

1. **Python 3.11+** installed
2. **pytest** installed: `pip install pytest pytest-cov`
3. **Database** (for integration tests):
   - PostgreSQL running
   - Database initialized: `python server/database/init_db.py`
   - Environment variables set (see `.env` file)

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up database (if running integration tests)
cd server/database
python init_db.py

# 3. Run tests
cd server
pytest tests/ -v
```

### Test Execution Options

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_recommendation_engine.py

# Run specific test
pytest tests/test_recommendation_engine.py::TestRecommendationEngine::test_engine_initialization

# Run tests matching pattern
pytest tests/ -k "test_calculate"

# Run and stop on first failure
pytest tests/ -x

# Run with detailed output
pytest tests/ -vv
```

## Test Results

### Latest Results

See **[TEST_RESULTS_SUMMARY.md](./TEST_RESULTS_SUMMARY.md)** for latest test execution results.

**Summary**: ✅ **43/43 tests passing (100%)**

- ✅ Unit Tests: 31/31 (100%)
- ✅ Integration Tests: 12/12 (100%)

## Notes

- Tests may require database connection for some integration tests
- Set environment variables for database connection if needed
- Some tests may skip if database is not available (graceful degradation)
- All tests are designed to be independent and idempotent

## Test Maintenance

### Adding New Tests

1. **Unit Tests**: Add to appropriate `test_*.py` file
2. **Integration Tests**: Add to `test_api.py`
3. **BDD Scenarios**: Add to appropriate `features/*.feature` file

### Test Naming Convention

- Test methods: `test_<what_is_being_tested>`
- Test classes: `Test<ComponentName>`
- Feature files: `<feature_name>.feature`

### Test Documentation

- Document test purpose in docstrings
- Include expected behavior in assertions
- Update test catalog when adding tests

## Related Documentation

- **[Module Documentation](../../docs/modules/)** - Technical documentation for components
- **[Database Documentation](../../docs/database/)** - Database setup and migration guides
- **[Setup Guides](../../docs/setup/)** - Installation and setup instructions
