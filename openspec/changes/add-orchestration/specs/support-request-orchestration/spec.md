## ADDED Requirements

### Requirement: Provider-neutral orchestration runtime
The system SHALL execute support-request orchestration through an application-owned runtime that is configurable for multiple LLM providers, including Anthropic, OpenAI, and local Ollama, without changing the frozen five-tool contract.

#### Scenario: Provider swap does not change orchestration surface
- **WHEN** runtime configuration selects a different supported provider
- **THEN** the orchestrator still uses the same extraction, planning, composition, and judge interfaces and continues to call only the frozen five tools

### Requirement: Structured extraction precedes tool planning
The system SHALL run a separate structured extraction step before tool planning to identify route intent and relevant entities such as `order_id`, `customer_id`, and customer email from the user message.

#### Scenario: Extraction identifies order lookup request
- **WHEN** the user asks for the status of `ord_2001`
- **THEN** extraction yields an order-lookup route candidate and captures `ord_2001` as the order identifier before any tool is called

#### Scenario: Ambiguous extraction fails closed
- **WHEN** extraction cannot produce a valid route or the required entities with schema-valid output
- **THEN** the orchestrator routes the request to handoff and records the ambiguity as the handoff reason

### Requirement: Policy gates constrain orchestration behavior
The system SHALL enforce routing and action policies in application code before final response emission.

#### Scenario: Sensitive action becomes proposal
- **WHEN** the user requests a refund, post-shipment cancellation, or post-shipment address change
- **THEN** the orchestrator uses `lookup_order` as needed, calls `propose_action`, and returns an approval-gated response instead of directly executing the action

#### Scenario: Missing evidence becomes escalation
- **WHEN** the selected route requires verified customer, order, or policy evidence that the system cannot obtain
- **THEN** the orchestrator creates or escalates a ticket rather than fabricating the missing facts

### Requirement: ReAct loop is bounded and terminates safely
The system SHALL enforce configured limits on orchestration turns and tool calls for each request.

#### Scenario: Loop completes within limits
- **WHEN** the request can be satisfied within the configured extraction and planning limits
- **THEN** the orchestrator returns a terminal response with the chosen route, tool traces, and final state

#### Scenario: Loop limit forces safe terminal state
- **WHEN** the orchestrator reaches its configured LLM-turn or tool-call limit before reaching a valid terminal response
- **THEN** it terminates the loop and returns a safe handoff outcome instead of continuing to reason indefinitely

### Requirement: Session and approval workflow state is persisted in SQLite
The system SHALL persist orchestration workflow state in SQLite, keyed by `session_id`, and SHALL store approval requests and approval review events as separate records linked by `approval_id`.

#### Scenario: Approval request is linked to session
- **WHEN** an action request produces a proposal
- **THEN** the approval request is stored with its originating `session_id`, route context, and proposal payload

#### Scenario: Review decision is stored separately
- **WHEN** a reviewer approves or rejects an approval request
- **THEN** the decision is stored as a review event linked to the same `approval_id` without being collapsed into the customer message history only

### Requirement: Responses remain structured and traceable
The system SHALL return a structured response that includes route, answer, citations when applicable, tool traces, and workflow state fields required by the chosen route.

#### Scenario: FAQ response includes citation evidence
- **WHEN** the request is answered through KB retrieval
- **THEN** the final response includes KB citations and a trace showing the retrieval tool inputs and summarized results

#### Scenario: Action response includes approval state
- **WHEN** the request results in an approval-gated proposal
- **THEN** the final response state includes the approval identifier and approval status

### Requirement: Demo verification emits structured judge results
The system SHALL support deterministic demo verification using temperature `0`, JSON Schema validation for model outputs, and a judge result that reports route correctness, tool-use correctness, policy compliance, and intent satisfaction.

#### Scenario: Judge reports failed checks explicitly
- **WHEN** a response does not satisfy one or more verification dimensions
- **THEN** the judge result identifies each failed check by name instead of returning only a single pass/fail flag
