import chromadb
from chromadb.utils import embedding_functions
import json
import os
import sys
from typing import Dict, List, Optional
from sentence_transformers import SentenceTransformer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class HuggingFaceEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self):
        self.model = SentenceTransformer('intfloat/multilingual-e5-base')

    def __call__(self, texts: List[str]) -> List[List[float]]:
        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            return [[0.0] * 768] * len(texts)  # E5 uses 768-dimensional vectors

class QuestionVectorStore:
    def __init__(self, persist_directory: str = "backend/data/vectorstore"):
        """Initialize the vector store for JLPT listening questions"""
        # Use absolute path to ensure consistency
        self.persist_directory = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "backend/data/vectorstore"
        )
        
        # Use HuggingFace embedding model
        self.embedding_fn = HuggingFaceEmbeddingFunction()
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Use Groq embedding model
        # self.embedding_fn = GroqEmbeddingFunction()
        
        # Create or get collections for each section type
        self.collections = {
            "section2": self.client.get_or_create_collection(
                name="section2_questions",
                embedding_function=self.embedding_fn,
                metadata={"description": "JLPT listening comprehension questions - Section 2"}
            ),
            "section3": self.client.get_or_create_collection(
                name="section3_questions",
                embedding_function=self.embedding_fn,
                metadata={"description": "JLPT phrase matching questions - Section 3"}
            )
        }

    def add_questions(self, section_num: int, questions: List[Dict], video_id: str):
        """Add questions to the vector store"""
        if section_num not in [2, 3]:
            raise ValueError("Only sections 2 and 3 are currently supported")
        
        # Get existing IDs to avoid duplicates
        collection = self.collections[f"section{section_num}"]
        existing = set(collection.get()['ids'])
        
        for idx, question in enumerate(questions):
            try:
                # Create a unique ID for each question
                question_id = f"{video_id}_{section_num}_{idx}"
                
                # Skip if already indexed
                if question_id in existing:
                    print(f"Question {question_id} already indexed, skipping...")
                    continue
                
                # Create searchable document based on question type
                if section_num == 2:
                    if 'Introduction' not in question or 'Conversation' not in question:
                        print(f"Skipping malformed section 2 question: {question}")
                        continue
                    document = f"""
                    Introduction: {question.get('Introduction', '')}
                    Conversation: {question.get('Conversation', '')}
                    Question: {question.get('Question', '')}
                    """
                else:  # section 3
                    if 'Situation' not in question:
                        print(f"Skipping malformed section 3 question: {question}")
                        continue
                    document = f"""
                    Situation: {question.get('Situation', '')}
                    Question: {question.get('Question', '')}
                    """
                
                # Add to collection
                collection.add(
                    ids=[question_id],
                    documents=[document],
                    metadatas=[{
                        'full_structure': json.dumps(question, ensure_ascii=False),
                        'source_file': video_id,
                        'section': section_num
                    }]
                )
                print(f"Added question {question_id} from {video_id}")
                
            except Exception as e:
                print(f"Error adding question {idx} from {video_id}: {str(e)}")
                continue

    def search_similar_questions(
        self, 
        section_num: int, 
        query: str, 
        n_results: int = 5
    ) -> List[Dict]:
        """Search for similar questions in the specified section"""
        print(f"Searching section {section_num} for: {query}")  # Debug
        collection_name = f"section{section_num}"
        if collection_name not in self.collections:
            print(f"Collection {collection_name} not found")  # Debug
            return []
        
        try:
            results = self.collections[collection_name].query(
                query_texts=[query],
                n_results=n_results
            )
            print(f"Search results: {results['ids'][0][0]}")  # Debug
            
            # Convert results to more usable format
            questions = []
            if results['metadatas'][0]:  # Check if we have any results
                for idx, metadata in enumerate(results['metadatas'][0]):
                    question_data = json.loads(metadata['full_structure'])
                    question_data['similarity_score'] = results['distances'][0][idx]
                    questions.append(question_data)
            
            return questions
            
        except Exception as e:
            print(f"Error searching questions: {str(e)}")  # Debug
            return []

    def get_question_by_id(self, section_num: int, question_id: str) -> Optional[Dict]:
        """Retrieve a specific question by its ID"""
        if section_num not in [2, 3]:
            raise ValueError("Only sections 2 and 3 are currently supported")
            
        collection = self.collections[f"section{section_num}"]
        
        result = collection.get(
            ids=[question_id],
            include=['metadatas']
        )
        
        if result['metadatas']:
            return json.loads(result['metadatas'][0]['full_structure'])
        return None

    def parse_questions_from_file(self, filename: str) -> List[Dict]:
        """Parse questions from a structured text file"""
        questions = []
        current_question = {}
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if line.startswith('<question>'):
                    current_question = {}
                elif line.startswith('Introduction:'):
                    i += 1
                    if i < len(lines):
                        current_question['Introduction'] = lines[i].strip()
                elif line.startswith('Conversation:'):
                    i += 1
                    if i < len(lines):
                        current_question['Conversation'] = lines[i].strip()
                elif line.startswith('Situation:'):
                    i += 1
                    if i < len(lines):
                        current_question['Situation'] = lines[i].strip()
                elif line.startswith('Question:'):
                    i += 1
                    if i < len(lines):
                        current_question['Question'] = lines[i].strip()
                elif line.startswith('Options:'):
                    options = []
                    for _ in range(4):
                        i += 1
                        if i < len(lines):
                            option = lines[i].strip()
                            if option.startswith('A)') or option.startswith('B)') or option.startswith('C)') or option.startswith('D)'):
                                options.append(option[2:].strip())
                    current_question['Options'] = options
                elif line.startswith('</question>'):
                    if current_question:
                        questions.append(current_question)
                        current_question = {}
                i += 1
            return questions
        except Exception as e:
            print(f"Error parsing questions from {filename}: {str(e)}")
            return []

    def index_questions_file(self, filename: str, section_num: int):
        """Index all questions from a file into the vector store"""
        # Extract video ID from filename
        video_id = os.path.basename(filename).split('_section')[0]
        
        # Parse questions from file
        questions = self.parse_questions_from_file(filename)
        
        # Add to vector store
        if questions:
            self.add_questions(section_num, questions, video_id)
            print(f"Indexed {len(questions)} questions from {filename}")

if __name__ == "__main__":
    # Initialize vector store
    store = QuestionVectorStore()
    
    # Get all question files from the questions directory
    questions_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "backend/data/questions"
    )
    question_files = []
    
    # Find all section files
    for filename in os.listdir(questions_dir):
        if filename.endswith("_section2.txt"):
            question_files.append((os.path.join(questions_dir, filename), 2))
        elif filename.endswith("_section3.txt"):
            question_files.append((os.path.join(questions_dir, filename), 3))
    
    print(f"Found {len(question_files)} question files")
    
    # Check which files need indexing
    for filename, section_num in question_files:
        if not os.path.exists(filename):
            print(f"File not found: {filename}")
            continue
            
        # Extract video ID from filename
        video_id = os.path.basename(filename).split('_section')[0]
        
        # Check if questions from this file are already indexed
        collection = store.collections[f"section{section_num}"]
        result = collection.get()
        existing_files = set(meta.get('source_file', '') for meta in result['metadatas'])
        
        if video_id in existing_files:
            print(f"\nSkipping {filename} - already indexed")
        else:
            # print(f"\nNeeds Indexing: {filename}")
            print(f"\nIndexing new file: {filename}")
            store.index_questions_file(filename, section_num)
    
    # Print summary of indexed questions
    print("\nCurrent database contents:")
    for section in [2, 3]:
        collection = store.collections[f"section{section}"]
        result = collection.get()
        print(f"\nSection {section}:")
        if result['ids']:
            files = set(meta.get('source_file', '') for meta in result['metadatas'])
            print(f"- {len(result['ids'])} questions from {len(files)} files")
            for file in sorted(files):
                print(f"  - {file}")
        else:
            print("No questions indexed")
