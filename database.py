# Import the sqlite3 library to work with SQLite databases
import sqlite3
# Import datetime to add timestamps when URLs are created
from datetime import datetime
# Import Path for file path operations (though not actively used here)
from pathlib import Path

# Set the name of our database file
DB_FILE = "urls.db"

# Create an in-memory cache dictionary to store URLs temporarily for faster access
memory_cache = {}


# Initialize the database and create the table if it doesn't already exist
def init_db():
    # Connect to the SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_FILE)
    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()
    
    # Create the 'urls' table with columns for short_code, original_url, created_at, and clicks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            short_code TEXT PRIMARY KEY,
            original_url TEXT NOT NULL,
            created_at TEXT NOT NULL,
            clicks INTEGER DEFAULT 0
        )
    ''')
    
    # Save the changes to the database
    conn.commit()
    # Load all existing URLs from the database into our memory cache
    load_cache_from_db()
    # Close the database connection
    conn.close()


# Load all URLs from the database into memory for quick access
def load_cache_from_db():
    # Tell Python we're using the global memory_cache variable
    global memory_cache
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    # Create a cursor to execute queries
    cursor = conn.cursor()
    
    # Fetch all URL records from the database
    cursor.execute('SELECT * FROM urls')
    # Get all the results
    rows = cursor.fetchall()
    
    # Loop through each URL record and add it to the cache
    for row in rows:
        # Unpack the row data into individual variables
        short_code, original_url, created_at, clicks = row
        # Store the URL information in our memory cache using the short_code as the key
        memory_cache[short_code] = {
            "original_url": original_url,
            "created_at": created_at,
            "clicks": clicks
        }
    
    # Close the database connection
    conn.close()
    # Print a message showing how many URLs were loaded
    print(f"Loaded {len(memory_cache)} URLs from database")


# Save a new shortened URL to the database and cache
def save_url(code: str, url: str):
    # Get the current date and time in ISO format for the timestamp
    created_at = datetime.utcnow().isoformat()
    
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    # Create a cursor to execute the insert command
    cursor = conn.cursor()
    
    # Insert the new URL record into the database with the short code, original URL, timestamp, and 0 clicks
    cursor.execute('''
        INSERT INTO urls (short_code, original_url, created_at, clicks)
        VALUES (?, ?, ?, ?)
    ''', (code, url, created_at, 0))
    
    # Save the changes to the database
    conn.commit()
    # Close the database connection
    conn.close()
    
    # Also add the URL to our in-memory cache for quick future access
    memory_cache[code] = {
        "original_url": url,
        "created_at": created_at,
        "clicks": 0
    }


# Retrieve a URL by its short code
def get_url(code: str):
    # First, check if the URL is already in our fast memory cache
    if code in memory_cache:
        # If found in cache, return it immediately
        return memory_cache[code]
    
    # If not in cache, query the database
    conn = sqlite3.connect(DB_FILE)
    # Create a cursor to execute the select query
    cursor = conn.cursor()
    
    # Search for the URL with the matching short code
    cursor.execute('SELECT * FROM urls WHERE short_code = ?', (code,))
    # Get the first matching result (or None if not found)
    row = cursor.fetchone()
    # Close the database connection
    conn.close()
    
    # If we found the URL in the database
    if row:
        # Unpack the row into individual variables
        short_code, original_url, created_at, clicks = row
        # Create a dictionary with the URL information
        data = {
            "original_url": original_url,
            "created_at": created_at,
            "clicks": clicks
        }
        # Store it in the memory cache for next time
        memory_cache[code] = data
        # Return the URL information
        return data
    
    # If no URL found, return None
    return None


# Get all URLs stored in the cache
def get_all_urls():
    # Return a copy of the memory cache (copy prevents external modifications)
    return memory_cache.copy()


# Increase the click count for a shortened URL
def increment_clicks(code: str):
    # Check if the short code exists in our cache
    if code not in memory_cache:
        # If not found, return False to indicate failure
        return False
    
    # Increase the click count by 1 in the memory cache
    memory_cache[code]["clicks"] += 1
    
    # Connect to the database to persist the updated click count
    conn = sqlite3.connect(DB_FILE)
    # Create a cursor to execute the update command
    cursor = conn.cursor()
    # Update the click count in the database for this short code
    cursor.execute('UPDATE urls SET clicks = ? WHERE short_code = ?', 
                   (memory_cache[code]["clicks"], code))
    # Save the changes to the database
    conn.commit()
    # Close the database connection
    conn.close()
    
    # Return True to indicate the operation was successful
    return True


# Delete a shortened URL from the system
def delete_url(code: str):
    # Check if the short code exists in our cache
    if code not in memory_cache:
        # If not found, return False to indicate failure
        return False
    
    # Remove the URL from our memory cache
    del memory_cache[code]
    
    # Connect to the database to delete the record
    conn = sqlite3.connect(DB_FILE)
    # Create a cursor to execute the delete command
    cursor = conn.cursor()
    # Delete the URL record from the database with the matching short code
    cursor.execute('DELETE FROM urls WHERE short_code = ?', (code,))
    # Save the changes to the database
    conn.commit()
    # Close the database connection
    conn.close()
    
    # Return True to indicate the operation was successful
    return True
