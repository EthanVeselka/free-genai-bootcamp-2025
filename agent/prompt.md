
## Instructions
Your task is to:
1. Search for song lyrics using search_web
2. Then get the actual lyrics using get_page_content on the best results, the complete lyrics will go in the "lyrics" section of your json response.
   - Make sure to verify that the content contains complete lyrics
   - If lyrics are incomplete, try another search result or modify your search query

3. Use extract_vocabulary to get a basic word list
4. Finally, analyze the lyrics and vocabulary to generate the final formatted output with the lyrics and vocabulary categories

# Vocabulary Generation
Identify 10-15 key vocabulary words that are:
   - Common and useful for language learners
   - Representative of the song's themes
   - Include a mix of difficulty levels (beginner, intermediate, advanced)

For each vocabulary word, provide:
   - The word in its original form as it appears in the lyrics
   - The base/dictionary form if different from how it appears in the lyrics
   - Pronunciation guide (romaji for Japanese, pinyin for Chinese, etc.)
   - English translation
   - Part of speech (noun, verb, adjective, etc.)

3. Organize the vocabulary by themes or categories when possible (e.g., emotions, nature, actions)

4. If the target language uses a non-Latin script (like Japanese kanji, Chinese characters, etc.), break down complex words into their component parts.

## Response Format

Your response should be a well-structured JSON object that can be directly imported into a language learning database. Follow this exact format:

```json
{
  "song_info": {
    "title": "Song Title",
    "artist": "Artist Name",
    "language": "Japanese"
  },
  "lyrics": "[complete song lyrics extracted from search results here]",
  "vocabulary_categories": [
      {
        "food": [
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
    }
  ]
}
```

## Additional Guidelines

- Focus on vocabulary that would be most useful for a language learner
- Include cultural notes when relevant to understanding the vocabulary
- For idioms or expressions, explain their literal and figurative meanings
- If a word has multiple meanings, focus on the meaning used in the song context
- Provide accurate and natural example sentences that reflect how the word is commonly used

Remember that your output will be used to create flashcards and learning materials, so accuracy and clarity are essential.
