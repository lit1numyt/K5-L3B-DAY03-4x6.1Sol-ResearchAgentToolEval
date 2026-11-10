from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent import ResearchAgent
from run_eval import case_messages, evaluate_phase_b
from versioning import artifact_version_dict, build_artifact_version

from app.public_data import public_result, public_value, public_tool_event


ROOT = Path(__file__).resolve().parents[1]
DATASETS = {
    "base": ROOT / "data" / "eval_base.json",
    "group": ROOT / "data" / "eval_group.json",
}
RUNS_ROOT = ROOT / "runs"


def _load_dataset(dataset: str) -> dict[str, Any]:
    path = DATASETS.get(dataset)
    if path is None or not path.is_file():
        raise FileNotFoundError(f"Unknown or unavailable dataset: {dataset}")
    return json.loads(path.read_text(encoding="utf-8"))


def list_cases(dataset: str) -> dict[str, Any]:
    data = _load_dataset(dataset)
    cases = []
    for case in data.get("cases", []):
        cases.append({
            "id": case.get("id"),
            "phase": case.get("phase"),
            "suite": case.get("suite"),
            "query": case.get("query") or case.get("input") or case.get("turns"),
            "turns": case.get("turns"),
            "expect": public_value(case.get("expect", {})),
            "metadata": public_value(case.get("metadata", {})),
        })
    return {"dataset": dataset, "dataset_id": data.get("dataset_id", dataset), "description": data.get("description", ""), "cases": cases}


def run_case(dataset: str, case_id: str, service: Any) -> dict[str, Any]:
    data = _load_dataset(dataset)
    case = next((item for item in data.get("cases", []) if item.get("id") == case_id), None)
    if case is None:
        raise KeyError(f"Unknown benchmark case: {case_id}")
    provider = service._get_provider()
    tools = service._get_tools()
    agent = ResearchAgent(provider, system_prompt=service.system_prompt_path.read_text(encoding="utf-8"), tools=tools, model=service.model, tool_functions=service._get_tool_functions())
    tool_choice = None if case.get("expect", {}).get("no_tool") else "required"
    try:
        run = agent.run(case_messages(case), tool_choice=tool_choice)
        calls = [{"name": call.name, "args": call.args} for call in run.tool_calls]
        evaluation = evaluate_phase_b(case, calls, run.text)
        tool_events = [public_tool_event({"tool": event.get("tool"), "args": event.get("args", {}), "result": event.get("result", {})}) for event in run.tool_results]
        status = "evaluated"
    except Exception:
        evaluation = {
            "passed": False,
            "failure_type": "provider_error",
            "observed_mismatch": "provider_error",
            "failures": ["The provider failed before benchmark evaluation completed."],
            "actual_tool_calls": [],
            "actual_text": None,
            "routing_correct": False,
            "args_correct": False,
        }
        tool_events = []
        status = "provider_error"
    artifact = build_artifact_version("web-demo", service.system_prompt_path, service.tools_path)
    return {
        "source": "live",
        "benchmark_evaluated": status == "evaluated",
        "status": status,
        "dataset": dataset,
        "case": {"id": case["id"], "query": public_value(case.get("query") or case.get("input") or case.get("turns")), "turns": public_value(case.get("turns")), "expect": public_value(case.get("expect", {})), "metadata": public_value(case.get("metadata", {}))},
        "actual": {"tool_calls": public_value(evaluation.get("actual_tool_calls", [])), "assistant_text": public_value(evaluation.get("actual_text")), "tool_events": tool_events},
        "evaluation": public_value(evaluation),
        "run_metadata": {**artifact_version_dict(artifact), "provider": service.provider_name, "model": service.model or getattr(provider, "default_model", None)},
    }


def list_saved_runs() -> list[dict[str, Any]]:
    if not RUNS_ROOT.is_dir():
        return []
    output = []
    for path in sorted(RUNS_ROOT.rglob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        output.append({"name": str(path.relative_to(RUNS_ROOT)), "run_id": data.get("run_id"), "version": data.get("version"), "provider": data.get("provider"), "model": data.get("model"), "generated_at": data.get("generated_at"), "summary": public_value(data.get("summary", {})), "artifact_version": data.get("artifact_version"), "prompt_hash": data.get("prompt_hash"), "tools_hash": data.get("tools_hash")})
    return output


def read_saved_run(name: str) -> dict[str, Any]:
    candidate = (RUNS_ROOT / name).resolve()
    if RUNS_ROOT not in candidate.parents or candidate.suffix != ".json" or not candidate.is_file():
        raise FileNotFoundError("Saved run not found")
    data = json.loads(candidate.read_text(encoding="utf-8"))
    return public_value({"source": "saved", "benchmark_evaluated": True, **data})
