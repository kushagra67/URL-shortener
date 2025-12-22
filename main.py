# main text
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import random
import string

from models import URLRequest, URLResponse
import database

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
    database.save_url(code, data.url)

    print("DB AFTER SAVE:", database.url_database)

    return URLResponse(short_code=code, original_url=data.url)


@app.get("/urls")
def list_urls():
    return database.url_database


@app.get("/info/{short_code}")
def url_info(short_code: str):
    if short_code not in database.url_database:
        raise HTTPException(status_code=404, detail="Short code not found")

    return database.url_database[short_code]


@app.delete("/{short_code}")
def delete_url(short_code: str):
    if short_code not in database.url_database:
        raise HTTPException(status_code=404, detail="Short code not found")

    del database.url_database[short_code]
    return {"message": "Deleted successfully"}


@app.get("/{short_code}")
def redirect_url(short_code: str):
    print("DB CONTENT:", database.url_database)

    if short_code not in database.url_database:
        raise HTTPException(status_code=404, detail="Short code not found")

    database.url_database[short_code]["clicks"] += 1
    return RedirectResponse(database.url_database[short_code]["original_url"])
