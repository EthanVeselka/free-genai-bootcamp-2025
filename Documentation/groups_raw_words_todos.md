# Groups Raw Words Endpoint Implementation

This document outlines the implementation and testing of the groups raw words endpoint.

## Implemented TODOs

GET `/groups/:id/words/raw`
- Returns a raw list of words for a specific group
- No pagination
- Used for direct data access

## Database Setup

Initialize the database with required tables:

```bash
cd lang-portal/backend-flask
invoke init-db
```

## Unit Tests

Created test file `tests/test_groups.py` with tests for:
- Getting raw words from a valid group
- Handling non-existent group requests

Run tests with:
```bash
python -m unittest tests/test_groups.py -v
```

## Manual Testing

1. Start the Flask server:
```bash
python app.py
```

2. Test with existing group (ID 1):
```bash
curl http://localhost:5000/groups/1/words/raw
```

Response shows list of Japanese verbs:
```json
[
  {
    "english": "to pay",
    "id": 1,
    "kanji": "払う",
    "romaji": "harau"
  },
  {
    "english": "to go",
    "id": 2,
    "kanji": "行く",
    "romaji": "iku"
  }
  // ... (60 verbs total)
]
```

3. Test with non-existent group (ID 3):
```bash
curl http://localhost:5000/groups/3/words/raw
```

Response shows error:
```json
{
  "error": "Group not found"
}
```

## Database Structure

The endpoint uses three tables:
- `groups`: Stores group information
- `words`: Stores the Japanese words
- `word_groups`: Links words to groups

Group 1 contains 60 common Japanese verbs with their kanji, romaji, and English translations.

## Error Handling

The endpoint handles:
- Non-existent groups (404 error)
- Database errors (500 error)
- Returns proper JSON responses in all cases 