# Research evidence tool implementation plan

**Goal:** Distinguish returned evidence, empty responses, and provider errors when reviewing research results.

**Architecture:** A local, deterministic tool accepts actual results from existing research tools, reports each source's status, and deduplicates linkable items. Its report does not establish that an item is true, relevant, or accessible. The existing prompt and declarations make the tool available after retrieval; historical v0–v3 files and base cases remain unchanged.

**Tech stack:** Python, existing tool registry and YAML schema, pytest, existing evaluator.

**Constraints:** No extra API key or network call; no sending; no invented content; preserve old run artifacts; do not call audit in place of the original search; account for per-source partial errors.

**Review focus:** empty versus errored sources; partial results; malformed source objects; unusable or duplicated URLs; paper versus web result shapes; actual model routing and base-case regressions.

1. Write offline tests for populated, empty, failed, partial, malformed and duplicate inputs. Run them and observe failure before implementation.
2. Implement and document the tool, register it, and add a targeted model-routing case. Run the unit and registry tests.
3. Adjust the current prompt for accurate reporting and appropriate tool use. Measure with the real provider, preserve raw runs, and report limitations without attributing unrelated base accuracy to this tool.
