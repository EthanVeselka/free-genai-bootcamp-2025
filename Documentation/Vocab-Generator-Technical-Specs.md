# Japanese Vocabulary Generator Technical Specifications

## Overview
A Streamlit-based tool that leverages Groq's LLM API to generate formatted Japanese vocabulary examples with kanji breakdowns and romaji translations, organized by category (prompt).

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

## Data Management

### Category Organization
- Entries automatically organized by category
- Case-insensitive category matching
- Categories normalized to lowercase with underscores
- Duplicate entry detection based on kanji field

### Duplicate Handling
- Checks for existing entries within categories
- Prevents duplicate kanji entries
- Merges new unique entries with existing ones
- Notes new vs duplicate entries

### File Structure
- Single JSON file (`generated_vocab.json`)
- Categorized entries
- UTF-8 encoding

## Output Formats

### File Output
- Location: generated_vocab.json
- Format: Categorized JSON
- UTF-8 encoding
- Maintains existing entries
- Prevents duplicates within categories

### Display Output
- Limited to 5 entries for readability
- Syntax highlighted JSON
- Info messages for:
  - Truncated results
  - Added/Duplicate entries

## User Interface

### Input Controls
- Text input for category/theme
- Number input for count (1-100)
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
- Category state tracking

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
1. Category management interface
2. Batch processing capabilities
3. Advanced filtering options
4. Custom formatting templates
5. Export to different formats
6. Integration with vocabulary management systems 