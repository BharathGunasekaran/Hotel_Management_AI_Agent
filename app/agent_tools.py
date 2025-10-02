import requests
import uuid
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from app.db import cursor, conn


# ---------------- Weather API -----------------
API_KEY = "1fba2b86614e3bf3acbc3f1995f3b371"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


# ---------------- Utility Functions -----------------

# Utility function to safely parse and format dates for MySQL
def format_date_for_mysql(date_str):
    """Parses a date string and returns it in YYYY-MM-DD format for MySQL."""
    try:
        # Parse the input string into a Python date object
        dt_obj = parse_date(date_str)
        # Format the date object back into the required SQL string format
        return dt_obj.strftime('%Y-%m-%d'), "Success"
    except ValueError:
        return None, "Invalid date format provided."

def overlap(s1, e1, s2, e2):
    return not (e1 < s2 or e2 < s1)

def daterange(start, end):
    for n in range((end - start).days + 1):
        yield start + timedelta(n)

# ---------------- Weather API -----------------
def get_weather(city):
    if not API_KEY or API_KEY == "INVALID_KEY_FALLBACK":
        return "Weather service failed: API Key not configured or is invalid."
        
    params = {"q": city, "appid": API_KEY, "units":"metric"}
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"Weather in {city}: {desc}, {temp}°C"
    
    try:
        error_message = response.json().get('message', 'Unknown error')
    except:
        error_message = f"HTTP Status {response.status_code}"
        
    return f"Could not fetch weather for {city}. Error: {error_message}"

# ---------------- Room Availability -----------------
def check_availability(room_type, start_date, end_date):
    if not cursor:
        return 0, 0, "Database connection failed."

    # Use the new utility to validate and get a safe date object for calculation
    s_formatted, s_msg = format_date_for_mysql(start_date)
    e_formatted, e_msg = format_date_for_mysql(end_date)
    
    if s_msg != "Success" or e_msg != "Success":
        # Return specific date validation error
        return 0, 0, s_msg if s_msg != "Success" else e_msg

    # We use the date objects parsed by format_date_for_mysql for comparisons
    s = parse_date(s_formatted).date()
    e = parse_date(e_formatted).date()

    if e < s:
        return 0, 0, "End date cannot be before start date."

    cursor.execute("SELECT total_rooms, price_per_night FROM rooms WHERE room_type=%s", (room_type,))
    room = cursor.fetchone()
    if not room: 
        return 0, 0, f"Room type '{room_type}' not found."

    cursor.execute("SELECT start_date, end_date FROM bookings WHERE room_type=%s", (room_type,))
    rows = cursor.fetchall()
    max_booked = 0
    
    for day in daterange(s, e):
        booked_today = sum(1 for b in rows if overlap(b['start_date'], b['end_date'], day, day))
        max_booked = max(max_booked, booked_today)
        
    available = room['total_rooms'] - max_booked
    # Standard nights calculation: number of days between check-in and check-out
    nights = (e - s).days 
    
    if nights <= 0:
        return max(0, available), 0, "Booking must be for at least one night."
        
    price = room['price_per_night'] * nights
    
    return max(0, available), price, "Success" # Returns 3-tuple

# ---------------- Create Booking -----------------
def create_booking(guest_name, room_type, start_date, end_date, contact=None):
    if not cursor:
        return False, "Database connection failed."

    # Use check_availability to validate dates and availability
    available, price, msg = check_availability(room_type, start_date, end_date)
    
    if msg != "Success" or available <= 0: 
        # Return the error message from check_availability
        return False, msg if msg != "Success" else "No rooms available for the requested dates."
    
    # 💡 CRITICAL FIX: Re-format the dates into YYYY-MM-DD for MySQL insertion
    start_date_mysql, _ = format_date_for_mysql(start_date)
    end_date_mysql, _ = format_date_for_mysql(end_date)
    
    try:
        booking_id = str(uuid.uuid4())[:8]
        cursor.execute("""
            INSERT INTO bookings (booking_id, guest_name, room_type, start_date, end_date, contact, price)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (booking_id, guest_name, room_type, start_date_mysql, end_date_mysql, contact, price))
        conn.commit()
        
        return True, {"booking_id": booking_id, "guest_name": guest_name, "room_type": room_type,
                      "start_date": start_date_mysql, "end_date": end_date_mysql, "contact": contact, "price": price}
    except Exception as e:
        conn.rollback()
        return False, f"An internal database error occurred: {e}"

# ---------------- Create Room -----------------
def create_room(room_type, total_rooms, price_per_night):
    if not cursor or not conn:
        return False, "Database connection failed."

    if total_rooms < 1 or price_per_night <= 0:
        return False, "Room count must be at least 1 and price must be greater than 0."

    print(room_type, type(room_type))
    # Check if room type already exists
    cursor.execute("SELECT room_type FROM rooms WHERE room_type=%s", (room_type,))
    if cursor.fetchone():
        return False, f"Room type '{room_type}' already exists."

    print(room_type, type(room_type))
    # Insert new room type
    cursor.execute("""
        INSERT INTO rooms (room_type, total_rooms, price_per_night) VALUES (%s, %s, %s)
    """, (room_type, total_rooms, price_per_night))
    conn.commit()

    return True, {"room_type": room_type, "total_rooms": total_rooms, "price_per_night": price_per_night}
