#models text
# Import BaseModel and field_validator from Pydantic for data validation
from pydantic import BaseModel, field_validator
# Import Optional to allow fields that can be None or have a value
from typing import Optional
# Import validators library to check if URLs are valid
import validators


# Define the data structure for URL requests from users
class URLRequest(BaseModel):
    # The long URL that the user wants to shorten
    url: str
    # Optional: users can provide their own short code instead of a random one
    custom_code: Optional[str] = None

    # This decorator runs automatic validation on the 'url' field
    @field_validator("url")
    # Define a custom validation method for the URL
    def validate_url(cls, v):
        # Check that the URL starts with http:// or https:// (required for web URLs)
        if not v.startswith(("http://", "https://")):
            # If not, raise an error with a helpful message
            raise ValueError("URL must start with http:// or https://")
        # Use the validators library to check if it's a valid URL format
        if not validators.url(v):
            # If the URL format is invalid, raise an error
            raise ValueError("Invalid URL")
        # If all checks pass, return the URL as-is
        return v


# Define the data structure for responses sent back to users
class URLResponse(BaseModel):
    # The shortened code (like "abc123") that represents the long URL
    short_code: str
    # The original long URL that was shortened
    original_url: str
