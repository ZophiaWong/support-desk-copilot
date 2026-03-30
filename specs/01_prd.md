# Product Requirements Document

## Product name
SupportDesk Copilot

## Goal
Build a support copilot for a simulated e-commerce company that helps agents handle FAQ, order lookup, refund/cancel requests, and escalation.

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

## Success criteria
- Answer policy questions with evidence
- Use tools for customer/order facts
- Convert sensitive actions into approval proposals
- Escalate correctly when information is insufficient
- Produce observable traces for debugging
