## Why

The project needs a hard Day 1 baseline so implementation can proceed without scope churn and inconsistent behavior targets. Freezing scope now reduces delivery risk for deterministic tool orchestration, approval-gated sensitive actions, and reproducible evaluations.

## What Changes

- Finalize and freeze a Day 1 scope package aligned to `specs/09_implementation_plan.md`:
- Finalize PRD boundaries for MVP and explicitly lock out new core features after Day 1.
- Finalize 12-15 user stories that define the MVP interaction surface.
- Freeze the 5 core tools and their JSON contracts (`search_kb`, `lookup_customer`, `lookup_order`, `propose_action`, `create_or_escalate_ticket`).
- Define 3 golden demo flows as canonical end-to-end behavior targets.
- Draft the first 20 offline evaluation cases as an initial reproducibility baseline.
- Add explicit non-goals for Day 1:
- No UI polish/features beyond what is required for demo flow validation.
- No new core tool categories beyond the frozen 5.
- No execution path that bypasses approval gating for sensitive actions.
- Record risky actions and approval-gate requirements as mandatory acceptance criteria for downstream implementation.

## Capabilities

### New Capabilities
- `scope-freeze-baseline`: Defines Day 1 scope freeze rules, PRD/story lock, and no-new-core-feature policy.
- `tool-contract-freeze`: Defines fixed JSON contracts and invariants for the 5 core tools.
- `golden-demo-flows`: Defines 3 canonical demo flows and pass/fail criteria.
- `eval-seed-cases`: Defines initial 20 eval cases and reproducibility constraints.

### Modified Capabilities
- None.

## Impact

- Specs and planning artifacts:
- `specs/09_implementation_plan.md`
- New OpenSpec artifacts under `openspec/changes/freeze-scope-and-write-specs/`
- Runtime and contract surfaces to be constrained by this change:
- `app/` (routing/orchestration behavior constrained by frozen scope)
- `app/tools/` or equivalent tool layer modules (must conform to frozen JSON contracts)
- `tests/` (must validate contract stability, approval-gate behavior, and deterministic outcomes)
- `data/` and `docs/` (demo-flow assumptions and policy evidence)
- Safety/approval implications:
- Sensitive actions (refund/address/cancel) remain approval-gated and must not be directly executed from model output.
- Golden flows and eval cases must include explicit checks that approval state is enforced and traceable.
