from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.agent_service import AgentService  # noqa: E402


logger = logging.getLogger("research_chatbot")
STATIC = Path(__file__).parent / "static"
app = FastAPI(title="Research Chatbot", version="1.0.0", docs_url="/docs", redoc_url=None)
service = AgentService()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=12_000)

    @field_validator("content")
    @classmethod
    def content_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("content must not be blank")
        return value


class ChatRequest(BaseModel):
    conversation_id: str | None = Field(default=None, max_length=128)
    messages: list[ChatMessage] = Field(min_length=1, max_length=100)

    @field_validator("messages")
    @classmethod
    def latest_message_is_user(cls, value: list[ChatMessage]) -> list[ChatMessage]:
        if value[-1].role != "user":
            raise ValueError("the latest message must have role 'user'")
        return value


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict:
    try:
        result = service.chat([message.model_dump() for message in request.messages])
    except Exception:
        logger.exception("Research agent request failed")
        raise HTTPException(status_code=500, detail="The chatbot encountered an internal error.")
    return {"conversation_id": request.conversation_id, **result}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/{asset_path:path}")
def static_assets(asset_path: str) -> FileResponse:
    candidate = (STATIC / asset_path).resolve()
    if STATIC not in candidate.parents or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(candidate)
