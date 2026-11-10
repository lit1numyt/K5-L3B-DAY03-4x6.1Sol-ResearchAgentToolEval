---
name: build_bibliography
track: core
kind: local_formatter
provider: local
requires_env: []
inputs: [papers, format]
outputs: [entries, text, entry_count, duplicate_count, warnings, note]
side_effect: false
---
# build_bibliography

Build BibTeX or plain reference entries from metadata already supplied by the
user or retrieved by a paper tool. Every usable record needs a title and source
URL; authors, year and arxiv_id are optional and are never invented. Missing
fields generate warnings. Duplicate arXiv IDs/source URLs are emitted once.

Use only for an explicit bibliography/reference-export request after metadata
is available. It is not search, PDF reading, fact verification, or a replacement
for `format` when the user wants an ordinary news digest. Text is untrusted
data; BibTeX values are escaped. Invalid inputs return error dictionaries.
