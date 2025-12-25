# Feature: Course Recommendations
# As a student
# I want to receive personalized course recommendations
# So that I can discover courses that match my profile

Feature: Course Recommendation System

  Background:
    Given I am authenticated as a student
    And I have a complete profile with subjects and grades

  Scenario: Get personalized recommendations
    Given my profile:
      | Field           | Value                          |
      | subjects        | Mathematics, Economics         |
      | predictedGrades | Mathematics: A*, Economics: A  |
      | preferredRegion | London                         |
      | maxBudget        | 10000                          |
    When I request recommendations
    Then I should receive a list of recommendations
    And each recommendation should include:
      | Field            | Type   |
      | course           | object |
      | matchScore       | number |
      | meetsRequirements| boolean|
      | reasons          | array  |
    And recommendations should be sorted by match score (highest first)
    And I should receive up to 50 recommendations

  Scenario: Get recommendations filtered by career interests
    Given my profile includes career interest "Business & Finance"
    And my subjects are "Mathematics", "Economics", "English Literature"
    When I request recommendations
    Then all recommendations should match "Business & Finance"
    And I should NOT receive courses containing "Computer Science"
    And I should NOT receive courses containing "Physics"
    And I should receive courses matching "Business", "Finance", or "Economics"

  Scenario: Recommendations prioritize highest predicted grade
    Given my predicted grades:
      | Subject           | Grade |
      | Mathematics       | B     |
      | English Literature| A*    |
      | History           | A     |
    And I have no career interests specified
    When I request recommendations
    Then courses related to "English Literature" should rank higher
    And courses should receive a bonus for matching my highest grade subject

  Scenario: Recommendations respect grade requirements
    Given my predicted grades:
      | Subject     | Grade |
      | Mathematics | B     |
      | Physics     | A     |
    And a course requires "Mathematics" grade "A"
    When I request recommendations
    Then the course requiring "Mathematics" grade "A" should have lower score
    And the recommendation should indicate I don't meet all requirements
    And courses where I meet requirements should rank higher

  Scenario: Recommendations match location preference
    Given my preferred region is "London"
    When I request recommendations
    Then courses in "London" should have higher preference scores
    And courses outside "London" should have lower preference scores
    And match reasons should mention location match

  Scenario: Recommendations respect budget constraint
    Given my maximum budget is "10000"
    When I request recommendations
    Then courses with fees <= "10000" should have higher scores
    And courses with fees > "10000" should have lower scores
    And match reasons should mention budget compatibility

  Scenario: Get recommendations with feedback influence
    Given I have previously given positive feedback to a course
    And I have similar career interests to other students
    When I request recommendations
    Then courses with positive feedback should rank higher
    And feedback from similar students should influence scores
    And the feedback weight should be applied to match scores

  Scenario: Recommendations include match reasons
    Given I request recommendations
    When I receive recommendations
    Then each recommendation should include match reasons
    And reasons should explain:
      | Reason Type          | Description                    |
      | Subject Match        | Matches my A-level subjects    |
      | Grade Match          | Meets/exceeds grade requirements|
      | Career Interest      | Matches my career interests    |
      | Location             | In my preferred region         |
      | Ranking              | Top-ranked university          |
      | Employability        | High employment rate           |

  Scenario: Get advanced recommendations using SQL
    Given I request advanced recommendations
    When the system processes my request
    Then recommendations should be calculated using complex SQL with CTEs
    And the response should include score breakdown:
      | Component        | Weight |
      | Subject Match    | 30%    |
      | Grade Match      | 25%    |
      | Region Match     | 20%    |
      | Budget Match     | 15%    |
      | Ranking          | 10%    |

  Scenario: Recommendations handle missing data gracefully
    Given a course with missing ranking data
    And a course with missing employability data
    When I request recommendations
    Then courses with missing data should still appear
    And missing data should use neutral/default scores
    And recommendations should not fail due to missing data

  Scenario: Recommendations are diverse
    Given I have subjects "Mathematics", "Economics", "English Literature"
    When I request recommendations
    Then I should receive recommendations from different universities
    And I should receive recommendations for different course types
    And courses matching multiple subjects should receive diversity bonus
