# Day 1 Verification Checklist

## Exit criteria checklist

- [x] No new core features added after Day 1 freeze baseline was recorded.
- [x] PRD boundaries finalized and linked.
- [x] 12-15 user stories finalized (13 stories present).
- [x] 5 tools and JSON contracts frozen.
- [x] 3 golden demo flows defined.
- [x] 20 eval seed cases defined.
- [x] All risky actions identified (refund, address change, cancellation).
- [x] Demo flow is stable on paper with expected traces and approval states.

## Verification commands

- `python scripts/validate_day1_artifacts.py`
- `python scripts/run_eval.py --validate-only`
- `pytest -q`
