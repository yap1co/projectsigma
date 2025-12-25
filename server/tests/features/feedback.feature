# Feature: Recommendation Feedback
# As a student
# I want to provide feedback on recommendations
# So that the system can learn and improve future recommendations

Feature: Recommendation Feedback System

  Background:
    Given I am authenticated as a student
    And I have received course recommendations

  Scenario: Submit positive feedback on a recommendation
    Given I have received a recommendation for "Business Management" course
    When I submit positive feedback for the course
    Then my feedback should be saved to the database
    And I should receive a success response
    And the feedback should include:
      | Field        | Value                    |
      | courseId     | Course identifier        |
      | feedbackType | positive                 |
      | matchScore   | Original match score     |
      | timestamp    | Current timestamp        |

  Scenario: Submit negative feedback on a recommendation
    Given I have received a recommendation for "Computer Science" course
    When I submit negative feedback for the course
    Then my feedback should be saved to the database
    And I should receive a success response
    And the feedback type should be "negative"

  Scenario: Submit feedback with notes
    Given I have received a recommendation
    When I submit feedback with notes "Not interested in this field"
    Then my feedback should include the notes
    And the notes should be saved (truncated to 500 chars if needed)

  Scenario: Get feedback history for a course
    Given I have submitted multiple feedback entries for a course
    When I request feedback history for the course
    Then I should receive all my feedback entries
    And entries should be sorted by date (newest first)
    And I should receive a summary:
      | Field     | Type |
      | positive  | int  |
      | negative  | int  |
      | total     | int  |

  Scenario: Feedback influences future recommendations
    Given I have given positive feedback to "Business Management" course
    And I have similar career interests to other students
    When I request new recommendations
    Then "Business Management" should rank higher
    And the feedback boost should be applied to the match score
    And feedback from similar students should also influence the score

  Scenario: Feedback decays over time
    Given I gave feedback 100 days ago
    When I request recommendations
    Then the old feedback should have reduced influence
    And feedback within the decay period should have full influence
    And the decay period is configurable (default 90 days)

  Scenario: Submit feedback without authentication
    Given I am not authenticated
    When I try to submit feedback
    Then I should receive a 401 Unauthorized response
    And my feedback should NOT be saved

  Scenario: Submit feedback for non-existent course
    Given I am authenticated
    When I try to submit feedback for course ID "INVALID_COURSE"
    Then I should receive a 404 Not Found response
    And my feedback should NOT be saved

  Scenario: Feedback requires minimum count for influence
    Given I have given feedback to a course
    And the total feedback count is below the minimum threshold
    When I request recommendations
    Then the feedback should NOT influence the score
    And when feedback count reaches the minimum, it should start influencing

  Scenario: Aggregate feedback from similar students
    Given multiple students with similar career interests have given feedback
    When I request recommendations
    Then feedback from similar students should be aggregated
    And the aggregated feedback should influence my recommendations
    And my own feedback should have higher weight (60%) than similar students (40%)
