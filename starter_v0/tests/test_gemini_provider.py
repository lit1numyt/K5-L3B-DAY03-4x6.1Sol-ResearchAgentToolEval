"""Exercise Gemini SDK serialization without network requests or real API keys."""
import copy
import json
from pathlib import Path

import httpx
import pytest
from google import genai
from google.genai import types

from providers.gemini_provider import GeminiProvider
from tools import load_tool_declarations, to_openai_tools


@pytest.fixture
def gemini_requests(monkeypatch):
    captured = []

    def respond(request):
        captured.append(json.loads(request.content))
        return httpx.Response(200, json={"candidates": [{"content": {
            "role": "model", "parts": [{"text": "Ready."}, {"functionCall": {
                "name": "clarify",
                "args": {"question": "Proceed?", "response_type": "yes_no"},
            }}],
        }}]})

    real_client = genai.Client

    def offline_client(*, api_key):
        return real_client(api_key=api_key, http_options=types.HttpOptions(
            client_args={"transport": httpx.MockTransport(respond)},
        ))

    monkeypatch.setenv("GEMINI_API_KEY", "offline-test-key")
    monkeypatch.setattr(genai, "Client", offline_client)
    return captured


@pytest.mark.parametrize("wrapped", [False, True])
def test_full_tool_schemas_survive_gemini_serialization(gemini_requests, wrapped):
    path = Path(__file__).resolve().parents[1] / "artifacts/tools_v8.yaml"
    declarations = load_tool_declarations(path)
    tools = to_openai_tools(declarations) if wrapped else declarations
    original = copy.deepcopy(tools)

    response = GeminiProvider().complete([
        {"role": "system", "content": "Research assistant."},
        {"role": "user", "content": "Prepare a Telegram post; do not send yet."},
    ], tools, model="offline-model")

    assert len(gemini_requests) == 1
    request = gemini_requests[0]
    sent = request["tools"][0]["functionDeclarations"]
    assert len(sent) == len(declarations) == 14
    for actual, expected in zip(sent, declarations):
        assert actual["name"] == expected["name"]
        assert actual["description"] == expected["description"]
        assert "parameters" not in actual
        # SDK versions use either the JSON alias or the protobuf field name.
        schema = actual.get("parametersJsonSchema", actual.get("parameters_json_schema"))
        assert schema == expected["parameters"]
    audit = next(tool for tool in sent if tool["name"] == "audit_research_evidence")
    schema = audit.get("parametersJsonSchema", audit.get("parameters_json_schema"))
    assert schema["properties"]["results"]["items"]["additionalProperties"] is True
    assert tools == original
    assert response.text == "Ready."
    assert [(call.name, call.args) for call in response.tool_calls] == [
        ("clarify", {"question": "Proceed?", "response_type": "yes_no"}),
    ]


def test_gemini_request_without_tools_omits_declarations(gemini_requests):
    GeminiProvider().complete([{"role": "user", "content": "Hello."}], model="offline-model")

    assert len(gemini_requests) == 1
    assert "tools" not in gemini_requests[0]
