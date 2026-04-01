## 1. Expand CSV Seed Data

- [x] 1.1 Add 8 new customer rows to `scripts/seed_mock_data.py` (covering tags: `vip`, `new_user`, `at_risk`, and empty tags; total ≥ 10 customers)
- [x] 1.2 Add 13 new order rows covering all edge-case statuses: `pending`, `shipped/in_transit`, `delivered` (within 30 days), `delivered` (>30 days old), `cancelled` (total ≥ 15 orders)
- [x] 1.3 Add 7 new refund rows covering statuses `approved`, `rejected`, `pending_review`; include at least one refund linked to an in-transit order and one linked to a >30-day delivered order (total ≥ 8 refunds)
- [x] 1.4 Annotate edge-case rows with inline comments in the seed script (e.g., `# edge: in-transit address change`, `# edge: >30-day refund window`)
- [x] 1.5 Verify no `customer_id` or `order_id` collides with identifiers used in `specs/06_eval_cases.jsonl`

## 2. Build KB Article Set

- [x] 2.1 Create `data/kb/` directory and migrate existing 3 stubs from `data/sample_kb/` (refund_policy.md, shipping_delay.md, address_change.md) — update content to include edge cases
- [x] 2.2 Write KB articles for: cancellation policy, partial refund policy, return window (opened items), order tracking (normal flow)
- [x] 2.3 Write KB articles for: late delivery complaint, damaged item policy, wrong item received, missing package investigation
- [x] 2.4 Write KB articles for: account suspension, password reset, duplicate order, payment failure
- [x] 2.5 Write KB articles for: escalation triggers (when to escalate), human review process, VIP customer SLA, high-priority ticket criteria
- [x] 2.6 Write KB articles for: international shipping policy, delivery estimate FAQ, carrier contact info, holiday delay notice
- [x] 2.7 Write KB articles for: exchange policy, gift card refund policy, bulk order support, subscription cancellation (total ≥ 20, target 25–28 articles)
- [x] 2.8 Verify all articles start with a `# ` heading on the first line and contain no YAML frontmatter
- [x] 2.9 Cross-check that numeric thresholds are consistent across all articles (14-day refund window, 5-day shipping escalation threshold, 30-day ineligibility cutoff)

## 3. Update Seed Script Entrypoint

- [x] 3.1 Update `scripts/seed_mock_data.py` to write KB articles to `data/kb/` in addition to CSVs (inline the article content or write from a `data/kb/` source directory)
- [x] 3.2 Add summary output: print row counts per CSV and article count written (e.g., `"Seeded 10 customers, 15 orders, 8 refunds. Wrote 25 KB articles to data/kb/"`)
- [x] 3.3 Ensure the script is idempotent (overwrites existing files, does not append duplicates on re-run)

## 4. Update Tool KB Path Reference

- [x] 4.1 Check `app/tools.py` for hardcoded `data/sample_kb` path; update to `data/kb` if needed
- [x] 4.2 Confirm `search_kb` tool still returns valid hits after path change by running a manual smoke test query

## 5. Verification

- [x] 5.1 Run `python scripts/seed_mock_data.py` from project root and confirm all files are generated without error
- [x] 5.2 Run `python scripts/seed_mock_data.py` a second time and confirm output is identical (idempotency check)
- [x] 5.3 Confirm `data/customers.csv` has ≥ 10 rows, `data/orders.csv` has ≥ 15 rows, `data/refunds.csv` has ≥ 8 rows
- [x] 5.4 Confirm `data/kb/` contains ≥ 20 `.md` files, all starting with `# `
- [x] 5.5 Run `python scripts/validate_day1_artifacts.py` (if applicable) and confirm no regressions
- [x] 5.6 Run `python scripts/run_eval.py` against existing eval cases to confirm no tool contract regressions from the data changes
