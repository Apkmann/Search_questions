import streamlit as st
import json
import re
import pandas as pd
import os
from typing import List, Dict, Any
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Tamil Lessons Search", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .result-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .highlight {
        background-color: yellow;
        padding: 0 2px;
    }
    .field-label {
        font-weight: bold;
        color: #1f77b4;
    }
    .thanglish-converter {
        border: 1px solid #ddd;
        border-radius: 5px;
        margin: 10px 0;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for storing files
if 'files_data' not in st.session_state:
    st.session_state.files_data = {}
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'converted_text' not in st.session_state:
    st.session_state.converted_text = ""

def load_json_file(uploaded_file):
    """Load and parse the uploaded JSON file."""
    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode("utf-8")
            data = json.loads(content)
            return data
        except json.JSONDecodeError:
            st.error("Error: Invalid JSON file. Please upload a valid JSON file.")
            return None
        except Exception as e:
            st.error(f"Error reading file: {e}")
            return None
    return None

def highlight_text(text, search_query):
    """Highlight the search query in the text."""
    if not search_query or not text:
        return text
    
    # Create a list of search terms if multiple words are provided
    search_terms = search_query.lower().split()
    
    highlighted = text
    for term in search_terms:
        pattern = re.compile(f"({re.escape(term)})", re.IGNORECASE)
        highlighted = pattern.sub(r'<span class="highlight">\1</span>', highlighted)
    
    return highlighted

def search_in_data(data: List[Dict[str, Any]], search_query: str, selected_fields: List[str]):
    """
    Search for the query in selected fields.
    Returns matching lessons with their details.
    """
    results = []
    
    if not search_query or not data:
        return results
    
    # Create a list of search terms if multiple words are provided
    search_terms = search_query.lower().split()
    
    for lesson in data:
        lesson_name = lesson.get("lesson_name", "")
        unit = lesson.get("unit", "")
        
        for qa_pair in lesson.get("questions_pairs", []):
            question = qa_pair.get("question", "")
            answer = qa_pair.get("answer", "")
            explanation = qa_pair.get("explanation", "")
            syllabus_area = qa_pair.get("syllabus_area", "")
            
            # Determine fields to search based on selection
            fields_to_search = {}
            if "question" in selected_fields:
                fields_to_search["question"] = question.lower()
            if "answer" in selected_fields:
                fields_to_search["answer"] = answer.lower()
            if "syllabus_area" in selected_fields:
                fields_to_search["syllabus_area"] = syllabus_area.lower()
            if "explanation" in selected_fields:
                fields_to_search["explanation"] = explanation.lower()
            
            # Check if all search terms exist in any of the selected fields
            match_found = False
            
            # For OR search (any term matches)
            if len(search_terms) == 1:
                # Single term search
                term = search_terms[0]
                for field_name, field_value in fields_to_search.items():
                    if term in field_value:
                        match_found = True
                        break
            else:
                # Multi-term search (OR operation)
                for term in search_terms:
                    for field_name, field_value in fields_to_search.items():
                        if term in field_value:
                            match_found = True
                            break
                    if match_found:
                        break
                        
            if match_found:
                results.append({
                    "lesson_name": lesson_name,
                    "unit": unit,
                    "question": question,
                    "answer": answer,
                    "explanation": explanation,
                    "syllabus_area": syllabus_area
                })
    
    return results

def display_results(results, search_query):
    """Display search results in a structured format with highlights."""
    if not results:
        st.info("No matching results found.")
        return
    
    st.success(f"Found {len(results)} matching results.")
    
    for idx, result in enumerate(results):
        with st.expander(f"{idx + 1}. {result['lesson_name']}"):
            st.markdown(f"<div class='field-label'>Unit:</div> {result['unit']}", unsafe_allow_html=True)
            
            # Highlight matches in each field
            highlighted_question = highlight_text(result['question'], search_query)
            highlighted_answer = highlight_text(result['answer'], search_query)
            highlighted_explanation = highlight_text(result['explanation'], search_query)
            highlighted_syllabus = highlight_text(result['syllabus_area'], search_query)
            
            st.markdown(f"<div class='field-label'>Question:</div> {highlighted_question}", unsafe_allow_html=True)
            st.markdown(f"<div class='field-label'>Answer:</div> {highlighted_answer}", unsafe_allow_html=True)
            st.markdown(f"<div class='field-label'>Explanation:</div> {highlighted_explanation}", unsafe_allow_html=True)
            st.markdown(f"<div class='field-label'>Syllabus Area:</div> {highlighted_syllabus}", unsafe_allow_html=True)

def main():
    # Sidebar for file management
    with st.sidebar:
        st.title("File Management")
        
        uploaded_file = st.file_uploader("Upload JSON file", type=["json"], key="file_uploader")
        
        if uploaded_file:
            file_name = uploaded_file.name
            data = load_json_file(uploaded_file)
            
            if data and file_name not in st.session_state.files_data:
                # Add new file to session state
                st.session_state.files_data[file_name] = data
                st.session_state.current_file = file_name
                st.success(f"File '{file_name}' loaded successfully!")
        
        # Display list of uploaded files
        st.subheader("Uploaded Files")
        if st.session_state.files_data:
            selected_file = st.radio(
                "Select a file to search:",
                list(st.session_state.files_data.keys()),
                index=list(st.session_state.files_data.keys()).index(st.session_state.current_file) if st.session_state.current_file else 0
            )
            st.session_state.current_file = selected_file
            
            # Option to remove files
            if st.button("Remove Selected File"):
                del st.session_state.files_data[selected_file]
                if not st.session_state.files_data:
                    st.session_state.current_file = None
                else:
                    st.session_state.current_file = list(st.session_state.files_data.keys())[0]
                st.experimental_rerun()
        else:
            st.info("No files uploaded yet.")
            
        # Thanglish to Tamil converter in sidebar
        st.subheader("Thanglish to Tamil")
        st.markdown("Use this tool to convert English keyboard input to Tamil:")
        components.iframe("https://www.easytyping.com/tamil-typing", height=400)
    
    # Main content area
    st.title("Tamil Lessons Search Tool")
    
    # Add a compact Thanglish to Tamil converter in the main area for easy access
    with st.expander("Thanglish to Tamil Converter"):
        st.markdown("""
        Use this converter to type in Thanglish (Tamil words using English letters) 
        and convert to Tamil script. This makes searching easier when using an English keyboard.
        """)
        components.iframe("https://www.easytyping.com/tamil-typing", height=500)
    
    if st.session_state.current_file:
        current_data = st.session_state.files_data[st.session_state.current_file]
        
        # Summary of the current file
        total_lessons = len(current_data)
        total_qa_pairs = sum(len(lesson.get("questions_pairs", [])) for lesson in current_data)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Lessons", total_lessons)
        with col2:
            st.metric("Total Q&A Pairs", total_qa_pairs)
        
        # Search functionality
        st.subheader("Search Lessons")
        
        # Select fields to search in
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("Enter keywords to search (Tamil or English)", key="search_input")
            st.markdown("""
            <small>You can use the Thanglish to Tamil converter above to convert English keyboard input to Tamil before searching.</small>
            """, unsafe_allow_html=True)
        with col2:
            search_fields = st.multiselect(
                "Fields to search",
                ["question", "answer", "syllabus_area", "explanation"],
                default=["question", "answer", "syllabus_area"],
                key="search_fields"
            )
        
        # Include a dedicated search button for better UX
        if st.button("Search", key="search_button"):
            if search_query and search_fields:
                results = search_in_data(current_data, search_query, search_fields)
                display_results(results, search_query)
            elif search_query and not search_fields:
                st.warning("Please select at least one field to search in.")
            elif not search_query:
                st.warning("Please enter a search term.")
        
        # Alternative search with Enter key
        if search_query and search_fields:
            results = search_in_data(current_data, search_query, search_fields)
            display_results(results, search_query)
        elif search_query and not search_fields:
            st.warning("Please select at least one field to search in.")
    
    else:
        st.info("Upload a JSON file to begin searching.")
        st.markdown("""
        ### Expected JSON Format:
        ```json
        [
            {
                "lesson_name": "பாடப்பொருள் பெயர்",
                "unit": "Related Unit",
                "questions_pairs": [
                    {
                        "question": "Question in Tamil",
                        "answer": "Answer in Tamil",
                        "explanation": "Detailed explanation",
                        "syllabus_area": "Sub-section"
                    },
                    // Additional question-answer pairs
                ]
            },
            // Additional lessons
        ]
        ```
        """)
        
        st.subheader("How to Use This App")
        st.markdown("""
        1. **Upload your JSON files** using the file uploader in the sidebar.
        2. **Convert Thanglish to Tamil** using the converter in the sidebar or expander.
        3. **Search through your data** by entering keywords and selecting which fields to search in.
        4. **View the results** with highlighted matching terms.
        
        This app helps you easily search through Tamil lessons content even if you have an English keyboard.
        """)

if __name__ == "__main__":
    main()
