import mysql.connector
import os
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

# Database connection details from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}
DB_NAME = os.getenv('DB_NAME')

def setup_database():
    """Creates the database, tables, and populates with an expanded room list in INR."""
    try:
        # Connect to MySQL server
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()

        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        print(f"Database '{DB_NAME}' created or already exists.")
        
        # Switch to the new database
        cursor.execute(f"USE {DB_NAME}")

        # Drop tables if they exist for a clean slate
        print("Dropping existing tables (if any)...")
        cursor.execute("DROP TABLE IF EXISTS bookings")
        cursor.execute("DROP TABLE IF EXISTS rooms")

        # Create rooms table
        print("Creating 'rooms' table...")
        cursor.execute("""
            CREATE TABLE rooms (
                room_id INT AUTO_INCREMENT PRIMARY KEY,
                room_number VARCHAR(10) NOT NULL UNIQUE,
                room_type ENUM('standard', 'deluxe', 'suite') NOT NULL,
                price_per_night DECIMAL(10, 2) NOT NULL
            )
        """)

        # Create bookings table
        print("Creating 'bookings' table...")
        cursor.execute("""
            CREATE TABLE bookings (
                booking_id INT AUTO_INCREMENT PRIMARY KEY,
                room_id INT,
                guest_name VARCHAR(255) NOT NULL,
                check_in_date DATE NOT NULL,
                check_out_date DATE NOT NULL,
                total_price DECIMAL(10, 2),
                FOREIGN KEY (room_id) REFERENCES rooms(room_id)
            )
        """)

        # --- UPDATED SECTION ---
        # Populate rooms table with 60 rooms in total, priced in INR.
        print("Populating 'rooms' table with 60 rooms (20 of each type)...")
        
        rooms_to_add = []
        
        # Generate 20 standard rooms (e.g., 101-120) at ₹3000/night
        for i in range(1, 21):
            room_number = str(100 + i)
            rooms_to_add.append((room_number, 'standard', 3000.00))

        # Generate 20 deluxe rooms (e.g., 201-220) at ₹6500/night
        for i in range(1, 21):
            room_number = str(200 + i)
            rooms_to_add.append((room_number, 'deluxe', 6500.00))

        # Generate 20 suite rooms (e.g., 301-320) at ₹12000/night
        for i in range(1, 21):
            room_number = str(300 + i)
            rooms_to_add.append((room_number, 'suite', 12000.00))
            
        insert_room_query = "INSERT INTO rooms (room_number, room_type, price_per_night) VALUES (%s, %s, %s)"
        cursor.executemany(insert_room_query, rooms_to_add)
        cnx.commit()
        # --- END OF UPDATED SECTION ---

        print(f"\nDatabase setup complete! {len(rooms_to_add)} rooms were added. ✨")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

if __name__ == "__main__":
    setup_database()
