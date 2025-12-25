# Feature: Recommendation Engine
# As a student
# I want to receive personalized course recommendations
# So that I can find courses that match my academic profile and preferences

Feature: Course Recommendation Generation
  Background:
    Given the recommendation engine is initialized
    And there are courses available in the database

  Scenario: Generate recommendations for student with perfect subject match
    Given a student with subjects "Mathematics", "Physics", "Chemistry"
    And predicted grades:
      | Subject      | Grade |
      | Mathematics  | A*    |
      | Physics      | A     |
      | Chemistry    | B     |
    When I request recommendations
    Then I should receive at least 10 recommendations
    And the top recommendation should have a match score greater than 0.7
    And the top recommendation should match my subjects

  Scenario: Generate recommendations with grade requirements
    Given a student with subjects "Mathematics", "Economics"
    And predicted grades:
      | Subject     | Grade |
      | Mathematics | B     |
      | Economics   | A*    |
    And a course requires "Mathematics" grade "A"
    When I request recommendations
    Then courses requiring "Mathematics" grade "A" should have lower scores
    And courses matching my "Economics" grade "A*" should rank higher

  Scenario: Filter recommendations by career interests
    Given a student with career interest "Business & Finance"
    And subjects "Mathematics", "Economics", "English Literature"
    When I request recommendations
    Then I should NOT receive courses containing "Computer Science"
    And I should NOT receive courses containing "Physics"
    And I should receive courses matching "Business", "Finance", or "Economics"
    And all recommendations should match my career interest

  Scenario: Prioritize courses by highest predicted grade
    Given a student with subjects "Mathematics", "English Literature", "History"
    And predicted grades:
      | Subject           | Grade |
      | Mathematics       | B     |
      | English Literature| A*    |
      | History           | A     |
    And no career interests specified
    When I request recommendations
    Then courses related to "English Literature" should rank higher
    And courses should receive a bonus for matching my highest grade subject

  Scenario: Match recommendations by location preference
    Given a student with preferred region "London"
    And subjects "Mathematics", "Economics"
    When I request recommendations
    Then courses in "London" should have higher preference scores
    And courses outside "London" should have lower preference scores

  Scenario: Match recommendations by budget constraint
    Given a student with maximum budget "10000"
    And subjects "Mathematics", "Physics"
    When I request recommendations
    Then courses with fees <= "10000" should have higher scores
    And courses with fees > "10000" should have lower scores

  Scenario: Calculate weighted composite score
    Given a student with complete profile
    And a course with:
      | Attribute           | Value                    |
      | Required Subjects   | Mathematics, Physics     |
      | Required Grades     | Mathematics: A, Physics: B |
      | University Ranking  | 10                       |
      | Employment Rate     | 90%                      |
      | Fees                | £9000                    |
    When the recommendation engine calculates the match score
    Then the score should combine:
      | Factor              | Weight |
      | Subject Match       | 35%    |
      | Grade Match         | 25%    |
      | Preference Match    | 15%    |
      | University Ranking  | 15%    |
      | Employability       | 10%    |
    And the final score should be between 0.0 and 1.0

  Scenario: Handle course with no entry requirements
    Given a student with subjects "Mathematics", "Physics"
    And a course with no entry requirements
    When I request recommendations
    Then the course should still appear in recommendations
    And the subject match score should be neutral (0.5)

  Scenario: Apply diversity bonus for multiple subject matches
    Given a student with subjects "Mathematics", "Economics", "English Literature"
    When I request recommendations
    Then courses matching multiple subjects should receive a diversity bonus
    And courses matching 2+ subjects should rank higher than single-subject matches

  Scenario: Filter out conflicting courses for career interests
    Given a student with career interest "Business & Finance"
    And a course named "Computer Science"
    When I request recommendations
    Then "Computer Science" should NOT appear in recommendations
    And the course should be filtered out before scoring

  Scenario: Generate match reasons for recommendations
    Given a student with subjects "Mathematics", "Economics"
    And predicted grades:
      | Subject     | Grade |
      | Mathematics | A*    |
      | Economics   | A     |
    When I request recommendations
    Then each recommendation should include match reasons
    And reasons should explain why the course matches
    And reasons should mention subject matches, grade matches, and preferences
