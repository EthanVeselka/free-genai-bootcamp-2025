# Create GroqChat
# groq_chat.py
import os
import sys
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend import client, DEFAULT_CHAT_MODEL


class GroqChat:
    def __init__(self, model_id: str = DEFAULT_CHAT_MODEL):
        """Initialize Groq chat client"""
        self.client = client
        self.model_id = model_id

    def generate_response(self, message: str, inference_config: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate a response using Groq"""
        if inference_config is None:
            inference_config = {
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.9
            }

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": "You are a Japanese language expert."},
                    {"role": "user", "content": message}
                ],
                **inference_config
            )
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return None


if __name__ == "__main__":
    chat = GroqChat()
    while True:
        user_input = input("You: ")
        if user_input.lower() == '/exit':
            break
        response = chat.generate_response(user_input)
        print("Bot:", response)
