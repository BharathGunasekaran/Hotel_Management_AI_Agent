import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

# Load credentials
load_dotenv()

# Database connection config
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def get_db_connection():
    """Establishes and returns a database connection."""
    return mysql.connector.connect(**DB_CONFIG)

# --- Agent Tools ---

def check_availability(room_type: str, check_in_date: str, check_out_date: str) -> str:
    """
    Checks for available rooms of a specific type between two dates.
    Args:
        room_type: The type of room to check for ('standard', 'deluxe', 'suite').
        check_in_date: The check-in date in 'YYYY-MM-DD' format.
        check_out_date: The check-out date in 'YYYY-MM-DD' format.
    """
    print(f"TOOL: Checking availability for '{room_type}' from {check_in_date} to {check_out_date}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Find rooms that are NOT booked during the requested period
        query = """
            SELECT r.room_number, r.price_per_night FROM rooms r
            WHERE r.room_type = %s AND r.room_id NOT IN (
                SELECT b.room_id FROM bookings b
                WHERE NOT (b.check_out_date <= %s OR b.check_in_date >= %s)
            )
        """
        cursor.execute(query, (room_type, check_in_date, check_out_date))
        available_rooms = cursor.fetchall()
        
        if not available_rooms:
            return f"Sorry, no '{room_type}' rooms are available from {check_in_date} to {check_out_date}."
        
        return f"Success! The following '{room_type}' rooms are available: {str(available_rooms)}"

    except mysql.connector.Error as err:
        return f"Database error: {err}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def book_room(room_number: str, guest_name: str, check_in_date: str, check_out_date: str) -> str:
    """
    Books a specific room for a guest for a given date range.
    Args:
        room_number: The number of the room to book.
        guest_name: The full name of the guest.
        check_in_date: The check-in date in 'YYYY-MM-DD' format.
        check_out_date: The check-out date in 'YYYY-MM-DD' format.
    """
    print(f"TOOL: Attempting to book room '{room_number}' for {guest_name}.")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # First, find room_id and price for the given room_number
        cursor.execute("SELECT room_id, price_per_night FROM rooms WHERE room_number = %s", (room_number,))
        room = cursor.fetchone()
        if not room:
            return f"Error: Room '{room_number}' does not exist."

        # Double-check availability before booking
        # This prevents race conditions where two people try to book at once
        cursor.execute("""
            SELECT booking_id FROM bookings
            WHERE room_id = %s AND NOT (check_out_date <= %s OR check_in_date >= %s)
        """, (room['room_id'], check_in_date, check_out_date))
        
        if cursor.fetchone():
            return f"Error: Room '{room_number}' is already booked for the selected dates."

        # Calculate total price
        start_date = datetime.strptime(check_in_date, '%Y-%m-%d')
        end_date = datetime.strptime(check_out_date, '%Y-%m-%d')
        num_nights = (end_date - start_date).days
        total_price = num_nights * room['price_per_night']

        # Insert booking
        insert_query = """
            INSERT INTO bookings (room_id, guest_name, check_in_date, check_out_date, total_price)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (room['room_id'], guest_name, check_in_date, check_out_date, total_price))
        booking_id = cursor.lastrowid
        conn.commit()
        
        return f"Success! Room {room_number} booked for {guest_name}. Booking ID is {booking_id}. Total price: ${total_price:.2f}"

    except (mysql.connector.Error, ValueError) as err:
        return f"Error during booking: {err}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
# (Add this function to your hotel_tools.py file)

def get_room_overview() -> str:
    """
    Provides a general list of all room numbers and their types available in the hotel.
    """
    print("TOOL: Getting a general overview of all rooms.")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT room_number, room_type FROM rooms ORDER BY room_number")
        rooms = cursor.fetchall()
        
        if not rooms:
            return "There are no rooms configured in the system."
            
        return f"The hotel has the following rooms: {str(rooms)}"

    except mysql.connector.Error as err:
        return f"Database error: {err}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()