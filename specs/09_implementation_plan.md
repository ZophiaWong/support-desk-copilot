# Detailed Implementation Plan

## Day 1 — Freeze scope and write specs
Deliverables:
- finalize PRD
- finalize 12–15 user stories
- freeze 5 tools and their JSON contracts
- define 3 golden demo flows
- draft first 20 eval cases

Exit criteria:
- no new core features added after today
- all risky actions identified
- demo flow is stable on paper

## Day 2 — Build simulated data and KB
Deliverables:
- seed customers/orders/refunds CSVs
- write 20–30 KB docs
- define policy edge cases
- load sample data into local store

Exit criteria:
- one command can recreate local environment
- at least 3 edge cases are represented in data

## Day 3 — Implement tool layer first
Deliverables:
- search_kb
- lookup_customer
- lookup_order
- propose_action
- create_or_escalate_ticket
- tool unit tests

Exit criteria:
- tools pass tests without any LLM involved
- tool responses are stable JSON

## Day 4 — Add orchestration
Deliverables:
- route selection
- prompt policy wiring
- response composer
- approval state handling
- handoff logic

Exit criteria:
- 3 happy-path demos run end-to-end
- no sensitive action is directly executed

## Day 5 — Demo surface and tracing
Deliverables:
- minimal UI or API demo page
- trace storage fields
- response state view
- approval panel mock

Exit criteria:
- every response shows tool trace
- you can screen-record the workflow

## Day 6 — Eval and failure analysis
Deliverables:
- expand eval set to 35–40 cases
- run baseline
- identify top 5 failures
- fix the top 3 failure modes

Exit criteria:
- you have before/after notes
- metrics are reproducible

## Day 7 — Job packaging
Deliverables:
- README cleanup
- architecture diagram
- resume bullets
- interview talking points
- 3-minute demo recording

Exit criteria:
- project is shareable
- you can explain design trade-offs without looking at notes
