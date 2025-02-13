# Japanese Vocabulary Generator Technical Specifications

## Overview
A Streamlit-based tool that leverages Groq's LLM API to generate properly formatted Japanese vocabulary entries with kanji breakdowns and romaji translations.

## Technical Requirements

### Dependencies
- Python 3.8+
- Streamlit >= 1.31.0
- Groq >= 0.4.2
- python-dotenv >= 1.0.0
- pyperclip >= 1.8.2

### Environment
- Groq API key required (setup in local env)
- Supports various environment setups (local, Conda, etc.)
- Cross-platform compatible

## Architecture

### Component Flow
```
User Input → Streamlit UI → Groq API → JSON Validation → Formatting → Display/Save
```

### Data Flow
1. User provides input parameters
2. Application sends structured prompt to Groq API
3. Response is validated and formatted
4. Results are:
   - Displayed (first 5 entries)
   - Saved to file (all entries)
   - Available for clipboard copy

## API Integration

### Groq API Usage
- Primary model: mixtral-8x7b-32768
- Backup models: qwen-2.5-32b, others
- Context window: Varies by model
- Temperature: 0.7
- Max tokens: 2000

### Prompt Structure
```python
system_prompt = f"""
You are a Japanese language expert. Generate {count} vocabulary words based on the given input.
    Format each word exactly like this JSON structure:
    {{
      "kanji": "偉い",
      "romaji": "erai",
      "english": "great",
      "parts": [
        {{ "kanji": "偉", "romaji": ["e","ra"] }},
        {{ "kanji": "い", "romaji": ["i"] }}
      ]
    }}
    
    Critical requirements:
    1. Return only the JSON array with {count} items. No additional text.
    2. Every word MUST include the kanji characters.
    3. The 'parts' array MUST break down EACH character of the word.
    4. Follow the exact JSON structure shown above.
    5. Ensure all Japanese text uses proper kanji where appropriate."""
"""
```

## Data Validation

### JSON Structure Validation
- Required fields: kanji, romaji, english, parts
- Parts array structure validation
- Romaji array validation
- Kanji string validation

### Error Handling
- API connection errors
- JSON parsing errors
- Invalid response structure
- Missing fields

## Output Formats

### File Output
- Location: generated_vocab.json
- Format: Formatted JSON with proper indentation
- UTF-8 encoding

### Display Output
- Limited to 5 entries for readability
- Syntax highlighted JSON
- Info message for truncated results

## User Interface

### Input Controls
- Text input for category/theme
- Number input for count (1-25)
- Model selection dropdown

### Output Controls
- Copy JSON button
- Success notifications
- Error messages
- Loading indicators

## Session Management
- Model list caching
- Results persistence
- Copy operation state management

## Error Messages
- API connection failures
- Invalid input handling
- Generation failures
- Validation errors

## Performance Considerations
- Model response caching
- Efficient JSON parsing
- Optimized display rendering
- Fast transitions

## Security
- API key management via environment variables
- No data persistence beyond current session
- Local file system usage only

## Future Enhancements
1. Batch processing capabilities
2. Advanced filtering options
3. Custom formatting templates
4. Export to different formats
5. Integration with vocabulary management systems 