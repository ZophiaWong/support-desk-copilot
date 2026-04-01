from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd
from rank_bm25 import BM25Okapi

from app.config import settings
from app.exceptions import ToolNotFoundError

_proposal_counter = 0
_ticket_counter = 0
_proposals: dict[str, dict[str, Any]] = {}
_tickets: dict[str, dict[str, Any]] = {}


def _tokenize(text: str) -> list[str]:
    return [token for token in text.lower().split() if token]


@lru_cache(maxsize=1)
def _load_customers() -> pd.DataFrame:
    path = settings.data_dir / "customers.csv"
    return pd.read_csv(path).fillna("")


@lru_cache(maxsize=1)
def _load_orders() -> pd.DataFrame:
    path = settings.data_dir / "orders.csv"
    return pd.read_csv(path)


@lru_cache(maxsize=1)
def _build_kb_index() -> tuple[BM25Okapi, list[dict[str, str]]]:
    kb_dir = settings.data_dir / "kb"
    documents: list[dict[str, str]] = []
    corpus: list[list[str]] = []

    for path in sorted(kb_dir.glob("*.md")):
        raw = path.read_text(encoding="utf-8").strip()
        lines = raw.splitlines()
        title = path.stem.replace("_", " ").title()
        body_lines = lines
        if lines and lines[0].startswith("# "):
            title = lines[0][2:].strip()
            body_lines = lines[1:]
        snippet = " ".join(line.strip() for line in body_lines if line.strip())
        documents.append({"article_id": path.stem, "title": title, "snippet": snippet})
        corpus.append(_tokenize(f"{title} {snippet}"))

    return BM25Okapi(corpus), documents


def find_customer(identifier: str) -> dict[str, Any]:
    customers = _load_customers()
    matches = customers[customers["customer_id"] == identifier]
    if matches.empty:
        normalized = identifier.lower()
        matches = customers[customers["email"].str.lower() == normalized]
    if matches.empty:
        raise ToolNotFoundError("lookup_customer", f"No customer found for identifier '{identifier}'")

    record = matches.iloc[0]
    raw_tags = str(record["tags"]).strip()
    tags = [tag for tag in raw_tags.split(",") if tag]
    return {
        "customer_id": str(record["customer_id"]),
        "email": str(record["email"]),
        "tags": tags,
    }


def find_order(identifier: str) -> dict[str, Any] | list[dict[str, Any]]:
    orders = _load_orders()
    if identifier.startswith("ord_"):
        matches = orders[orders["order_id"] == identifier]
        if matches.empty:
            raise ToolNotFoundError("lookup_order", f"No order found for identifier '{identifier}'")
        record = matches.iloc[0]
        return {
            "order_id": str(record["order_id"]),
            "customer_id": str(record["customer_id"]),
            "status": str(record["status"]),
            "shipping_status": str(record["shipping_status"]),
            "total_amount": float(record["total_amount"]),
        }

    matches = orders[orders["customer_id"] == identifier]
    if matches.empty:
        raise ToolNotFoundError("lookup_order", f"No order found for identifier '{identifier}'")

    return [
        {
            "order_id": str(record["order_id"]),
            "customer_id": str(record["customer_id"]),
            "status": str(record["status"]),
            "shipping_status": str(record["shipping_status"]),
            "total_amount": float(record["total_amount"]),
        }
        for _, record in matches.iterrows()
    ]


def search_kb(query: str, top_k: int = 3) -> list[dict[str, str]]:
    bm25, documents = _build_kb_index()
    tokens = _tokenize(query)
    if not tokens:
        return []

    scores = bm25.get_scores(tokens)
    ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
    hits: list[dict[str, str]] = []
    for index, score in ranked:
        if score <= 0:
            continue
        hits.append(documents[index])
        if len(hits) >= top_k:
            break
    return hits


def store_proposal(action_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    global _proposal_counter
    _proposal_counter += 1
    approval_id = f"apr_{_proposal_counter}"
    proposal = {
        "approval_id": approval_id,
        "action_type": action_type,
        "status": "needs_human_approval",
        "payload": payload,
    }
    _proposals[approval_id] = proposal
    return proposal


def store_ticket(reason: str, priority: str, summary: str) -> dict[str, Any]:
    global _ticket_counter
    _ticket_counter += 1
    ticket_id = f"tkt_{_ticket_counter}"
    ticket = {
        "ticket_id": ticket_id,
        "status": "escalated",
        "priority": priority,
        "summary": summary,
        "reason": reason,
    }
    _tickets[ticket_id] = ticket
    return ticket


def reset_state() -> None:
    global _proposal_counter, _ticket_counter
    _proposal_counter = 0
    _ticket_counter = 0
    _proposals.clear()
    _tickets.clear()
    _load_customers.cache_clear()
    _load_orders.cache_clear()
    _build_kb_index.cache_clear()
