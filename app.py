import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import hotel_tools

# --- Page Configuration ---
st.set_page_config(
    page_title="Hotel Management AI Agent 🏨",
    page_icon="🏨",
    layout="centered"
)

@st.cache_resource
def initialize_agent():
    print("--- Initializing Gemini Agent ---")
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    # api_key = st.secreats["GEMINI_API_KEY"]
    if not api_key:
        st.error("GEMINI_API_KEY not found. Please set it in the .env file.")
        st.stop()
    
    # Configure the Gemini client
    genai.configure(api_key=api_key)

    # Define the tools the model can use
    tools = [
        hotel_tools.check_availability,
        hotel_tools.book_room,
        hotel_tools.get_room_overview,
        hotel_tools.cancel_booking,
    ]

    # Initialize the Agent with the tools
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        tools=tools
    )
    return model

# --- Chat Session Management ---

def get_chat_session():
    if "chat" not in st.session_state:
        model = initialize_agent()
        # Enable automatic function calling
        st.session_state.chat = model.start_chat(enable_automatic_function_calling=True)
    return st.session_state.chat

# --- Main App UI ---

st.title("🏨 AI Hotel Management Agent")
st.info("Ask me to check room availability, book a room, or show an overview of rooms, etc...!")

# Initialize or get the chat session
chat = get_chat_session()

# Initialize message history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("e.g., Are any deluxe rooms free next week?"):
    # Add user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get and display the agent's response
    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):
            try:
                # Send the message to the Gemini model
                response = chat.send_message(prompt)
                
                # The model's response text will automatically contain the result
                # of any function calls it made.
                response_text = response.text
                st.markdown(response_text)
                
                # Add agent's response to session state
                st.session_state.messages.append({"role": "assistant", "content": response_text})

            except Exception as e:
                error_message = f"An error occurred: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})