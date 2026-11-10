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


def test_saved_pass_is_adapted_for_ui_instead_of_showing_false_fail(monkeypatch, tmp_path):
    import json
    from app import benchmark_service
    monkeypatch.setattr(benchmark_service, "RUNS_ROOT", tmp_path)
    payload = {"version": "old-label", "summary": {"total_cases": 1, "measured_cases": 1, "provider_error_cases": 0}, "results": [{
        "id": "case-a", "input": "A request", "expect": {"no_tool": True},
        "result": {"passed": True, "actual_tool_calls": [], "actual_text": "Answer"}, "tool_results": [],
    }]}
    (tmp_path / "v4_B_base_example.json").write_text(json.dumps(payload), encoding="utf8")
    result = client.get("/api/benchmark/runs/v4_B_base_example.json?case_id=case-a").json()
    assert result["evaluation"]["passed"] is True
    assert result["actual"]["assistant_text"] == "Answer"
    assert result["case"]["id"] == "case-a"
    assert result["run_metadata"]["original_version"] == "old-label"


def test_saved_failure_and_tool_error_remain_visible(monkeypatch, tmp_path):
    import json
    from app import benchmark_service
    monkeypatch.setattr(benchmark_service, "RUNS_ROOT", tmp_path)
    payload = {"summary": {}, "results": [{"id": "bad", "result": {
        "passed": False, "actual_tool_calls": [{"name": "lookup", "args": {"query": "AI"}}],
        "failures": ["extra tool call lookup"],
    }, "tool_results": [{"tool": "lookup", "args": {}, "result": {"error": "Timeout"}}]}]}
    (tmp_path / "bad.json").write_text(json.dumps(payload), encoding="utf8")
    result = client.get("/api/benchmark/runs/bad.json").json()
    assert result["evaluation"]["passed"] is False
    assert result["evaluation"]["failures"] == ["extra tool call lookup"]
    assert result["actual"]["tool_events"][0]["result"]["status"] == "failed"


def test_saved_run_list_excludes_fixtures_and_shows_filename_version(monkeypatch, tmp_path):
    import json
    from app import benchmark_service
    monkeypatch.setattr(benchmark_service, "RUNS_ROOT", tmp_path)
    (tmp_path / "fixture.json").write_text('{"cases": []}', encoding="utf8")
    (tmp_path / "v5_B_base_example.json").write_text(json.dumps({"version": "v4", "summary": {"measured_cases": 1}, "results": []}), encoding="utf8")
    runs = client.get("/api/benchmark/runs").json()["runs"]
    assert len(runs) == 1
    assert runs[0]["version"] == "v5" and runs[0]["original_version"] == "v4"


def test_loop_reports_tool_called_when_final_round_has_no_new_calls():
    from chat import run_model_tool_loop
    from providers.base import ToolCall
    class Provider:
        count = 0
        def complete(self, *args, **kwargs):
            self.count += 1
            return ModelResponse(text="Done", tool_calls=[] if self.count > 1 else [ToolCall("format", {"items": [], "template": "brief"})])
    result = run_model_tool_loop(provider=Provider(), messages=[], tools=[], model=None, max_tool_rounds=3)
    assert result["execution_status"] == "tool_called"
    assert len(result["tool_events"]) == 1
