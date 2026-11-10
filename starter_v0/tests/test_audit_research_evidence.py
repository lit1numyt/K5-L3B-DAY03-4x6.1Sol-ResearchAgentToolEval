from tools.audit_research_evidence.tool import audit_research_evidence


def test_reports_linked_results_from_search_and_papers():
    result = audit_research_evidence(results=[
        {"tool": "web_search", "items": [{"title": "Web", "url": "https://example.org/a"}]},
        {"tool": "research_paper", "papers": [{"summary": "Abstract", "url": "https://arxiv.org/abs/1234.5678"}]},
    ])
    assert [source["status"] for source in result["sources"]] == ["ok", "ok"]
    assert result["unique_item_count"] == 2
    assert result["items"][1]["url"] == "https://arxiv.org/abs/1234.5678"


def test_distinguishes_empty_response_from_api_error():
    result = audit_research_evidence(results=[
        {"tool": "timeline", "items": []},
        {"tool": "arxiv_search", "error": "ReadTimeout", "message": "timed out"},
    ])
    assert [source["status"] for source in result["sources"]] == ["empty", "error"]
    assert result["sources"][1]["error"] == "ReadTimeout"
    assert result["unique_item_count"] == 0


def test_reports_partial_error_without_discarding_real_items():
    result = audit_research_evidence(results=[{"tool": "research_paper", "error": "ReadTimeout", "papers": [
        {"title": "Paper", "url": "https://arxiv.org/abs/1234.5678"},
    ]}])
    assert result["sources"][0]["status"] == "partial"
    assert result["unique_item_count"] == 1


def test_accepts_actual_chat_loop_event_wrappers():
    result = audit_research_evidence(results=[
        {"tool": "timeline", "args": {"screenname": "elonmusk"}, "result": {"tool": "get_user_tweets", "items": []}},
        {"tool": "arxiv_search", "args": {}, "result": {"tool": "arxiv_search", "error": "ReadTimeout"}},
    ])
    assert [source["tool"] for source in result["sources"]] == ["timeline", "arxiv_search"]
    assert [source["status"] for source in result["sources"]] == ["empty", "error"]


def test_deduplicates_across_sources_without_collapsing_distinct_queries():
    result = audit_research_evidence(results=[{"tool": "web_search", "items": [
        {"title": "One", "url": "https://example.org/a?x=1#part"},
        {"title": "Duplicate", "url": "https://EXAMPLE.org/a?x=1"},
        {"title": "Different", "url": "https://example.org/a?x=2"},
    ]}])
    assert result["unique_item_count"] == 2
    assert result["duplicate_item_count"] == 1


def test_counts_bad_items_without_creating_sources():
    result = audit_research_evidence(results=[{"tool": "timeline", "items": [
        {"summary": "Missing link"}, {"url": "javascript:alert(1)", "title": "Unsafe"},
        {"url": "https://example.org/no-content"}, "invalid",
    ]}])
    assert result["sources"][0]["status"] == "unusable"
    assert result["sources"][0]["unusable_item_count"] == 4
    assert result["items"] == []


def test_rejects_missing_or_malformed_input():
    assert audit_research_evidence(results=[])['error'] == 'invalid_input'
    assert audit_research_evidence(results='bad')['error'] == 'invalid_input'
    result = audit_research_evidence(results=[{}, {"tool": "lookup", "items": "bad"}, None])
    assert [source["status"] for source in result["sources"]] == ["invalid", "invalid", "invalid"]
