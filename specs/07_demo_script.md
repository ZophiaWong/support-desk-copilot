# Demo Script (Day 1 Golden Flows)

This file intentionally defines exactly 3 golden flows.

## Flow 1: Policy QA with citation
User asks: "What is the refund window for unopened items?"

Expected sequence:
1. Route to FAQ path
2. Call `search_kb`
3. Return cited answer

Expected final state:
- `route=faq`
- `requires_human_approval=false`

Expected trace evidence:
- trace contains `tool_name=search_kb`
- trace captures query argument and at least one KB hit summary

## Flow 2: Order lookup with verified status
User asks: "Where is order ord_2001?"

Expected sequence:
1. Route to order lookup path
2. Call `lookup_order`
3. Return shipping status from tool output (no fabricated facts)

Expected final state:
- `route=order_lookup`
- `requires_human_approval=false`

Expected trace evidence:
- trace contains `tool_name=lookup_order`
- trace includes order identifier input and status in result summary

## Flow 3: Sensitive action with approval gate
User asks: "Please refund my shipped order ord_2001."

Expected sequence:
1. Route to action request path
2. Call `lookup_order`
3. Call `propose_action`
4. Return proposal status; do not execute refund directly

Expected final state:
- `route=action_request`
- `approval_status=needs_human_approval`
- `approval_id` is present

Expected trace evidence:
- traces include `lookup_order` and `propose_action`
- trace order reflects lookup before proposal
