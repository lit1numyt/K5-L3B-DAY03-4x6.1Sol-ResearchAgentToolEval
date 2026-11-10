"""Regression coverage for grading audit payloads, not just tool names."""
import json
from pathlib import Path

from run_eval import compare_subset, evaluate_phase_b, normalize_value


def test_audit_payload_comparison_accepts_identical_object_arrays():
    results = [{"tool": "timeline", "items": []}, {"tool": "arxiv_search", "error": "ReadTimeout"}]
    assert compare_subset({"results": results}, {"results": results}) == (True, [], 1, 1)


def test_audit_payload_wrong_source_fails_without_provider_error():
    case = {"failure_type": "wrong_arg_value", "expect": {"tool_calls": [{
        "name": "audit_research_evidence", "args": {"results": [{"tool": "timeline", "items": []}]},
    }]}}
    actual = [{"name": "audit_research_evidence", "args": {"results": [{"tool": "timeline", "items": [
        {"title": "Invented", "url": "https://example.org/invented"},
    ]}]}}]
    result = evaluate_phase_b(case, actual, None)
    assert not result["passed"]
    assert result["observed_mismatch"] == "wrong_arg_value"


def test_existing_scalar_list_normalization_stays_order_independent():
    assert normalize_value([" B ", "a"]) == ["a", "b"]


def test_group_suite_has_ten_unique_cases_with_required_fields():
    root = Path(__file__).resolve().parents[1]
    cases = json.loads((root / "data/eval_group.json").read_text(encoding="utf8"))["cases"]
    assert len(cases) == len({case["id"] for case in cases}) == 10
    assert sum("query" in case for case in cases) == 5
    assert sum("turns" in case for case in cases) == 5
    for case in cases:
        assert case["phase"] == "B"
        assert bool(case.get("query")) != bool(case.get("turns"))
        assert case["metadata"]["what_it_tests"].strip()
        assert case["expect"].get("no_tool") or case["expect"].get("tool_calls")
