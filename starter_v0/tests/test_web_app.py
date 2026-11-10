from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app, service
from providers.base import ModelResponse


client = TestClient(app)


def request_payload() -> dict:
    return {"conversation_id": "test", "messages": [{"role": "user", "content": "Find papers"}]}


def test_stream_success_includes_real_tool_and_arguments(monkeypatch):
    monkeypatch.setattr(service, "stream_chat", lambda messages: iter([
        {"type": "round_started", "round": 1},
        {"type": "tool_started", "round": 1, "call_index": 1, "tool": "lookup", "args": {"query": "AI", "topic": "news"}},
        {"type": "tool_completed", "round": 1, "call_index": 1, "tool": "lookup", "args": {"query": "AI", "topic": "news"}, "status": "succeeded"},
        {"type": "completed", "result": {"status": "answered", "execution_status": "tool_called", "assistant_text": "Here are the findings.", "rounds": [], "tool_events": [{"tool": "lookup", "args": {"query": "AI"}, "result": {"status": "succeeded"}}]}},
    ]))
    response = client.post("/api/chat/stream", json=request_payload())
    assert response.status_code == 200
    assert '"status": "running"' in response.text
    assert '"status": "succeeded"' in response.text
    assert '"query": "AI"' in response.text


def test_stream_failed_tool_is_visible(monkeypatch):
    monkeypatch.setattr(service, "stream_chat", lambda messages: iter([
        {"type": "tool_started", "round": 1, "call_index": 1, "tool": "lookup", "args": {"query": "AI"}},
        {"type": "tool_completed", "round": 1, "call_index": 1, "tool": "lookup", "args": {"query": "AI"}, "status": "failed", "error": "Timeout"},
        {"type": "error", "message": "provider failed after tool"},
    ]))
    response = client.post("/api/chat/stream", json=request_payload())
    assert '"status": "failed"' in response.text
    assert "known activity" in response.text
    assert "Timeout" in response.text


def test_stream_no_tool_called_is_explicit(monkeypatch):
    monkeypatch.setattr(service, "stream_chat", lambda messages: iter([
        {"type": "no_tool_called", "round": 1},
        {"type": "completed", "result": {"status": "answered", "execution_status": "no_tool_called", "assistant_text": "I am a research agent.", "rounds": [], "tool_events": []}},
    ]))
    response = client.post("/api/chat/stream", json=request_payload())
    assert "No tool called." in response.text


def test_stream_waiting_state_is_distinct(monkeypatch):
    monkeypatch.setattr(service, "stream_chat", lambda messages: iter([
        {"type": "tool_started", "round": 1, "call_index": 1, "tool": "clarify", "args": {"question": "Which account?"}},
        {"type": "tool_completed", "round": 1, "call_index": 1, "tool": "clarify", "args": {"question": "Which account?"}, "status": "waiting"},
        {"type": "completed", "result": {"status": "waiting_for_user", "execution_status": "waiting_for_user", "assistant_text": "Which account?", "rounds": [], "tool_events": [{"tool": "clarify", "args": {}, "result": {"status": "waiting", "message": "Which account?"}}]}},
    ]))
    response = client.post("/api/chat/stream", json=request_payload())
    assert '"status": "waiting"' in response.text
    assert "waiting_for_user" in response.text


def test_stream_preserves_multiple_tool_order(monkeypatch):
    events = [
        {"type": "tool_started", "round": 1, "call_index": 1, "tool": "lookup", "args": {"query": "AI"}},
        {"type": "tool_completed", "round": 1, "call_index": 1, "tool": "lookup", "args": {"query": "AI"}, "status": "succeeded"},
        {"type": "tool_started", "round": 1, "call_index": 2, "tool": "social_search", "args": {"query": "AI"}},
        {"type": "tool_completed", "round": 1, "call_index": 2, "tool": "social_search", "args": {"query": "AI"}, "status": "succeeded"},
        {"type": "completed", "result": {"status": "answered", "execution_status": "tool_called", "assistant_text": "Done", "rounds": [], "tool_events": []}},
    ]
    monkeypatch.setattr(service, "stream_chat", lambda messages: iter(events))
    response = client.post("/api/chat/stream", json=request_payload())
    assert response.text.index("lookup") < response.text.index("social_search")


def test_benchmark_expected_vs_actual_is_evaluated(monkeypatch):
    class NoToolProvider:
        default_model = "mock-model"

        def complete(self, messages, tools=None, *, model=None, temperature=0.0, tool_choice=None):
            return ModelResponse(text="I can answer generally.", tool_calls=[])

    monkeypatch.setattr(service, "_provider", NoToolProvider())
    response = client.post("/api/benchmark/run", json={"dataset": "base", "case_id": "R03_web_news_routing"})
    payload = response.json()
    assert response.status_code == 200
    assert payload["benchmark_evaluated"] is True
    assert payload["evaluation"]["passed"] is False
    assert payload["evaluation"]["failures"]
    assert payload["actual"]["tool_calls"] == []


def test_benchmark_cases_expose_demo_scenarios():
    payload = client.get("/api/benchmark/cases?dataset=base").json()
    ids = {case["id"] for case in payload["cases"]}
    assert {"R03_web_news_routing", "R09_no_tool_capability", "R10_missing_handle", "R12_confirm_before_send", "M06_switch_tool"}.issubset(ids)


def test_index_exposes_chat_and_benchmark_modes():
    response = client.get("/")
    assert response.status_code == 200
    assert "Benchmark lab" in response.text
    assert "/css/benchmark.css" in response.text
