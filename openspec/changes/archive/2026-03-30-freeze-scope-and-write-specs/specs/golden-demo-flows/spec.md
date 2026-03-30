## ADDED Requirements

### Requirement: Three golden demo flows are defined
The project MUST define exactly three golden demo flows that represent canonical end-to-end customer support journeys and expected outcomes.

#### Scenario: Golden flow completeness
- **WHEN** Day 1 golden flows are reviewed
- **THEN** exactly three flows are documented with ordered user/system/tool steps and expected final response state

### Requirement: Golden flows enforce approval gating
Any golden flow containing a sensitive action MUST demonstrate that the model does not directly execute the action and instead routes through explicit approval gating.

#### Scenario: Sensitive action path in golden flow
- **WHEN** a golden flow includes refund, address change, or cancellation intent
- **THEN** the flow shows `propose_action` and approval-state handling before any action is finalized

### Requirement: Golden flows include trace expectations
Each golden flow MUST specify expected tool-trace evidence that can be surfaced in response output.

#### Scenario: Traceability in demo
- **WHEN** a golden flow completes
- **THEN** the expected output includes tool usage trace elements sufficient to explain how the answer was produced
