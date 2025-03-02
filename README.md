# ConnectSense - South Asian Connectivity Planning Assistant

## Overview

ConnectSense is a specialized AI-powered chatbot designed to assist government officials, educators, healthcare administrators, and community leaders in South Asia with connectivity planning. The app leverages advanced language models (LLMs) like Groq and Gemini to provide expert guidance on implementing connectivity solutions in underserved areas. It simplifies complex technical concepts, offers region-specific recommendations, and helps users make informed decisions about network infrastructure.

The app is built using **Streamlit** for the frontend, **LlamaIndex** for querying and indexing, and integrates with **Groq** and **Gemini** APIs for LLM capabilities. It also uses **GeminiEmbedding** for embedding models to enhance the quality of responses.

---

## Key Features

1. **Region-Specific Expertise**: Tailored solutions for South Asian countries like Pakistan, India, Bangladesh, and Nepal.
2. **Technical Simplification**: Breaks down complex network concepts into easy-to-understand language.
3. **Resource Optimization**: Provides cost-effective and practical recommendations for connectivity planning.
4. **Interactive Chat Interface**: A user-friendly chatbot interface for seamless interaction.
5. **Dynamic LLM Switching**: Automatically switches between Groq and Gemini based on availability.
6. **Context-Aware Responses**: Maintains chat history for context-aware and coherent conversations.
7. **README Integration**: Includes a detailed README section for users to understand the app's purpose and functionality.

---

## Folder Structure

```
ConnectSense/
├── app.py                  # Main application file containing the Streamlit app logic
├── config.py               # Configuration file for system prompts and README content
├── vector_db/              # Directory containing the pre-built vector database
│   └── full_index.pkl      # Pickle file storing the indexed data for querying
├── .env                    # Environment variables file for storing API keys
├── requirements.txt        # List of Python dependencies
└── README.md               # Project documentation (this file)
```

---

## How It Works

1. **Initialization**:
   - The app loads environment variables (API keys for Groq and Gemini) from the `.env` file.
   - It initializes the embedding model (`GeminiEmbedding`) and the LLM (either Groq or Gemini, depending on availability).
   - The pre-built vector database (`full_index.pkl`) is loaded to enable querying.

2. **User Interaction**:
   - Users interact with the chatbot through a Streamlit interface.
   - The app maintains a chat history to provide context-aware responses.
   - Users can ask questions about connectivity planning, and the app generates detailed, structured responses.

3. **Dynamic LLM Switching**:
   - The app first attempts to use Groq as the primary LLM. If Groq fails, it falls back to Gemini.

4. **README Integration**:
   - Users can toggle the README section to learn more about the app's purpose and functionality.

5. **Error Handling**:
   - The app includes robust error handling to manage issues during initialization or query execution.

---

## Setup Instructions

1. **Install Dependencies**:
   - Install the required Python packages using the `requirements.txt` file:
     ```bash
     pip install -r requirements.txt
     ```

2. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory and add your API keys:
     ```
     GOOGLE_API_KEY=your_google_api_key
     GROQ_API_KEY=your_groq_api_key
     ```

3. **Run the App**:
   - Start the Streamlit app by running:
     ```bash
     streamlit run app.py
     ```

4. **Access the App**:
   - Open the provided URL in your browser to interact with the ConnectSense chatbot.

---

## Usage

1. **Ask Questions**:
   - Type your questions about connectivity planning in the chat input box.
   - The app will generate detailed, context-aware responses.

2. **Toggle README**:
   - Click the "README" button in the sidebar to view detailed information about the app.

3. **Clear Chat**:
   - Use the "Clear Chat" button in the sidebar to reset the chat history.

---

## System Requirements

- Python 3.8 or higher
- Streamlit
- LlamaIndex
- Groq and Gemini API keys
- Google API key for GeminiEmbedding

---

## About the App

ConnectSense is designed to bridge the digital divide in South Asia by providing accessible, expert-level guidance on connectivity planning. It combines advanced AI technologies with a user-friendly interface to empower non-technical stakeholders to make informed decisions. Whether you're planning a rural internet project, improving telemedicine capabilities, or enhancing disaster-resilient communications, ConnectSense is your go-to assistant.

---

## Author

ConnectSense Team  
*Bridging communities through connectivity across South Asia*

---

*For more information, click the "README" button in the app sidebar.*