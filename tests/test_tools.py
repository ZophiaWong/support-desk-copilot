import pytest

from app.exceptions import ToolNotFoundError
from app.schemas import (
    CreateOrEscalateTicketOutput,
    LookupCustomerOutput,
    LookupOrderOutput,
    ProposeActionOutput,
    SearchKbOutput,
)
from app.tools import (
    create_or_escalate_ticket,
    lookup_customer,
    lookup_order,
    propose_action,
    search_kb,
)


def test_search_kb_returns_hits():
    result = search_kb("refund")
    validated = SearchKbOutput.model_validate(result)
    assert validated.tool == "search_kb"
    assert len(validated.hits) >= 1


def test_lookup_customer_has_customer():
    result = lookup_customer("alice@example.com")
    validated = LookupCustomerOutput.model_validate(result)
    assert validated.customer.customer_id == "cust_5001"
    assert validated.customer.tags == ["vip"]


def test_lookup_order_has_status():
    result = lookup_order("ord_5102")
    validated = LookupOrderOutput.model_validate(result)
    assert validated.order.status == "shipped"
    assert validated.order.shipping_status == "in_transit"


def test_propose_action_requires_approval():
    result = propose_action("refund_request", {"order_id": "ord_5102"})
    validated = ProposeActionOutput.model_validate(result)
    assert validated.status == "needs_human_approval"
    assert validated.approval_id == "apr_1"


def test_create_or_escalate_ticket_returns_ticket():
    result = create_or_escalate_ticket("insufficient_information", "medium", "Need manual review")
    validated = CreateOrEscalateTicketOutput.model_validate(result)
    assert validated.status == "escalated"
    assert validated.ticket_id == "tkt_1"


def test_lookup_customer_not_found_raises() -> None:
    with pytest.raises(ToolNotFoundError):
        lookup_customer("missing@example.com")


def test_lookup_order_not_found_raises() -> None:
    with pytest.raises(ToolNotFoundError):
        lookup_order("ord_9999")


def test_search_kb_refund_query_returns_refund_article() -> None:
    result = search_kb("refund")
    titles = [hit["title"].lower() for hit in result["hits"]]
    article_ids = [hit["article_id"] for hit in result["hits"]]
    assert any("refund" in title for title in titles)
    assert "refund_policy" in article_ids
