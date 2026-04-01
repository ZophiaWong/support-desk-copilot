# kb-articles Specification

## Purpose
TBD - created by archiving change build-simulated-data-and-kb. Update Purpose after archive.
## Requirements
### Requirement: KB directory contains 20–30 markdown articles covering all support domains
The system SHALL provide a `data/kb/` directory containing between 20 and 30 markdown files. Articles MUST cover at minimum these domains: refund policy, return window, shipping delays, address change, order cancellation, order status tracking, account issues, escalation triggers, and partial refund policy.

#### Scenario: search_kb returns results for a refund query
- **WHEN** `search_kb` is called with query `"can I get a refund on an unopened item"`
- **THEN** at least one hit references the refund policy article with a relevant snippet

#### Scenario: search_kb returns results for a cancellation query
- **WHEN** `search_kb` is called with query `"cancel my order"`
- **THEN** at least one hit references a cancellation policy article

#### Scenario: search_kb returns results for an escalation query
- **WHEN** `search_kb` is called with query `"tracking not updated for 5 days"`
- **THEN** at least one hit references the shipping delay or escalation policy article

### Requirement: KB articles contain policy-specific edge case content
Each KB article that covers a policy domain with numeric thresholds SHALL include the exact threshold value (e.g., "14 calendar days", "30 days", "5 days"). Articles MUST be internally consistent — the same threshold MUST NOT appear with different values across articles.

#### Scenario: Refund window is consistently 14 days across all KB articles
- **WHEN** any KB article mentions the standard refund window
- **THEN** the window is stated as 14 calendar days

#### Scenario: Shipping delay escalation threshold is consistently 5 days
- **WHEN** any KB article references the threshold for escalating a shipping delay
- **THEN** the threshold is stated as 5 days without tracking update

### Requirement: KB articles use consistent markdown format with title as first heading
Each KB article SHALL begin with a level-1 markdown heading (`# Title`) as the first line. The article SHALL be plain markdown without YAML frontmatter.

#### Scenario: All KB articles have a top-level heading
- **WHEN** the seed script generates or copies KB articles to `data/kb/`
- **THEN** every `.md` file in `data/kb/` starts with a `# ` heading on the first line

