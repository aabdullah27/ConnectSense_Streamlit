import os
import pickle
import streamlit as st
from dotenv import load_dotenv

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

# Set page config
st.set_page_config(
    page_title="ConnectSense | Connecting the Dots",
    page_icon="🔗",
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "query_engine" not in st.session_state:
    st.session_state.query_engine = None

if "primary_llm" not in st.session_state:
    st.session_state.primary_llm = None

if "show_readme" not in st.session_state:
    st.session_state.show_readme = False

# ConnectSense README content
readme_content = README_CONTENT

# Initialize the system automatically
if st.session_state.query_engine is None:
    with st.spinner("Loading vector database...", show_time=True):
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
                st.warning(f"Groq initialization failed. Falling back to Gemini.")
                llm = Gemini(model=GEMINI_MODEL, api_key=GOOGLE_API_KEY, temperature=0.5)
                Settings.llm = llm
                st.session_state.primary_llm = "Gemini"
            
            # Set up query engine
            query_engine = index.as_query_engine(
                similarity_top_k=3
            )
            st.session_state.query_engine = query_engine
            
        except Exception as e:
            st.error(f"Error initializing application: {str(e)}")

# Sidebar
with st.sidebar:
    st.header("System Controls ⚙️")
    
    # README button
    if st.button("README"):
        st.session_state.show_readme = not st.session_state.show_readme
    
    # Show system status
    if st.session_state.query_engine is not None:
        st.success(f"System Ready - Using {st.session_state.primary_llm}")
    else:
        st.error("System initialization failed")
    
    # Clear chat button in sidebar
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# Main content area
if st.session_state.show_readme:
    # Show README content only
    st.markdown(readme_content)
else:
    # Display the title only when not showing README
    st.title("ConnectSense Chatbot")
    
    # Display chat messages
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
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking...", show_time=True):
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
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            error_msg = "System initialization failed. Please check the application logs for more information."
            st.markdown(error_msg)
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

# Simple footer - Always visible
st.caption("ConnectSense System © 2025")