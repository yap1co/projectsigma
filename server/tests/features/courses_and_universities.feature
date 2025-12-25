# Feature: Courses and Universities
# As a student
# I want to browse courses and universities
# So that I can explore available options

Feature: Course and University Browsing

  Scenario: Get all courses
    Given courses exist in the database
    When I request all courses
    Then I should receive a list of courses
    And each course should include:
      | Field              | Type   |
      | course_id          | string |
      | name               | string |
      | university         | object |
      | entryRequirements  | object |
      | fees               | object |
      | employability      | object |
    And the response should include total count

  Scenario: Get courses with limit
    Given courses exist in the database
    When I request courses with limit "10"
    Then I should receive at most 10 courses
    And the response should indicate the limit applied

  Scenario: Filter courses by subject
    Given courses exist in the database
    When I request courses filtered by subject "Mathematics"
    Then I should receive only courses related to "Mathematics"
    And all returned courses should match the subject filter

  Scenario: Filter courses by university
    Given courses exist in the database
    When I request courses filtered by university "University of Oxford"
    Then I should receive only courses from "University of Oxford"
    And all returned courses should be from the specified university

  Scenario: Filter courses by maximum fee
    Given courses exist in the database
    When I request courses with max_fee "10000"
    Then I should receive only courses with fees <= "10000"
    And all returned courses should be within budget

  Scenario: Combine multiple filters
    Given courses exist in the database
    When I request courses with:
      | Filter    | Value                |
      | subject   | Mathematics           |
      | university| University of Oxford  |
      | max_fee   | 10000                 |
      | limit     | 20                    |
    Then I should receive courses matching all filters
    And the result should be limited to 20 courses

  Scenario: Get all universities
    Given universities exist in the database
    When I request all universities
    Then I should receive a list of universities
    And each university should include:
      | Field              | Type   |
      | university_id      | string |
      | name                | string |
      | region              | string |
      | ranking             | object |
      | employability_score | number |
      | website_url         | string |
    And universities should be sorted by ranking

  Scenario: Handle invalid filter parameters
    Given courses exist in the database
    When I request courses with invalid max_fee "-1000"
    Then I should receive an error response
    And the error should indicate invalid parameter
    And no courses should be returned

  Scenario: Handle missing courses gracefully
    Given no courses exist in the database
    When I request courses
    Then I should receive an empty list
    And the total count should be 0
    And the response should not error

  Scenario: Course includes entry requirements
    Given courses exist in the database
    When I request courses
    Then each course should include entry requirements
    And entry requirements should include:
      | Field  | Type  |
      | subjects | array |
      | grades   | object|
    And subjects should list required A-level subjects
    And grades should map subjects to required grades

  Scenario: Course includes university information
    Given courses exist in the database
    When I request courses
    Then each course should include university information
    And university information should include:
      | Field  | Type   |
      | name   | string |
      | region | string |
      | ranking| object |
    And the university name should match the course's university
