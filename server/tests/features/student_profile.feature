# Feature: Student Profile Management
# As a student
# I want to manage my profile information
# So that I can keep my academic details and preferences up to date

Feature: Student Profile Management

  Background:
    Given I am authenticated as a student

  Scenario: Get my profile
    Given I have a complete profile with:
      | Field            | Value                    |
      | email            | student@example.com      |
      | firstName        | Jane                    |
      | lastName         | Smith                   |
      | subjects         | Mathematics, Economics  |
      | predictedGrades  | Mathematics: A*, Economics: A |
      | preferredRegion  | London                  |
      | maxBudget        | 10000                   |
    When I request my profile
    Then I should receive my complete profile
    And the profile should include all my information
    And the password should NOT be included in the response

  Scenario: Update my preferences
    Given I have an existing profile
    When I update my preferences with:
      | Field           | Value     |
      | preferredRegion | Manchester|
      | maxBudget       | 12000     |
    Then my preferences should be updated in the database
    And I should receive a success response
    And when I request my profile, it should show the updated preferences

  Scenario: Update my academic profile
    Given I have an existing profile
    When I update my academic profile with:
      | Field           | Value                          |
      | aLevelSubjects  | Mathematics, Physics, Chemistry |
      | predictedGrades | Mathematics: A*, Physics: A, Chemistry: B |
    Then my academic profile should be updated
    And I should receive a success response
    And when I request my profile, it should show the updated subjects and grades

  Scenario: Change my password
    Given I have an existing account with password "oldpassword123"
    When I change my password with:
      | Field           | Value            |
      | currentPassword | oldpassword123   |
      | newPassword     | newpassword456   |
    Then my password should be updated
    And I should receive a success response
    And I should be able to login with the new password

  Scenario: Change password with incorrect current password
    Given I have an existing account with password "correctpass"
    When I try to change my password with:
      | Field           | Value            |
      | currentPassword | wrongpass        |
      | newPassword     | newpassword456   |
    Then I should receive an error response
    And the error should indicate incorrect current password
    And my password should NOT be changed

  Scenario: Change password with weak new password
    Given I have an existing account
    When I try to change my password with new password "123"
    Then I should receive an error response
    And the error should indicate password requirements
    And my password should NOT be changed

  Scenario: Update profile with invalid preferences
    Given I have an existing profile
    When I try to update preferences with invalid region "InvalidRegion"
    Then I should receive an error response
    And the error should indicate invalid region
    And my preferences should NOT be updated

  Scenario: Update profile with invalid budget
    Given I have an existing profile
    When I try to update preferences with maxBudget "-1000"
    Then I should receive an error response
    And the error should indicate invalid budget
    And my preferences should NOT be updated

  Scenario: Profile autosave on navigation
    Given I am on the profile setup screen
    And I have entered my subjects and grades
    When I navigate to another screen
    Then my profile data should be automatically saved
    And when I return to the profile screen, my data should be preserved
