## Context

The project's eval harness (`scripts/run_eval.py`) and 5 frozen tools require realistic fixture data to produce deterministic, testable outputs. Currently:

- `data/customers.csv`: 2 rows — insufficient to represent edge cases (VIP customers, customers with no orders, missing fields)
- `data/orders.csv`: 2 rows — no cancelled orders, no pending orders, no >30-day-old deliveries
- `data/refunds.csv`: 1 row — only `pending_review` status; no `approved`, `rejected`, or partial refunds
- `data/sample_kb/`: 3 stub articles — covers only refund policy, shipping delay, and address change; missing cancellation, return window, order tracking, account issues, escalation triggers

`search_kb` reads markdown files from a directory. `lookup_customer` and `lookup_order` query CSVs via `app/tools.py`. The seed script (`scripts/seed_mock_data.py`) is the single-command entrypoint for local environment setup.

## Goals / Non-Goals

**Goals:**
- Expand CSVs to ~10 customers, ~15 orders, ~8 refunds covering all policy edge cases
- Add 20–30 KB markdown articles to `data/kb/` covering all support domains
- Ensure one command (`python scripts/seed_mock_data.py`) recreates the full local environment
- Represent at least 3 distinct policy edge cases in the data (in-transit address change, >30-day refund window, cancelled order refund attempt)
- Keep data format 100% compatible with existing tool contracts (no schema changes)

**Non-Goals:**
- Changing tool contracts or routing logic
- Adding a database — CSV + markdown files remain the data layer for MVP
- Generating synthetic data programmatically — hand-authored fixtures are sufficient and more predictable for eval
- Multilingual KB articles

## Decisions

**Decision 1: Keep CSV + markdown as the data format (no SQLite or vector store)**
- Alternatives considered: SQLite for structured data, Chroma for KB semantic search
- Rationale: The tool contracts already reference CSV lookups and markdown file reads. Introducing a DB adds infrastructure complexity without MVP benefit. The eval harness needs reproducible, file-diffable state.

**Decision 2: Use `data/kb/` as the canonical KB directory, with `data/sample_kb/` as a legacy alias or migrated**
- Alternatives considered: Keep everything in `data/sample_kb/`
- Rationale: `sample_kb` signals "placeholder" — renaming to `kb/` clarifies production-like intent. `app/tools.py` will need a one-line path update if it hardcodes `sample_kb`.

**Decision 3: Inline edge cases as distinct CSV rows rather than a separate edge-case fixture file**
- Alternatives considered: separate `data/edge_cases/` CSVs
- Rationale: A single CSV per entity type is simpler for the tool's CSV reader and keeps the seeding script a single pass. Edge cases are annotated in comments within the seed script.

**Decision 4: KB articles are flat markdown with a frontmatter-style header comment**
- Alternatives considered: YAML frontmatter for structured metadata
- Rationale: `search_kb` currently returns `article_id`, `title`, and `snippet` — derived from filename and content. No parser change needed for flat markdown.

## Risks / Trade-offs

- [Risk] `app/tools.py` may hardcode `data/sample_kb/` path → **Mitigation**: Check and update path reference in the same PR; if `data/kb/` is new, both directories can coexist with a symlink until migration is confirmed
- [Risk] Expanded CSV rows could cause unintended matches in existing eval cases → **Mitigation**: Review `specs/06_eval_cases.jsonl` to ensure new `customer_id`/`order_id` values don't collide with existing eval fixtures
- [Risk] 20–30 KB articles may introduce inconsistent policy language → **Mitigation**: Use a consistent authoring template per article; policy numbers (days, amounts) must match the existing 3 stubs
