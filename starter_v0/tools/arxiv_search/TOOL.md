---
name: arxiv_search
track: web
kind: live_api
provider: arXiv API
requires_env: [ARXIV_USER_AGENT]
inputs: [query, max_results, sort_by, sort_order, start, date_from, date_to, author, title, categories]
outputs: [items, total_results]
side_effect: false
---
# arxiv_search

Searches arXiv through the official Atom API. Supports query constraints,
author/title filters, date ranges, categories, sorting, and pagination.
