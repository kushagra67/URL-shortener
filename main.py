
# Import FastAPI (the web framework) and HTTPException (for error handling)
from fastapi import FastAPI, HTTPException
# Import RedirectResponse to send users to a different URL
from fastapi.responses import RedirectResponse
# Import random module to generate random characters for short codes
import random
# Import string module to access sets of letters and digits
import string

# Import our custom data models for request and response validation
from models import URLRequest, URLResponse
# Import our database module to handle all database operations
import database

# Create the main FastAPI application instance with a descriptive title
app = FastAPI(title="URL Shortener")

# This decorator tells FastAPI to run this function when the server starts up
@app.on_event("startup")
# An async function that runs during server startup to prepare the app
async def startup_event():
    # Initialize the database and load all existing URLs into memory cache
    database.init_db()
    # Print a confirmation message to let us know everything is ready
    print("Database initialized and cache loaded")


# This handles GET requests to the root path (/) - the welcome page
@app.get("/")
# Send back a simple welcome message when someone visits the root
def root():
    # Return a JSON response with a friendly welcome message
    return {"message": "Welcome to URL Shortener"}


# Health check endpoint - lets monitoring tools know the server is alive
@app.get("/health")
# Simple function to check if the server is running properly
def health():
    # Return a status showing everything is working fine
    return {"status": "ok"}


# Handle POST requests to create a shortened URL
@app.post("/shorten", response_model=URLResponse)
# Take a long URL from the user and return a shortened version
def shorten_url(data: URLRequest):
    # Generate a random 6-character code using letters and numbers
    code = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    # Save this new short code and its original URL to the database
    database.save_url(code, data.url)

    # Print the cache contents for debugging purposes
    print("Cache after save:", database.memory_cache)

    # Return the short code and original URL back to the user
    return URLResponse(short_code=code, original_url=data.url)


# Endpoint to retrieve all shortened URLs stored in the system
@app.get("/urls")
# Return a list of every shortened URL we have created
def list_urls():
    # Fetch and return a copy of all URLs from our database cache
    return database.get_all_urls()


# Endpoint to get detailed information about a specific shortened URL
@app.get("/info/{short_code}")
# Look up details about a URL using its short code
def url_info(short_code: str):
    # Search the database for the URL with this short code
    url_data = database.get_url(short_code)
    # If the short code doesn't exist, return a 404 error
    if not url_data:
        raise HTTPException(status_code=404, detail="Short code not found")

    # Return all the information we have about this URL
    return url_data


# Endpoint to delete a shortened URL from the system
@app.delete("/{short_code}")
# Remove a shortened URL using its short code
def delete_url(short_code: str):
    # Try to delete the URL from the database
    if not database.delete_url(short_code):
        # If it doesn't exist, return a 404 error
        raise HTTPException(status_code=404, detail="Short code not found")

    # Let the user know the deletion was successful
    return {"message": "Deleted successfully"}


# Main endpoint - when users visit a short URL, redirect them to the original
@app.get("/{short_code}")
# Handle the redirect when someone clicks a shortened URL
def redirect_url(short_code: str):
    # Print what's in our cache for debugging and troubleshooting
    print("Cache content:", database.memory_cache)

    # Look up the original URL using the short code
    url_data = database.get_url(short_code)
    # If the short code doesn't exist, return a 404 error
    if not url_data:
        raise HTTPException(status_code=404, detail="Short code not found")

    # Add 1 to the click counter to track how many times this URL was used
    database.increment_clicks(short_code)
    # Redirect the user to the original URL they shortened
    return RedirectResponse(url_data["original_url"])
