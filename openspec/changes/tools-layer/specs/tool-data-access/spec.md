## ADDED Requirements

### Requirement: KB article indexing with BM25
The system SHALL load all markdown files from `data/kb/` at startup and build a BM25 index over their content. Each article SHALL be identified by its filename stem (e.g., `refund_policy`), its title extracted from the first markdown heading, and its snippet from the remaining body text.

#### Scenario: Index built on module load
- **WHEN** the data-access module is imported
- **THEN** all 27 KB articles are indexed and available for search

#### Scenario: Search returns ranked results
- **WHEN** `search_kb` is called with query "refund policy"
- **THEN** results are ranked by BM25 relevance and the top-k hits are returned with article_id, title, and snippet

#### Scenario: Search with no matches
- **WHEN** `search_kb` is called with a query that matches no terms
- **THEN** an empty hits list is returned (no error raised)

### Requirement: Customer lookup by ID or email
The system SHALL load `data/customers.csv` and support lookup by `customer_id` or `email`. Lookup SHALL be case-insensitive for email.

#### Scenario: Lookup by customer_id
- **WHEN** `find_customer` is called with "cust_5001"
- **THEN** the customer record for Alice Wang is returned with customer_id, email, and tags

#### Scenario: Lookup by email
- **WHEN** `find_customer` is called with "alice@example.com"
- **THEN** the same customer record is returned

#### Scenario: Customer not found
- **WHEN** `find_customer` is called with "nonexistent"
- **THEN** a `ToolNotFoundError` is raised with tool="lookup_customer"

### Requirement: Order lookup by order_id or customer_id
The system SHALL load `data/orders.csv` and support lookup by `order_id` (returns single record) or `customer_id` (returns all matching orders).

#### Scenario: Lookup by order_id
- **WHEN** `find_order` is called with "ord_5101"
- **THEN** a single order dict is returned with order_id, customer_id, status, shipping_status, total_amount

#### Scenario: Lookup by customer_id
- **WHEN** `find_order` is called with "cust_5001"
- **THEN** a list of all orders for that customer is returned

#### Scenario: Order not found
- **WHEN** `find_order` is called with "ord_9999"
- **THEN** a `ToolNotFoundError` is raised with tool="lookup_order"

### Requirement: In-memory proposal store
The system SHALL store action proposals in an in-memory dict with auto-incrementing approval_ids. Each proposal SHALL record action_type, payload, and status "needs_human_approval".

#### Scenario: Store a proposal
- **WHEN** `store_proposal` is called with action_type="refund_request" and a payload
- **THEN** a dict is returned with a unique approval_id, action_type, status="needs_human_approval", and the payload

#### Scenario: Multiple proposals get unique IDs
- **WHEN** two proposals are stored sequentially
- **THEN** they receive different approval_ids

### Requirement: In-memory ticket store
The system SHALL store tickets in an in-memory dict with auto-incrementing ticket_ids. Each ticket SHALL record reason, priority, summary, and status "escalated".

#### Scenario: Store a ticket
- **WHEN** `store_ticket` is called with reason, priority="high", and summary
- **THEN** a dict is returned with a unique ticket_id, status="escalated", and the provided fields

### Requirement: Typed exceptions for tool errors
The system SHALL define `ToolError`, `ToolNotFoundError`, and `ToolValidationError` in `app/exceptions.py`. All data-access failures SHALL raise the appropriate exception with tool name, error_code, message, and retryable flag.

#### Scenario: ToolNotFoundError attributes
- **WHEN** a `ToolNotFoundError` is raised
- **THEN** it carries tool, error_code="not_found", a descriptive message, and retryable=False
