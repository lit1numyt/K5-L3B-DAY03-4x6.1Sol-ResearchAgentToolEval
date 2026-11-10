from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit, urlunsplit


def _url_key(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    try:
        parts = urlsplit(value.strip())
        if parts.scheme.lower() not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
            return ""
        # Accessing port also rejects malformed port numbers.
        port = f":{parts.port}" if parts.port is not None else ""
        host = parts.hostname.lower()
        if ":" in host:
            host = f"[{host}]"
        return urlunsplit((parts.scheme.lower(), host + port, parts.path, parts.query, ""))
    except ValueError:
        return ""


def audit_research_evidence(results: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Summarize actual research-tool outputs without asserting factual correctness."""
    if not isinstance(results, list) or not results:
        return {"tool": "audit_research_evidence", "error": "invalid_input", "message": "Provide a non-empty list of research tool result objects."}

    sources: list[dict[str, Any]] = []
    items: list[dict[str, str]] = []
    seen: set[str] = set()
    duplicate_count = 0
    for result in results:
        if not isinstance(result, dict):
            sources.append({"tool": "unknown", "status": "invalid", "item_count": 0, "unusable_item_count": 0})
            continue
        name = result.get("tool")
        source: dict[str, Any] = {"tool": name if isinstance(name, str) and name.strip() else "unknown", "item_count": 0, "unusable_item_count": 0}
        payload = result.get("result") if isinstance(result.get("result"), dict) else result
        failure = payload.get("error")
        raw_items = payload.get("items", payload.get("papers"))
        if not isinstance(raw_items, list):
            source["status"] = "error" if failure else "invalid"
            if failure:
                source["error"] = str(failure)
            sources.append(source)
            continue
        source["item_count"] = len(raw_items)
        usable = 0
        for item in raw_items:
            if not isinstance(item, dict):
                source["unusable_item_count"] += 1
                continue
            key = _url_key(item.get("url"))
            title = item.get("title") if isinstance(item.get("title"), str) else ""
            summary = item.get("summary") if isinstance(item.get("summary"), str) else ""
            if not key or not (title.strip() or summary.strip()):
                source["unusable_item_count"] += 1
                continue
            usable += 1
            if key in seen:
                duplicate_count += 1
                continue
            seen.add(key)
            source_name = item.get("source") if isinstance(item.get("source"), str) else ""
            items.append({"title": title, "summary": summary, "url": item["url"].strip(), "source": source_name})
        if failure:
            source["status"] = "partial" if usable else "error"
            source["error"] = str(failure)
        else:
            source["status"] = "ok" if usable else ("empty" if not raw_items else "unusable")
        sources.append(source)

    return {"tool": "audit_research_evidence", "sources": sources, "items": items,
            "unique_item_count": len(items), "duplicate_item_count": duplicate_count,
            "note": "Checks result structure only; does not verify truth, relevance, or URL accessibility."}
