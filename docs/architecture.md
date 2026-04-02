# Architecture

## Goal
Build a support copilot that is:
- explainable
- safe for sensitive actions
- measurable
- easy to demo

## Request flow
1. User sends `/chat` request with `session_id`
2. Session history is loaded from SQLite
3. Provider-neutral extraction identifies route intent and entities
4. Policy gates fail closed on ambiguous inputs and force approval paths for sensitive actions
5. A bounded orchestration loop plans the next tool step
6. Application code executes one of the frozen five tools
7. Response composition returns answer + citations + tool trace + state
8. Workflow artifacts are persisted:
   - session messages
   - tool traces
   - approval requests
   - approval review events
   - tickets
9. Optional judge output records route correctness, tool-use correctness, policy compliance, and intent satisfaction

## Runtime layers

- `app/llm.py`: provider-neutral adapter and provider stubs for OpenAI, Anthropic, and Ollama
- `app/orchestrator.py`: extraction, policy gate, bounded planning loop, response assembly
- `app/persistence.py`: SQLite persistence for sessions, traces, approvals, reviews, and tickets
- `app/tools.py`: frozen business-tool surface

## State model

- `session_id` is the top-level key for customer conversation state
- `approval_id` links approval requests to separate review events
- `ticket_id` links fail-closed handoff outcomes to escalation records
- judge results are verification metadata and do not control workflow transitions

## Future production upgrades
- replace local SQLite and stubs with PostgreSQL/pgvector plus real provider clients
- add approval queue UI on top of persisted review events
- add retrieval reranker
- add structured trace storage
- add role-based access control
