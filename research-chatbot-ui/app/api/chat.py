"""POST /api/chat: validates input, delegates to the agent service."""
import logging
from typing import Any, Literal, Optional

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field, field_validator, model_validator

from app.services import agent_service

log = logging.getLogger("chat")
router = APIRouter(prefix="/api")

MAX_MESSAGES = 100
MAX_MESSAGE_CHARS = 8000
MAX_TOTAL_CHARS = 60000


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)

    @field_validator("content")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("content must not be blank")
        return v


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = Field(default=None, max_length=128)
    messages: list[ChatMessage] = Field(min_length=1, max_length=MAX_MESSAGES)

    @model_validator(mode="after")
    def check_history(self):
        if self.messages[-1].role != "user":
            raise ValueError("the latest message must have the 'user' role")
        if sum(len(m.content) for m in self.messages) > MAX_TOTAL_CHARS:
            raise ValueError("conversation is too large")
        return self


class ChatResponse(BaseModel):
    conversation_id: Optional[str] = None
    status: Literal["answered", "waiting_for_user", "max_tool_rounds"]
    assistant_text: str
    rounds: list[Any] = []
    tool_events: list[Any] = []


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    messages = [m.model_dump() for m in req.messages]
    try:
        result = await run_in_threadpool(agent_service.chat, messages)
    except Exception:
        # Full traceback server-side only; generic message to the browser.
        log.exception("Agent execution failed (conversation_id=%s)", req.conversation_id)
        raise HTTPException(status_code=500, detail="The chatbot encountered an internal error.")
    return ChatResponse(conversation_id=req.conversation_id, **result)
