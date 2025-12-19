# main text
from fastapi import FastAPI
import random
import string

from models import URLRequest, URLResponse
from database import save_url

app = FastAPI(title="URL Shortener")


@app.get("/")
def root():
    return {"message": "Welcome to URL Shortener"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/shorten", response_model=URLResponse)
def shorten_url(data: URLRequest):
    code = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    save_url(code, data.url)
    return URLResponse(short_code=code, original_url=data.url)
