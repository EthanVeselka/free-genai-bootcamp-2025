# Japanese Writing Practice App

A Gradio-based application for practicing Japanese writing, integrated with Lang-Portal for study session tracking.

## Features
- Word writing practice with OCR recognition
- Sentence writing practice with AI grading
- Integration with Lang-Portal study sessions
- Real-time feedback and grading
- Support for both individual words and complete sentences

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
GROQ_API_KEY=your_groq_api_key
GROUP_ID=your_group_id  # From Lang-Portal
```

3. Launch the app:
```bash
# For word practice:
python gradio_word.py

# For sentence practice:
python gradio_app.py
```

## Usage
1. Select a word group in Lang-Portal
2. Click "Launch" to start a study session
3. Practice writing Japanese characters
4. Get instant feedback and grading
5. Track your progress in Lang-Portal 