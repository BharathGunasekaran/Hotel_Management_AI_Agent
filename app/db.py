import mysql.connector
import os # Import os to access environment variables

# Best practice: use environment variables for sensitive data
# You would need to set these in your environment, e.g., in a .env file and load them.
# For demonstration, I'm using placeholders that assume env vars are set.
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "xxxxx") # IMPORTANT: Set this securely!
DB_DATABASE = os.getenv("DB_DATABASE", "hotel_db")


try:
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE
    )
    # Use cursor with dictionary=True for column name access
    cursor = conn.cursor(dictionary=True)
    print("Database connection successful.")
except mysql.connector.Error as err:
    print(f"Error connecting to database: {err}")
    # In a real application, you'd handle this more robustly
    conn = None
    cursor = None