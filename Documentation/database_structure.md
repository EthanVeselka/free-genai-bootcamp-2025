# Database Structure

This document outlines the database schema and relationships for the language learning application.

## Tables

### 1. groups
```sql
CREATE TABLE groups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  words_count INTEGER DEFAULT 0  -- Counter cache for the number of words in the group
);
```

### 2. words
```sql
CREATE TABLE words (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kanji TEXT NOT NULL,
  romaji TEXT NOT NULL,
  english TEXT NOT NULL,
  parts TEXT NOT NULL  -- Store parts as JSON string
);
```

### 3. word_groups (Relationship table)
```sql
CREATE TABLE word_groups (
  word_id INTEGER NOT NULL,
  group_id INTEGER NOT NULL,
  FOREIGN KEY (word_id) REFERENCES words(id),
  FOREIGN KEY (group_id) REFERENCES groups(id)
);
```

### 4. study_activities
```sql
CREATE TABLE study_activities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,  -- Name of the activity (e.g., "Flashcards", "Quiz")
  url TEXT NOT NULL,  -- The full url of the study activity
  preview_url TEXT    -- The url to the preview image for the activity
);
```

### 5. study_sessions
```sql
CREATE TABLE study_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  group_id INTEGER NOT NULL,  -- The group of words being studied
  study_activity_id INTEGER NOT NULL,  -- The activity performed
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Timestamp of the session
  FOREIGN KEY (group_id) REFERENCES groups(id),
  FOREIGN KEY (study_activity_id) REFERENCES study_activities(id)
);
```

### 6. word_review_items
```sql
CREATE TABLE word_review_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  word_id INTEGER NOT NULL,
  study_session_id INTEGER NOT NULL,  -- Link to study session
  correct BOOLEAN NOT NULL,  -- Whether the answer was correct (true) or wrong (false)
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Timestamp of the review
  FOREIGN KEY (word_id) REFERENCES words(id),
  FOREIGN KEY (study_session_id) REFERENCES study_sessions(id)
);
```

### 7. word_reviews (Aggregated statistics)
```sql
CREATE TABLE word_reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  word_id INTEGER NOT NULL,
  correct_count INTEGER DEFAULT 0,
  wrong_count INTEGER DEFAULT 0,
  last_reviewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (word_id) REFERENCES words(id)
);
```

## Relationships

1. Words to Groups (Many-to-Many)
   - Through `word_groups` junction table
   - One word can be in multiple groups
   - One group can have multiple words
   - Foreign keys ensure referential integrity:
     - `word_groups.word_id` → `words.id`
     - `word_groups.group_id` → `groups.id`

2. Study Sessions
   - Links a group with a study activity
   - Records when users study words
   - Foreign keys:
     - `study_sessions.group_id` → `groups.id`
     - `study_sessions.study_activity_id` → `study_activities.id`
   - Tracks individual word reviews through `word_review_items`

3. Word Reviews Flow
   - Individual reviews stored in `word_review_items`:
     - Links to `study_sessions` and `words`
     - Records correct/incorrect answers
     - Timestamps each review
   - Aggregated statistics in `word_reviews`:
     - Maintains running totals of correct/incorrect answers
     - Tracks last review timestamp
     - One summary row per word

## Database Management

### Initialize Database
```bash
cd lang-portal/backend-flask
invoke init-db
```

### Reset Database
```bash
# Option 1: Clear study data only
curl -X POST http://localhost:5000/api/study-sessions/reset

# Option 2: Complete reset
rm words.db
# Then run invoke init-db
```

### Check Database State
```bash
# List all tables
sqlite3 words.db ".tables"

# Check groups
sqlite3 words.db "SELECT * FROM groups;"

# Count words in a group
sqlite3 words.db "SELECT COUNT(*) FROM word_groups WHERE group_id = 1;"
``` 