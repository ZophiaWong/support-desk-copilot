## ADDED Requirements

### Requirement: Initial offline eval set contains 20 cases
The project MUST define at least 20 initial offline eval cases as the Day 1 baseline for reproducible behavior checks.

#### Scenario: Eval baseline count
- **WHEN** Day 1 eval artifacts are validated
- **THEN** the offline eval set contains 20 or more uniquely identified cases

### Requirement: Eval set covers safety and routing risks
The initial eval set MUST include coverage for tool selection, retrieval quality, approval gating, and risky-action handling.

#### Scenario: Coverage validation
- **WHEN** eval categories are reviewed
- **THEN** the set includes at least one case for each category: tool selection, retrieval quality, approval gating, and risky-action handling

### Requirement: Eval cases are reproducible
Each eval case MUST define deterministic inputs, expected behavior criteria, and a stable pass/fail interpretation that does not depend on online services.

#### Scenario: Reproducibility check
- **WHEN** the same eval case is executed in the same local environment
- **THEN** it yields the same pass/fail result under unchanged data and code
