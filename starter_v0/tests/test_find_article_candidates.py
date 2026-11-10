import pytest
import requests

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

search = TOOL_FUNCTIONS["find_article_candidates"]


def test_candidates_request_and_mapping(monkeypatch, fake_http):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": [
        {"title": "GPT-4", "url": "https://www.example.com/a", "content": "A report", "score": 0.8},
        {"title": "GPT-4 paper", "url": "https://example.org/b"},
    ]}))
    result = search(" GPT-4 report ", 2)
    assert calls[0]["url"] == "https://api.tavily.com/search"
    assert calls[0]["json"] == {"query": "GPT-4 report", "topic": "general", "max_results": 2, "search_depth": "basic"}
    assert calls[0]["allow_redirects"] is False
    assert result["item_count"] == 2
    assert result["items"][0] == {"title": "GPT-4", "url": "https://www.example.com/a", "source": "example.com", "summary": "A report", "score": 0.8}
    assert result["items"][1]["summary"] == ""


def test_empty_and_limit(monkeypatch, fake_http):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    fake_http(FakeResponse({"results": []}))
    assert search("known title")["items"] == []
    fake_http(FakeResponse({"results": [{"title": "one"}, {"title": "two"}]}))
    assert search("known title", 1)["item_count"] == 1


@pytest.mark.parametrize("description,limit", [(None, 5), ("", 5), ("  ", 5), (123, 5), ("title", 0), ("title", 11), ("title", True), ("title", "3")])
def test_bad_input_never_calls_api(monkeypatch, fake_http, description, limit):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse())
    assert search(description, limit)["error"] == "ValueError"
    assert calls == []


def test_missing_key_never_calls_api(fake_http):
    calls = fake_http(FakeResponse())
    assert search("known title")["error"] == "RuntimeError"
    assert calls == []


@pytest.mark.parametrize("response,error", [(FakeResponse(status_code=429), "HTTPError"), (FakeResponse(status_code=302), "ValueError"), (requests.Timeout("timeout"), "Timeout"), (FakeResponse({}), "ValueError")])
def test_api_failure_returns_error(monkeypatch, fake_http, response, error):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    fake_http(response)
    assert search("known title")["error"] == error
