from __future__ import annotations

import logging
import json
import sys
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
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


def sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"


@app.post("/api/chat/stream")
def chat_stream(request: ChatRequest) -> StreamingResponse:
    messages = [message.model_dump() for message in request.messages]

    def generate():
        yield sse_event("connected", {"conversation_id": request.conversation_id})
        for event in service.stream_chat(messages):
            event_type = event.get("type")
            if event_type == "round_started":
                yield sse_event("progress", {"message": f"Working through research round {event['round']}…", "round": event["round"]})
            elif event_type == "tool_completed":
                tool_name = event.get("tool", "research")
                success = bool(event.get("ok"))
                yield sse_event("progress", {
                    "message": f"{tool_name} {'completed' if success else 'failed'}",
                    "tool": tool_name,
                    "success": success,
                    "round": event.get("round"),
                })
            elif event_type == "completed":
                result = event["result"]
                text = result.get("assistant_text", "")
                for index in range(0, len(text), 48):
                    yield sse_event("delta", {"text": text[index:index + 48]})
                yield sse_event("done", {"conversation_id": request.conversation_id, **result})
            elif event_type == "error":
                yield sse_event("error", {"detail": "The chatbot encountered an internal error."})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/{asset_path:path}")
def static_assets(asset_path: str) -> FileResponse:
    candidate = (STATIC / asset_path).resolve()
    if STATIC not in candidate.parents or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(candidate)
