# Feature: User Authentication
# As a student
# I want to register and login to my account
# So that I can access personalized recommendations

Feature: Student Registration and Authentication

  Scenario: Register new student with valid data
    Given I am a new user
    When I register with:
      | Field      | Value              |
      | email      | test@example.com  |
      | password   | securepass123     |
      | firstName  | John              |
      | lastName   | Doe               |
    Then I should receive a success response
    And I should receive an access token
    And I should receive a student ID
    And my account should be created in the database

  Scenario: Register with missing required fields
    Given I am a new user
    When I register with only email "test@example.com"
    Then I should receive an error response
    And the error should indicate missing required fields
    And my account should NOT be created

  Scenario: Register with invalid email format
    Given I am a new user
    When I register with email "invalid-email"
    Then I should receive an error response
    And the error should indicate invalid email format
    And my account should NOT be created

  Scenario: Register with weak password
    Given I am a new user
    When I register with password "123"
    Then I should receive an error response
    And the error should indicate password requirements
    And my account should NOT be created

  Scenario: Register with duplicate email
    Given a student with email "existing@example.com" already exists
    When I register with email "existing@example.com"
    Then I should receive an error response
    And the error should indicate user already exists
    And my account should NOT be created

  Scenario: Login with valid credentials
    Given a student with email "test@example.com" and password "password123" exists
    When I login with:
      | Field    | Value              |
      | email    | test@example.com  |
      | password | password123       |
    Then I should receive a success response
    And I should receive an access token
    And I should receive my student ID

  Scenario: Login with invalid email
    Given no student with email "nonexistent@example.com" exists
    When I login with email "nonexistent@example.com" and password "anypassword"
    Then I should receive an error response
    And the error should indicate invalid credentials
    And I should NOT receive an access token

  Scenario: Login with incorrect password
    Given a student with email "test@example.com" and password "correctpass" exists
    When I login with email "test@example.com" and password "wrongpass"
    Then I should receive an error response
    And the error should indicate invalid credentials
    And I should NOT receive an access token

  Scenario: Login with missing fields
    Given I am trying to login
    When I submit login with only email "test@example.com"
    Then I should receive an error response
    And the error should indicate missing password field

  Scenario: Access protected endpoint without authentication
    Given I am not authenticated
    When I request my profile
    Then I should receive a 401 Unauthorized response
    And I should NOT receive my profile data

  Scenario: Access protected endpoint with valid token
    Given I am authenticated with a valid token
    When I request my profile
    Then I should receive a 200 OK response
    And I should receive my profile data
    And the data should include my email, subjects, and preferences

  Scenario: Access protected endpoint with expired token
    Given I have an expired access token
    When I request my profile
    Then I should receive a 401 Unauthorized response
    And I should NOT receive my profile data

  Scenario: Access protected endpoint with invalid token
    Given I have an invalid access token
    When I request my profile
    Then I should receive a 401 Unauthorized response
    And I should NOT receive my profile data
