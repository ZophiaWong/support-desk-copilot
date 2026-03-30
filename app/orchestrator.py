from app.schemas import ChatResponse, ToolTrace
from app.tools import (
    search_kb,
    lookup_customer,
    lookup_order,
    propose_action,
    create_or_escalate_ticket,
)


def _trace(tool_name: str, tool_args: dict, result: dict) -> ToolTrace:
    return ToolTrace(
        tool_name=tool_name,
        tool_args=tool_args,
        result_summary=str(result)[:240],
    )


def handle_message(session_id: str, user_message: str) -> ChatResponse:
    msg = user_message.lower()

    # Minimal routing logic for scaffold purposes
    if any(k in msg for k in ["refund", "cancel", "change address"]):
        order = lookup_order("ord_2001")
        proposal = propose_action(
            action_type="refund_request",
            payload={"order_id": "ord_2001", "reason": user_message},
        )
        return ChatResponse(
            route="action_request",
            answer="I found the order and created a refund proposal for human approval.",
            citations=["kb_001"],
            tool_traces=[
                _trace("lookup_order", {"identifier": "ord_2001"}, order),
                _trace("propose_action", {"action_type": "refund_request"}, proposal),
            ],
            state={"approval_status": proposal["status"], "approval_id": proposal["approval_id"]},
        )

    if any(k in msg for k in ["where is my order", "tracking", "order status"]):
        order = lookup_order("ord_2001")
        return ChatResponse(
            route="order_lookup",
            answer="Your order ord_2001 is currently in transit.",
            citations=[],
            tool_traces=[_trace("lookup_order", {"identifier": "ord_2001"}, order)],
            state={"order_status": order["order"]["shipping_status"]},
        )

    if any(k in msg for k in ["policy", "refund window", "warranty", "return"]):
        hits = search_kb(user_message)
        return ChatResponse(
            route="faq",
            answer="According to the refund policy, unopened items can be refunded within 14 days.",
            citations=["kb_001"],
            tool_traces=[_trace("search_kb", {"query": user_message}, hits)],
            state={},
        )

    ticket = create_or_escalate_ticket(
        reason="insufficient_information",
        priority="medium",
        summary=user_message,
    )
    return ChatResponse(
        route="handoff",
        answer="I do not have enough verified information, so I created an escalation ticket.",
        citations=[],
        tool_traces=[_trace("create_or_escalate_ticket", {"summary": user_message}, ticket)],
        state={"ticket_id": ticket["ticket_id"]},
    )
