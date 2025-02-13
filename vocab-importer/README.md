# Japanese Vocabulary Generator

A Streamlit application that generates Japanese vocabulary with proper kanji, romaji, and English translations using the Groq API.

## Features
- Generate Japanese vocabulary based on categories or themes
- Multiple LLM model options (Mixtral-8x7B recommended)
- Proper JSON formatting matching seed data structure
- Copy to clipboard functionality
- Auto-save to file
- Display limiting for better readability

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Groq API key:
```bash
# Option 1: Environment variable
export GROQ_API_KEY=your_key_here

# Option 2: Create .env file
echo "GROQ_API_KEY=your_key_here" > .env
```

3. Run the application:
```bash
streamlit run vocab_generator.py
```

## Usage
1. Enter a category, word, or phrase (e.g., "food", "emotions", "daily activities")
2. Select number of words to generate (1-25)
3. Choose a model (Mixtral-8x7B by default)
4. Click "Generate"
5. Use "Copy JSON" to copy the output to your clipboard
6. Find complete results in `generated_vocab.json`

## Output Format
```json
[
  {
    "kanji": "食べ物",
    "romaji": "tabemono",
    "english": "food",
    "parts": [
      {"kanji": "食", "romaji": ["ta", "be"]},
      {"kanji": "べ", "romaji": ["be"]},
      {"kanji": "物", "romaji": ["mono"]}
    ]
  }
]
``` 