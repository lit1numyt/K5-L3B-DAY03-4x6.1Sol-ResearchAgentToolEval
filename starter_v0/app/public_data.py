from __future__ import annotations

import re
from typing import Any


SECRET_KEY = re.compile(r"(api[_-]?key|token|secret|password|authorization|credential)", re.I)
SECRET_VALUE = re.compile(r"(?i)(bearer\s+|bot\d+:[\w-]+|sk-[\w-]+|AIza[\w-]+)")


def public_value(value: Any, *, key: str = "") -> Any:
    if SECRET_KEY.search(key):
        return "[redacted]"
    if isinstance(value, dict):
        return {str(item_key): public_value(item_value, key=str(item_key)) for item_key, item_value in value.items()}
    if isinstance(value, list):
        return [public_value(item, key=key) for item in value]
    if isinstance(value, str):
        return SECRET_VALUE.sub("[redacted]", value)
    return value


def public_tool_event(event: dict[str, Any]) -> dict[str, Any]:
    raw_result = event.get("result") if isinstance(event.get("result"), dict) else {}
    if raw_result.get("awaiting_user") or raw_result.get("status") == "needs_confirmation":
        status = "waiting"
    elif raw_result.get("error"):
        status = "failed"
    else:
        status = "succeeded"
    result: dict[str, Any] = {"status": status}
    if status == "waiting":
        result["message"] = raw_result.get("question") or raw_result.get("message") or "Waiting for user input or confirmation."
    elif status == "failed":
        error_name = str(raw_result.get("error") or "tool_error")
        result["message"] = f"{error_name}: the tool could not complete this request."
    return {
        "tool": event.get("tool", "unknown_tool"),
        "args": public_value(event.get("args", {})),
        "result": result,
    }


def public_result(result: dict[str, Any]) -> dict[str, Any]:
    output = dict(result)
    output["tool_events"] = [public_tool_event(event) for event in result.get("tool_events", [])]
    output["rounds"] = public_value(result.get("rounds", []))
    return public_value(output)
