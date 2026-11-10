from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err


def find_article_candidates(description: str = "", max_results: int = 5) -> dict[str, Any]:
    """Search the web for candidate articles using user-provided details."""
    try:
        if not isinstance(description, str) or not description.strip():
            raise ValueError("description must be a non-empty string")
        if isinstance(max_results, bool) or not isinstance(max_results, int) or not 1 <= max_results <= 10:
            raise ValueError("max_results must be an integer between 1 and 10")
        key = os.getenv("TAVILY_API_KEY")
        if not key:
            raise RuntimeError("Missing TAVILY_API_KEY env var")
        query = description.strip()
        response = requests.post(
            "https://api.tavily.com/search",
            json={"query": query, "topic": "general", "max_results": max_results, "search_depth": "basic"},
            headers={"Authorization": f"Bearer {key}"}, timeout=TIMEOUT,
            allow_redirects=False,
        )
        response.raise_for_status()
        if 300 <= response.status_code < 400:
            raise ValueError("Tavily returned a redirect")
        results = response.json().get("results")
        if not isinstance(results, list):
            raise ValueError("Tavily returned invalid results")
        items = []
        for item in results[:max_results]:
            url = item.get("url") or ""
            items.append({"title": item.get("title") or "", "url": url,
                          "source": domain(url), "summary": item.get("content") or "",
                          "score": item.get("score")})
        return {"tool": "find_article_candidates", "query": query, "items": items,
                "item_count": len(items)}
    except Exception as exc:
        return err("find_article_candidates", exc)
