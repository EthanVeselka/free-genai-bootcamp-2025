# Flask Backend Technical Specifications

## Goal

Prototype learning portal for Language learning that serves three main purposes:
- Manage an inventory of learnable vocabulary
- Function as a Learning Record Store (LRS) to track practice performance
- Provide a unified platform to launch various learning activities

## Technical Requirements

- Backend Framework: Flask (Python)
- Database: SQLite3
- Response Format: JSON only
- Authentication: None (single user system)
- Development Environment: Python 3.10+

## Directory Structure

```text
backend-flask/
├── app/
│   ├── __init__.py
│   ├── routes/          # API endpoint handlers
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── groups.py
│   │   ├── study_sessions.py
│   │   └── words.py
│   └── models/          # Database table definitions using SQLAlchemy
│       ├── __init__.py
│       ├── group.py
│       ├── study_session.py
│       ├── word.py
│       └── word_review.py
├── db/
│   ├── migrations/      # SQL files for creating database tables
│   │   ├── 0001_init.sql
│   │   └── 0002_create_tables.sql
│   └── seeds/          # Initial data for the database
│       └── basic_words.json
├── tests/
│   ├── __init__.py
│   └── test_routes/    # API endpoint tests
│       └── test_words.py
├── .gitignore
├── config.py           # Application configuration
├── requirements.txt    # Python package dependencies
└── words.db           # SQLite database file
```

## Database Schema

The application uses a SQLite database (`words.db`) with the following schema:

### Tables

**words**
- id: Integer (Primary Key)
- japanese: String
- romaji: String
- english: String
- parts: JSON

**groups**
- id: Integer (Primary Key)
- name: String

**words_groups**
- id: Integer (Primary Key)
- word_id: Integer (Foreign Key)
- group_id: Integer (Foreign Key)

**study_sessions**
- id: Integer (Primary Key)
- group_id: Integer (Foreign Key)
- created_at: DateTime
- study_activity_id: Integer

**study_activities**
- id: Integer (Primary Key)
- study_session_id: Integer (Foreign Key)
- group_id: Integer (Foreign Key)
- created_at: DateTime

**word_review_items**
- id: Integer (Primary Key)
- word_id: Integer (Foreign Key)
- study_session_id: Integer (Foreign Key)
- correct: Boolean
- created_at: DateTime

## API Endpoints

### Dashboard Endpoints

#### GET /api/dashboard/last_study_session
Returns the most recent study session information.

Response:
```json
{
  "id": 123,
  "group_id": 456,
  "created_at": "2024-03-08T17:20:23-05:00",
  "study_activity_id": 789,
  "group_name": "Basic Greetings"
}
```

#### GET /api/dashboard/study_progress
Returns study progress statistics.

Response:
```json
{
  "total_words_studied": 3,
  "total_available_words": 124
}
```

### Words Endpoints

#### GET /api/words
Returns paginated list of vocabulary words.

Response:
```json
{
  "items": [
    {
      "japanese": "こんにちは",
      "romaji": "konnichiwa",
      "english": "hello",
      "correct_count": 5,
      "wrong_count": 2
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 500,
    "items_per_page": 100
  }
}
```

### Study Session Endpoints

#### POST /api/study_sessions/:id/words/:word_id/review
Submit a review for a word in a study session.

Request:
```json
{
  "correct": true
}
```

Response:
```json
{
  "success": true,
  "word_id": 1,
  "study_session_id": 123,
  "correct": true,
  "created_at": "2024-03-08T17:33:07-05:00"
}
```

## Database Management

### Initialization
Database initialization is handled through Flask-Migrate:
```bash
flask db init
flask db migrate
flask db upgrade
```

### Seeding Data
Seed data is provided in JSON format and loaded through a custom Flask CLI command:
```bash
flask seed-db
```

Example seed file format:
```json
[
  {
    "japanese": "こんにちは",
    "romaji": "konnichiwa",
    "english": "hello"
  }
]
```

## Testing

The application uses pytest for testing. Run tests with:
```bash
pytest
```

Test files are organized to mirror the application structure:
```text
tests/
├── conftest.py           # Test fixtures
├── test_routes/
│   ├── test_dashboard.py
│   ├── test_words.py
│   └── test_study_sessions.py
└── test_models/
    └── test_word.py
```

## Error Handling

All API endpoints return appropriate HTTP status codes:
- 200: Successful operation
- 400: Bad request
- 404: Resource not found
- 500: Server error

Error responses follow the format:
```json
{
  "error": "Error message description",
  "status_code": 400
}
``` 