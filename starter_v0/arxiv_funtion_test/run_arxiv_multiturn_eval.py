from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chat import run_model_tool_loop
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from run_arxiv_eval import DEFAULT_CASES, DEFAULT_RUBRIC, evaluate_case, load_suite, performance_label, print_benchmark

load_lab_env(ROOT)


def run_conversation(cases: list[dict[str, Any]], *, system_prompt: str, provider: Any, tools: list[dict[str, Any]], model: str | None, max_tool_rounds: int, conversation_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    history: list[dict[str, str]] = []
    results: list[dict[str, Any]] = []
    transcript: list[dict[str, Any]] = []
    for turn_index, case in enumerate(cases, start=1):
        messages = [{"role": "system", "content": system_prompt}, *history, {"role": "user", "content": case["input"]}]
        try:
            run = run_model_tool_loop(provider=provider, messages=messages, tools=tools, model=model, max_tool_rounds=max_tool_rounds)
        except Exception as exc:
            run = {"status": "provider_error", "assistant_text": "", "rounds": [], "tool_events": [{"result": {"error": type(exc).__name__, "message": str(exc)}}]}
        scored = evaluate_case(case, run)
        scored["test_id"] = f"{conversation_id}.T{turn_index}/{case['id']}"
        scored["conversation_id"] = conversation_id
        scored["turn_index"] = turn_index
        results.append(scored)
        transcript.append({"turn": turn_index, "source_case": case["id"], "user": case["input"], "assistant": run.get("assistant_text", ""), "status": run.get("status"), "tool_calls": scored.get("actual_tool_calls", [])})
        history.extend([{"role": "user", "content": case["input"]}, {"role": "assistant", "content": run.get("assistant_text", "")}])
    return results, transcript


def main() -> None:
    parser = argparse.ArgumentParser(description="Run five sampled multi-turn ArXiv conversations in the terminal.")
    parser.add_argument("--provider", choices=["openai", "openrouter", "anthropic", "gemini", "ollama"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--rubric", type=Path, default=DEFAULT_RUBRIC)
    parser.add_argument("--system-prompt", type=Path, default=ROOT / "artifacts" / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ROOT / "artifacts" / "tools.yaml")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "runs" / "arxiv")
    parser.add_argument("--conversations", type=int, default=5)
    parser.add_argument("--turns-per-conversation", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    args = parser.parse_args()

    suite, bank = load_suite(args.cases)
    rubric = json.loads(args.rubric.read_text(encoding="utf-8"))
    if args.conversations < 1 or args.turns_per_conversation < 2:
        raise SystemExit("--conversations must be positive and --turns-per-conversation must be at least 2")
    required = args.conversations * args.turns_per_conversation
    if required > len(bank):
        raise SystemExit(f"Question bank has {len(bank)} cases, but {required} unique questions are required")

    rng = random.Random(args.seed)
    sampled = rng.sample(bank, required)
    conversations = [sampled[i:i + args.turns_per_conversation] for i in range(0, required, args.turns_per_conversation)]
    provider = make_provider(args.provider)
    system_prompt = args.system_prompt.read_text(encoding="utf-8")
    tools = to_openai_tools(load_tool_declarations(args.tools))
    all_results: list[dict[str, Any]] = []
    transcripts: list[dict[str, Any]] = []

    print(f"Running {len(conversations)} multi-turn conversations ({args.turns_per_conversation} turns each), seed={args.seed}...")
    for index, cases in enumerate(conversations, start=1):
        conversation_id = f"MT{index:02d}"
        print(f"\n{conversation_id}: " + " -> ".join(case["id"] for case in cases), flush=True)
        results, transcript = run_conversation(cases, system_prompt=system_prompt, provider=provider, tools=tools, model=args.model, max_tool_rounds=args.max_tool_rounds, conversation_id=conversation_id)
        all_results.extend(results)
        transcripts.append({"conversation_id": conversation_id, "source_cases": [case["id"] for case in cases], "turns": transcript})
        for result in results:
            print(f"  T{result['turn_index']} {result['test_id']}: {result['earned_score']}/10 {'PASS' if result['passed'] else 'FAIL'}")

    dimensions = {dimension: round(sum(item["dimension_scores"][dimension] for item in all_results) / max(1, len(all_results)) / 2 * 100, 1) for dimension in ["tool_selection", "argument_extraction", "query_construction", "execution_strategy", "final_response"]}
    earned = sum(item["earned_score"] for item in all_results)
    maximum = len(all_results) * 10
    normalized = earned / maximum * 100 if maximum else 0.0
    critical_counts: dict[str, int] = {}
    for item in all_results:
        for failure in item["critical_failure_ids"]:
            critical_counts[failure] = critical_counts.get(failure, 0) + 1
    summary = {"conversations": len(conversations), "turns_per_conversation": args.turns_per_conversation, "total_cases": len(all_results), "passed_cases": sum(1 for item in all_results if item["passed"]), "earned_score": earned, "maximum_score": maximum, "normalized_score": round(normalized, 2), "performance": performance_label(normalized, rubric), "critical_failures": sum(1 for item in all_results if item["critical_failure"]), "critical_failure_counts": critical_counts, "dimensions": dimensions, "seed": args.seed}
    print_benchmark(all_results, summary)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / f"arxiv_multiturn_eval_{args.provider}_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    payload = {"suite": suite, "rubric": rubric["rubric_name"], "provider": args.provider, "model": args.model or getattr(provider, "default_model", None), "generated_at": datetime.now().isoformat(timespec="seconds"), "sampling": {"seed": args.seed, "conversations": len(conversations), "turns_per_conversation": args.turns_per_conversation}, "summary": summary, "conversations": transcripts, "results": all_results}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\nSaved multi-turn benchmark: {output}")


if __name__ == "__main__":
    main()
