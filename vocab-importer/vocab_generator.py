import streamlit as st
import json
import os
from datetime import datetime
from typing import Dict, List
import pyperclip
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')

if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

# Initialize Groq client
client = Groq(
    api_key=groq_api_key,
)

def validate_vocab_entry(entry: Dict) -> bool:
    """Validate a single vocabulary entry"""
    try:
        # Check required fields exist
        required_fields = ["kanji", "romaji", "english", "parts"]
        if not all(field in entry for field in required_fields):
            print(f"Missing required fields: {entry}")
            return False
        
        # Validate parts structure
        if not isinstance(entry["parts"], list):
            print(f"Invalid parts structure: {entry}")
            return False
            
        for part in entry["parts"]:
            # Each part must have kanji and romaji
            if not all(field in part for field in ["kanji", "romaji"]):
                print(f"Missing kanji or romaji in part: {part}")
                return False
            # Romaji must be a list of strings
            if not isinstance(part["romaji"], list):
                print(f"Invalid romaji structure: {part}")
                return False
            if not all(isinstance(r, str) for r in part["romaji"]):
                print(f"Invalid romaji structure: {part}")
                return False
            # Kanji must be a string
            if not isinstance(part["kanji"], str):
                print(f"Invalid kanji structure: {part}")
                return False
            
        # # Validate string fields
        # if not all(isinstance(entry[field], str) for field in required_fields):
        #     return False
            
        return True
    except Exception:
        return False

def generate_vocab(prompt: str, count: int = 3, model: str = "mixtral-8x7b-32768") -> List[Dict]:
    """Generate vocabulary using Groq API"""
    system_prompt = f"""You are a Japanese language expert. Generate {count} vocabulary words based on the given input.
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

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
            top_p=0.9
        )
        
        # Parse the response as JSON
        response_data = json.loads(completion.choices[0].message.content)
        
        # Validate response is a list
        if not isinstance(response_data, list):
            st.error("Invalid response format: not a list")
            return []
        
        # Validate each entry
        valid_entries = []
        for entry in response_data:
            if validate_vocab_entry(entry):
                valid_entries.append(entry)
            else:
                st.warning(f"Skipped invalid entry: {json.dumps(entry, ensure_ascii=False)}")
        
        if not valid_entries:
            st.error("No valid vocabulary entries were generated")
            return []
            
        if len(valid_entries) < count:
            st.warning(f"Only {len(valid_entries)} valid entries were generated out of {count} requested")
            
        return valid_entries
        
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON response: {str(e)}")
        return []
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return []

def format_vocab_json(data: List[Dict]) -> str:
    """Format vocabulary JSON to match seed data format"""
    formatted_entries = []
    for entry in data:
        # Format parts array more compactly
        parts_str = []
        for part in entry["parts"]:
            part_str = json.dumps(part, ensure_ascii=False)
            # Remove newlines and extra spaces in parts
            part_str = part_str.replace('\n', '').replace('  ', ' ')
            parts_str.append('      ' + part_str)
        
        # Create the entry string
        entry_str = (
            '  {\n'
            f'    "kanji": {json.dumps(entry["kanji"], ensure_ascii=False)},\n'
            f'    "romaji": {json.dumps(entry["romaji"], ensure_ascii=False)},\n'
            f'    "english": {json.dumps(entry["english"], ensure_ascii=False)},\n'
            '    "parts": [\n' +
            ',\n'.join(parts_str) + '\n' +
            '    ]\n'
            '  }'
        )
        formatted_entries.append(entry_str)
    
    return '[\n' + ',\n'.join(formatted_entries) + '\n]'

def save_to_file(data: List[Dict], category: str):
    """Save generated vocabulary to file, organized by category"""
    try:
        filename = 'generated_vocab.json'
        existing_data = {}
        
        # Load existing data if file exists
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = {}
        
        # Clean and lowercase the category name
        clean_category = category.lower()
        clean_category = "".join(x for x in clean_category if x.isalnum() or x in (' ','-','_')).strip()
        clean_category = clean_category.replace(' ', '_')
        
        # Get existing entries for this category
        existing_entries = existing_data.get(clean_category, [])
        existing_kanji = {entry['kanji'] for entry in existing_entries}
        
        # Add only new entries
        new_entries = existing_entries.copy()
        added_count = 0
        for entry in data:
            if entry['kanji'] not in existing_kanji:
                new_entries.append(entry)
                existing_kanji.add(entry['kanji'])
                added_count += 1
        
        if added_count > 0:
            # Update category with merged entries
            existing_data[clean_category] = new_entries
            
            # Format each category's data
            formatted_output = "{\n"
            for cat, entries in existing_data.items():
                formatted_output += f'  "{cat}": ' + format_vocab_json(entries) + ",\n"
            formatted_output = formatted_output.rstrip(",\n") + "\n}"
            
            # Save formatted data
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatted_output)
                
            # Update session state
            st.session_state.current_file = filename
            
            # Notify about merged entries
            if added_count < len(data):
                st.info(f"Added {added_count} new entries to category '{category}'. {len(data) - added_count} were duplicates.")
            
    except Exception as e:
        st.error(f"Error saving to file: {str(e)}")

def copy_to_clipboard(data: str):
    """Copy data to clipboard"""
    try:
        pyperclip.copy(data)
        st.toast("Copied to clipboard!", icon="✅")
    except Exception as e:
        st.error(f"Error copying to clipboard: {str(e)}")

def get_available_models() -> List[str]:
    """Fetch available models from Groq API"""
    try:
        if 'models' not in st.session_state:
            models = client.models.list()
            available_models = []
            for model in models.data:
                if "whisper" not in model.id.lower() and "vision" not in model.id.lower():
                    available_models.append(model.id)
            
            available_models.sort(key=lambda x: 0 if x == "mixtral-8x7b-32768" else 1)
            st.session_state.models = available_models
        return st.session_state.models
    except Exception as e:
        st.error(f"Error fetching models: {str(e)}")
        return []

def copy_callback():
    """Callback for copy button that uses session state"""
    if 'current_json' in st.session_state:
        copy_to_clipboard(st.session_state.current_json)

def main():
    st.title("Japanese Vocabulary Generator")
    
    # Custom CSS
    st.markdown("""
        <style>
        /* Increase width of the selectbox */
        .stSelectbox div[data-baseweb="select"] {
            min-width: 300px;
        }
        
        /* Add pointer cursor on hover */
        .stSelectbox div[data-baseweb="select"]:hover {
            cursor: pointer;
        }
        
        /* Ensure the cursor stays as pointer when hovering over the inner elements */
        .stSelectbox [role="listbox"]:hover,
        .stSelectbox [role="option"]:hover {
            cursor: pointer;
        }

        /* Style the Generate button hover effect */
        div[data-testid="stButton"] > button:first-child:hover {
            box-shadow: 0 0 10px #21c45d;
            border-color: #21c45d;
            color: #21c45d;
            transition: all 0.3s ease;
        }

        /* Style only the Copy JSON button */
        div[data-testid="stButton"]:not(:first-child) button {
            padding: 0.75rem 1rem;
            height: 2rem;
            line-height: 1.5;
        }

        /* Speed up transitions */
        .element-container, .stMarkdown, .stButton, .stText {
            transition: opacity 0.1s !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Get available models once and store in session state
    models = get_available_models()
    
    if not models:
        st.error("Could not fetch available models from Groq API")
        return
    
    # Initialize selected model in session state if not exists
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = models[0] if models else None
    
    # Input area with adjusted column ratios
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        prompt = st.text_input(
            "Enter category, word, or phrase",
            placeholder="e.g., food, emotions, daily activities"
        )
    with col2:
        count = st.number_input(
            "Count",
            min_value=1,
            max_value=100,
            value=3
        )
    with col3:
        st.session_state.selected_model = st.selectbox(
            "Model",
            options=models,
            help="Select a model to use for generation",
            key="model_selector"
        )
    
    if st.button("Generate"):
        if prompt:
            with st.spinner("Generating vocabulary..."):
                vocab_data = generate_vocab(
                    prompt=prompt, 
                    count=count,
                    model=st.session_state.selected_model
                )
                
                if vocab_data:
                    # Store results in session state
                    st.session_state.vocab_data = vocab_data
                    st.session_state.formatted_json = format_vocab_json(vocab_data)
                    
                    # Save to categorized file
                    save_to_file(vocab_data, prompt)

    # Display results if they exist in session state
    if 'vocab_data' in st.session_state:
        # Display only first 5 entries
        display_data = st.session_state.vocab_data[:5]
        
        # Info and copy button in same row
        col1, col2 = st.columns([5, 1])
        with col1:
            if len(st.session_state.vocab_data) > 5:
                filename = st.session_state.current_file.split('/')[-1]
                st.info(f"Showing first 5 of {len(st.session_state.vocab_data)} entries. Full results saved to {filename}")
        with col2:
            if st.button("Copy JSON", key='copy_button'):
                copy_to_clipboard(st.session_state.formatted_json)
        
        # Display results with custom formatting
        st.code(format_vocab_json(display_data), language="json")

if __name__ == "__main__":
    main() 