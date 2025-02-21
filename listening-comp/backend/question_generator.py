import boto3
import json
import time
from typing import Dict, List, Optional
from backend.vector_store import QuestionVectorStore
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend import client, DEFAULT_CHAT_MODEL

class QuestionGenerator:
    def __init__(self):
        """Initialize Groq client and vector store"""
        self.client = client
        self.vector_store = QuestionVectorStore()
        self.model_id = DEFAULT_CHAT_MODEL
        self.retry_delay = 5  # seconds between retries
        self.max_retries = 3

    def _invoke_groq(self, prompt: str, retries=0) -> Optional[str]:
        """Invoke Groq with retry logic for rate limits"""
        try:
            print("\n=== Sending prompt to Groq ===")
            print(f"Prompt length: {len(prompt)}")
            print("First 100 chars:", prompt[:100])
            
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": "You are a Japanese language expert specializing in JLPT listening questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                top_p=0.9
            )
            
            response = completion.choices[0].message.content
            print("\n=== Received response from Groq ===")
            print(f"Response length: {len(response) if response else 0}")
            
            if not response or len(response.strip()) < 10:  # Arbitrary minimum length
                print("Response too short or empty, retrying...")
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
                    return self._invoke_groq(prompt, retries + 1)
                else:
                    print("Max retries reached, returning None")
                    return None
                    
            return response
            
        except Exception as e:
            error_msg = str(e).lower()
            print(f"\n=== Error from Groq ===\n{error_msg}")
            
            if "rate limit" in error_msg and retries < self.max_retries:
                # Extract wait time if available
                wait_time = self.retry_delay
                try:
                    if "try again in" in error_msg:
                        wait_str = error_msg.split("try again in")[1].split("s")[0]
                        wait_time = float(wait_str.strip()) + 1
                except:
                    pass
                
                print(f"Rate limit hit, waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                return self._invoke_groq(prompt, retries + 1)
            else:
                print(f"Error invoking Groq: {str(e)}")
                return None

    def generate_similar_question(self, section_num: int, topic: str) -> Dict:
        """Generate a new question similar to existing ones on a given topic"""
        # First try to get similar questions
        similar_questions = self.vector_store.search_similar_questions(section_num, topic, n_results=1)
        
        # If search fails or no results, generate without context
        if not similar_questions:
            print("Generating question without examples...")
            return self._generate_new_question(section_num, topic)
        
        # Create context from similar questions
        context = self._create_context(similar_questions, section_num)
        return self._generate_new_question(section_num, topic, context)

    def _create_context(self, similar_questions: List[Dict], section_num: int) -> str:
        """Create context string from similar questions"""
        context = "Here are some example JLPT listening questions:\n\n"
        for idx, q in enumerate(similar_questions, 1):
            if section_num == 2:
                context += f"Example {idx}:\n"
                context += f"Introduction: {q.get('Introduction', '')}\n"
                context += f"Conversation: {q.get('Conversation', '')}\n"
                context += f"Question: {q.get('Question', '')}\n"
                if 'Options' in q:
                    context += "Options:\n"
                    for i, opt in enumerate(q['Options'], 1):
                        context += f"{opt}\n"
            else:  # section 3
                context += f"Example {idx}:\n"
                context += f"Situation: {q.get('Situation', '')}\n"
                context += f"Question: {q.get('Question', '')}\n"
                if 'Options' in q:
                    context += "Options:\n"
                    for i, opt in enumerate(q['Options'], 1):
                        context += f"{opt}\n"
            context += "\n"
        return context

    # def _validate_question(self, question: Dict, section_num: int) -> bool:
    #     """Validate question has required fields"""
    #     required = ['Question', 'Options']
    #     if section_num == 2:
    #         required.extend(['Introduction', 'Conversation'])
    #     else:
    #         required.append('Situation')
    #     return all(field in question for field in required)

    def _generate_new_question(self, section_num: int, topic: str, context: str = "") -> Dict:
        """Generate a new question with or without examples"""
        print(f"\n=== Generating new question ===")
        print(f"Section: {section_num}, Topic: {topic}")
        print(f"Has context: {bool(context)}")
        
        if not context:
            # Create basic prompt without examples
            components = "- Introduction\n- Conversation" if section_num == 2 else "- Situation"
            prompt = f"""Create a new JLPT listening question about {topic}. The entire question MUST be in Japanese only.

            Important rules:
            1. ALL text should be in Japanese only - do not include any English.
            2. Make the question challenging but fair for JLPT level
            3. Ensure all options are plausible with one correct answer, do not label the correct answer.
            4. Do not include translations or explanations

            Format the question exactly like this:
            {"Introduction:" if section_num == 2 else "Situation:"}
            [text in Japanese]

            {"Conversation:" if section_num == 2 else ""}
            [dialogue in Japanese]

            Question:
            [question in Japanese]

            Options:
            A) [option in Japanese]
            B) [option in Japanese]
            C) [option in Japanese]
            D) [option in Japanese]
            """
        else:
            # Use provided context
            prompt = f"""Based on the following example JLPT listening question, create a NEW question about {topic}.

            {context}

            Important rules:
            1. ALL text should be in Japanese only - do not include any English.
            2. Make the question challenging but fair for JLPT level
            3. Ensure all options are plausible with one correct answer, do not label the correct answer.
            4. Do not include translations or explanations
            5. Follow the exact format given below

            Format the question exactly like this:
            {"Introduction:" if section_num == 2 else "Situation:"}
            [text in Japanese]

            {"Conversation:" if section_num == 2 else ""}
            [dialogue in Japanese]

            Question:
            [question in Japanese]

            Options:
            A) [option in Japanese]
            B) [option in Japanese]
            C) [option in Japanese]
            D) [option in Japanese]
            """

        print("Context: Examples provided")
        print("---------------------------")
        print(context)
        print("---------------------------")
        # Generate and parse question
        response = self._invoke_groq(prompt)
        if not response:
            print("No response from Groq")
            return None

        # Parse the generated question
        try:
            print("\n=== Parsing response ===")
            lines = response.strip().split('\n')
            print(f"Number of lines: {len(lines)}")
            question = {}
            current_key = None
            options = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('Introduction:'):
                    current_key = 'Introduction'
                    question[current_key] = line.replace('Introduction:', '').strip()
                elif line.startswith('Conversation:'):
                    current_key = 'Conversation'
                    question[current_key] = line.replace('Conversation:', '').strip()
                elif line.startswith('Situation:'):
                    current_key = 'Situation'
                    question[current_key] = line.replace('Situation:', '').strip()
                elif line.startswith('Question:'):
                    current_key = 'Question'
                    question[current_key] = line.replace('Question:', '').strip()
                elif line.startswith('Options:'):
                    current_key = 'Options'
                    options = []
                elif current_key == 'Options':
                    # Only accept options that start with A), B), C), D)
                    if line.startswith(('A)', 'B)', 'C)', 'D)')):
                        option_text = line.split(')', 1)[1].strip()
                        if option_text:  # Only add if there's text after the letter
                            options.append(line)  # Keep the full "A) text" format
                            
                elif current_key:
                    # Append to existing key
                    question[current_key] = question.get(current_key, '') + ' ' + line
            
            if options:
                question['Options'] = options
            
            print("\n=== Parsed question ===")
            print(json.dumps(question, indent=2, ensure_ascii=False))
            
            # Validate
            # if not question or not all(k in question for k in ['Question', 'Options']):
            #     print("Missing required fields")
            #     return None
                
            return question
            
        except Exception as e:
            print(f"\n=== Error parsing question ===\n{str(e)}")
            return None

    def get_feedback(self, question: Dict, selected_answer: int) -> Dict:
        """Generate feedback for the selected answer"""
        if not question or 'Options' not in question:
            return None

        # Create prompt for generating feedback
        prompt = f"""Given this JLPT listening question and the selected answer, provide feedback explaining if it's correct 
        and why. Keep the explanation clear and concise.
        
        """
        if 'Introduction' in question:
            prompt += f"Introduction: {question['Introduction']}\n"
            prompt += f"Conversation: {question['Conversation']}\n"
        else:
            prompt += f"Situation: {question['Situation']}\n"
        
        prompt += f"Question: {question['Question']}\n"
        prompt += "Options:\n"
        for i, opt in enumerate(question['Options'], 1):
            prompt += f"{opt}\n"
        
        prompt += f"\nSelected Answer: {selected_answer}\n"
        prompt += "\nProvide feedback in JSON format with these fields:\n"
        prompt += "- correct: true/false\n"
        prompt += "- explanation: brief explanation of why the answer is correct/incorrect\n"
        prompt += "- correct_answer: the number of the correct option (1-4)\n"

        # Get feedback
        response = self._invoke_groq(prompt)
        if not response:
            return None

        try:
            # Parse the JSON response
            feedback = json.loads(response.strip())
            return feedback
        except:
            # If JSON parsing fails, return a basic response with a default correct answer
            return {
                "correct": False,
                "explanation": "Unable to generate detailed feedback. Please try again.",
                "correct_answer": 1  # Default to first option
            }
