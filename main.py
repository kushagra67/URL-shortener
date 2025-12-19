# main text
from fastapi import FastAPI

app = FastAPI(title="URL Shortener")


@app.get("/")
def root():
    return {"message": "Welcome to URL Shortener"}


@app.get("/health")
def health():
    return {"status": "ok"}
