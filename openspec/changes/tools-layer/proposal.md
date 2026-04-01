## Why

The 5 core tools (`search_kb`, `lookup_customer`, `lookup_order`, `propose_action`, `create_or_escalate_ticket`) currently return hardcoded stub data regardless of input. Until they query real seed data, the orchestrator can't route meaningfully, eval cases can't measure actual retrieval quality, and the demo is non-functional. This is the Day 3 critical path — everything downstream (orchestration, eval, demo) depends on working tools.

## What Changes

- Add `app/data_access.py` — a data-access layer that loads CSVs (`data/customers.csv`, `data/orders.csv`, `data/refunds.csv`) and indexes KB articles (`data/kb/*.md`) using BM25
- Rewrite all 5 tool functions in `app/tools.py` to call the data-access layer instead of returning hardcoded dicts
- Add `rank_bm25` to `requirements.txt` for KB search
- Add `app/exceptions.py` with tool-specific exceptions (`ToolNotFoundError`, `ToolValidationError`) — tools raise on error, orchestrator catches
- Store proposals and tickets in-memory (dict) for now; SQLite deferred to Day 4
- Expand `tests/test_tools.py` to cover happy paths, not-found cases, and contract compliance against Pydantic schemas
- Add `tests/conftest.py` with fixtures that point to the real seed data directory

## Capabilities

### New Capabilities
- `tool-data-access`: Data-access layer that loads and queries CSV seed data and BM25-indexed KB articles

### Modified Capabilities
- `tool-contract-freeze`: Tool function signatures stay the same, but implementations now return real query-dependent data and raise exceptions on errors instead of always succeeding

## Impact

- **New files**: `app/data_access.py`, `app/exceptions.py`, `tests/conftest.py`
- **Modified files**: `app/tools.py`, `tests/test_tools.py`, `requirements.txt`
- **New dependency**: `rank_bm25`
- **No API changes**: FastAPI endpoints and Pydantic schemas remain unchanged
- **No approval-gate changes**: `propose_action` still returns `needs_human_approval`; storage is in-memory dict until SQLite is added
