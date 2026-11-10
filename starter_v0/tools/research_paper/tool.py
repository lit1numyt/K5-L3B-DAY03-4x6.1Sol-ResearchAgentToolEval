from __future__ import annotations

from typing import Any

from tools.papers.tool import arxiv_search
from tools.paper_text.tool import get_arxiv_paper_text
from tools._shared import err


def research_paper(
    question: str = "",
    arxiv_id: str = "",
    max_results: int = 3,
    include_text: bool = False,
    max_pages: int = 5,
) -> dict[str, Any]:
    """Find relevant arXiv papers and optionally inspect one paper's PDF text."""
    if not isinstance(question, str) or not isinstance(arxiv_id, str):
        return {"tool": "research_paper", "error": "invalid_input", "message": "question and arxiv_id must be strings."}
    if not isinstance(include_text, bool):
        return {"tool": "research_paper", "error": "invalid_input", "message": "include_text must be a boolean."}
    if (isinstance(max_results, bool) or not isinstance(max_results, int) or not 1 <= max_results <= 10
            or isinstance(max_pages, bool) or not isinstance(max_pages, int) or not 1 <= max_pages <= 50):
        return {"tool": "research_paper", "error": "invalid_input", "message": "max_results must be 1..10 and max_pages must be 1..50 (integers)."}
    if not question.strip() and not arxiv_id.strip():
        return {
            "tool": "research_paper",
            "error": "missing_question",
            "message": "Provide a research question or an arXiv ID.",
        }
    if not question.strip() and not include_text:
        return {"tool": "research_paper", "error": "invalid_input", "message": "An ID-only request requires include_text=true; use arxiv_search to discover metadata."}

    result: dict[str, Any] = {
        "tool": "research_paper",
        "question": question,
        "arxiv_id": arxiv_id,
        "papers": [],
    }

    if question.strip():
        try:
            search = arxiv_search(query=question, max_results=max_results)
        except Exception as exc:
            return {**result, **err("research_paper", exc)}
        if search.get("error"):
            return {**result, "search": search, "error": search["error"], "message": search.get("message", "arXiv search failed")}
        result["papers"] = search.get("items", [])
        result["total_results"] = search.get("total_results")
        result["api_query"] = search.get("api_query")

    selected_id = arxiv_id.strip()
    if include_text and not selected_id and result["papers"]:
        selected_id = str(result["papers"][0].get("arxiv_id", ""))
    if include_text and selected_id:
        try:
            text_result = get_arxiv_paper_text(arxiv_url=selected_id, max_pages=max_pages)
        except Exception as exc:
            return {**result, **err("research_paper", exc)}
        result["paper_text"] = text_result
        if text_result.get("error"):
            result["error"] = text_result["error"]
            result["message"] = text_result.get("message", "Paper text extraction failed")

    return result
