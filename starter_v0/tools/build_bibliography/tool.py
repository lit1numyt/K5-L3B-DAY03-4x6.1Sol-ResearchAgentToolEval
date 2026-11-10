"""Build bibliography entries from supplied metadata without fetching or inventing facts."""
from __future__ import annotations

import hashlib
import re
from typing import Any
from urllib.parse import urlsplit


def _tex(value: str) -> str:
    replacements = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}",
                    "&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_"}
    return "".join(replacements.get(char, char) for char in " ".join(value.split()))


def _web_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value.strip())
        _ = parsed.port
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False


def build_bibliography(papers: list[dict[str, Any]] | None = None, format: str = "bibtex") -> dict[str, Any]:
    """Return BibTeX/plain citations, retaining missing-data warnings and source URLs."""
    if not isinstance(papers, list) or not papers or len(papers) > 50 or not isinstance(format, str) or format not in {"bibtex", "plain"}:
        return {"tool": "build_bibliography", "error": "invalid_input",
                "message": "Provide 1..50 paper metadata objects and format=bibtex or plain."}
    entries: list[dict[str, Any]] = []
    warnings: list[str] = []
    seen: set[str] = set()
    duplicates = 0
    for index, paper in enumerate(papers, start=1):
        if not isinstance(paper, dict) or not isinstance(paper.get("title"), str) or not paper["title"].strip() or not _web_url(paper.get("url")):
            warnings.append(f"Item {index}: skipped; a nonempty title and an HTTP(S) source URL are required.")
            continue
        authors = paper.get("authors", [])
        year = paper.get("year")
        arxiv_id = paper.get("arxiv_id", "")
        if not isinstance(authors, list) or any(not isinstance(name, str) or not name.strip() for name in authors):
            warnings.append(f"Item {index}: skipped; authors must be a list of nonempty strings.")
            continue
        if year is not None and (isinstance(year, bool) or not isinstance(year, (int, str)) or not re.fullmatch(r"\d{4}", str(year))):
            warnings.append(f"Item {index}: skipped; year must be a supplied four-digit year.")
            continue
        if not isinstance(arxiv_id, str) or (arxiv_id and not re.fullmatch(r"\d{4}\.\d{4,5}(?:v\d+)?", arxiv_id)):
            warnings.append(f"Item {index}: skipped; invalid arxiv_id.")
            continue
        url = paper["url"].strip()
        identity = re.sub(r"v\d+$", "", arxiv_id) if arxiv_id else url
        if identity in seen:
            duplicates += 1
            continue
        seen.add(identity)
        key = "arxiv" + re.sub(r"[^0-9]", "", identity) if arxiv_id else "source" + hashlib.sha256(url.encode()).hexdigest()[:10]
        title = paper["title"].strip()
        fields = [("title", title)]
        if authors:
            fields.append(("author", " and ".join(name.strip() for name in authors)))
        else:
            warnings.append(f"{key}: authors absent; omitted rather than invented.")
        if year is not None:
            fields.append(("year", str(year)))
        else:
            warnings.append(f"{key}: year absent; omitted rather than inferred.")
        fields.append(("url", url))
        if arxiv_id:
            fields.extend([("eprint", arxiv_id), ("archivePrefix", "arXiv")])
        bibtex = "@misc{" + key + ",\n" + ",\n".join("  " + name + " = {" + _tex(value) + "}" for name, value in fields) + "\n}"
        entries.append({"key": key, "title": title, "url": url, "authors": list(authors),
                        "year": year, "arxiv_id": arxiv_id, "bibtex": bibtex})
    if not entries:
        return {"tool": "build_bibliography", "error": "no_usable_papers", "entries": [],
                "text": "", "warnings": warnings, "message": "No usable metadata; nothing was fabricated."}
    text = "\n\n".join(entry["bibtex"] for entry in entries) if format == "bibtex" else "\n".join(
        f"{index}. {entry['title']}" + (f" ({entry['year']})" if entry["year"] is not None else "") + f". {entry['url']}"
        for index, entry in enumerate(entries, start=1)
    )
    return {"tool": "build_bibliography", "format": format, "entries": entries, "text": text,
            "entry_count": len(entries), "duplicate_count": duplicates, "warnings": warnings,
            "note": "Formats supplied metadata only; does not verify authorship, publication, or factual claims."}
