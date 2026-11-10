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
from app.benchmark_service import list_cases, list_saved_runs, read_saved_run, run_case  # noqa: E402
from app.public_data import public_result, public_tool_event, public_value  # noqa: E402


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


@app.get("/api/meta")
def meta() -> dict:
    return service.metadata()


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict:
    try:
        result = service.chat([message.model_dump() for message in request.messages])
    except Exception:
        logger.exception("Research agent request failed")
        raise HTTPException(status_code=500, detail="The chatbot encountered an internal error.")
    return {"conversation_id": request.conversation_id, **public_result(result), "run_metadata": service.metadata()}


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
            elif event_type == "tool_started":
                yield sse_event("tool", {
                    "round": event.get("round"),
                    "call_index": event.get("call_index"),
                    "tool": event.get("tool"),
                    "args": public_value(event.get("args", {})),
                    "status": "running",
                })
            elif event_type == "tool_completed":
                tool_name = event.get("tool", "research")
                status = event.get("status", "failed")
                yield sse_event("tool", {
                    "message": f"{tool_name} {status}",
                    "tool": tool_name,
                    "args": public_value(event.get("args", {})),
                    "status": status,
                    "error": f"{event.get('error')}: the tool could not complete this request." if status == "failed" else None,
                    "round": event.get("round"),
                    "call_index": event.get("call_index"),
                })
            elif event_type == "no_tool_called":
                yield sse_event("execution", {"status": "no_tool_called", "message": "No tool called."})
            elif event_type == "completed":
                result = public_result(event["result"])
                text = result.get("assistant_text", "")
                for index in range(0, len(text), 48):
                    yield sse_event("delta", {"text": text[index:index + 48]})
                yield sse_event("done", {"conversation_id": request.conversation_id, **result, "run_metadata": service.metadata()})
            elif event_type == "error":
                yield sse_event("error", {"detail": "The provider or agent failed before the turn completed. Tool activity shown above is the known activity."})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/benchmark/cases")
def benchmark_cases(dataset: str = "base") -> dict:
    try:
        return list_cases(dataset)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/api/benchmark/run")
def benchmark_run(payload: dict) -> dict:
    dataset = payload.get("dataset", "base")
    case_id = payload.get("case_id")
    if not isinstance(case_id, str) or not case_id:
        raise HTTPException(status_code=422, detail="case_id is required")
    try:
        return run_case(dataset, case_id, service)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception:
        logger.exception("Benchmark request failed")
        raise HTTPException(status_code=500, detail="The benchmark could not be completed.")


@app.get("/api/benchmark/runs")
def benchmark_runs() -> dict:
    return {"runs": list_saved_runs()}


@app.get("/api/benchmark/runs/{run_name:path}")
def benchmark_saved_run(run_name: str) -> dict:
    try:
        return read_saved_run(run_name)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/{asset_path:path}")
def static_assets(asset_path: str) -> FileResponse:
    candidate = (STATIC / asset_path).resolve()
    if STATIC not in candidate.parents or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(candidate)
