import os
import json
import tempfile
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple
from google.cloud import texttospeech
from google.oauth2 import service_account
from backend import client, DEFAULT_CHAT_MODEL

class AudioGenerator:
    def __init__(self):
        """Initialize the TTS client and setup voices"""
        # Get credentials from environment variable
        credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not credentials_json:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not found in environment")
            
        try:
            # Create credentials object from the JSON file
            credentials = service_account.Credentials.from_service_account_file(
                credentials_json
            )
            
            # Initialize client with explicit credentials
            self.client = texttospeech.TextToSpeechClient(credentials=credentials)
        except Exception as e:
            raise Exception(f"Failed to initialize Google Cloud client: {str(e)}")
        
        # Define Japanese neural voices by gender
        self.voices = {
            'male': ['ja-JP-Neural2-C', 'ja-JP-Neural2-D'],  # Male voices
            'female': ['ja-JP-Neural2-A', 'ja-JP-Neural2-B'],  # Female voices
            'announcer': 'ja-JP-Neural2-D'  # Default announcer voice
        }
        
        # Create audio output directory using absolute path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.audio_dir = os.path.abspath(os.path.join(
            current_dir,
            "..",
            "frontend",
            "static",
            "audio"
        ))
        os.makedirs(self.audio_dir, exist_ok=True)

    def validate_conversation_parts(self, parts: List[Tuple[str, str, str]]) -> bool:
        """
        Validate that the conversation parts are properly formatted.
        Returns True if valid, False otherwise.
        """
        if not parts:
            print("Error: No conversation parts generated")
            return False
            
        # Check that we have an announcer for intro
        if not parts[0][0].lower() == 'announcer':
            print("Error: First speaker must be Announcer")
            return False
            
        # Check that each part has valid content
        for i, (speaker, text, gender) in enumerate(parts):
            # Check speaker
            if not speaker or not isinstance(speaker, str):
                print(f"Error: Invalid speaker in part {i+1}")
                return False
                
            # Check text
            if not text or not isinstance(text, str):
                print(f"Error: Invalid text in part {i+1}")
                return False
                
            # Check gender
            if gender not in ['male', 'female']:
                print(f"Error: Invalid gender in part {i+1}: {gender}")
                return False
                
            # Check text contains Japanese characters
            if not any('\u4e00' <= c <= '\u9fff' or '\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text):
                print(f"Error: Text does not contain Japanese characters in part {i+1}")
                return False
        
        return True

    def parse_conversation(self, question: Dict) -> List[Tuple[str, str, str]]:
        """
        Convert question into a format for audio generation.
        Returns a list of (speaker, text, gender) tuples.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Ask Nova to parse the conversation and assign speakers and genders
                prompt = f"""
                You are a JLPT listening test audio script generator. Format the following question for audio generation.

                Rules:
                1. Introduction and Question parts:
                   - Must start with 'Speaker: Announcer (Gender: male)'
                   - Keep as separate parts

                2. Conversation parts:
                   - Name speakers based on their role (Student, Teacher, etc.)
                   - Must specify gender EXACTLY as either 'Gender: male' or 'Gender: female'
                   - Use consistent names for the same speaker
                   - Split long speeches at natural pauses

                Format each part EXACTLY like this, with no variations:
                Speaker: [name] (Gender: male)
                Text: [Japanese text]
                ---

                Example format:
                Speaker: Announcer (Gender: male)
                Text: 次の会話を聞いて、質問に答えてください。
                ---
                Speaker: Student (Gender: female)
                Text: すみません、この電車は新宿駅に止まりますか。
                ---

                Question to format:
                {json.dumps(question, ensure_ascii=False, indent=2)}

                Output ONLY the formatted parts in order: introduction, conversation, question.
                Make sure to specify gender EXACTLY as shown in the example.
                """
                
                response = client.chat.completions.create(
                    model=DEFAULT_CHAT_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a Japanese audio script formatter."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )
                
                response_text = response.choices[0].message.content
                
                # Parse the response into speaker parts
                parts = []
                current_speaker = None
                current_gender = None
                current_text = None
                
                # Track speakers to maintain consistent gender
                speaker_genders = {}
                
                for line in response_text.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                        
                    if line.startswith('Speaker:'):
                        # Save previous speaker's part if exists
                        if current_speaker and current_text:
                            parts.append((current_speaker, current_text, current_gender))
                        
                        # Parse new speaker and gender
                        try:
                            speaker_part = line.split('Speaker:')[1].strip()
                            current_speaker = speaker_part.split('(')[0].strip()
                            gender_part = speaker_part.split('Gender:')[1].split(')')[0].strip().lower()
                            
                            # Normalize gender
                            if '男' in gender_part or 'male' in gender_part:
                                current_gender = 'male'
                            elif '女' in gender_part or 'female' in gender_part:
                                current_gender = 'female'
                            else:
                                raise ValueError(f"Invalid gender format: {gender_part}")
                            
                            # Check for gender consistency
                            if current_speaker in speaker_genders:
                                if current_gender != speaker_genders[current_speaker]:
                                    print(f"Warning: Gender mismatch for {current_speaker}. Using previously assigned gender {speaker_genders[current_speaker]}")
                                current_gender = speaker_genders[current_speaker]
                            else:
                                speaker_genders[current_speaker] = current_gender
                        except Exception as e:
                            print(f"Error parsing speaker/gender: {line}")
                            raise e
                            
                    elif line.startswith('Text:'):
                        current_text = line.split('Text:')[1].strip()
                        
                    elif line == '---' and current_speaker and current_text:
                        parts.append((current_speaker, current_text, current_gender))
                        current_speaker = None
                        current_gender = None
                        current_text = None
                
                # Add final part if exists
                if current_speaker and current_text:
                    parts.append((current_speaker, current_text, current_gender))
                
                # Validate the parsed parts
                if self.validate_conversation_parts(parts):
                    return parts
                    
                print(f"Attempt {attempt + 1}: Invalid conversation format, retrying...")
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception("Failed to parse conversation after multiple attempts")
        
        raise Exception("Failed to generate valid conversation format")

    def get_voice_for_gender(self, gender: str) -> str:
        """Get an appropriate voice for the given gender"""
        if gender == 'male':
            return self.voices['male'][0]  # First male voice
        else:
            return self.voices['female'][0]  # First female voice

    def generate_audio_part(self, text: str, voice_name: str) -> str:
        """Generate audio for a single part using Google Cloud TTS"""
        try:
            # Set the text input to be synthesized
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Build the voice request
            voice = texttospeech.VoiceSelectionParams(
                language_code="ja-JP",
                name=voice_name
            )

            # Select the type of audio file
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,  # Normal speed
                pitch=0.0  # Normal pitch
            )

            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(response.audio_content)
                return temp_file.name
                
        except Exception as e:
            print(f"Error generating audio part: {str(e)}")
            return None

    def generate_silence(self, duration_ms: int) -> str:
        """Generate a silent audio file of specified duration"""
        output_file = os.path.join(self.audio_dir, f'silence_{duration_ms}ms.mp3')
        if not os.path.exists(output_file):
            subprocess.run([
                'ffmpeg', '-f', 'lavfi', '-i',
                f'anullsrc=r=24000:cl=mono:d={duration_ms/1000}',
                '-c:a', 'libmp3lame', '-b:a', '48k',
                output_file
            ])
        return output_file

    def combine_audio_files(self, audio_files: List[str], output_file: str):
        """Combine multiple audio files using ffmpeg"""
        file_list = None
        try:
            # Create file list for ffmpeg
            with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as f:
                for audio_file in audio_files:
                    if audio_file and os.path.exists(audio_file):
                        f.write(f"file '{audio_file}'\n")
                file_list = f.name
            
            # First concatenate the audio files
            temp_output = os.path.join(self.audio_dir, "temp_concat.mp3")
            subprocess.run([
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', file_list, 
                '-filter_complex', 'apad=pad_dur=0.5',  # Add 0.5s silence between files
                '-c:a', 'libmp3lame', '-b:a', '64k',
                temp_output
            ], check=True)
            
            # Move temp file to final output
            os.rename(temp_output, output_file)
            return True
            
        except Exception as e:
            print(f"Error combining audio files: {str(e)}")
            if os.path.exists(output_file):
                os.unlink(output_file)
            return False
        finally:
            # Clean up temporary files
            if file_list and os.path.exists(file_list):
                os.unlink(file_list)
            for audio_file in audio_files:
                if audio_file and os.path.exists(audio_file):
                    try:
                        os.unlink(audio_file)
                    except Exception as e:
                        print(f"Error cleaning up {audio_file}: {str(e)}")

    def _concatenate_audio_files(self, audio_files: List[str], output_file: str) -> bool:
        """Concatenate multiple audio files with silence between them"""
        try:
            # Create file list for ffmpeg
            with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as f:
                for audio_file in audio_files:
                    f.write(f"file '{audio_file}'\n")
                    # Instead of silence file, add small pause using ffmpeg
                    f.write(f"file 'anullsrc=r=44100:cl=stereo:d=2'\n")  # 2 second pause
                file_list = f.name

            # Run ffmpeg to concatenate files
            subprocess.run([
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', file_list, '-c:a', 'libmp3lame', '-b:a', '64k',
                output_file
            ], check=True)

            os.unlink(file_list)
            return True
            
        except Exception as e:
            print(f"Error concatenating audio files: {str(e)}")
            return False

    def generate_audio(self, question: Dict) -> str:
        """Generate audio for the entire question"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.audio_dir, f"question_{timestamp}.mp3")
        
        try:
            # Parse conversation into parts
            parts = self.parse_conversation(question)
            
            # Generate audio for each part
            audio_parts = []
            current_section = None
            
            for speaker, text, gender in parts:
                # Get appropriate voice for this speaker
                voice = self.get_voice_for_gender(gender)
                print(f"Using voice {voice} for {speaker} ({gender})")
                
                # Generate audio for this part
                audio_file = self.generate_audio_part(text, voice)
                if not audio_file:
                    raise Exception("Failed to generate audio part")
                audio_parts.append(audio_file)
            
            # Combine all parts into final audio
            if not self.combine_audio_files(audio_parts, output_file):
                raise Exception("Failed to combine audio files")
            
            return output_file
            
        except Exception as e:
            # Clean up the output file if it exists
            if os.path.exists(output_file):
                os.unlink(output_file)
            raise Exception(f"Audio generation failed: {str(e)}")
