import os
import pickle
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import base64
from io import BytesIO
from functools import lru_cache

from llama_index.core import Settings
from llama_index.llms.groq import Groq
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

from config import SYSTEM_PROMPT, README_CONTENT

# Load environment variables
load_dotenv()

# Get API keys from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Set constants
GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "models/gemini-2.0-flash"
EMBEDDING_MODEL = "models/embedding-001"

# Helper function to convert image to base64 (cached to avoid repeated conversions)
@lru_cache(maxsize=10)
def image_to_base64(image_path):
    try:
        with Image.open(image_path) as img:
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        return None

# Set page config
st.set_page_config(
    page_title="ConnectSense | Connecting the Dots",
    page_icon="🔗",
    layout="wide"
)

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "query_engine" not in st.session_state:
    st.session_state.query_engine = None
if "primary_llm" not in st.session_state:
    st.session_state.primary_llm = None
if "show_readme" not in st.session_state:
    st.session_state.show_readme = True

readme_content = README_CONTENT

# Custom CSS to improve UI with dark mode support
st.markdown("""
<style>
    /* Dark mode aware styling */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    
    .logo-image {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .title-container {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 30px;
        background-color: transparent;
        padding: 15px 20px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    .title-text {
        margin: 0;
        color: inherit;
        font-weight: 600;
        font-size: 2.2em;
    }
    
    .divider {
        height: 1px; 
        background: rgba(128, 128, 128, 0.3);
        margin: 20px 0;
    }
    
    .footer-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 10px;
        text-align: center;
        font-size: 0.8em;
        border-top: 1px solid rgba(128, 128, 128, 0.2);
        background-color: transparent;
        backdrop-filter: blur(10px);
    }
    
    .footer-highlight {
        font-weight: bold;
    }
    
    /* Improved buttons */
    .stButton button {
        transition: all 0.3s ease;
        border-radius: 8px;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Quick action buttons container */
    .quick-actions {
        margin-bottom: 20px;
    }
    
    /* Hide status indicators from main UI */
    .status-indicator {
        display: none;
    }
    
    /* Enhance sidebar header */
    .sidebar-header {
        font-size: 1.5em;
        font-weight: 600;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(128, 128, 128, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize the system automatically
if st.session_state.query_engine is None:
    with st.spinner("Loading vector database..."):
        try:
            # Load the vector database
            with open("vector_db/full_index.pkl", "rb") as f:
                index = pickle.load(f)
            
            # Initialize embedding model
            embed_model = GeminiEmbedding(model_name=EMBEDDING_MODEL, api_key=GOOGLE_API_KEY)
            Settings.embed_model = embed_model
            
            # Try to initialize Groq as primary LLM
            try:
                llm = Groq(api_key=GROQ_API_KEY, model=GROQ_MODEL, temperature=0.5)
                Settings.llm = llm
                st.session_state.primary_llm = "Groq"
            except Exception as e:
                st.warning(f"Groq initialization failed: {str(e)}. Falling back to Gemini.")
                try:
                    llm = Gemini(model=GEMINI_MODEL, api_key=GOOGLE_API_KEY, temperature=0.5)
                    Settings.llm = llm
                    st.session_state.primary_llm = "Gemini"
                except Exception as e:
                    st.error(f"Gemini initialization also failed: {str(e)}")
                    st.session_state.primary_llm = None
            
            # Set up query engine if LLM is initialized
            if st.session_state.primary_llm:
                st.session_state.query_engine = index.as_query_engine(similarity_top_k=3)
            else:
                st.error("No LLM available. Please check your API keys and try again.")
            
        except Exception as e:
            st.error(f"Error initializing application: {str(e)}")

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header">ConnectSense Controls</div>', unsafe_allow_html=True)
    
    # Display logo in sidebar
    logo_path = "assets/ConnectSense.jpg"
    if os.path.exists(logo_path):
        base64_image = image_to_base64(logo_path)
        if base64_image:
            st.markdown(
                f"""
                <div class="logo-container">
                    <img src="data:image/jpeg;base64,{base64_image}" alt="ConnectSense Logo" width="180" class="logo-image">
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # README toggle button
    if st.button(f"{'📚 Switch to Chatbot' if st.session_state.show_readme else '📖 View README'}", use_container_width=True):
        st.session_state.show_readme = not st.session_state.show_readme
        st.rerun()
    
    # Clear chat button in sidebar
    if st.button("🧹 Clear Conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Main content area
if st.session_state.show_readme:
    # Show logo at the top of README
    logo_path = "assets/ConnectSense.jpg"
    if os.path.exists(logo_path):
        base64_image = image_to_base64(logo_path)
        if base64_image:
            st.markdown(
                f"""
                <div class="logo-container">
                    <img src="data:image/jpeg;base64,{base64_image}" alt="ConnectSense Logo" width="300" class="logo-image">
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Show README content with a continue button
    st.markdown(readme_content)
    
    # Add a centered continue button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Using ConnectSense", use_container_width=True):
            st.session_state.show_readme = False
            st.rerun()
else:
    # Display the title and logo when not showing README
    logo_path = "assets/ConnectSense.jpg"
    if os.path.exists(logo_path):
        base64_image = image_to_base64(logo_path)
        if base64_image:
            st.markdown(
                f"""
                <div class="title-container">
                    <img src="data:image/jpeg;base64,{base64_image}" alt="ConnectSense Logo" width="100" style="border-radius: 10px;">
                    <h1 class="title-text">ConnectSense 🔗</h1>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.title("ConnectSense 🔗")
    
    # Quick action buttons
    st.markdown('<div class="quick-actions">', unsafe_allow_html=True)
    st.markdown("### Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("📊 Resource Allocation", key="button1", help="Resource Allocation", disabled=True, use_container_width=True)
    with col2:
        st.button("📚 Non-Technical Guides", key="button2", help="Non-Technical Guides", disabled=True, use_container_width=True)
    with col3:
        st.button("🌐 Connectivity Helper", key="button3", help="Connectivity Helper", disabled=True, use_container_width=True)
    with col4:
        st.button("🔧 Troubleshooting Tips", key="button4", help="Troubleshooting Tips", disabled=True, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Create a clear separation between buttons and chat
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Display chat messages in a container
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    user_input = st.chat_input("Ask about your documents...")

    # Process user input
    if user_input and st.session_state.query_engine is not None:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
        
        # Generate and display assistant response
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Build context from recent messages (last 5 interactions / 10 messages)
                        context_str = ""
                        if st.session_state.chat_history:
                            recent = st.session_state.chat_history[-10:]
                            for i in range(0, len(recent), 2):
                                if i+1 < len(recent):
                                    context_str += f"### Previous Interaction:\n**User**: {recent[i]['content']}\n**Assistant**: {recent[i+1]['content']}\n\n"
                        
                        # Combine system prompt, context, and current question
                        full_query = f"{SYSTEM_PROMPT}\n\n{context_str}\n### New Question:\n{user_input}"
                        
                        # Execute query with the full query as input
                        response = st.session_state.query_engine.query(full_query)
                        response_text = str(response)
                        
                        st.markdown(response_text)
                        
                        # Add assistant message to chat history
                        st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                        
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.markdown(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
    elif user_input and st.session_state.query_engine is None:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
        
        # Generate and display assistant response
        with chat_container:
            with st.chat_message("assistant"):
                error_msg = "System initialization failed. Please check the application logs for more information."
                st.markdown(error_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

# Footer with version and copyright
st.markdown(
    """
    <div class="footer-container">
        ConnectSense System © 2025 🌐 | <span class="footer-highlight">Connecting the Dots</span>
    </div>
    """,
    unsafe_allow_html=True
)
