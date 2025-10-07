import google.generativeai as genai
import os
from dotenv import load_dotenv
import hotel_tools # Our tool functions

# --- Initialization ---
print("🤖 Hotel Management Agent Initializing...")

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set it in the .env file.")

# Configure the Gemini client
genai.configure(api_key=api_key)

# Define the tools the model can use
# The model uses the function names and docstrings to decide when to call them.
tools = [
    hotel_tools.check_availability,
    hotel_tools.book_room,
    hotel_tools.get_room_overview, 
]

# Create the generative model with the tools
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    tools=tools
)

# --- Main Conversation Loop ---
print("✅ Agent is ready! How can I help you with your hotel management needs? (Type 'quit' to exit)")
chat = model.start_chat(enable_automatic_function_calling=True)

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == 'quit':
        print("\n🤖 Goodbye!")
        break
    
    try:
        # Send the user's message to the model
        response = chat.send_message(user_input)
        
        # The model's response will automatically include the result
        # of any function calls it decided to make.
        print(f"\nAgent: {response.text}")

    except Exception as e:
        print(f"An error occurred: {e}")