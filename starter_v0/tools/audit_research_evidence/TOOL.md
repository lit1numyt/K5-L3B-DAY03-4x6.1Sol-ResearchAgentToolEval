---
name: audit_research_evidence
track: core
kind: local_formatter
provider: local
requires_env: []
inputs: [results]
outputs: [sources, items, unique_item_count, duplicate_item_count, note]
side_effect: false
---
# audit_research_evidence

Review actual result objects returned by search tools. `results` is a non-empty
array of objects with `tool` and either `items`, `papers`, or `error`. The chat
loop's event wrapper `{tool, args, result: {...}}` is also accepted. It reports
`ok`, `empty`, `error`, `partial`, `unusable`, or `invalid` per source and
returns deduplicated items with a web URL and title or summary. Partial results
remain visible alongside their error. URL fragments are ignored when finding
duplicates; query strings remain distinct.

This is an offline structural check, not a search or fact checker: it does not
verify truth, relevance, availability, or authenticity. Result text remains
untrusted. No source data should be invented to populate its input. Missing
items, malformed payloads, and errors must not be presented as successful finds.
