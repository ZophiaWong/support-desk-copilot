from app.tools import search_kb, lookup_customer, lookup_order, propose_action


def test_search_kb_returns_hits():
    result = search_kb("refund")
    assert result["tool"] == "search_kb"
    assert len(result["hits"]) >= 1


def test_lookup_customer_has_customer():
    result = lookup_customer("alice@example.com")
    assert result["customer"]["customer_id"] == "cust_1001"


def test_lookup_order_has_status():
    result = lookup_order("ord_2001")
    assert result["order"]["status"] == "shipped"


def test_propose_action_requires_approval():
    result = propose_action("refund_request", {"order_id": "ord_2001"})
    assert result["status"] == "needs_human_approval"
