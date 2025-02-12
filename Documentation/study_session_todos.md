# Study Sessions Implementation

This document outlines the implementation of study session endpoints and their testing.

## Implemented TODOs

1. POST `/api/study-sessions`
   - Creates a new study session
   - Links a group of words with a study activity
   - Returns session details including start time

2. POST `/api/study-sessions/:id/review`
   - Submits a review for a word in a study session
   - Records whether the answer was correct or incorrect
   - Updates review counts for the session

## Database Setup

Initialize the database with required tables:

```bash
cd lang-portal/backend-flask
invoke init-db
```

## Unit Tests

Created test file `tests/test_study_sessions.py` with tests for:
- Creating a new study session
- Submitting a review for a session

Run tests with:
```bash
python -m unittest tests/test_study_sessions.py -v
```

## Manual Testing

1. Start the Flask server:
```bash
python app.py
```

2. Create a new study session:
```bash
curl -X POST http://localhost:5000/api/study-sessions \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": 1,
    "study_activity_id": 1
  }'
```

Expected response:
```json
{
  "id": 1,
  "group_id": 1,
  "group_name": "Test Group",
  "activity_id": 1,
  "activity_name": "Typing Tutor",
  "start_time": "2025-02-08 19:26:36",
  "end_time": "2025-02-08 19:26:36",
  "review_items_count": 0
}
```

3. Submit a review for the session:
```bash
curl -X POST http://localhost:5000/api/study-sessions/1/review \
  -H "Content-Type: application/json" \
  -d '{
    "word_id": 1,
    "correct": true
  }'
```

Expected response:
```json
{
  "message": "Review submitted successfully"
}
``` 