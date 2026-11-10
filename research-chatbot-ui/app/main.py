"""FastAPI entry point. Serves the API and the static frontend from one origin."""
import logging
import os
from pathlib import Path

from dotenv import load_dotenv  # already a dependency in most agent projects; remove if unused

load_dotenv()

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.chat import router as chat_router

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

STATIC_DIR = Path(__file__).parent / "static"

# Interactive docs are off unless ENABLE_DOCS=1 (keep off for public demos).
docs_on = os.getenv("ENABLE_DOCS", "0") == "1"
app = FastAPI(
    title="Research Chatbot",
    docs_url="/docs" if docs_on else None,
    redoc_url=None,
    openapi_url="/openapi.json" if docs_on else None,
)

app.include_router(chat_router)


@app.get("/health")
def health():
    return {"status": "ok"}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")
