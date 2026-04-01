## Context

The 5 core tools in `app/tools.py` return hardcoded stubs. Seed data exists in `data/customers.csv` (10 rows), `data/orders.csv` (15 rows), `data/refunds.csv` (8 rows), and `data/kb/` (27 markdown articles). The tools need to query this data and return real, input-dependent results so downstream orchestration and eval can function.

Current tool signatures and Pydantic schemas (`app/schemas.py`) are frozen — only the implementations change.

## Goals / Non-Goals

**Goals:**
- Wire all 5 tools to real seed data through a data-access layer
- BM25 search over KB articles with ranked results
- Multi-column customer lookup (customer_id, email)
- Order lookup by order_id or customer_id (returns list when by customer)
- In-memory stores for proposals and tickets with auto-generated IDs
- Raise typed exceptions on not-found / validation errors
- All tools testable without LLM or network

**Non-Goals:**
- SQLite persistence (deferred to Day 4)
- Vector/embedding search for KB
- Session or conversation state
- Refund data integration into tools (no `lookup_refund` tool exists)
- Phone-based customer lookup (not in CSV columns)

## Decisions

### 1. Data-access layer in `app/data_access.py`

Introduce a module that owns all data loading and querying. Tools call this layer; they don't touch CSVs or files directly.

**Why over keeping it in tools.py:** Separates query logic from tool contract formatting. Makes it trivial to swap CSV for SQLite later. Shows clean architecture on a resume.

**Structure:**
```
app/data_access.py
├── _load_customers() → pd.DataFrame  (module-level cache)
├── _load_orders() → pd.DataFrame     (module-level cache)
├── _build_kb_index() → BM25 + doc list (module-level cache)
├── find_customer(identifier: str) → dict
├── find_order(identifier: str) → dict | list[dict]
├── search_kb(query: str, top_k: int = 3) → list[dict]
├── store_proposal(action_type, payload) → dict
├── store_ticket(reason, priority, summary) → dict
```

DataFrames and BM25 index are loaded once at module import. With 10-27 rows this is instant and avoids repeated I/O.

### 2. BM25 for KB search

Use `rank_bm25.BM25Okapi`. Each KB article is one document — tokenize on whitespace + lowercase. Return top-k hits with `article_id` derived from filename (e.g., `refund_policy.md` → `refund_policy`), `title` from first `#` heading, and `snippet` from remaining content.

**Why over TF-IDF:** No scikit-learn dependency. BM25 is the standard IR baseline — recognizable on a resume. `rank_bm25` is a single lightweight package.

**Why over embeddings:** 27 docs don't need semantic search. Adds API/model dependency that violates "no LLM in tool tests" exit criteria.

### 3. Customer lookup: match on customer_id OR email

`find_customer(identifier)` checks `customer_id` column first, then `email`. Returns first match or raises `ToolNotFoundError`. Phone lookup excluded — column not in CSV.

### 4. Order lookup: by order_id or customer_id

`find_order(identifier)` checks if identifier starts with `ord_` → match on `order_id`, return single dict. Otherwise treats it as customer_id → returns all matching orders as a list. Raises `ToolNotFoundError` if no results.

### 5. In-memory stores for proposals and tickets

Module-level dicts: `_proposals: dict[str, dict]` and `_tickets: dict[str, dict]`. IDs auto-increment: `apr_1`, `apr_2`, ... and `tkt_1`, `tkt_2`, ...

**Why not SQLite now:** Day 3 exit criteria is "tools pass tests." In-memory is simpler to test (no teardown), and the interface (`store_proposal`, `store_ticket`) stays the same when we swap to SQLite.

### 6. Exceptions in `app/exceptions.py`

```python
class ToolError(Exception):
    """Base for tool-layer errors."""
    def __init__(self, tool: str, error_code: str, message: str, retryable: bool = False): ...

class ToolNotFoundError(ToolError):
    """Raised when a lookup finds no matching record."""

class ToolValidationError(ToolError):
    """Raised when input fails validation beyond Pydantic."""
```

Tools raise these. The orchestrator (Day 4) catches and wraps into `ToolErrorEnvelope`. For Day 3 tests, we assert the exception type and attributes directly.

### 7. Data directory resolution

Use `app/config.py`'s existing `Settings.data_dir` (defaults to `./data`). Pass it to data-access functions or use the settings singleton. This keeps paths configurable for tests.

## Risks / Trade-offs

- **BM25 quality on tiny corpus** → Might return poor rankings for vague queries. Mitigation: top_k=3 is generous for 27 docs; eval cases will catch regressions.
- **Module-level data loading** → If CSV is malformed, import fails at startup. Mitigation: pandas will raise clear errors; seed data is version-controlled.
- **In-memory state lost on restart** → Proposals/tickets vanish. Acceptable for Day 3; SQLite in Day 4 fixes this.
- **No refund lookup tool** → Data contract has refunds but no tool uses it yet. Not a risk — just unused data for now.
