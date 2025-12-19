#models text
from pydantic import BaseModel
from typing import Optional


class URLRequest(BaseModel):
    url: str
    custom_code: Optional[str] = None


class URLResponse(BaseModel):
    short_code: str
    original_url: str
