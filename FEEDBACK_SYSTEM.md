# Recommendation Feedback System

## Overview
The recommendation engine now includes a feedback-based learning system that allows students to provide thumbs up/down feedback on recommendations, which is then used to improve future recommendations dynamically.

## Features

### 1. Generic Subject Matching Logic
- **Problem Solved**: Removed hardcoded subject lists (e.g., `['computer science', 'physics', 'chemistry', 'biology']`)
- **Solution**: Implemented generic `_is_legitimate_match()` method that:
  - Uses configurable `generic_terms` set for common false positives
  - Uses `legitimate_generic_matches` dictionary with lambda functions for dynamic checking
  - Works for any subject combination without hardcoding

### 2. Feedback System
- **Database Table**: `recommendation_feedback`
  - Stores: `student_id`, `course_id`, `feedback_type` (positive/negative), `feedback_at`, `search_criteria`, `match_score`, `notes`
- **Settings Table**: `recommendation_settings`
  - Tunable parameters: `feedback_weight`, `feedback_decay_days`, `min_feedback_count`, `positive_feedback_boost`, `negative_feedback_penalty`

### 3. API Endpoints

#### Submit Feedback
```
POST /api/recommendations/feedback
Headers: Authorization: Bearer <token>
Body: {
  "courseId": "COURSE123",
  "feedbackType": "positive" | "negative",
  "matchScore": 0.65,
  "searchCriteria": {...},
  "notes": "Optional notes"
}
```

#### Get Course Feedback History
```
GET /api/recommendations/feedback/<course_id>
Headers: Authorization: Bearer <token>
Returns: Feedback history and summary for the course
```

#### Get Settings
```
GET /api/recommendations/settings
Headers: Authorization: Bearer <token>
Returns: All tunable settings with descriptions
```

#### Update Setting
```
PUT /api/recommendations/settings/<setting_key>
Headers: Authorization: Bearer <token>
Body: {
  "value": 0.2
}
```

### 4. Dynamic Learning
- Feedback scores are calculated based on:
  - Net feedback (positive - negative)
  - Recency (feedback decays after `feedback_decay_days`)
  - Minimum count threshold (`min_feedback_count`)
- Feedback is applied to match scores with configurable weight (`feedback_weight`)
- Settings can be adjusted on-the-fly without code changes

## Database Migration

Run the migration to create the feedback tables:
```sql
-- Located at: server/database/migrations/004_recommendation_feedback.sql
```

## Usage Example

1. Student gets recommendations
2. Student clicks thumbs up/down on a course
3. Feedback is stored in database
4. Next time student searches with similar criteria:
   - System retrieves feedback for courses
   - Applies feedback-based score adjustments
   - Courses with positive feedback rank higher
   - Courses with negative feedback rank lower

## Tunable Settings

All settings can be adjusted via API or database:

- `feedback_weight` (0-1): How much feedback affects final score (default: 0.15)
- `feedback_decay_days` (int): Days before feedback relevance decays (default: 90)
- `min_feedback_count` (int): Minimum feedback needed to apply boost (default: 3)
- `positive_feedback_boost` (float): Score boost multiplier for positive feedback (default: 0.2)
- `negative_feedback_penalty` (float): Score penalty multiplier for negative feedback (default: -0.3)

## Implementation Details

### Generic Matching Logic
The `_is_legitimate_match()` method:
1. Checks if term is generic (in `generic_terms` set)
2. If generic, uses `legitimate_generic_matches` dictionary
3. Lambda functions check if student subject legitimately contains the term
4. Works for any subject without hardcoding

### Feedback Integration
- Feedback scores are fetched after initial course selection (top 100)
- Scores are applied as final adjustment to match scores
- Only courses with minimum feedback count are adjusted
- Feedback decays over time (configurable)
