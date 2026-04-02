## Why

The current runtime in `app/orchestrator.py` is a scaffold with keyword routing, hardcoded identifiers, canned responses, and no durable session state. Day 4 needs a real orchestration layer so the three golden demos can run end-to-end with provider-backed LLM reasoning, approval gating, and traceable state transitions.

## What Changes

- Add a provider-agnostic orchestration runtime in `app/` that supports Anthropic, OpenAI, and local Ollama through one abstraction layer.
- Add a separate structured extraction step that pulls intent and entities from user messages before any tool planning or response composition.
- Replace one-shot scaffold routing with a bounded ReAct-style orchestration loop that can plan tool usage but stops after configured LLM/tool limits.
- Add SQLite-backed session, approval, ticket, and trace persistence keyed by `session_id` and `approval_id`.
- Add policy enforcement that fails closed to handoff when extraction is ambiguous or evidence is insufficient, and always converts sensitive actions into proposals.
- Add deterministic demo-verification hooks using temperature `0`, JSON Schema validation, and a judge result that reports which checks failed.

## Capabilities

### New Capabilities
- `support-request-orchestration`: Provider-neutral LLM orchestration for extraction, policy-gated tool use, session persistence, approval tracking, and judge-assisted verification.

### Modified Capabilities
- None.

## Impact

- Runtime code in `app/orchestrator.py`, `app/main.py`, `app/config.py`, `app/schemas.py`, `app/tracing.py`, and new provider/session storage modules under `app/`.
- Local persistence moves beyond in-memory counters in `app/data_access.py` to SQLite-backed orchestration state.
- Tests expand from tool-only coverage in `tests/` to orchestration, persistence, and judge-output validation.
- Environment configuration and docs update in `.env.example`, `README.md`, and `docs/architecture.md`.
