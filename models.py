#models text
from pydantic import BaseModel, validators
from typing import Optional
import validators


class URLRequest(BaseModel):
    url: str
    custom_code: Optional[str] = None

    @validators("url")
    def validate_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        if not validators.url(v):
            raise ValueError("Invalid URL")
        return v


class URLResponse(BaseModel):
    short_code: str
    original_url: str
