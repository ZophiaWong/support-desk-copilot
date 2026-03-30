## ADDED Requirements

### Requirement: Day 1 scope freeze policy
The project MUST define and adopt a Day 1 scope freeze baseline that finalizes PRD boundaries, finalizes 12-15 user stories, and prohibits adding new core features after Day 1 completion.

#### Scenario: Scope freeze activated at Day 1 exit
- **WHEN** Day 1 deliverables are marked complete
- **THEN** the project records a no-new-core-feature rule as an active planning constraint

#### Scenario: Change request after freeze
- **WHEN** a proposal introduces a new core feature after Day 1
- **THEN** the request is rejected from the active implementation scope unless a separate approved change explicitly updates the freeze baseline

### Requirement: Risky action inventory is mandatory
The project MUST maintain an explicit list of risky actions, including refund, address change, and cancellation, as part of the Day 1 freeze baseline.

#### Scenario: Baseline validation
- **WHEN** Day 1 artifacts are reviewed
- **THEN** the risky action inventory explicitly includes refund, address change, and cancellation
