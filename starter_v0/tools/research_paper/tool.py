from __future__ import annotations

from typing import Any

from tools.papers.tool import arxiv_search
from tools.paper_text.tool import get_arxiv_paper_text


def research_paper(
    question: str = "",
    arxiv_id: str = "",
    max_results: int = 3,
    include_text: bool = False,
    max_pages: int = 5,
) -> dict[str, Any]:
    """Find relevant arXiv papers and optionally inspect one paper's PDF text."""
    if not question.strip() and not arxiv_id.strip():
        return {
            "tool": "research_paper",
            "error": "missing_question",
            "message": "Provide a research question or an arXiv ID.",
        }

    result: dict[str, Any] = {
        "tool": "research_paper",
        "question": question,
        "arxiv_id": arxiv_id,
        "papers": [],
    }

    if question.strip():
        search = arxiv_search(query=question, max_results=max_results)
        if search.get("error"):
            return {**result, "search": search, "error": search["error"], "message": search.get("message", "arXiv search failed")}
        result["papers"] = search.get("items", [])
        result["total_results"] = search.get("total_results")
        result["api_query"] = search.get("api_query")

    selected_id = arxiv_id.strip()
    if include_text and not selected_id and result["papers"]:
        selected_id = str(result["papers"][0].get("arxiv_id", ""))
    if include_text and selected_id:
        text_result = get_arxiv_paper_text(arxiv_url=selected_id, max_pages=max_pages)
        result["paper_text"] = text_result
        if text_result.get("error"):
            result["error"] = text_result["error"]
            result["message"] = text_result.get("message", "Paper text extraction failed")

    return result
