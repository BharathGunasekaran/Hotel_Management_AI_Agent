# 🏨 Hotel Management AI Agent

A chat-based AI agent for hotel front-desk tasks. Guests or staff type requests in plain
English, for example *"Are any deluxe rooms free next week?"*, and the agent uses **Gemini
function calling** to check availability, book rooms and cancel bookings in a **MySQL** database.

## Features

- 💬 Natural-language chat UI built with **Streamlit**
- 🔎 Check room availability by room type and dates
- 🛏️ Book a room for a guest, with the total price worked out automatically
- ❌ Cancel a booking by its ID
- 📊 Get an overview of all rooms and their status
- 🤖 Gemini picks and calls the right tool automatically (automatic function calling)

## Tech stack

| Layer | Technology |
|---|---|
| LLM / agent | Google Gemini 2.5 Flash (`google-generativeai`) with function calling |
| UI | Streamlit |
| Database | MySQL (`mysql-connector-python`) |
| Config | python-dotenv |

## How it works

```text
User message ──▶ Streamlit chat ──▶ Gemini ──▶ chooses a tool ──▶ hotel_tools.py ──▶ MySQL
                                       ▲                                   │
                                       └──────────── tool result ──────────┘
```

The agent's tools live in `hotel_tools.py`:

| Tool | What it does |
|---|---|
| `check_availability(room_type, check_in_date, check_out_date)` | Lists free rooms of a type for the given dates |
| `book_room(room_number, guest_name, check_in_date, check_out_date)` | Creates a booking and calculates the total price |
| `get_room_overview()` | Summarises all rooms |
| `cancel_booking(booking_id)` | Cancels an existing booking |

## Getting started

### Prerequisites
- Python 3.10+
- A running MySQL server
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=hotel_db
```

### 3. Create and seed the database
```bash
python database_setup.py
```
This creates the `rooms` and `bookings` tables and adds 60 rooms:

| Room type | Rooms | Price per night |
|---|---|---|
| Standard | 20 | ₹3,000 |
| Deluxe | 20 | ₹6,500 |
| Suite | 20 | ₹12,000 |

> ⚠️ Running the setup script drops and recreates the tables, so existing bookings are deleted.

### 4. Run the app
```bash
streamlit run app.py
```

## Project structure

```text
Hotel_Management_AI_Agent/
├── app.py              # Streamlit chat UI and Gemini agent setup
├── hotel_tools.py      # Tools the agent can call (MySQL queries)
├── database_setup.py   # Creates and seeds the database
├── requirements.txt    # Python dependencies
└── packages.txt        # System packages (for Streamlit Cloud deployment)
```
