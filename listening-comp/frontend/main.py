import streamlit as st
import sys
import os
import json
from datetime import datetime
from streamlit.components.v1 import html

# Use absolute imports with sys.path modification
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.question_generator import QuestionGenerator
from backend.audio_generator import AudioGenerator

# Page config
st.set_page_config(
    page_title="JLPT Listening Practice",
    page_icon="🎧",
    layout="wide"
)

st.markdown("""
<style>
.delete-button {
    color: #FF4B4B;
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
    font-size: 16px;
}
.delete-button:hover {
    color: #FF0000;
}
</style>
""", unsafe_allow_html=True)

def load_stored_questions():
    """Load previously stored questions from JSON file"""
    questions_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "backend/data/stored_questions.json"
    )
    if os.path.exists(questions_file):
        with open(questions_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_question(question, practice_type, topic, audio_file=None):
    """Save a generated question to JSON file or update existing one"""
    if not question:
        return None
        
    questions_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "backend/data/stored_questions.json"
    )
    
    # Load existing questions
    stored_questions = load_stored_questions()
    
    # Check if question already exists
    existing_id = None
    for qid, qdata in stored_questions.items():
        if qdata['question'] == question:
            existing_id = qid
            break
    
    if existing_id:
        # Update existing question
        stored_questions[existing_id].update({
            "audio_file": audio_file,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        question_id = existing_id
    else:
        # Create new question
        question_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        stored_questions[question_id] = {
            "question": question,
            "practice_type": practice_type,
            "topic": topic,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "audio_file": audio_file
        }
    
    # Save back to file
    os.makedirs(os.path.dirname(questions_file), exist_ok=True)
    with open(questions_file, 'w', encoding='utf-8') as f:
        json.dump(stored_questions, f, ensure_ascii=False, indent=2)
    
    return question_id

def delete_question(question_id: str) -> bool:
    """Delete a specific question from stored questions"""
    questions_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "backend/data/stored_questions.json"
    )
    try:
        # Load existing questions
        stored_questions = load_stored_questions()
        
        # Delete the question if it exists
        if question_id in stored_questions:
            # Delete associated audio file if it exists
            audio_file = stored_questions[question_id].get('audio_file')
            if audio_file and os.path.exists(audio_file):
                os.unlink(audio_file)
            
            # Remove from stored questions
            del stored_questions[question_id]
            
            # Save back to file
            with open(questions_file, 'w', encoding='utf-8') as f:
                json.dump(stored_questions, f, ensure_ascii=False, indent=2)
            return True
    except Exception as e:
        print(f"Error deleting question: {str(e)}")
    return False

def clear_all_questions() -> bool:
    """Delete all stored questions and their audio files"""
    questions_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "backend/data/stored_questions.json"
    )
    try:
        # Load existing questions to get audio files
        stored_questions = load_stored_questions()
        
        # Delete all associated audio files
        for qdata in stored_questions.values():
            audio_file = qdata.get('audio_file')
            if audio_file and os.path.exists(audio_file):
                os.unlink(audio_file)
        
        # Clear the questions file
        with open(questions_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        return True
    except Exception as e:
        print(f"Error clearing questions: {str(e)}")
    return False

def render_interactive_stage():
    """Render the interactive learning stage"""
    # Initialize session state
    if 'question_generator' not in st.session_state:
        st.session_state.question_generator = QuestionGenerator()
    if 'audio_generator' not in st.session_state:
        st.session_state.audio_generator = AudioGenerator()
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'feedback' not in st.session_state:
        st.session_state.feedback = None
    if 'current_practice_type' not in st.session_state:
        st.session_state.current_practice_type = None
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = None
    if 'current_audio' not in st.session_state:
        st.session_state.current_audio = None
        
    # Load stored questions for sidebar
    stored_questions = load_stored_questions()
    
    # Create sidebar
    with st.sidebar:
        st.header("Saved Questions")
        
        # Add Clear All button at the top if there are questions
        if stored_questions:
            if st.button("Clear question history"):
                if clear_all_questions():
                    st.success("Reset history")
                    st.rerun()
                else:
                    st.error("Failed to clear questions")
            
            # Create two columns for each question
            for qid, qdata in stored_questions.items():
                col1, col2 = st.columns([5, 1])
                
                # Question button in first column
                with col1:
                    button_label = f"{qdata['practice_type']} - {qdata['topic']}\n{qdata['created_at']}"
                    if st.button(button_label, key=f"q_{qid}"):
                        st.session_state.current_question = qdata['question']
                        st.session_state.current_practice_type = qdata['practice_type']
                        st.session_state.current_topic = qdata['topic']
                        st.session_state.current_audio = qdata.get('audio_file')
                        st.session_state.feedback = None
                        st.rerun()
                
                # Delete button in second column with OpenAI-style icon
                with col2:
                    if st.button("⌫", key=f"del_{qid}", help="Delete this question"):
                        if delete_question(qid):
                            st.success("Question deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete question")
        else:
            st.info("No saved questions yet. Generate some questions to see them here!")
    
    # Practice type selection
    practice_type = st.selectbox(
        "Select Practice Type",
        ["Dialogue Practice", "Phrase Matching"]
    )
    
    # Topic selection
    topics = {
        "Dialogue Practice": ["Daily Conversation", "Shopping", "Restaurant", "Travel", "School/Work"],
        "Phrase Matching": ["Announcements", "Instructions", "Weather Reports", "News Updates"]
    }
    
    topic = st.selectbox(
        "Select Topic",
        topics[practice_type]
    )
    
    # Generate new question button
    if st.button("Generate New Question"):
        generate_new_question(practice_type, topic)
    
    if st.session_state.current_question:
        st.subheader("Practice Scenario")
        
        # Display question components
        if practice_type == "Dialogue Practice":
            st.write("**Introduction:**")
            st.write(st.session_state.current_question['Introduction'])
            st.write("**Conversation:**")
            st.write(st.session_state.current_question['Conversation'])
        else:
            st.write("**Situation:**")
            st.write(st.session_state.current_question['Situation'])
        
        st.write("**Question:**")
        st.write(st.session_state.current_question['Question'])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Display options
            options = st.session_state.current_question['Options']
            
            # If we have feedback, show which answers were correct/incorrect
            if st.session_state.feedback:
                correct = st.session_state.feedback.get('correct', False)
                correct_answer = st.session_state.feedback.get('correct_answer', 1) - 1
                selected_index = st.session_state.selected_answer - 1 if hasattr(st.session_state, 'selected_answer') else -1
                
                st.write("\n**Your Answer:**")
                for i, option in enumerate(options):
                    if i == correct_answer and i == selected_index:
                        st.success(f"{option} ✓ (Correct!)")
                    elif i == correct_answer:
                        st.success(f"{option} ✓ (This was the correct answer)")
                    elif i == selected_index:
                        st.error(f"{option} ✗ (Your answer)")
                    else:
                        st.write(f"{option}")
                
                # Show explanation
                st.write("\n**Explanation:**")
                explanation = st.session_state.feedback.get('explanation', 'No feedback available')
                if correct:
                    st.success(explanation)
                else:
                    st.error(explanation)
                
                # Add button to try new question
                if st.button("Try Another Question"):
                    generate_new_question(st.session_state.current_practice_type, st.session_state.current_topic)
            else:
                # Display options as radio buttons when no feedback yet
                selected = st.radio(
                    "Choose your answer:",
                    options,
                    index=None,
                    format_func=lambda x: f"{x}"  # Just show the option as-is since it already has A) B) etc.
                )
                
                # Submit answer button
                if selected and st.button("Submit Answer"):
                    selected_index = options.index(selected) + 1
                    st.session_state.selected_answer = selected_index
                    st.session_state.feedback = st.session_state.question_generator.get_feedback(
                        st.session_state.current_question,
                        selected_index
                    )
                    st.rerun()
        
        with col2:
            st.subheader("Audio")
            
            # Show generate audio button if no audio exists
            if not st.session_state.current_audio and st.session_state.current_question:
                if st.button("Generate Audio"):
                    with st.spinner("Generating audio..."):
                        try:
                            audio_file = st.session_state.audio_generator.generate_audio(
                                st.session_state.current_question
                            )
                            
                            if os.path.exists(audio_file):
                                st.session_state.current_audio = audio_file
                                # Save audio file path with question
                                save_question(
                                    st.session_state.current_question,
                                    st.session_state.current_practice_type,
                                    st.session_state.current_topic,
                                    audio_file
                                )
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error generating audio: {str(e)}")
            
            # Show audio player if audio exists
            if st.session_state.current_audio and os.path.exists(st.session_state.current_audio):
                # Display audio player
                st.audio(st.session_state.current_audio, format='audio/mp3')
                
            
            elif st.session_state.current_question:
                # Check if this question has audio already saved
                stored_questions = load_stored_questions()
                for qdata in stored_questions.values():
                    if (qdata['question'] == st.session_state.current_question and 
                        qdata.get('audio_file') and 
                        os.path.exists(qdata['audio_file'])):
                        st.session_state.current_audio = qdata['audio_file']
                        st.rerun()
                        break
            else:
                st.info("Generate a question to create audio.")
    else:
        st.info("Click 'Generate New Question' to start practicing!")

def generate_new_question(practice_type, topic):
    """Helper function to generate and save a new question"""
    with st.spinner("Generating new question..."):
        try:
            section_num = 2 if practice_type == "Dialogue Practice" else 3
            new_question = st.session_state.question_generator.generate_similar_question(
                section_num, topic
            )
            
            if new_question:
                st.session_state.current_question = new_question
                st.session_state.current_practice_type = practice_type
                st.session_state.current_topic = topic
                st.session_state.feedback = None
                
                # Save the generated question
                question_id = save_question(new_question, practice_type, topic)
                st.session_state.current_audio = None
                st.rerun()
            else:
                st.error("Failed to generate a valid question. Please try again.")
        except Exception as e:
            st.error(f"Error generating question: {str(e)}")

def main():
    st.title("JLPT Listening Practice")
    render_interactive_stage()

if __name__ == "__main__":
    main()
