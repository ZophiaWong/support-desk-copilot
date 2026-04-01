# seed-data-loader Specification

## Purpose
TBD - created by archiving change build-simulated-data-and-kb. Update Purpose after archive.
## Requirements
### Requirement: Single command recreates the full local data environment
The system SHALL allow a developer to recreate all local fixture data (CSVs and KB articles) by running a single command: `python scripts/seed_mock_data.py`. The script MUST be idempotent — running it multiple times MUST produce the same output files.

#### Scenario: Running seed script produces all required data files
- **WHEN** `python scripts/seed_mock_data.py` is executed from the project root
- **THEN** `data/customers.csv`, `data/orders.csv`, `data/refunds.csv`, and all files in `data/kb/` are created or overwritten with the full fixture set

#### Scenario: Seed script is idempotent
- **WHEN** `python scripts/seed_mock_data.py` is run twice in succession
- **THEN** the second run produces byte-for-byte identical output files to the first run

#### Scenario: Seed script requires no external dependencies
- **WHEN** the seed script is executed in a fresh Python 3.12 environment with only the project's dependencies installed
- **THEN** the script completes without error and all data files are written

### Requirement: Seed script prints a summary of files written
The seed script SHALL print a human-readable summary after completion listing the number of rows written per CSV and the number of KB articles written.

#### Scenario: Seed script outputs summary on success
- **WHEN** `python scripts/seed_mock_data.py` completes successfully
- **THEN** stdout includes counts such as "Seeded N customers, M orders, K refunds" and "Wrote X KB articles to data/kb/"

