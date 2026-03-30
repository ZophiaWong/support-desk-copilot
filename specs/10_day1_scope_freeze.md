# Day 1 Scope Freeze Baseline

Reference:
- `specs/09_implementation_plan.md` (Day 1 section)

## Frozen core scope
- Finalized PRD boundaries for MVP are recorded in `specs/01_prd.md`.
- Finalized user stories are recorded in `specs/02_user_stories.md` (13 stories).
- Core tools are frozen to:
  - `search_kb`
  - `lookup_customer`
  - `lookup_order`
  - `propose_action`
  - `create_or_escalate_ticket`
- Golden demos are frozen to exactly three flows in `specs/07_demo_script.md`.
- Eval baseline is frozen to the first 20 cases in `specs/06_eval_cases.jsonl`.

## No-new-core-feature policy
After Day 1 freeze, no new core capability/tool category can be added to MVP without a new approved OpenSpec change.

Allowed after freeze:
- bug fixes
- wording clarifications
- tests/docs improvements
- implementation details that do not alter frozen capability scope

Not allowed after freeze (without spec change):
- new core tool category
- bypassing approval gate for risky actions
- replacing golden flow goals with different primary workflows

## Links
- Risky action inventory: `specs/11_risky_actions.md`
- Day 1 verification checklist: `specs/12_day1_verification.md`
- Tool contracts: `specs/05_tool_contracts/`
