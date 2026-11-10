"""Offline behavior and failure cases omitted by the original starter examples."""
from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest
import requests

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS


@pytest.mark.parametrize("response_type", ["text", "yes_no"])
def test_clarify_preserves_question_and_waits_without_choices(response_type):
    result = TOOL_FUNCTIONS["clarify"](question="Duyệt đúng bản này?", response_type=response_type)
    assert result["question"] == "Duyệt đúng bản này?"
    assert result["response_type"] == response_type
    assert result["options"] == []
    assert result["awaiting_user"] is True


def test_format_daily_digest_preserves_grouped_content_and_source_links():
    result = TOOL_FUNCTIONS["format"](items=[
        {"section": "Paper", "summary": "Kết quả", "url": "https://example.org/paper"},
        {"section": "Tin", "title": "Tin mới", "url": "https://example.org/news"},
    ], template="daily_ai_vn")
    assert "**Tin tức hôm nay**" in result["markdown"]
    assert "**Paper**" in result["markdown"] and "**Tin**" in result["markdown"]
    assert "[example.org](https://example.org/paper)" in result["markdown"]
    assert "Tin mới" in result["markdown"]


@pytest.mark.parametrize("name,key,kwargs", [
    ("fetch", "FIRECRAWL_API_KEY", {"url": "https://example.org/a"}),
    ("timeline", "RAPIDAPI_KEY", {"screenname": "researcher"}),
    ("social_search", "RAPIDAPI_KEY", {"query": "AI"}),
])
def test_read_tools_without_credentials_return_error_without_http(name, key, kwargs, fake_http):
    calls = fake_http(FakeResponse())
    result = TOOL_FUNCTIONS[name](**kwargs)
    assert result["error"] == "RuntimeError"
    assert key in result["message"]
    assert calls == []


@pytest.mark.parametrize("name,key,kwargs", [
    ("lookup", "TAVILY_API_KEY", {"query": "AI"}),
    ("fetch", "FIRECRAWL_API_KEY", {"url": "https://example.org/a"}),
    ("timeline", "RAPIDAPI_KEY", {"screenname": "researcher"}),
    ("social_search", "RAPIDAPI_KEY", {"query": "AI"}),
    ("send", "TELEGRAM_BOT_TOKEN", {"text": "Bản đã duyệt", "confirmed": True}),
])
@pytest.mark.parametrize("failure,expected", [
    (FakeResponse(status_code=503), "HTTPError"),
    (requests.Timeout("offline simulated timeout"), "Timeout"),
])
def test_http_tools_report_dependency_failures_instead_of_success(name, key, kwargs, failure, expected, monkeypatch, fake_http):
    monkeypatch.setenv(key, "test-key")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "test-channel")
    calls = fake_http(failure)
    result = TOOL_FUNCTIONS[name](**kwargs)
    assert result["error"] == expected
    assert result.get("status") != "sent"
    assert len(calls) == 1


@pytest.mark.parametrize("name,kwargs,payload", [
    ("lookup", {"query": "AI", "max_results": "not a number"}, {}),
    ("timeline", {"screenname": "researcher", "limit": "not a number"}, {"timeline": []}),
    ("social_search", {"query": "AI", "limit": "not a number"}, {"tweets": []}),
])
def test_numeric_argument_errors_return_error_dict(name, kwargs, payload, monkeypatch, fake_http):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    fake_http(FakeResponse(payload))
    assert TOOL_FUNCTIONS[name](**kwargs)["error"] == "ValueError"


@pytest.mark.parametrize("confirmed", [False, None, 0, 1, "false", "true"])
def test_send_requires_literal_boolean_true_before_any_network(confirmed, monkeypatch, fake_http):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-key")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "test-channel")
    calls = fake_http(FakeResponse({"ok": True}))
    result = TOOL_FUNCTIONS["send"](text="Do not publish without boolean approval", confirmed=confirmed)
    assert result["status"] == "needs_confirmation"
    assert calls == []


def test_policy_bad_document_returns_error_dict(monkeypatch, tmp_path):
    module = importlib.import_module("tools.policy.tool")
    (tmp_path / "bad.md").write_text("---\npolicy_area: [\n---\n## Rules\nCitation.", encoding="utf-8")
    monkeypatch.setattr(module, "POLICY_DIR", tmp_path)
    result = TOOL_FUNCTIONS["policy"](query="citation")
    assert result["error"] == "ParserError"
    assert not result.get("results")


ATOM_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <opensearch:totalResults>7</opensearch:totalResults>
  <entry>
    <id>https://arxiv.org/abs/2305.14314v2</id>
    <title>Paper title</title><summary>Line one
      line two</summary>
    <author><name>A. Author</name></author>
    <published>2023-05-23T00:00:00Z</published><updated>2023-06-01T00:00:00Z</updated>
    <link title="pdf" href="https://arxiv.org/pdf/2305.14314v2.pdf"/>
    <arxiv:primary_category term="cs.LG"/><category term="cs.LG"/>
  </entry>
</feed>"""


@pytest.fixture
def arxiv_without_sleep(monkeypatch):
    module = importlib.import_module("tools.papers.tool")
    monkeypatch.setattr(module, "_rate_limit_arxiv", lambda: None)
    monkeypatch.setattr(module.time, "sleep", lambda seconds: None)
    return module


@pytest.mark.parametrize("tool_name", ["papers", "arxiv_search"])
def test_arxiv_search_maps_atom_metadata_and_transmits_filters(tool_name, arxiv_without_sleep, monkeypatch, fake_http):
    monkeypatch.setenv("ARXIV_USER_AGENT", "offline-unit-test/1.0")
    calls = fake_http(FakeResponse(text=ATOM_FEED))
    result = TOOL_FUNCTIONS[tool_name](query="neural networks", author="A. Author", title="Paper",
        categories=["cs.LG"], date_from="2024-01-01", date_to="2024-12-31", start=5,
        max_results=2, sort_by="submittedDate", sort_order="ascending")
    assert len(calls) == 1
    request = calls[0]
    assert request["url"] == "https://export.arxiv.org/api/query"
    assert request["headers"]["User-Agent"] == "offline-unit-test/1.0"
    assert request["params"]["start"] == 5 and request["params"]["max_results"] == 2
    assert request["params"]["sortBy"] == "submittedDate"
    assert request["params"]["sortOrder"] == "ascending"
    query = request["params"]["search_query"]
    assert 'au:"A. Author"' in query and 'ti:"Paper"' in query
    assert "cat:cs.LG" in query and "202401010000 TO 202412312359" in query
    assert "all:neural" in query and "all:networks" in query
    assert result["total_results"] == 7
    paper = result["items"][0]
    assert paper["arxiv_id"] == "2305.14314v2"
    assert paper["title"] == "Paper title" and paper["summary"] == "Line one line two"
    assert paper["authors"] == ["A. Author"] and paper["primary_category"] == "cs.LG"
    assert paper["pdf_url"] == "https://arxiv.org/pdf/2305.14314v2.pdf"


def test_arxiv_search_clamps_pagination_and_defaults_invalid_sort(arxiv_without_sleep, fake_http):
    calls = fake_http(FakeResponse(text=ATOM_FEED))
    result = TOOL_FUNCTIONS["papers"](query="AI", start=-8, max_results=100, sort_by="invalid", sort_order="invalid")
    assert calls[0]["params"]["start"] == 0
    assert calls[0]["params"]["max_results"] == 50
    assert calls[0]["params"]["sortBy"] == "relevance"
    assert calls[0]["params"]["sortOrder"] == "descending"
    assert result["filters"]["start"] == 0 and result["filters"]["max_results"] == 50


@pytest.mark.parametrize("tool_name", ["papers", "arxiv_search"])
def test_arxiv_bad_numeric_input_returns_error_before_network(tool_name, arxiv_without_sleep, fake_http):
    calls = fake_http(FakeResponse(text=ATOM_FEED))
    result = TOOL_FUNCTIONS[tool_name](query="AI", max_results="not a number")
    assert result["error"] == "ValueError"
    assert calls == []


@pytest.mark.parametrize("response,expected", [
    (FakeResponse(status_code=503), "HTTPError"),
    (FakeResponse(text="not XML"), "ParseError"),
    (requests.Timeout("offline timeout"), "Timeout"),
])
def test_arxiv_search_dependency_errors_return_error_dict(response, expected, arxiv_without_sleep, fake_http):
    fake_http(response)
    assert TOOL_FUNCTIONS["papers"](query="AI")["error"] == expected


def test_arxiv_rate_limit_retries_are_bounded(arxiv_without_sleep, fake_http):
    calls = fake_http(FakeResponse(status_code=429))
    result = TOOL_FUNCTIONS["arxiv_search"](query="AI")
    assert result["error"] == "HTTPError"
    assert len(calls) == 3


@pytest.fixture
def paper_text_local(monkeypatch, tmp_path):
    module = importlib.import_module("tools.paper_text.tool")
    monkeypatch.setattr(module, "ARXIV_DIR", tmp_path / "pdfs")
    monkeypatch.setattr(module, "_rate_limit_arxiv", lambda: None)
    return module


@pytest.mark.parametrize("max_chars,expected_chars", [(20, 1000), (1500, 1500), (50000, 20000)])
def test_paper_text_writes_download_and_bounded_excerpt(max_chars, expected_chars, paper_text_local, monkeypatch, fake_http):
    raw_pdf = b"%PDF-offline-fixture"
    calls = fake_http(FakeResponse(content=raw_pdf))
    def extract(path, max_pages):
        assert path.read_bytes() == raw_pdf
        assert max_pages == 2
        return "Đ" * 25000, 8
    monkeypatch.setattr(paper_text_local, "_extract_pdf_text", extract)
    result = TOOL_FUNCTIONS["paper_text"](arxiv_url="https://arxiv.org/abs/2305.14314v2", max_pages=2, max_chars=max_chars)
    assert len(calls) == 1 and calls[0]["stream"] is True
    assert calls[0]["url"] == "https://arxiv.org/pdf/2305.14314v2.pdf"
    assert result["pages_read"] == 2 and result["page_count"] == 8
    assert result["chars_returned"] == expected_chars
    assert result["items"][0]["summary"] == "Đ" * expected_chars
    assert (paper_text_local.ARXIV_DIR / "2305.14314v2.txt").read_text(encoding="utf-8") == "Đ" * expected_chars
    assert result["url"] == "https://arxiv.org/abs/2305.14314v2"


def test_paper_text_invalid_id_does_not_download_or_create_files(paper_text_local, fake_http):
    calls = fake_http(FakeResponse())
    assert TOOL_FUNCTIONS["paper_text"](arxiv_url="not an arxiv ID")["error"] == "ValueError"
    assert calls == [] and not paper_text_local.ARXIV_DIR.exists()


@pytest.mark.parametrize("failure,expected", [(FakeResponse(status_code=404), "HTTPError"), (requests.Timeout("offline PDF timeout"), "Timeout")])
def test_paper_text_download_failure_has_no_success_excerpt(failure, expected, paper_text_local, fake_http):
    fake_http(failure)
    result = TOOL_FUNCTIONS["paper_text"](arxiv_url="2305.14314")
    assert result["error"] == expected
    assert not result.get("items")
    assert list(paper_text_local.ARXIV_DIR.glob("*.txt")) == []


def test_paper_text_malformed_pdf_returns_parser_error(paper_text_local, fake_http):
    fake_http(FakeResponse(content=b"this is not a PDF"))
    result = TOOL_FUNCTIONS["paper_text"](arxiv_url="2305.14314")
    assert result.get("error")
    assert not result.get("items")
    assert list(paper_text_local.ARXIV_DIR.glob("*.txt")) == []


def test_pdf_extraction_reads_only_requested_pages_and_ignores_empty_text(monkeypatch, tmp_path):
    import pypdf
    module = importlib.import_module("tools.paper_text.tool")
    pages = [SimpleNamespace(extract_text=lambda text=text: text) for text in ["First", None, "Third"]]
    monkeypatch.setattr(pypdf, "PdfReader", lambda path: SimpleNamespace(pages=pages))
    text, count = module._extract_pdf_text(tmp_path / "fixture.pdf", max_pages=2)
    assert text == "First" and count == 3


def test_research_paper_uses_first_discovered_id_for_pdf(monkeypatch):
    module = importlib.import_module("tools.research_paper.tool")
    paper = {"arxiv_id": "2305.14314", "title": "Actual result"}
    monkeypatch.setattr(module, "arxiv_search", lambda **kwargs: {"items": [paper], "total_results": 1})
    calls = []
    def read(**kwargs):
        calls.append(kwargs)
        return {"items": [{"summary": "Read from the selected result"}]}
    monkeypatch.setattr(module, "get_arxiv_paper_text", read)
    result = TOOL_FUNCTIONS["research_paper"](question="quantization", include_text=True)
    assert calls == [{"arxiv_url": "2305.14314", "max_pages": 5}]
    assert result["papers"] == [paper]
    assert result["paper_text"]["items"][0]["summary"] == "Read from the selected result"


def test_research_paper_search_error_does_not_invent_papers(monkeypatch):
    module = importlib.import_module("tools.research_paper.tool")
    monkeypatch.setattr(module, "arxiv_search", lambda **kwargs: {"error": "HTTPError", "message": "arXiv unavailable"})
    result = TOOL_FUNCTIONS["research_paper"](question="AI", include_text=True)
    assert result["error"] == "HTTPError" and result["papers"] == []
    assert "paper_text" not in result


def test_bibliography_plain_format_has_title_year_and_source():
    result = TOOL_FUNCTIONS["build_bibliography"](papers=[{"title": "Paper A", "year": 2023, "url": "https://example.org/a"}], format="plain")
    assert result["text"] == "1. Paper A (2023). https://example.org/a"
    assert "@misc" not in result["text"]


def test_bibliography_deduplicates_arxiv_versions_without_replacing_metadata():
    result = TOOL_FUNCTIONS["build_bibliography"](papers=[
        {"title": "Original", "arxiv_id": "2305.14314v1", "url": "https://arxiv.org/abs/2305.14314v1"},
        {"title": "Later", "arxiv_id": "2305.14314v2", "url": "https://arxiv.org/abs/2305.14314v2"},
    ])
    assert result["entry_count"] == 1 and result["duplicate_count"] == 1
    assert result["entries"][0]["title"] == "Original"
    assert "Later" not in result["text"]


@pytest.mark.parametrize("field,value", [("authors", "A. Author"), ("year", True), ("year", "unknown"), ("arxiv_id", "not an ID"), ("url", "https://user:password@example.org/a")])
def test_bibliography_invalid_metadata_is_not_turned_into_citation(field, value):
    paper = {"title": "Paper A", "url": "https://example.org/a", field: value}
    result = TOOL_FUNCTIONS["build_bibliography"](papers=[paper])
    assert result["error"] == "no_usable_papers"
    assert result["entries"] == [] and result["text"] == ""
    assert result["warnings"]
