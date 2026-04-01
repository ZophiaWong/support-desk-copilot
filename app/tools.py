from typing import Any

from app import data_access
from app.exceptions import ToolValidationError


def search_kb(query: str) -> dict[str, Any]:
    return {
        "tool": "search_kb",
        "hits": data_access.search_kb(query),
    }


def lookup_customer(identifier: str) -> dict[str, Any]:
    return {
        "tool": "lookup_customer",
        "customer": data_access.find_customer(identifier),
    }


def lookup_order(identifier: str) -> dict[str, Any]:
    order = data_access.find_order(identifier)
    if isinstance(order, list):
        raise ToolValidationError(
            "lookup_order",
            f"Identifier '{identifier}' matched multiple orders; provide an order_id instead.",
        )
    return {
        "tool": "lookup_order",
        "order": {
            "order_id": order["order_id"],
            "status": order["status"],
            "shipping_status": order["shipping_status"],
            "total_amount": order["total_amount"],
        },
    }


def propose_action(action_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    proposal = data_access.store_proposal(action_type, payload)
    return {"tool": "propose_action", **proposal}


def create_or_escalate_ticket(reason: str, priority: str, summary: str) -> dict[str, Any]:
    ticket = data_access.store_ticket(reason, priority, summary)
    return {"tool": "create_or_escalate_ticket", **ticket}
