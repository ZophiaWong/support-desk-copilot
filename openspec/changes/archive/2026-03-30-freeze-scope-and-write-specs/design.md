## Context

The Day 1 plan in `specs/09_implementation_plan.md` requires freezing scope and producing stable, testable artifacts before implementation begins. Current repository content includes implementation intent and high-level planning, but lacks a formalized OpenSpec contract that locks capabilities, tool interfaces, golden flows, and eval seed requirements. Without this freeze, downstream development in `app/`, `tests/`, and `data/` can diverge.

Constraints:
- Keep MVP limited to the existing 5-tool architecture.
- Preserve deterministic behavior and reproducibility for offline eval.
- Enforce approval gating for sensitive actions (refund/address/cancel).

## Goals / Non-Goals

**Goals:**
- Define a concrete scope-freeze policy that blocks new core features after Day 1.
- Freeze JSON contracts for the 5 core tools and define contract invariants.
- Define 3 golden demo flows as canonical acceptance targets.
- Define the first 20 eval cases and reproducibility expectations.
- Ensure all artifacts explicitly encode approval-gate and safety checks.

**Non-Goals:**
- Implementing runtime orchestration, tools, or UI in this change.
- Expanding beyond the 5 core tools.
- Finalizing full benchmark coverage beyond initial 20 eval cases.
- Addressing optimization/performance tuning outside correctness and reproducibility.

## Decisions

1. Decision: Model Day 1 freeze as four separate capabilities.
- Rationale: Separating policy (`scope-freeze-baseline`), contracts (`tool-contract-freeze`), demos (`golden-demo-flows`), and evaluation (`eval-seed-cases`) keeps requirements modular and testable.
- Alternative considered: One monolithic spec file.
- Why not chosen: Harder to trace ownership and validate completeness across artifacts.

2. Decision: Express all behavior with normative SHALL/MUST requirements and scenario-based acceptance criteria.
- Rationale: OpenSpec archive/apply and later test mapping are clearer when every requirement has explicit WHEN/THEN scenarios.
- Alternative considered: Narrative-only acceptance section.
- Why not chosen: Less precise and harder to convert into automated checks.

3. Decision: Encode approval-gate checks in both golden-flow and eval-case capabilities.
- Rationale: Safety needs two layers: demo acceptance (visible behavior) and regression evaluation (repeatable checks).
- Alternative considered: Keep approval-gate rules only in tool contracts.
- Why not chosen: Contract checks alone do not guarantee orchestration-level behavior.

4. Decision: Keep references repo-relative and implementation-targeted (`app/`, `tests/`, `data/`, `specs/`).
- Rationale: Reduces ambiguity for follow-up task generation and implementation.
- Alternative considered: Tool-agnostic architecture statements.
- Why not chosen: Not actionable enough for immediate Day 2-Day 4 execution.

## Risks / Trade-offs

- [Risk] Scope freeze is too rigid and blocks necessary course correction. → Mitigation: permit clarifications/bug fixes that do not add new core features.
- [Risk] Tool contract freeze misses edge-case fields discovered during implementation. → Mitigation: require explicit change proposal to modify contracts, with backward-compatibility analysis.
- [Risk] Golden flows may pass while non-demo paths fail. → Mitigation: pair golden flows with eval seed requirements and expand cases on Day 6.
- [Risk] Initial 20 eval cases may underrepresent failure modes. → Mitigation: enforce risk-category coverage and planned expansion to 35-40 cases.

## Migration Plan

1. Land this OpenSpec change with proposal/design/specs/tasks artifacts complete.
2. Use generated tasks as the implementation backlog for Day 1 completion.
3. During implementation (`/opsx:apply`), enforce that no new core capability enters scope without a separate change.
4. If a rollback is needed, revert the change directory and restore previous planning docs; do not partially retain frozen contracts without corresponding specs.

## Open Questions

- Where should the canonical frozen tool JSON contracts live after apply (`specs/`, `docs/`, or `app/schemas/` as source of truth)?
- Should golden flow fixtures be represented as markdown scenarios only or also as machine-readable YAML/JSON in Day 1?
- Which exact risk taxonomy should label the first 20 eval cases (policy, retrieval, tool-selection, approval, traceability)?
