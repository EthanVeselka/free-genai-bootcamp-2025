import os
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

# Default models
DEFAULT_CHAT_MODEL = "mixtral-8x7b-32768"  # For chat/text generation
DEFAULT_EMBEDDING_MODEL = "mixtral-8x7b-32768"  # For embeddings
DEFAULT_WHISPER_MODEL = "whisper-large-v3"  # For audio transcription

# Export main classes
from .audio_generator import AudioGenerator
from .question_generator import QuestionGenerator
from .vector_store import QuestionVectorStore
from .structured_data import TranscriptStructurer
from .chat import GroqChat
