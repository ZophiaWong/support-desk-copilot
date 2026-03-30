# SupportDesk Copilot

面向 **模拟真实电商客服场景** 的闭环工单 Agent。这个 repo 的目标不是做一个“会聊天的 FAQ bot”，而是做一个更像企业内部支持系统的 **support copilot**：

- 知识库检索
- 订单 / 用户查询
- 敏感动作提案（退款、改地址、取消订单）
- 人工审批与升级工单
- 可追踪的 tool trace 与离线评测

## Why this project is job-oriented

这个项目刻意覆盖招聘里最常见的 AI 应用能力组合：

- RAG / 检索增强
- Tool calling / API integration
- Workflow orchestration
- Human-in-the-loop / guardrails
- Evaluation / tracing / failure analysis
- FastAPI backend + demo UI

## Simulated environment statement

本项目基于 **公开对象模型 + 合成业务数据 + 规则化 KB** 搭建模拟环境，不声称接入真实企业私有数据。
你在简历里应明确写：

> Built in a simulated e-commerce support environment using public-style object definitions, synthetic orders/refunds, and reproducible offline evals.

## Repository layout

```text
support-desk-copilot/
  app/
    main.py
    config.py
    schemas.py
    tools.py
    orchestrator.py
    tracing.py
  data/
    sample_kb/
  docs/
    architecture.md
  scripts/
    seed_mock_data.py
    run_eval.py
  specs/
    00_hiring_map.md
    01_prd.md
    02_user_stories.md
    03_data_contracts.md
    04_prompt_policy.md
    05_tool_contracts/
    06_eval_cases.jsonl
    07_demo_script.md
    08_metrics.md
  tests/
    test_tools.py
  .env.example
  requirements.txt
```

## Tech stack

- Backend: FastAPI
- Storage: PostgreSQL/pgvector for real build, SQLite + local files for MVP scaffold
- Retrieval: vector store abstraction (you can swap to pgvector/Qdrant/FAISS later)
- Demo UI: Streamlit or a tiny frontend
- Eval: JSONL cases + simple runner

## MVP scope

只保留 5 个核心工具：

1. `search_kb`
2. `lookup_customer`
3. `lookup_order`
4. `propose_action`
5. `create_or_escalate_ticket`

## Day 1 frozen artifacts

- Scope freeze baseline: `specs/10_day1_scope_freeze.md`
- Risky action inventory: `specs/11_risky_actions.md`
- Verification checklist: `specs/12_day1_verification.md`
- Tool contracts: `specs/05_tool_contracts/*.json`
- Golden demo flows: `specs/07_demo_script.md`
- Eval seed set (20): `specs/06_eval_cases.jsonl`
- Implementation notes and verification outputs: `docs/day1_implementation_notes.md`

Verification commands:

```bash
python scripts/validate_day1_artifacts.py
python scripts/run_eval.py --validate-only
PYTHONPATH=. pytest -q
```

## What makes this more credible than a toy demo

- 敏感动作不直接执行，只返回 `needs_human_approval`
- 订单/客户查询不让 LLM 瞎编，必须走工具
- 所有输出保留 evidence / trace
- 有固定离线 eval cases，而不是“感觉差不多能用”

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/seed_mock_data.py
uvicorn app.main:app --reload
```

## Resume bullets (editable)

- Built a support copilot in a simulated e-commerce environment, integrating knowledge retrieval, order lookup, structured action proposals, and human escalation workflows.
- Designed JSON-schema based tools and approval gates for sensitive actions such as refunds and address changes, preventing direct execution by the model.
- Created a reproducible offline eval set to measure routing accuracy, tool selection quality, citation coverage, and unsafe-action blocking.

## What to build next

- Replace local data access with PostgreSQL/pgvector
- Add real retrieval pipeline
- Add trace viewer and approval queue UI
- Add authentication / role separation
