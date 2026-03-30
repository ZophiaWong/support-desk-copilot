# Day 1 Implementation Notes

Date: 2026-03-30

## Scope freeze checks

- Confirmed no new core tools were introduced beyond:
  - `search_kb`
  - `lookup_customer`
  - `lookup_order`
  - `propose_action`
  - `create_or_escalate_ticket`
- Added explicit no-new-core-feature policy in `specs/10_day1_scope_freeze.md`.
- Finalized Day 1 artifacts:
  - PRD scope boundary in `specs/01_prd.md`
  - 13 frozen user stories in `specs/02_user_stories.md`
  - risky action inventory in `specs/11_risky_actions.md`
  - Day 1 checklist in `specs/12_day1_verification.md`

## Approval-gate consistency checks

- `specs/11_risky_actions.md` mandates approval for refund/address/cancel.
- `specs/05_tool_contracts/propose_action.json` enforces output `status=needs_human_approval`.
- `specs/07_demo_script.md` Flow 3 requires proposal path with approval ID.
- `specs/06_eval_cases.jsonl` includes approval-gating and risky-action categories.

## Verification command outputs

### 1) Artifact validation
Command:
`python scripts/validate_day1_artifacts.py`

Output:
`Day 1 artifact validation passed.`

### 2) Eval seed validation
Command:
`python scripts/run_eval.py --validate-only`

Output summary:
- Loaded 20 eval cases
- approval_gating: 4
- retrieval_quality: 4
- risky_action_handling: 4
- tool_selection: 8
- Validation-only mode complete

### 3) Test suite
Command:
`PYTHONPATH=. pytest -q`

Output:
`7 passed in 0.01s`

## Notes

- Plain `pytest -q` failed in this environment because `app` was not on import path.
- Using `PYTHONPATH=.` resolves the local package import for test execution.
