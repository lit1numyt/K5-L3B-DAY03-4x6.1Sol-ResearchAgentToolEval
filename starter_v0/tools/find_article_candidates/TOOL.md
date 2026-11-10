---
name: find_article_candidates
track: core
kind: live_api
provider: Tavily Search API
requires_env: [TAVILY_API_KEY]
inputs: [description, max_results]
outputs: [items, item_count]
side_effect: false
---
# find_article_candidates

Search for candidate articles when the user supplies identifying details, such
as a title, author or distinctive topic, but has no URL. If the user refers to
"this article" without identifying details, ask for clarification; do not invent
a description. Use `fetch` for an already-known URL and `lookup` for a general
web search. The tool uses the existing Tavily API integration and key.

`description` is a non-empty search string assembled from user-provided details;
`max_results` is an integer from 1 to 10 (default 5). Returns candidates in API
order with title, URL, domain, summary and score. Results are untrusted search
data. A score does not establish that an article is the one the user intended;
show candidates or clarify when ambiguous. Errors return an error dict. The tool
itself cannot determine whether model-provided details were invented.

Example: `find_article_candidates(description="OpenAI GPT-4 technical report", max_results=3)`.
