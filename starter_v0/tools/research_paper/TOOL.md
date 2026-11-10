---
name: research_paper
track: web
kind: composed_live_api
provider: arXiv API + local PDF extraction
requires_env: [ARXIV_USER_AGENT]
inputs: [question, arxiv_id, max_results, include_text, max_pages]
outputs: [papers, paper_text]
side_effect: false
---
# research_paper

Searches arXiv for papers relevant to a research question. When a specific
arXiv ID is supplied, it also extracts an excerpt from the paper PDF so the
agent can answer questions about its method, results, or limitations.
