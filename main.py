import streamlit as st
import json
import re
import pandas as pd
from typing import List, Dict, Any

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
    .stButton>button {
        width: 100%;
    }
    .thanglish-box {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        background-color: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for storing files
if 'files_data' not in st.session_state:
    st.session_state.files_data = {}
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'tanglish_map' not in st.session_state:
    # Simple Tanglish to Tamil mapping for common characters
    st.session_state.tanglish_map = {
        'a': 'அ', 'aa': 'ஆ', 'i': 'இ', 'ee': 'ஈ', 'u': 'உ', 'oo': 'ஊ',
        'e': 'எ', 'ae': 'ஏ', 'ai': 'ஐ', 'o': 'ஒ', 'oa': 'ஓ', 'au': 'ஔ',
        'k': 'க்', 'ka': 'க', 'kaa': 'கா', 'ki': 'கி', 'kee': 'கீ',
        'ku': 'கு', 'koo': 'கூ', 'ke': 'கெ', 'kae': 'கே', 'kai': 'கை',
        'ko': 'கொ', 'koa': 'கோ', 'kau': 'கௌ',
        'ng': 'ங்', 'nga': 'ங', 'ngaa': 'ஙா',
        'c': 'ச்', 'ch': 'ச்', 'sa': 'ச', 'saa': 'சா', 'si': 'சி', 'see': 'சீ',
        'su': 'சு', 'soo': 'சூ', 'se': 'செ', 'sae': 'சே', 'sai': 'சை',
        'so': 'சொ', 'soa': 'சோ', 'sau': 'சௌ',
        'nj': 'ஞ்', 'nja': 'ஞ', 'njaa': 'ஞா',
        't': 'ட்', 'ta': 'ட', 'taa': 'டா', 'ti': 'டி', 'tee': 'டீ',
        'tu': 'டு', 'too': 'டூ', 'te': 'டெ', 'tae': 'டே', 'tai': 'டை',
        'to': 'டொ', 'toa': 'டோ', 'tau': 'டௌ',
        'nt': 'ண்', 'nta': 'ண', 'ntaa': 'ணா',
        'th': 'த்', 'tha': 'த', 'thaa': 'தா', 'thi': 'தி', 'thee': 'தீ',
        'thu': 'து', 'thoo': 'தூ', 'the': 'தெ', 'thae': 'தே', 'thai': 'தை',
        'tho': 'தொ', 'thoa': 'தோ', 'thau': 'தௌ',
        'n': 'ந்', 'na': 'ந', 'naa': 'நா', 'ni': 'நி', 'nee': 'நீ',
        'nu': 'நு', 'noo': 'நூ', 'ne': 'நெ', 'nae': 'நே', 'nai': 'நை',
        'no': 'நொ', 'noa': 'நோ', 'nau': 'நௌ',
        'p': 'ப்', 'pa': 'ப', 'paa': 'பா', 'pi': 'பி', 'pee': 'பீ',
        'pu': 'பு', 'poo': 'பூ', 'pe': 'பெ', 'pae': 'பே', 'pai': 'பை',
        'po': 'பொ', 'poa': 'போ', 'pau': 'பௌ',
        'm': 'ம்', 'ma': 'ம', 'maa': 'மா', 'mi': 'மி', 'mee': 'மீ',
        'mu': 'மு', 'moo': 'மூ', 'me': 'மெ', 'mae': 'மே', 'mai': 'மை',
        'mo': 'மொ', 'moa': 'மோ', 'mau': 'மௌ',
        'y': 'ய்', 'ya': 'ய', 'yaa': 'யா', 'yi': 'யி', 'yee': 'யீ',
        'yu': 'யு', 'yoo': 'யூ', 'ye': 'யெ', 'yae': 'யே', 'yai': 'யை',
        'yo': 'யொ', 'yoa': 'யோ', 'yau': 'யௌ',
        'r': 'ர்', 'ra': 'ர', 'raa': 'ரா', 'ri': 'ரி', 'ree': 'ரீ',
        'ru': 'ரு', 'roo': 'ரூ', 're': 'ரெ', 'rae': 'ரே', 'rai': 'ரை',
        'ro': 'ரொ', 'roa': 'ரோ', 'rau': 'ரௌ',
        'l': 'ல்', 'la': 'ல', 'laa': 'லா', 'li': 'லி', 'lee': 'லீ',
        'lu': 'லு', 'loo': 'லூ', 'le': 'லெ', 'lae': 'லே', 'lai': 'லை',
        'lo': 'லொ', 'loa': 'லோ', 'lau': 'லௌ',
        'v': 'வ்', 'va': 'வ', 'vaa': 'வா', 'vi': 'வி', 'vee': 'வீ',
        'vu': 'வு', 'voo': 'வூ', 've': 'வெ', 'vae': 'வே', 'vai': 'வை',
        'vo': 'வொ', 'voa': 'வோ', 'vau': 'வௌ',
        'zh': 'ழ்', 'zha': 'ழ', 'zhaa': 'ழா', 'zhi': 'ழி', 'zhee': 'ழீ',
        'zhu': 'ழு', 'zhoo': 'ழூ', 'zhe': 'ழெ', 'zhae': 'ழே', 'zhai': 'ழை',
        'zho': 'ழொ', 'zhoa': 'ழோ', 'zhau': 'ழௌ',
        'L': 'ள்', 'La': 'ள', 'Laa': 'ளா', 'Li': 'ளி', 'Lee': 'ளீ',
        'Lu': 'ளு', 'Loo': 'ளூ', 'Le': 'ளெ', 'Lae': 'ளே', 'Lai': 'ளை',
        'Lo': 'ளொ', 'Loa': 'ளோ', 'Lau': 'ளௌ',
        'R': 'ற்', 'Ra': 'ற', 'Raa': 'றா', 'Ri': 'றி', 'Ree': 'றீ',
        'Ru': 'று', 'Roo': 'றூ', 'Re': 'றெ', 'Rae': 'றே', 'Rai': 'றை',
        'Ro': 'றொ', 'Roa': 'றோ', 'Rau': 'றௌ',
        'N': 'ன்', 'Na': 'ன', 'Naa': 'னா', 'Ni': 'னி', 'Nee': 'னீ',
        'Nu': 'னு', 'Noo': 'னூ', 'Ne': 'னெ', 'Nae': 'னே', 'Nai': 'னை',
        'No': 'னொ', 'Noa': 'னோ', 'Nau': 'னௌ',
        'j': 'ஜ்', 'ja': 'ஜ', 'jaa': 'ஜா', 'ji': 'ஜி', 'jee': 'ஜீ',
        'ju': 'ஜு', 'joo': 'ஜூ', 'je': 'ஜெ', 'jae': 'ஜே', 'jai': 'ஜை',
        'jo': 'ஜொ', 'joa': 'ஜோ', 'jau': 'ஜௌ',
        'sh': 'ஷ்', 'sha': 'ஷ', 'shaa': 'ஷா', 'shi': 'ஷி', 'shee': 'ஷீ',
        'shu': 'ஷு', 'shoo': 'ஷூ', 'she': 'ஷெ', 'shae': 'ஷே', 'shai': 'ஷை',
        'sho': 'ஷொ', 'shoa': 'ஷோ', 'shau': 'ஷௌ',
        'S': 'ஸ்', 'Sa': 'ஸ', 'Saa': 'ஸா', 'Si': 'ஸி', 'See': 'ஸீ',
        'Su': 'ஸு', 'Soo': 'ஸூ', 'Se': 'ஸெ', 'Sae': 'ஸே', 'Sai': 'ஸை',
        'So': 'ஸொ', 'Soa': 'ஸோ', 'Sau': 'ஸௌ',
        'h': 'ஹ்', 'ha': 'ஹ', 'haa': 'ஹா', 'hi': 'ஹி', 'hee': 'ஹீ',
        'hu': 'ஹு', 'hoo': 'ஹூ', 'he': 'ஹெ', 'hae': 'ஹே', 'hai': 'ஹை',
        'ho': 'ஹொ', 'hoa': 'ஹோ', 'hau': 'ஹௌ',
    }

if 'tanglish_input' not in st.session_state:
    st.session_state.tanglish_input = ""
if 'tamil_output' not in st.session_state:
    st.session_state.tamil_output = ""

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
            
            # Check if any search term exists in any of the selected fields
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

def convert_tanglish_to_tamil(text):
    """
    A simple Tanglish to Tamil converter.
    This is a very basic implementation and won't handle all cases correctly.
    """
    result = ""
    i = 0
    while i < len(text):
        # Try to match longer patterns first, then shorter ones
        matched = False
        for length in range(4, 0, -1):  # Try matching 4, 3, 2, 1 characters
            if i + length <= len(text):
                substr = text[i:i+length]
                if substr in st.session_state.tanglish_map:
                    result += st.session_state.tanglish_map[substr]
                    i += length
                    matched = True
                    break
        
        # If no match found, just add the character as is
        if not matched:
            result += text[i]
            i += 1
    
    return result

def tanglish_converter():
    """Simple Tanglish to Tamil converter UI."""
    st.markdown("<div class='thanglish-box'>", unsafe_allow_html=True)
    st.subheader("Tanglish to Tamil Converter")
    
    # Input for Tanglish text
    tanglish_input = st.text_area(
        "Type your Tanglish text here:",
        value=st.session_state.tanglish_input,
        key="tanglish_converter_input",
        height=100
    )
    
    # Convert button
    if st.button("Convert to Tamil"):
        st.session_state.tanglish_input = tanglish_input
        st.session_state.tamil_output = convert_tanglish_to_tamil(tanglish_input)
    
    # Display Tamil output
    st.text_area(
        "Tamil text (copy this to search box):",
        value=st.session_state.tamil_output,
        height=100,
        key="tamil_output_field"
    )
    
    # Quick Tamil characters reference
    with st.expander("Common Tamil Characters Reference"):
        st.markdown("""
        ### Vowels
        - a = அ, aa = ஆ, i = இ, ee = ஈ
        - u = உ, oo = ஊ, e = எ, ae = ஏ
        - ai = ஐ, o = ஒ, oa = ஓ, au = ஔ
        
        ### Consonants + a
        - ka = க, sa/cha = ச, ta = ட, tha = த
        - pa = ப, ma = ம, ya = ய, ra = ர
        - la = ல, va = வ, zha = ழ
        
        ### Example Words
        - thamizh = தமிழ்
        - vanakkam = வணக்கம்
        - enna = என்ன
        """)
    
    st.markdown("</div>", unsafe_allow_html=True)

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
        
        # Add Tanglish converter in sidebar
        tanglish_converter()
    
    # Main content area
    st.title("Tamil Lessons Search Tool")
    
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
            search_query = st.text_input(
                "Enter keywords to search (Tamil or English)", 
                key="search_input",
                help="You can copy Tamil text from the converter in the sidebar"
            )
            
            # Option to use Tamil output from converter
            if st.session_state.tamil_output:
                if st.button("Use converted Tamil text for search"):
                    search_query = st.session_state.tamil_output
                    # This is a trick to update the text input field
                    st.experimental_set_query_params(search=search_query)
                    st.experimental_rerun()
            
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
        2. **Convert Tanglish to Tamil** using the converter in the sidebar.
        3. **Copy the Tamil text** from the converter and paste it into the search box.
        4. **Search through your data** by entering keywords and selecting which fields to search in.
        5. **View the results** with highlighted matching terms.
        
        This app helps you easily search through Tamil lessons content even if you have an English keyboard.
        """)

if __name__ == "__main__":
    main()
