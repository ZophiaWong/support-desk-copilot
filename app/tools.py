from typing import Any


def search_kb(query: str) -> dict[str, Any]:
    # TODO: replace with real vector/BM25 retrieval
    return {
        "tool": "search_kb",
        "hits": [
            {"article_id": "kb_001", "title": "Refund Policy", "snippet": "Unopened items can be refunded within 14 days."}
        ]
    }


def lookup_customer(identifier: str) -> dict[str, Any]:
    # TODO: replace with DB lookup
    return {
        "tool": "lookup_customer",
        "customer": {
            "customer_id": "cust_1001",
            "email": "alice@example.com",
            "tags": ["vip"],
        },
    }


def lookup_order(identifier: str) -> dict[str, Any]:
    # TODO: replace with DB lookup
    return {
        "tool": "lookup_order",
        "order": {
            "order_id": "ord_2001",
            "status": "shipped",
            "shipping_status": "in_transit",
            "total_amount": 129.00,
        },
    }


def propose_action(action_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    # All sensitive actions become proposals, never direct execution
    return {
        "tool": "propose_action",
        "approval_id": "apr_3001",
        "action_type": action_type,
        "status": "needs_human_approval",
        "payload": payload,
    }


def create_or_escalate_ticket(reason: str, priority: str, summary: str) -> dict[str, Any]:
    return {
        "tool": "create_or_escalate_ticket",
        "ticket_id": "tkt_4001",
        "status": "escalated",
        "priority": priority,
        "summary": summary,
        "reason": reason,
    }
