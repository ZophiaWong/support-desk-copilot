# Demo Script

## Flow 1: Policy QA
User asks: "What is the refund window for unopened items?"
Expected:
- tool: search_kb
- answer with citation
- no approval

## Flow 2: Order lookup
User asks: "Where is order ord_2001?"
Expected:
- tool: lookup_order
- answer with shipping status
- no fabricated facts

## Flow 3: Sensitive action
User asks: "Refund my shipped order."
Expected:
- lookup_order
- propose_action
- state shows needs_human_approval

## Flow 4: Handoff
User asks a vague or unsupported question.
Expected:
- create_or_escalate_ticket
- structured handoff summary
