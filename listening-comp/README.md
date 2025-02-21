# JLPT Listening Practice

An AI-powered tool for generating and practicing JLPT-style listening comprehension questions.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Create .env file with:
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json  # For Text-to-Speech
GROQ_API_KEY=your_groq_api_key  # For Groq LLM API

```

3. Initialize the data:
```bash
# Create necessary directories
mkdir -p backend/data/questions
mkdir -p frontend/static/audio

# Download and process transcripts (optional)
python backend/transcript_processor.py
# You can specify the video/playlist to pull from
```

## Usage

1. Start the app:
```bash
streamlit run frontend/main.py
```

2. Select practice type:
- Dialogue Practice (Section 2)
- Phrase Matching (Section 3)

3. Choose a topic and generate a question

4. Features:
- AI-generated questions based on JLPT examples
- Text-to-speech audio generation
- Instant feedback with explanations
- Save questions for later practice

## Data Structure

Questions are stored in `backend/data/questions/` as text files:
- Section 2: Dialogue-based questions
- Section 3: Phrase matching questions

Audio files are generated in `frontend/static/audio/`.