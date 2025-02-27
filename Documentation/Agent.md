# Lyrics Vocabulary Generator

An AI-powered tool that generates vocabulary lists from song lyrics using Groq's LLM API and DuckDuckGo search.

## Overview

This tool:
1. Searches for song lyrics using DuckDuckGo
2. Extracts the lyrics from the webpage
3. Processes the lyrics to create a structured vocabulary list
4. Outputs the results in a JSON format

## Setup

1. Install dependencies:
```bash
pip install groq duckduckgo_search python-dotenv requests html2text tenacity
```

2. Create a `.env` file with your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

## Usage

Run the script with:
```bash
python agent.py --song "Song Name" --language "Language" [--artist "Artist Name"] [--output "output.json"]
```

Required arguments:
- `--song`: Name of the song
- `--language`: Language of the song

Optional arguments:
- `--artist`: Artist name (helps improve search accuracy)
- `--output`: Custom output file path (default: output.json)

Example:
```bash
python agent.py --song "Sugar" --artist "Maroon 5" --language "English"
```

## Output Format

The tool generates a JSON file with:
```json
{
  "song_info": {
    "title": "Song Title",
    "artist": "Artist Name",
    "language": "Language"
  },
  "lyrics": "[Song lyrics]",
  "vocabulary_categories": [
    {
      "category_name": "Category Name",
      "vocabulary_items": [
        {
          "original_form": "Word as it appears in lyrics",
          "base_form": "Base/dictionary form",
          "pronunciation": "IPA pronunciation",
          "english": "English translation",
          "part_of_speech": "noun/verb/etc",
          "example_sentence": "Example from lyrics",
          "example_translation": "Translation of example"
        }
      ]
    }
  ]
}
```

## Configuration

The tool uses multiple models for different tasks:
- Routing: llama-3.3-70b-versatile
- Tool Use: llama-3.3-70b-versatile
- General: llama-3.3-70b-versatile
- Japanese Enhancement: mixtral-8x7b-32768 (for adding kanji to vocabulary)

Search settings:
- Max 5 search results per query
- 5-second base delay between retries
- Maximum 5 retries for failed searches

Content limits:
- Lyrics are truncated to 5000 characters
- Maximum 5 turns of tool usage

## Language Support

The tool supports multiple languages, with special handling for Japanese:

### Japanese Language Support

For Japanese songs, the tool uses a two-step process:
1. First, Llama models handle the tool calls to search for lyrics and generate initial vocabulary
2. Then, the Mixtral model enhances the vocabulary by adding proper kanji characters

This approach combines Llama's reliable tool use with Mixtral's better handling of Japanese characters.

### Other Languages

For non-Japanese languages, the tool uses Llama models for the entire process, which works well for most Latin-based scripts.

## Error Handling

The tool includes several error handling features:
- Retries for failed API calls
- Exponential backoff for search retries
- Fallback to text output if JSON parsing fails
- Rate limit handling for DuckDuckGo searches

## Required Files

- `agent.py`: Main script
- `prompt.md`: Instructions for vocabulary generation
- `.env`: Environment variables file

## Known Limitations

1. DuckDuckGo Search:
   - Subject to rate limiting
   - May return incomplete results
   - Limited to 5 results per query

2. Groq API:
   - May occasionally fail with tool use errors
   - Requires valid API key
   - Subject to API rate limits

3. Content:
   - Lyrics limited to 5000 characters
   - May not handle all languages equally well
   - Vocabulary categorization depends on model accuracy

## Troubleshooting

1. Rate Limit Errors:
   - Wait a few minutes before retrying
   - Reduce the number of requests
   - Check if DuckDuckGo is accessible

2. Tool Use Errors:
   - Verify Groq API key is valid
   - Check if the models are available
   - Try with a different song/language

3. JSON Parsing Errors:
   - Check output.txt for raw response
   - Verify the song exists
   - Try adding artist name for better results