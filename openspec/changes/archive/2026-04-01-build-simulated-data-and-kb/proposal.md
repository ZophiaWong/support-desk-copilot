## Why

The tool layer and eval harness require realistic, edge-case-rich fixture data and a substantial KB to produce meaningful outputs and test routing decisions. The current seed (`scripts/seed_mock_data.py`) has only 2 customers, 2 orders, and 1 refund — not enough to cover the 3+ policy edge cases required by Day 2 exit criteria.

## What Changes

- **Expand `scripts/seed_mock_data.py`**: grow CSVs from 2 rows to ~10 customers, ~15 orders, ~8 refunds, covering edge cases (in-transit orders, >30-day deliveries, VIP tags, missing data)
- **Add `data/kb/` directory with 20–30 markdown KB articles**: expand beyond the 3 existing stubs (`refund_policy.md`, `shipping_delay.md`, `address_change.md`) with articles covering cancellation, order tracking, returns, account issues, and escalation policies
- **Document policy edge cases inline** in KB articles (e.g., partial refund, late refund window, address change on unshipped vs. in-transit orders)
- **Add `scripts/load_data.py`** (or extend seed script) so a single command recreates the full local environment
- **No changes to tool contracts, routing logic, or app code** — data layer only

## Capabilities

### New Capabilities

- `simulated-customer-data`: Expanded customer/order/refund CSV fixtures with realistic edge cases for eval and tool testing
- `kb-articles`: 20–30 markdown KB articles covering all support policy domains used by `search_kb`

### Modified Capabilities

- `seed-data-loader`: Existing `scripts/seed_mock_data.py` extended to produce richer fixture data and remain the single entrypoint for environment recreation

## Impact

- `scripts/seed_mock_data.py`: extended with more rows and edge-case records
- `data/customers.csv`, `data/orders.csv`, `data/refunds.csv`: regenerated with richer fixture set
- `data/kb/` (new subdirectory): 20–30 `.md` articles added
- `data/sample_kb/`: existing 3 stubs migrated into `data/kb/` or supplemented
- No changes to `app/`, `specs/05_tool_contracts/`, or eval harness schema
