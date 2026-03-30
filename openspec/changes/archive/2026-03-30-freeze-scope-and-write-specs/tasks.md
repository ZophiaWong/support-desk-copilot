## 1. Scope Freeze Baseline

- [x] 1.1 Finalize Day 1 PRD boundary statements in `specs/` and explicitly document no-new-core-feature policy after Day 1.
- [x] 1.2 Finalize and list 12-15 MVP user stories in a single canonical Day 1 artifact under `specs/`.
- [x] 1.3 Create a risky-action inventory (refund, address change, cancellation) and link it from Day 1 scope artifacts.
- [x] 1.4 Add a verification checklist that confirms Day 1 exit criteria are met before implementation proceeds.

## 2. Tool Contract Freeze

- [x] 2.1 Define canonical JSON input/output contracts for `search_kb`, `lookup_customer`, `lookup_order`, `propose_action`, and `create_or_escalate_ticket` in repo docs/spec artifacts.
- [x] 2.2 Define shared error envelope and required field/type invariants for all five tools.
- [x] 2.3 Add/adjust Pydantic schema stubs in `app/` to match frozen contracts without adding new tool categories.
- [x] 2.4 Add contract validation tests in `tests/` that fail on field add/remove/rename without spec updates.

## 3. Golden Demo Flows

- [x] 3.1 Document exactly three golden demo flows with ordered user intent, tool calls, and expected final response state.
- [x] 3.2 Ensure at least one golden flow contains a sensitive action and explicitly shows approval-gate handling before action finalization.
- [x] 3.3 Define expected tool-trace evidence for each golden flow so demo outputs are explainable.
- [x] 3.4 Add a lightweight demo-flow validation test/check script in `scripts/` or `tests/` that verifies flow definitions are complete.

## 4. Eval Seed Cases

- [x] 4.1 Create the first 20 offline eval cases with stable identifiers and deterministic inputs.
- [x] 4.2 Tag eval cases for coverage across tool selection, retrieval quality, approval gating, and risky-action handling.
- [x] 4.3 Define pass/fail criteria per case and ensure criteria are executable offline.
- [x] 4.4 Add or update a local eval runner command in `scripts/` that can execute the Day 1 eval seed set reproducibly.

## 5. Integration and Verification

- [x] 5.1 Cross-check all Day 1 artifacts to ensure no requirement introduces a new core feature beyond frozen scope.
- [x] 5.2 Verify approval-gate constraints are consistently reflected across contracts, golden flows, and eval cases.
- [x] 5.3 Run relevant tests/eval commands and record outputs in Day 1 notes (for example: `pytest -q`, eval runner command).
- [x] 5.4 Update `README.md` and/or `docs/` with links to frozen scope artifacts, contract sources, and verification commands.
