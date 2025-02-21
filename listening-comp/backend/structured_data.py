from typing import Optional, Dict, List
import boto3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend import client, DEFAULT_CHAT_MODEL

class TranscriptStructurer:
    def __init__(self, model_id: str = DEFAULT_CHAT_MODEL):
        """Initialize Groq client"""
        self.client = client
        self.model_id = model_id
        self.prompts = {
            1: """Extract questions from section 問題1 of this JLPT transcript where the answer can be determined solely from the conversation without needing visual aids.
            
            ONLY include questions that meet these criteria:
            - The answer can be determined purely from the spoken dialogue
            - No spatial/visual information is needed (like locations, layouts, or physical appearances)
            - No physical objects or visual choices need to be compared
            
            For example, INCLUDE questions about:
            - Times and dates
            - Numbers and quantities
            - Spoken choices or decisions
            - Clear verbal directions
            
            DO NOT include questions about:
            - Physical locations that need a map or diagram
            - Visual choices between objects
            - Spatial arrangements or layouts
            - Physical appearances of people or things

            Format each question exactly like this:

            <question>
            Introduction:
            [the situation setup in japanese]
            
            Conversation:
            [the dialogue in japanese]
            
            Question:
            [the question being asked in japanese]

            Options:
            1. [first option in japanese]
            2. [second option in japanese]
            3. [third option in japanese]
            4. [fourth option in japanese]
            </question>

            Rules:
            - Only extract questions from the 問題1 section
            - Only include questions where answers can be determined from dialogue alone
            - Ignore any practice examples (marked with 例)
            - Do not translate any Japanese text
            - Do not include any section descriptions or other text
            - Output questions one after another with no extra text between them
            """,
            
            2: """Extract questions from section 問題2 of this JLPT transcript where the answer can be determined solely from the conversation without needing visual aids.
            
            ONLY include questions that meet these criteria:
            - The answer can be determined purely from the spoken dialogue
            - No spatial/visual information is needed (like locations, layouts, or physical appearances)
            - No physical objects or visual choices need to be compared
            
            For example, INCLUDE questions about:
            - Times and dates
            - Numbers and quantities
            - Spoken choices or decisions
            - Clear verbal directions
            
            DO NOT include questions about:
            - Physical locations that need a map or diagram
            - Visual choices between objects
            - Spatial arrangements or layouts
            - Physical appearances of people or things

            Format each question exactly like this:

            <question>
            Introduction:
            [the situation setup in japanese]
            
            Conversation:
            [the dialogue in japanese]
            
            Question:
            [the question being asked in japanese]
            </question>

            Rules:
            - Only extract questions from the 問題2 section
            - Only include questions where answers can be determined from dialogue alone
            - Ignore any practice examples (marked with 例)
            - Do not translate any Japanese text
            - Do not include any section descriptions or other text
            - Output questions one after another with no extra text between them
            """,
            
            3: """Extract all questions from section 問題3 of this JLPT transcript.
            Format each question exactly like this:

            <question>
            Situation:
            [the situation in japanese where a phrase is needed]
            
            Question:
            何と言いますか
            </question>

            Rules:
            - Only extract questions from the 問題3 section
            - Ignore any practice examples (marked with 例)
            - Do not translate any Japanese text
            - Do not include any section descriptions or other text
            - Output questions one after another with no extra text between them
            """
        }

    def _invoke_groq(self, prompt: str, transcript: str) -> Optional[str]:
        """Make a single call to Groq with the given prompt"""
        full_prompt = f"{prompt}\n\nHere's the transcript:\n{transcript}"
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": "You are a JLPT transcript analysis expert."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0,
                max_tokens=2000
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Error invoking Groq: {str(e)}")
            return None

    def structure_transcript(self, transcript: str) -> Dict[int, str]:
        """Structure the transcript into three sections using separate prompts"""
        results = {}
        for section_num in range(2, 4):
            result = self._invoke_groq(self.prompts[section_num], transcript)
            if result:
                results[section_num] = result
        return results

    def save_questions(self, structured_sections: Dict[int, str], base_filename: str) -> bool:
        """Save each section to a separate file"""
        try:
            # Create questions directory if it doesn't exist
            os.makedirs(os.path.dirname(base_filename), exist_ok=True)
            
            # Save each section
            for section_num, content in structured_sections.items():
                filename = f"{os.path.splitext(base_filename)[0]}_section{section_num}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
            return True
        except Exception as e:
            print(f"Error saving questions: {str(e)}")
            return False

    def load_transcript(self, filename: str) -> Optional[str]:
        """Load transcript from a file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading transcript: {str(e)}")
            return None

def get_processed_video_ids():
    """Get list of video IDs that have already been processed"""
    questions_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "backend/data/questions"
    )
    
    processed_ids = set()
    if os.path.exists(questions_dir):
        for filename in os.listdir(questions_dir):
            if filename.endswith(('_section2.txt', '_section3.txt')):
                video_id = filename.split('_section')[0]
                processed_ids.add(video_id)
    
    return processed_ids

def process_transcripts():
    """Process only new transcripts into structured question files"""
    transcripts_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "backend/data/transcripts"
    )
    
    # Get list of already processed videos
    processed_ids = get_processed_video_ids()
    
    # Process only new transcripts
    for filename in os.listdir(transcripts_dir):
        if not filename.endswith('.txt'):
            continue
            
        video_id = filename.split('.')[0]
        if video_id in processed_ids:
            print(f"Skipping {filename} - already processed")
            continue
            
        print(f"\nProcessing new transcript: {filename}")
        transcript_path = os.path.join(transcripts_dir, filename)
        
        try:
            structurer = TranscriptStructurer()
            
            # Load and structure transcript
            transcript = structurer.load_transcript(transcript_path)
            if transcript:
                # Structure into sections
                structured_sections = structurer.structure_transcript(transcript)
                
                # Save structured questions
                output_base = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    f"backend/data/questions/{video_id}"
                )
                if structurer.save_questions(structured_sections, output_base):
                    print(f"Successfully processed {filename}")
                else:
                    print(f"Failed to save questions for {filename}")
            else:
                print(f"Failed to load transcript {filename}")
        except Exception as e:
            print(f"Error processing transcript {filename}: {str(e)}")

if __name__ == "__main__":
    process_transcripts()