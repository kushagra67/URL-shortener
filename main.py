# main text
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import random
import string

from models import URLRequest, URLResponse
from database import save_url, url_database

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


@app.get("/{short_code}")
def redirect_url(short_code: str):
    if short_code not in url_database:
        raise HTTPException(status_code=404, detail="Short code not found")

    url_database[short_code]["clicks"] += 1
    return RedirectResponse(url_database[short_code]["original_url"])
