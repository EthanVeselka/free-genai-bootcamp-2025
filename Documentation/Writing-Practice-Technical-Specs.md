# Writing Practice App - Technical Documentation

## Architecture Overview

The writing practice app consists of two main components:
1. Word Practice (`gradio_word.py`)
2. Sentence Practice (`gradio_app.py`)

Both integrate with Lang-Portal for session tracking and word management.

## Components

### Word Practice
- Simple word-by-word practice
- Binary correct/incorrect grading
- Direct integration with study sessions
- Uses MangaOCR for handwriting recognition

### Sentence Practice
- Complete sentence generation using Groq LLM
- Advanced grading (S/A/B/C) with detailed feedback
- Translation validation
- Uses MangaOCR for handwriting recognition

## Integration Points

### Lang-Portal Integration
1. Study Session Creation
```python
url = "http://localhost:5000/api/study-sessions"
data = {
    'group_id': int(group_id),
    'study_activity_id': 2  # Writing practice activity
}
```

2. Word Loading
```python
url = f"http://localhost:5000/groups/{group_id}/words/raw"
```

3. Review Submission
```python
url = f"http://localhost:5000/api/study-sessions/{session_id}/review"
data = {
    'word_id': word_id,
    'correct': is_correct
}
```

## Dependencies
- Gradio: UI framework
- MangaOCR: Japanese handwriting recognition
- Groq: LLM for sentence generation and grading
- Requests: API communication
- Python-dotenv: Environment management

## Data Flow

1. Session Initialization:
```
Lang-Portal Launch → Create Study Session → Load Word Group → Start Practice
```

2. Practice Flow:
```
Get Word → Display → User Input → OCR → Grade → Submit Review → Next Word
```

3. Grading Flow (Sentence Practice):
```
Image → OCR → Translation → LLM Grading → Feedback → Submit Review
```

## Environment Variables
- `GROQ_API_KEY`: For LLM access
- `GROUP_ID`: Selected word group from Lang-Portal
- `SESSION_ID`: Created study session ID

## API Endpoints Used
| Endpoint | Purpose | Method |
|----------|---------|--------|
| `/api/study-sessions` | Create session | POST |
| `/groups/:id/words/raw` | Get words | GET |
| `/api/study-sessions/:id/review` | Submit review | POST |

## Error Handling
- Session creation failures
- Word loading errors
- OCR processing errors
- LLM API errors
- Review submission failures

## Future Enhancements
1. Offline mode support
2. Batch review submission
3. Progress visualization
4. Custom grading criteria
5. Multiple OCR engine support 