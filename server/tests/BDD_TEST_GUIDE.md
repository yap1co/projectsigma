# BDD Test Guide - Gherkin/Cucumber Format

## Overview

This document explains the Behavior-Driven Development (BDD) test scenarios written in Gherkin format for the University Course Recommender system.

## What is Gherkin?

Gherkin is a plain-text language used to write test scenarios in a human-readable format. It uses keywords like `Given`, `When`, `Then` to describe test steps.

## Feature Files

All Gherkin feature files are located in `server/tests/features/`:

1. **`recommendation_engine.feature`** - Recommendation algorithm scenarios
2. **`authentication.feature`** - User registration and login scenarios
3. **`student_profile.feature`** - Profile management scenarios
4. **`recommendations.feature`** - Recommendation API scenarios
5. **`feedback.feature`** - Feedback system scenarios
6. **`courses_and_universities.feature`** - Course and university browsing scenarios

## Gherkin Syntax

### Keywords

- **Feature**: Describes the feature being tested
- **Scenario**: A single test case
- **Background**: Steps that run before each scenario
- **Given**: Precondition/setup step
- **When**: Action step
- **Then**: Expected outcome/assertion
- **And/But**: Continuation of previous step

### Example

```gherkin
Feature: User Registration
  As a student
  I want to register for an account
  So that I can access personalized recommendations

  Scenario: Register with valid data
    Given I am a new user
    When I register with email "test@example.com" and password "password123"
    Then I should receive an access token
    And my account should be created
```

## Feature File Structure

### Recommendation Engine Feature

**Purpose**: Test recommendation algorithm logic

**Key Scenarios**:
- Perfect subject matching
- Grade requirement matching
- Career interest filtering
- Highest grade prioritization
- Location and budget preferences
- Weighted score calculation
- Diversity bonuses
- Match reason generation

### Authentication Feature

**Purpose**: Test user registration and login

**Key Scenarios**:
- Successful registration
- Registration validation (missing fields, invalid email, weak password)
- Duplicate email handling
- Successful login
- Login failure (invalid credentials)
- Protected endpoint access
- Token validation

### Student Profile Feature

**Purpose**: Test profile management

**Key Scenarios**:
- Get profile
- Update preferences
- Update academic profile
- Change password
- Password validation
- Profile autosave

### Recommendations Feature

**Purpose**: Test recommendation API endpoints

**Key Scenarios**:
- Get personalized recommendations
- Career interest filtering
- Grade requirement handling
- Location and budget matching
- Feedback influence
- Match reasons
- Advanced SQL recommendations
- Missing data handling

### Feedback Feature

**Purpose**: Test feedback system

**Key Scenarios**:
- Submit positive/negative feedback
- Feedback with notes
- Get feedback history
- Feedback influence on recommendations
- Feedback decay over time
- Similar student feedback aggregation

### Courses and Universities Feature

**Purpose**: Test course and university browsing

**Key Scenarios**:
- Get all courses
- Filter courses (subject, university, fee)
- Combine filters
- Get all universities
- Handle invalid parameters
- Entry requirements display

## Implementing Step Definitions

To execute these Gherkin scenarios, you need to implement step definitions. Here's an example using pytest-bdd:

### Example Step Definitions

```python
# server/tests/step_definitions/test_steps.py

from pytest_bdd import given, when, then, parsers
from app import app
import json

@given("the recommendation engine is initialized")
def recommendation_engine_initialized():
    from recommendation_engine import RecommendationEngine
    return RecommendationEngine()

@given("a student with subjects {subjects}")
def student_with_subjects(subjects):
    subject_list = [s.strip() for s in subjects.split(",")]
    return {'subjects': subject_list}

@when("I request recommendations")
def request_recommendations(client, student_data):
    response = client.post('/api/recommendations', 
                          json=student_data,
                          headers={'Authorization': f'Bearer {token}'})
    return response

@then("I should receive at least {count:d} recommendations")
def verify_recommendation_count(response, count):
    data = json.loads(response.data)
    assert len(data['recommendations']) >= count
```

## Running BDD Tests

### Option 1: Using pytest-bdd

```bash
# Install pytest-bdd
pip install pytest-bdd

# Run all BDD tests
pytest tests/features/ -v

# Run specific feature
pytest tests/features/recommendation_engine.feature -v
```

### Option 2: Using Cucumber (Python)

```bash
# Install cucumber
pip install behave

# Run tests
behave tests/features/
```

### Option 3: Manual Execution

The Gherkin scenarios serve as:
1. **Test Documentation**: Human-readable test specifications
2. **Test Planning**: Guide for test implementation
3. **Requirements**: Acceptance criteria for features

You can manually execute tests based on these scenarios.

## Mapping Gherkin to Existing Tests

### Recommendation Engine Scenarios

| Gherkin Scenario | Existing Test | Status |
|------------------|---------------|--------|
| Generate recommendations for perfect match | `test_calculate_subject_match_perfect` | ✅ |
| Filter by career interests | Indirectly tested | ⚠️ |
| Prioritize by highest grade | Not explicitly tested | ❌ |
| Match by location | `test_calculate_preference_match_region` | ✅ |
| Match by budget | `test_calculate_preference_match_budget` | ✅ |
| Calculate weighted score | `test_calculate_match_score_weighted` | ✅ |

### Authentication Scenarios

| Gherkin Scenario | Existing Test | Status |
|------------------|---------------|--------|
| Register with valid data | `test_register_valid_data` | ✅ |
| Register with missing fields | `test_register_missing_fields` | ✅ |
| Login with valid credentials | Not explicitly tested | ❌ |
| Login with invalid credentials | `test_login_invalid_credentials` | ✅ |
| Access protected endpoint | `test_get_profile_without_auth` | ✅ |

## Test Coverage Gaps

Based on Gherkin scenarios, these areas need additional tests:

1. **Career Interest Filtering**: Explicit test for strict filtering
2. **Highest Grade Prioritization**: Test for grade-based bonus
3. **Feedback Influence**: Test feedback affecting recommendations
4. **Profile Autosave**: Test automatic profile saving
5. **Advanced SQL Recommendations**: Test CTE-based recommendations
6. **Feedback Aggregation**: Test similar student feedback

## Benefits of BDD/Gherkin

1. **Human-Readable**: Non-technical stakeholders can understand tests
2. **Living Documentation**: Tests serve as executable specifications
3. **Collaboration**: Developers, testers, and business analysts can collaborate
4. **Traceability**: Link tests to requirements
5. **Maintainability**: Easy to update when requirements change

## Next Steps

1. **Implement Step Definitions**: Create Python step definitions for all scenarios
2. **Run BDD Tests**: Execute scenarios using pytest-bdd or behave
3. **Fill Coverage Gaps**: Add tests for scenarios not yet covered
4. **CI Integration**: Add BDD tests to CI pipeline
5. **Generate Reports**: Create human-readable test reports

## Tools and Resources

- **pytest-bdd**: BDD plugin for pytest
- **behave**: BDD framework for Python
- **Gherkin Reference**: https://cucumber.io/docs/gherkin/reference/
- **BDD Best Practices**: https://cucumber.io/docs/bdd/

## Example: Complete Feature Implementation

```python
# server/tests/step_definitions/recommendation_steps.py

from pytest_bdd import given, when, then, scenario
from recommendation_engine import RecommendationEngine

@scenario('recommendation_engine.feature', 
          'Generate recommendations for student with perfect subject match')
def test_perfect_subject_match():
    pass

@given("a student with subjects {subjects}")
def student_subjects(subjects):
    return [s.strip().strip('"') for s in subjects.split(",")]

@given("predicted grades:")
def predicted_grades(table):
    return {row['Subject']: row['Grade'] for row in table}

@when("I request recommendations")
def request_recommendations(student_subjects, predicted_grades):
    engine = RecommendationEngine()
    return engine.get_recommendations(
        student_subjects,
        predicted_grades,
        {},
        {}
    )

@then("I should receive at least {count:d} recommendations")
def verify_count(recommendations, count):
    assert len(recommendations) >= count

@then("the top recommendation should have a match score greater than {score:g}")
def verify_top_score(recommendations, score):
    assert recommendations[0]['matchScore'] > score
```

## Conclusion

The Gherkin feature files provide:
- ✅ Comprehensive test scenarios
- ✅ Human-readable test documentation
- ✅ Acceptance criteria for features
- ✅ Guide for test implementation
- ✅ Living documentation

These scenarios can be executed using BDD frameworks or used as documentation for manual testing.
