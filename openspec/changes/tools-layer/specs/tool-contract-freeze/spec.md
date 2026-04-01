## MODIFIED Requirements

### Requirement: Tool functions return query-dependent data
Each tool function in `app/tools.py` SHALL delegate to `app/data_access.py` for data retrieval instead of returning hardcoded stubs. Tool functions SHALL format the data-access results into the existing Pydantic output schemas. Tool functions SHALL raise `ToolNotFoundError` or `ToolValidationError` on failures instead of always succeeding.

#### Scenario: search_kb returns real BM25 results
- **WHEN** `search_kb("refund policy")` is called
- **THEN** the result contains hits ranked by BM25 relevance from actual KB articles

#### Scenario: lookup_customer returns real CSV data
- **WHEN** `lookup_customer("cust_5001")` is called
- **THEN** the result contains the actual customer record from customers.csv

#### Scenario: lookup_order returns real CSV data
- **WHEN** `lookup_order("ord_5101")` is called
- **THEN** the result contains the actual order record from orders.csv

#### Scenario: propose_action stores and returns proposal
- **WHEN** `propose_action("refund_request", {"order_id": "ord_5101"})` is called
- **THEN** the result contains a unique approval_id and status "needs_human_approval"

#### Scenario: create_or_escalate_ticket stores and returns ticket
- **WHEN** `create_or_escalate_ticket("unclear request", "medium", "Customer needs help")` is called
- **THEN** the result contains a unique ticket_id and status "escalated"

#### Scenario: Tool raises on not-found
- **WHEN** `lookup_customer("nonexistent")` is called
- **THEN** a `ToolNotFoundError` is raised
