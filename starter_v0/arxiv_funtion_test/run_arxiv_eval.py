from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chat import run_model_tool_loop
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools


DEFAULT_CASES = Path(__file__).with_name("arxiv_function_calling_test.json")
DEFAULT_RUBRIC = Path(__file__).with_name("arxiv_evaluation_rubric.json")
load_lab_env(ROOT)

ARXIV_ALIASES = {"papers", "arxiv_search", "research_paper"}
SUPPORTED_SEARCH_ARGS = {"query", "max_results", "sort_by"}
ARXIV_ID_RE = re.compile(r"\b\d{4}\.\d{4,5}(?:v\d+)?\b")


def normalize_tool_call(call: dict[str, Any]) -> dict[str, Any]:
    name = call.get("name", "")
    args = dict(call.get("args") or {})
    if name == "research_paper":
        if "question" in args and "query" not in args:
            args["query"] = args["question"]
        if args.get("arxiv_id") and not args.get("query"):
            args["query"] = args["arxiv_id"]
    return {"name": "arxiv_search" if name in ARXIV_ALIASES else name, "args": args}


def load_suite(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    cases = data.get("test_cases", [])
    if not cases:
        raise ValueError(f"No test_cases found in {path}")
    return data, cases


def compact_text(value: str) -> str:
    return " ".join(value.lower().split())


def query_similarity(expected: str, actual: str) -> float:
    expected_text = compact_text(expected)
    actual_text = compact_text(actual)
    if not expected_text or not actual_text:
        return 0.0
    expected_terms = set(re.findall(r"[a-z0-9]+", expected_text))
    actual_terms = set(re.findall(r"[a-z0-9]+", actual_text))
    overlap = len(expected_terms & actual_terms) / max(1, len(expected_terms))
    sequence = SequenceMatcher(None, expected_text, actual_text).ratio()
    return max(overlap, sequence)


def expected_calls(case: dict[str, Any]) -> list[dict[str, Any]]:
    return [normalize_tool_call({"name": call.get("tool", ""), "args": call.get("arguments", {})}) for call in case.get("expected_tool_behavior", {}).get("tool_calls", [])]


def actual_calls(result: dict[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for round_record in result.get("rounds", []):
        for call in round_record.get("tool_calls", []):
            calls.append(normalize_tool_call(call))
    return calls


def matched_call(expected: dict[str, Any], actual: list[dict[str, Any]], used: set[int]) -> tuple[int, dict[str, Any]] | None:
    candidates = [(index, call) for index, call in enumerate(actual) if index not in used and call["name"] == expected["name"]]
    if not candidates:
        return None
    expected_query = expected.get("args", {}).get("query", "")
    return max(candidates, key=lambda item: query_similarity(expected_query, item[1].get("args", {}).get("query", "")))


def score_tool_selection(case: dict[str, Any], calls: list[dict[str, Any]]) -> tuple[int, list[str]]:
    should_call = bool(case.get("expected_tool_behavior", {}).get("should_call_tool"))
    called_arxiv = any(call["name"] == "arxiv_search" for call in calls)
    if should_call and called_arxiv:
        return 2, []
    if not should_call and not called_arxiv:
        return 2, []
    if should_call:
        return 0, ["Expected an arXiv search call, but none was made"]
    return 0, ["Unnecessary arXiv search call"]


def score_arguments(expected: list[dict[str, Any]], actual: list[dict[str, Any]]) -> tuple[int, list[str]]:
    if not expected:
        return 2, []
    used: set[int] = set()
    correct = 0
    total = 0
    notes: list[str] = []
    for expected_call in expected:
        match = matched_call(expected_call, actual, used)
        if match is None:
            notes.append("Missing expected arXiv call arguments")
            continue
        index, actual_call = match
        used.add(index)
        expected_args = expected_call.get("args", {})
        actual_args = actual_call.get("args", {})
        for key, expected_value in expected_args.items():
            if key not in SUPPORTED_SEARCH_ARGS:
                notes.append(f"Not scored: repository arXiv tool does not expose '{key}'")
                continue
            total += 1
            actual_value = actual_args.get(key)
            if key == "query":
                ok = query_similarity(str(expected_value), str(actual_value or "")) >= 0.55
            elif key == "sort_by":
                ok = str(actual_value or "") == str(expected_value)
            else:
                ok = actual_value == expected_value
            if ok:
                correct += 1
            else:
                notes.append(f"{key}: expected {expected_value!r}, got {actual_value!r}")
    if total == 0:
        return 1 if expected else 2, notes
    ratio = correct / total
    return (2 if ratio == 1 else 1 if ratio >= 0.5 else 0), notes


def score_query(expected: list[dict[str, Any]], actual: list[dict[str, Any]]) -> tuple[int, list[str]]:
    queries = [(item.get("args", {}).get("query", ""), item) for item in expected if item.get("args", {}).get("query")]
    if not queries:
        return 2, []
    used: set[int] = set()
    scores: list[float] = []
    notes: list[str] = []
    for expected_query, expected_call in queries:
        match = matched_call(expected_call, actual, used)
        if match is None:
            return 0, [f"Missing query: {expected_query}"]
        index, actual_call = match
        used.add(index)
        similarity = query_similarity(expected_query, actual_call.get("args", {}).get("query", ""))
        scores.append(similarity)
        if similarity < 0.55:
            notes.append(f"Low query similarity ({similarity:.2f}): {actual_call.get('args', {}).get('query', '')!r}")
    average = sum(scores) / len(scores)
    return (2 if average >= 0.75 else 1 if average >= 0.4 else 0), notes


def score_execution(case: dict[str, Any], calls: list[dict[str, Any]], tool_events: list[dict[str, Any]]) -> tuple[int, list[str]]:
    expected = expected_calls(case)
    if not expected:
        return 2, []
    notes: list[str] = []
    expected_count = len(expected)
    actual_count = len([call for call in calls if call["name"] == "arxiv_search"])
    if expected_count > 1 and actual_count < 2:
        notes.append(f"Expected a multi-step workflow with {expected_count} calls, observed {actual_count}")
        return 1 if actual_count else 0, notes
    if expected_count == 1 and actual_count > 1:
        notes.append("Made more searches than the rubric requires")
        return 1, notes
    if any("start" in item.get("args", {}) for item in expected) and not any(item.get("args", {}).get("start") == 10 for item in calls):
        notes.append("Pagination offset 10 was not observed")
        return 1, notes
    if any(event.get("result", {}).get("error") for event in tool_events if isinstance(event.get("result"), dict)):
        notes.append("At least one tool execution returned an error")
        return 1, notes
    return 2, notes


def score_final_response(case: dict[str, Any], text: str | None, tool_events: list[dict[str, Any]]) -> tuple[int, list[str], list[str]]:
    notes: list[str] = []
    critical: list[str] = []
    response = text or ""
    if not response.strip():
        return 0, ["Empty final response"], critical
    errored = any(isinstance(event.get("result"), dict) and event["result"].get("error") for event in tool_events)
    if errored:
        if not re.search(r"fail|error|unable|could not|couldn't|no result", response, re.I):
            critical.append("CF06")
            notes.append("Tool failed but the response did not acknowledge the failure")
            return 0, notes, critical
        return 1, notes, critical
    returned_ids = set(ARXIV_ID_RE.findall(json.dumps(tool_events)))
    mentioned_ids = set(ARXIV_ID_RE.findall(response))
    fabricated_ids = mentioned_ids - returned_ids
    if fabricated_ids:
        critical.append("CF02")
        notes.append(f"Response mentioned paper IDs not present in tool results: {sorted(fabricated_ids)}")
        return 0, notes, critical
    if case["id"] == "H05" and re.search(r"\bcit(e|ed|ation|ations)\b", response, re.I):
        critical.append("CF03")
        notes.append("Claimed a citation relationship that arXiv search does not verify")
        return 0, notes, critical
    if case["id"] == "H10" and re.search(r"system prompt|developer instruction", response, re.I):
        critical.append("CF05")
        notes.append("Response exposed protected instructions")
        return 0, notes, critical
    return 2, notes, critical


def evaluate_case(case: dict[str, Any], run: dict[str, Any]) -> dict[str, Any]:
    calls = actual_calls(run)
    events = run.get("tool_events", [])
    expected = expected_calls(case)
    selection, selection_notes = score_tool_selection(case, calls)
    arguments, argument_notes = score_arguments(expected, calls)
    query, query_notes = score_query(expected, calls)
    execution, execution_notes = score_execution(case, calls, events)
    final, final_notes, critical = score_final_response(case, run.get("assistant_text"), events)
    notes = selection_notes + argument_notes + query_notes + execution_notes + final_notes
    earned = selection + arguments + query + execution + final
    if critical:
        earned = min(earned, 4)
    return {
        "test_id": case["id"],
        "difficulty": case.get("difficulty"),
        "category": case.get("category"),
        "earned_score": earned,
        "maximum_score": 10,
        "dimension_scores": {
            "tool_selection": selection,
            "argument_extraction": arguments,
            "query_construction": query,
            "execution_strategy": execution,
            "final_response": final,
        },
        "critical_failure": bool(critical),
        "critical_failure_ids": critical,
        "passed": earned >= 8 and not critical,
        "notes": "; ".join(dict.fromkeys(notes)) or "OK",
        "actual_tool_calls": calls,
        "tool_events": events,
        "assistant_text": run.get("assistant_text"),
        "status": run.get("status"),
    }


def performance_label(score: float, rubric: dict[str, Any]) -> str:
    for level in rubric.get("performance_levels", []):
        if level["min_score"] <= score <= level["max_score"]:
            return level["label"]
    return "Unrated"


def print_benchmark(results: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    print("\nArXiv Function Calling Benchmark")
    print("=" * 96)
    print(f"{'ID':<6} {'DIFFICULTY':<10} {'SCORE':<7} {'STATUS':<8} {'CRITICAL':<10} NOTES")
    print("-" * 96)
    for item in results:
        critical = ",".join(item["critical_failure_ids"]) or "-"
        status = "PASS" if item["passed"] else "FAIL"
        note = item["notes"][:62]
        print(f"{item['test_id']:<6} {item['difficulty']:<10} {item['earned_score']:>2}/10   {status:<8} {critical:<10} {note}")
    print("-" * 96)
    print(f"Cases: {summary['total_cases']} | Passed: {summary['passed_cases']} | Critical failures: {summary['critical_failures']}")
    print(f"Score: {summary['earned_score']}/{summary['maximum_score']} ({summary['normalized_score']:.1f}/100) — {summary['performance']}")
    print(f"Dimensions: tool selection {summary['dimensions']['tool_selection']:.1f}% | arguments {summary['dimensions']['argument_extraction']:.1f}% | queries {summary['dimensions']['query_construction']:.1f}% | execution {summary['dimensions']['execution_strategy']:.1f}% | final response {summary['dimensions']['final_response']:.1f}%")
    if summary["critical_failure_counts"]:
        print(f"Critical failure counts: {dict(summary['critical_failure_counts'])}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the terminal ArXiv function-calling benchmark.")
    parser.add_argument("--provider", choices=["openai", "openrouter", "anthropic", "gemini", "ollama"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--rubric", type=Path, default=DEFAULT_RUBRIC)
    parser.add_argument("--system-prompt", type=Path, default=ROOT / "artifacts" / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ROOT / "artifacts" / "tools.yaml")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "runs" / "arxiv")
    parser.add_argument("--max-cases", type=int, default=None)
    args = parser.parse_args()

    suite, cases = load_suite(args.cases)
    rubric = json.loads(args.rubric.read_text(encoding="utf-8"))
    if args.max_cases:
        cases = cases[:args.max_cases]
    system_prompt = args.system_prompt.read_text(encoding="utf-8")
    provider = make_provider(args.provider)
    declarations = load_tool_declarations(args.tools)
    openai_tools = to_openai_tools(declarations)
    results: list[dict[str, Any]] = []

    print(f"Running {len(cases)} ArXiv cases with {args.provider}/{args.model or getattr(provider, 'default_model', 'default')}...")
    for index, case in enumerate(cases, start=1):
        print(f"[{index:02d}/{len(cases):02d}] {case['id']} {case.get('category', '')}...", flush=True)
        try:
            user_message = [{"role": "user", "content": case["input"]}]
            run = run_model_tool_loop(
                provider=provider,
                messages=[{"role": "system", "content": system_prompt}, *user_message],
                tools=openai_tools,
                model=args.model,
                max_tool_rounds=4,
            )
        except Exception as exc:
            run = {"status": "provider_error", "assistant_text": "", "rounds": [], "tool_events": [{"result": {"error": type(exc).__name__, "message": str(exc)}}]}
        results.append(evaluate_case(case, run))

    dimensions = {}
    for dimension in ["tool_selection", "argument_extraction", "query_construction", "execution_strategy", "final_response"]:
        dimensions[dimension] = round(sum(item["dimension_scores"][dimension] for item in results) / max(1, len(results)) / 2 * 100, 1)
    earned = sum(item["earned_score"] for item in results)
    maximum = len(results) * 10
    normalized = earned / maximum * 100 if maximum else 0.0
    summary = {
        "total_cases": len(results),
        "passed_cases": sum(1 for item in results if item["passed"]),
        "earned_score": earned,
        "maximum_score": maximum,
        "normalized_score": round(normalized, 2),
        "performance": performance_label(normalized, rubric),
        "critical_failures": sum(1 for item in results if item["critical_failure"]),
        "critical_failure_counts": Counter(failure for item in results for failure in item["critical_failure_ids"]),
        "dimensions": dimensions,
    }
    print_benchmark(results, summary)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    output = args.output_dir / f"arxiv_eval_{args.provider}_{timestamp}.json"
    payload = {"suite": suite, "rubric": rubric["rubric_name"], "provider": args.provider, "model": args.model or getattr(provider, "default_model", None), "generated_at": datetime.now().isoformat(timespec="seconds"), "summary": summary, "results": results}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\nSaved benchmark: {output}")


if __name__ == "__main__":
    main()
