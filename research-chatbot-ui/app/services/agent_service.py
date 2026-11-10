"""Thin adapter between the web API and the EXISTING agent loop.

>>> ADAPT THE BLOCK MARKED "ADAPT" TO YOUR REPOSITORY. <<<
Nothing here reimplements the provider, tools, or tool-calling loop.
"""
import logging
import os
from functools import lru_cache
from pathlib import Path

log = logging.getLogger("agent_service")

# ---------------------------------------------------------------- ADAPT ----
# Replace these imports with the real module paths in your repo.
from agent import (  # noqa: E402  (placeholder module name)
    run_model_tool_loop,
    trim_history,
    make_provider,
    TOOL_FUNCTIONS,  # noqa: F401  (used inside the loop; imported to ensure registration)
)
# Use whatever your repo already uses to load/convert tool declarations, e.g.:
from agent import load_tool_declarations, to_openai_tools  # noqa: E402

SYSTEM_PROMPT_PATH = Path(os.getenv("SYSTEM_PROMPT_PATH", "artifacts/system_prompt.md"))
TOOLS_PATH = Path(os.getenv("TOOLS_PATH", "artifacts/tools.yaml"))
# ---------------------------------------------------------------------------

PROVIDER_NAME = os.getenv("BOT_PROVIDER", "openai")
MODEL = os.getenv("BOT_MODEL") or None
HISTORY_WINDOW = int(os.getenv("HISTORY_WINDOW", "5"))
MAX_TOOL_ROUNDS = int(os.getenv("MAX_TOOL_ROUNDS", "4"))


@lru_cache(maxsize=1)
def _setup():
    """Load prompt, tools and provider once (lazily, on first request)."""
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    tools = to_openai_tools(load_tool_declarations(TOOLS_PATH))  # ADAPT
    provider = make_provider(PROVIDER_NAME)  # ADAPT if the signature differs
    return system_prompt, tools, provider


_STATUS_MAP = {
    "answered": "answered",
    "final": "answered",
    "awaiting_user": "waiting_for_user",
    "waiting_for_user": "waiting_for_user",
    "max_tool_rounds": "max_tool_rounds",
}


def _normalize(result) -> dict:
    """Map the agent loop's output to the API contract.

    ADAPT the key names below if your loop returns something different.
    """
    if not isinstance(result, dict):
        return {"status": "answered", "assistant_text": str(result), "rounds": [], "tool_events": []}

    status = _STATUS_MAP.get(str(result.get("status", "answered")), "answered")
    text = result.get("assistant_text") or result.get("text") or result.get("content") or ""
    rounds = result.get("rounds") or []
    events = result.get("tool_events")
    if events is None:
        events = [r for rd in rounds if isinstance(rd, dict) for r in (rd.get("tool_results") or [])]
    if not text and status == "max_tool_rounds":
        text = "I reached the maximum number of tool steps before finishing. Try narrowing the request."
    return {"status": status, "assistant_text": text, "rounds": rounds, "tool_events": events}


def chat(messages: list[dict]) -> dict:
    """messages: [{'role': 'user'|'assistant', 'content': str}, ...]"""
    system_prompt, tools, provider = _setup()
    history = trim_history(messages, HISTORY_WINDOW)  # ADAPT if it expects different args
    agent_messages = [{"role": "system", "content": system_prompt}, *history]

    result = run_model_tool_loop(  # ADAPT keyword names to your signature
        provider=provider,
        messages=agent_messages,
        tools=tools,
        model=MODEL,
        max_tool_rounds=MAX_TOOL_ROUNDS,
    )
    return _normalize(result)
