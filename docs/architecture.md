# Architecture

## Goal
Build a support copilot that is:
- explainable
- safe for sensitive actions
- measurable
- easy to demo

## Request flow
1. User asks a question
2. Router decides between FAQ / order lookup / action request / handoff
3. Orchestrator calls tools
4. Sensitive actions are converted into proposals
5. Response includes final answer + citations + tool trace + state

## Future production upgrades
- replace local stubs with PostgreSQL/pgvector
- add approval queue table
- add retrieval reranker
- add structured trace storage
- add role-based access control
