# JLPT Listening Practice - Technical Documentation

## Architecture Overview

```
├── backend/
│   ├── question_generator.py   # Question generation using LLMs
│   ├── audio_generator.py      # Text-to-speech conversion
│   ├── vector_store.py         # Similarity search for questions
│   └── data/
│       ├── questions/          # Structured question files
│       ├── stored_questions.json  # User's saved questions
│       └── vectorstore/        # ChromaDB embeddings
├── frontend/
│   ├── main.py                # Streamlit UI
│   └── static/
│       └── audio/            # Generated audio files
```

## Data Pipeline

1. **Question Collection**
   - YouTube transcripts processed into structured format
   - Stored in `questions/*.txt` files
   - Format includes Introduction, Conversation/Situation, Question

2. **Vector Embeddings**
   - Using Sentence Transformers (multilingual-e5-base)
   - ChromaDB for similarity search
   - Enables finding similar questions for generation

3. **Question Generation**
   - Uses Mistral8x7b for generating new questions
   - Can generate based on similar existing questions
   - Maintains JLPT format and difficulty

4. **Audio Generation**
   - Google Cloud Text-to-Speech
   - Multiple Japanese voices
   - Gender-appropriate voice selection
   - Automatic silence insertion

## Models & APIs

### Language Models
- Mistral8x7b: Question generation and feedback
- Sentence Transformers: Question similarity search and embeddings

### Text-to-Speech
- Google Cloud TTS
- Neural Japanese voices
- Voice mapping based on speaker gender

## Frontend Features

1. **Practice Types**
   - Section 2: Dialogue comprehension
   - Section 3: Phrase matching

2. **Question Management**
   - Save/load questions
   - Track practice history
   - Delete questions

3. **Audio Controls**
   - Generate audio
   - Play/replay controls
   - Automatic file cleanup

4. **Feedback System**
   - Immediate answer validation
   - Detailed explanations
   - Japanese language insights

## Data Formats

### Question Structure
```json
{
  "Introduction": "Text...",
  "Conversation": "Text...",  // or "Situation" for Section 3
  "Question": "Text...",
  "Options": ["A", "B", "C", "D"]
}
```

### Stored Questions
```json
{
  "question_id": {
    "question": {},
    "practice_type": "string",
    "topic": "string",
    "created_at": "timestamp",
    "audio_file": "path/string"
  }
}
``` 