from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import random
import string

from models import URLRequest, URLResponse
import database

app = FastAPI(title="URL Shortener")

@app.on_event("startup")
async def startup_event():
    database.init_db()
    print("Database initialized and cache loaded")


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

    print("Cache after save:", database.memory_cache)

    return URLResponse(short_code=code, original_url=data.url)


@app.get("/urls")
def list_urls():
    return database.get_all_urls()


@app.get("/info/{short_code}")
def url_info(short_code: str):
    url_data = database.get_url(short_code)
    if not url_data:
        raise HTTPException(status_code=404, detail="Short code not found")

    return url_data


@app.delete("/{short_code}")
def delete_url(short_code: str):
    if not database.delete_url(short_code):
        raise HTTPException(status_code=404, detail="Short code not found")

    return {"message": "Deleted successfully"}


@app.get("/{short_code}")
def redirect_url(short_code: str):
    print("Cache content:", database.memory_cache)

    url_data = database.get_url(short_code)
    if not url_data:
        raise HTTPException(status_code=404, detail="Short code not found")

    database.increment_clicks(short_code)
    return RedirectResponse(url_data["original_url"])
