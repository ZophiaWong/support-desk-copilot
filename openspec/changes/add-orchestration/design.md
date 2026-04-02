## Context

`app/orchestrator.py` currently implements a scaffold: it routes on keywords, hardcodes `ord_2001`, returns canned answers, and stores no session state. Day 3 made the five tools data-backed, but Day 4 still lacks the workflow layer that turns those tools into an explainable support copilot. The orchestration layer has to preserve the existing MVP shape: five frozen tools, approval gating for sensitive actions, response traces, and behavior that is demoable and testable.

The user decisions for this change are:
- the LLM layer must be provider-agnostic and support Anthropic, OpenAI, and local Ollama
- orchestration may use a ReAct-style loop, but it must be bounded
- sessions and approval state must be stored in SQLite
- entity extraction must be a separate step, not implicit inside tool planning
- ambiguous extraction must fail closed to handoff for now
- verification should use temperature `0`, JSON Schema validation, and a judge result that reports which checks failed across route correctness, tool-use correctness, policy compliance, and intent satisfaction

## Goals / Non-Goals

**Goals:**
- Replace scaffold routing with a structured orchestration pipeline that can run the three golden flows end-to-end.
- Introduce a provider-neutral LLM interface without coupling orchestration behavior to one vendor's native tool-calling API.
- Persist session history, tool traces, tickets, and approval requests in SQLite so workflows are inspectable and resumable.
- Enforce policy gates in application code so sensitive actions are always converted into proposals and ambiguous cases hand off safely.
- Produce deterministic enough outputs for demos and tests through structured extraction, schema validation, and judge reporting.

**Non-Goals:**
- Replacing the frozen five-tool contract or directly executing refunds, cancellations, or address changes.
- Building the Day 5 approval UI or trace viewer.
- Replacing the Day 1 offline eval baseline with online-model-dependent scoring.
- Supporting multi-turn clarification requests for ambiguous extraction in this change.

## Decisions

### 1. Keep tool execution application-controlled behind a provider-neutral LLM adapter

The orchestration layer will call a local adapter interface such as extraction, next-action planning, final response composition, and judge evaluation. Provider implementations for Anthropic, OpenAI, and Ollama will translate those requests to provider-specific APIs, but Python application code will remain the sole owner of actual tool execution.

Why this approach:
- It keeps business safety rules in `app/`, not hidden inside provider-specific native tool use.
- It allows Ollama support without assuming every provider exposes the same tool-calling semantics.
- It makes tests easier because the adapter can be stubbed with deterministic fixtures.

Alternatives considered:
- Use Anthropic native tool use directly in the orchestrator. Rejected because it couples the runtime to one provider and weakens portability.
- Build a single generic chat method that handles every stage. Rejected because extraction, planning, composition, and judging have different schemas and failure modes.

### 2. Split orchestration into explicit stages: extract, gate, act, compose, judge

The request pipeline will be:
1. load session from SQLite
2. run extraction to produce structured intent/entities
3. validate extraction JSON
4. apply policy gates and choose the initial route
5. run a bounded planning/tool loop
6. compose the user-facing response
7. persist traces and workflow state
8. optionally run the judge for demo verification

Why this approach:
- Extraction becomes debuggable and independently testable.
- Policy gates can fail closed before the model starts planning tool usage.
- Composition can be constrained by tool results and final route/state instead of free-form reasoning.

Alternatives considered:
- Let a single ReAct loop discover route, entities, tools, and answer in one pass. Rejected because it makes failures opaque and harder to test.

### 3. Use bounded ReAct limits with fail-closed fallback

The runtime will enforce separate limits for LLM turns and tool calls. A practical MVP target is one extraction call plus a planning loop capped at a small number of iterations, with no more than three tool invocations per request. If the loop cannot reach a valid terminal response within limits, the system will create or escalate a ticket rather than continue reasoning.

Why this approach:
- It is enough to demonstrate agentic behavior without making the runtime open-ended.
- It bounds cost, latency, and failure surface.
- It gives deterministic failure semantics for tests and demos.

Alternatives considered:
- A single deterministic route map with no loop. Rejected because the user explicitly wants a ReAct-style orchestrator.
- An unbounded loop. Rejected because it undermines safety and demo reliability.

### 4. Persist orchestration state in SQLite with review events separated from customer session events

SQLite will store sessions, session messages, tool traces, approval requests, approval review events, and tickets. Approval review decisions will be separate records keyed by `approval_id`, while still storing the originating `session_id` for joins.

Why this approach:
- It preserves a clean distinction between customer-facing conversation events and internal reviewer actions.
- It supports a future Day 5 approval queue without restructuring state again.
- SQLite is sufficient for local reproducibility and requires no external service.

Alternatives considered:
- Keep everything in memory keyed by `session_id`. Rejected because approval tracking would disappear across process restarts and demos would not be auditable.
- Store approval decisions as plain session messages only. Rejected because review history is a separate workflow concept.

### 5. Treat ambiguous extraction and insufficient evidence as immediate handoff

If extraction cannot produce a valid route or the required entity set for the route, the orchestrator will not ask clarifying questions in this change. It will create a handoff/ticket with a reason code describing the ambiguity or evidence gap.

Why this approach:
- It matches the current product decision to fail closed.
- It avoids hidden multi-turn complexity in the first orchestration cut.
- It keeps safety behavior easy to reason about.

Alternatives considered:
- Ask a follow-up clarification question. Deferred to a later change.

### 6. Use judge results for verification, not control

The judge model output will evaluate four checks: route correctness, tool-use correctness, policy compliance, and intent satisfaction. It must name failed checks explicitly. Judge output will be stored for verification and demo traceability, but it will not mutate workflow state or overrule the orchestrator.

Why this approach:
- It provides a structured quality signal without adding another control path.
- It avoids an "LLM judging LLM and changing behavior" feedback loop.
- It gives useful failure diagnostics for demos and future eval expansion.

Alternatives considered:
- Skip the judge and rely only on schema validation. Rejected because schema-valid responses can still miss user intent.
- Let the judge decide pass/fail and rewrite outputs. Rejected because that makes runtime state harder to trust.

## Risks / Trade-offs

- [Provider differences in structured output behavior] -> Hide providers behind strict adapter contracts and validate every model response with JSON Schema before use.
- [SQLite schema creep during MVP] -> Keep the schema minimal and aligned to current workflows: sessions, traces, approvals, review events, tickets.
- [Judge adds latency and cost] -> Make judge invocation optional or limited to demo/test modes.
- [Bounded loop still produces non-deterministic wording] -> Assert structure, route, tool sequence, and state fields in tests rather than exact prose.
- [Failing closed to handoff may reduce helpfulness] -> Record explicit handoff reasons so later clarification support can target the most common ambiguous cases.
