# Product Requirements Document

## Product name
SupportDesk Copilot

## Goal
Build a support copilot for a simulated e-commerce company that helps agents handle FAQ, order lookup, refund/cancel requests, and escalation.

## Day 1 frozen scope boundary
This repository adopts a Day 1 scope freeze aligned with `specs/09_implementation_plan.md`.

- After Day 1, no new core tool categories are added without a new approved spec change.
- MVP remains constrained to the 5 core tools in `specs/05_tool_contracts/`.
- Sensitive actions (refund/address/cancel) are proposal-only and human approval gated.

## Target user
Internal support agents and support team leads.

## Core pains
1. FAQ lookup is slow and inconsistent.
2. Support responses may hallucinate order or policy details.
3. Sensitive actions should not be executed directly by the model.
4. Agents need structured context before escalating a case.

## Non-goals
- full CRM replacement
- real payment/refund execution
- production authentication / billing
- multilingual optimization in v1
- adding core tools beyond the frozen 5 during Day 1-Day 7 execution

## Success criteria
- Answer policy questions with evidence
- Use tools for customer/order facts
- Convert sensitive actions into approval proposals
- Escalate correctly when information is insufficient
- Produce observable traces for debugging
