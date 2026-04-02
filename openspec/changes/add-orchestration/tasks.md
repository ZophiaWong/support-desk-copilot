## 1. Provider and configuration foundation

- [x] 1.1 Add provider-neutral LLM configuration to `app/config.py` and `.env.example`, including provider name, model name, temperature, and orchestration limits
- [x] 1.2 Create an LLM adapter module under `app/` that defines structured interfaces for extraction, next-action planning, response composition, and judge evaluation
- [x] 1.3 Add provider implementations or stubs for Anthropic, OpenAI, and Ollama behind the shared adapter contract

## 2. SQLite workflow state

- [x] 2.1 Add a SQLite-backed persistence module for sessions, messages, tool traces, approval requests, approval review events, and tickets
- [x] 2.2 Replace transient orchestration state needed for approvals and handoff tracking with SQLite reads/writes keyed by `session_id` and `approval_id`
- [x] 2.3 Update the `/approval` path in `app/main.py` to persist review decisions as approval review events rather than echoing request data only

## 3. Orchestration pipeline

- [x] 3.1 Refactor `app/orchestrator.py` to load session state, run structured extraction, validate extraction output, and fail closed to handoff on ambiguity
- [x] 3.2 Implement policy-gated route handling for FAQ, order lookup, action request, and handoff using the frozen five tools only
- [x] 3.3 Add a bounded ReAct-style planning loop with separate limits for orchestration turns and tool calls and a safe terminal fallback when limits are exceeded
- [x] 3.4 Replace canned answers and hardcoded identifiers with response composition driven by extracted entities, tool outputs, citations, and final workflow state

## 4. Verification and tests

- [x] 4.1 Extend `app/schemas.py` with structured extraction, orchestration state, and judge-result models validated by JSON Schema-compatible constraints
- [x] 4.2 Add orchestration tests covering the three golden flows, ambiguous extraction handoff, loop-limit fallback, and approval-state persistence
- [x] 4.3 Add judge-result tests asserting the four verification dimensions and explicit reporting of failed checks
- [x] 4.4 Add deterministic test doubles or fixtures for provider adapters so orchestration tests do not depend on live model APIs

## 5. Docs and operator workflow

- [x] 5.1 Update `README.md` and `docs/architecture.md` with the staged orchestration flow, SQLite state model, and supported provider configuration
- [x] 5.2 Document local verification commands for seeded data, orchestration tests, and any demo-mode judge checks needed to confirm the Day 4 exit criteria
