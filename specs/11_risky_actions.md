# Risky Action Inventory (Day 1)

## Sensitive actions requiring human approval

1. Refund (`refund_request`)
2. Address change (`address_change`)
3. Order cancellation (`cancel_order`)

## Mandatory policy
- The model MUST NOT directly execute any risky action.
- Risky action requests MUST route through `propose_action`.
- Result state MUST include `needs_human_approval` and an `approval_id`.

## Verification links
- Golden flow coverage: `specs/07_demo_script.md` (Flow 3)
- Eval coverage: `specs/06_eval_cases.jsonl` (approval-gate cases)
- Contract shape: `specs/05_tool_contracts/propose_action.json`
