## 1. Foundation

- [x] 1.1 Create `app/exceptions.py` with `ToolError`, `ToolNotFoundError`, `ToolValidationError`
- [x] 1.2 Add `rank_bm25` to `requirements.txt` and install

## 2. Data Access Layer

- [x] 2.1 Create `app/data_access.py` with CSV loaders (`_load_customers`, `_load_orders`) using pandas and `Settings.data_dir`
- [x] 2.2 Add KB indexer (`_build_kb_index`) that reads `data/kb/*.md`, extracts title/snippet, builds BM25 index
- [x] 2.3 Implement `find_customer(identifier)` — match on customer_id or email, raise `ToolNotFoundError` on miss
- [x] 2.4 Implement `find_order(identifier)` — match on order_id (single) or customer_id (list), raise `ToolNotFoundError` on miss
- [x] 2.5 Implement `search_kb(query, top_k=3)` — tokenize, BM25 rank, return hits list
- [x] 2.6 Implement `store_proposal(action_type, payload)` — in-memory dict with auto-increment ID
- [x] 2.7 Implement `store_ticket(reason, priority, summary)` — in-memory dict with auto-increment ID

## 3. Rewire Tools

- [x] 3.1 Rewrite `search_kb` in `app/tools.py` to call `data_access.search_kb`
- [x] 3.2 Rewrite `lookup_customer` to call `data_access.find_customer`
- [x] 3.3 Rewrite `lookup_order` to call `data_access.find_order`
- [x] 3.4 Rewrite `propose_action` to call `data_access.store_proposal`
- [x] 3.5 Rewrite `create_or_escalate_ticket` to call `data_access.store_ticket`

## 4. Tests

- [x] 4.1 Create `tests/conftest.py` with fixture pointing to real `data/` directory
- [x] 4.2 Rewrite `tests/test_tools.py` — happy paths for all 5 tools against real seed data
- [x] 4.3 Add not-found tests: bad customer ID, bad order ID → `ToolNotFoundError`
- [x] 4.4 Add KB search quality test: query "refund" returns refund-related articles
- [x] 4.5 Add contract compliance tests: validate tool outputs against Pydantic schemas
- [x] 4.6 Run full test suite, verify all pass
