from pathlib import Path
import csv

root = Path(__file__).resolve().parents[1]
data_dir = root / "data"
data_dir.mkdir(exist_ok=True)
kb_dir = data_dir / "kb"
kb_dir.mkdir(exist_ok=True)

customers = [
    ["customer_id", "email", "first_name", "last_name", "tags"],
    ["cust_5001", "alice@example.com", "Alice", "Wang", "vip"],  # edge: VIP customer
    ["cust_5002", "bob@example.com", "Bob", "Li", "new_user"],  # edge: first purchase
    ["cust_5003", "carol@example.com", "Carol", "Chen", "at_risk"],  # edge: churn risk
    ["cust_5004", "david@example.com", "David", "Zhou", ""],  # edge: empty tags
    ["cust_5005", "eve@example.com", "Eve", "Liu", "vip"],
    ["cust_5006", "frank@example.com", "Frank", "Huang", "new_user"],
    ["cust_5007", "grace@example.com", "Grace", "Lin", "at_risk"],
    ["cust_5008", "henry@example.com", "Henry", "Wu", ""],
    ["cust_5009", "ivy@example.com", "Ivy", "Xu", "vip"],
    ["cust_5010", "jack@example.com", "Jack", "Guo", "new_user"],
]

orders = [
    ["order_id", "customer_id", "status", "shipping_status", "total_amount"],
    ["ord_5101", "cust_5001", "pending", "not_shipped", "129.00"],  # edge: pending
    ["ord_5102", "cust_5002", "shipped", "in_transit", "59.00"],  # edge: in-transit address change
    ["ord_5103", "cust_5003", "delivered", "delivered", "89.00"],  # delivered within 30 days
    ["ord_5104", "cust_5004", "delivered", "delivered", "45.00"],  # edge: delivered >30 days
    ["ord_5105", "cust_5005", "cancelled", "cancelled", "99.00"],  # edge: cancelled order
    ["ord_5106", "cust_5006", "shipped", "in_transit", "210.00"],
    ["ord_5107", "cust_5007", "pending", "not_shipped", "39.00"],
    ["ord_5108", "cust_5008", "delivered", "delivered", "75.00"],
    ["ord_5109", "cust_5009", "cancelled", "cancelled", "149.00"],
    ["ord_5110", "cust_5010", "shipped", "in_transit", "65.00"],
    ["ord_5111", "cust_5001", "delivered", "delivered", "15.00"],  # edge: low-value delivered
    ["ord_5112", "cust_5002", "pending", "not_shipped", "320.00"],  # edge: high-value pending
    ["ord_5113", "cust_5003", "delivered", "delivered", "52.00"],
    ["ord_5114", "cust_5004", "shipped", "in_transit", "83.00"],
    ["ord_5115", "cust_5005", "delivered", "delivered", "115.00"],  # edge: delivered >30 days
]

refunds = [
    ["refund_id", "order_id", "refund_status", "requested_at"],
    ["ref_6101", "ord_5103", "approved", "2026-03-01"],
    ["ref_6102", "ord_5104", "rejected", "2026-03-02"],  # edge: >30-day refund window
    ["ref_6103", "ord_5102", "pending_review", "2026-03-03"],  # edge: in-transit refund attempt
    ["ref_6104", "ord_5105", "rejected", "2026-03-04"],  # edge: cancelled order refund attempt
    ["ref_6105", "ord_5108", "approved", "2026-03-05"],
    ["ref_6106", "ord_5110", "pending_review", "2026-03-06"],
    ["ref_6107", "ord_5115", "rejected", "2026-03-07"],  # edge: >30-day delivered order
    ["ref_6108", "ord_5113", "approved", "2026-03-08"],
]

kb_articles = {
    "refund_policy.md": """# Refund Policy
Unopened items are eligible for refund within 14 calendar days of delivery.
Opened items require manual review and are not instant-approved.
Orders delivered more than 30 days ago are not eligible for standard refunds.
""",
    "shipping_delay.md": """# Shipping Delay Policy
If tracking has not changed for 5 days, escalate for logistics review.
Support should include the latest carrier update in the escalation note.
""",
    "address_change.md": """# Address Change Policy
Address updates are allowed before shipment confirmation.
Address change for in-transit shipments requires human approval.
""",
    "cancellation_policy.md": """# Cancellation Policy
Orders in pending status can be cancelled immediately.
Cancellation of shipped orders requires approval and case-by-case review.
""",
    "partial_refund_policy.md": """# Partial Refund Policy
Partial refunds are allowed for damaged or incomplete deliveries.
Requests must be filed within 14 calendar days after delivery.
""",
    "return_window_opened_items.md": """# Return Window for Opened Items
Opened items can be reviewed for return eligibility within 14 calendar days.
Opened-item returns are not auto-approved and require support review.
""",
    "order_tracking_normal_flow.md": """# Order Tracking Normal Flow
Use tracking events to confirm shipment progress.
Escalate only when tracking has no update for 5 days.
""",
    "late_delivery_complaint.md": """# Late Delivery Complaint
If no tracking movement occurs for 5 days, escalate to logistics.
If movement resumes, keep the case open and monitor for 24 hours.
""",
    "damaged_item_policy.md": """# Damaged Item Policy
Damaged items can receive replacement or partial refund support.
Claims should be submitted within 14 calendar days.
""",
    "wrong_item_received.md": """# Wrong Item Received
Wrong-item cases qualify for exchange or refund support.
Request handling follows the 14 calendar day window.
""",
    "missing_package_investigation.md": """# Missing Package Investigation
Start carrier investigation when package is marked delivered but not received.
Escalate after 5 days without carrier progress update.
""",
    "account_suspension.md": """# Account Suspension Support
Account suspension requests require identity verification before action.
Escalate suspicious access cases to security support.
""",
    "password_reset.md": """# Password Reset Assistance
Password reset requires identity confirmation via registered email.
Escalate repeated failed verification attempts.
""",
    "duplicate_order.md": """# Duplicate Order Handling
Duplicate pending orders can be cancelled quickly to avoid double shipment.
Duplicate shipped orders require approval-based resolution.
""",
    "payment_failure.md": """# Payment Failure Handling
Payment failures should prompt retry instructions and payment method checks.
Escalate to billing support when failures persist after 2 attempts.
""",
    "escalation_triggers.md": """# Escalation Triggers
Escalate when policy cannot be confidently applied or risk is high.
Mandatory escalation threshold includes 5 days without tracking updates.
""",
    "human_review_process.md": """# Human Review Process
Refund, address change, and cancellation for risky states require approval.
Approval decisions must include rationale and reviewer identity.
""",
    "vip_customer_sla.md": """# VIP Customer SLA
VIP cases should be triaged first and escalated rapidly when blocked.
Policy thresholds remain unchanged: 14-day refund window and 5-day shipping escalation.
""",
    "high_priority_ticket_criteria.md": """# High-Priority Ticket Criteria
Mark high priority when customer impact is severe or compliance risk exists.
Escalate immediately for unresolved shipping delays beyond 5 days.
""",
    "international_shipping_policy.md": """# International Shipping Policy
International deliveries may have longer transit times.
Escalate if no tracking update is observed for 5 days.
""",
    "delivery_estimate_faq.md": """# Delivery Estimate FAQ
Provide estimated delivery windows from the latest carrier status.
Escalate only when tracking is stale for 5 days.
""",
    "carrier_contact_info.md": """# Carrier Contact Information
Use carrier support channels when tracking details are inconsistent.
Escalate internally if no carrier response within 5 days.
""",
    "holiday_delay_notice.md": """# Holiday Delay Notice
Holiday periods can increase delivery times by several days.
Use the same 5-day no-update threshold before escalation.
""",
    "exchange_policy.md": """# Exchange Policy
Exchanges are supported for eligible products within 14 calendar days.
Opened item exchanges require support review.
""",
    "gift_card_refund_policy.md": """# Gift Card Refund Policy
Gift card purchases are generally non-refundable unless legally required.
Any exception request requires human approval and policy review.
""",
    "bulk_order_support.md": """# Bulk Order Support
Bulk orders require enhanced verification before cancellation or refund.
For shipment issues, escalate when tracking is unchanged for 5 days.
""",
    "subscription_cancellation.md": """# Subscription Cancellation
Subscription cancellation requests are effective at cycle end by default.
Immediate cancellation requests with active fulfillment require approval.
""",
}

for name, rows in [("customers.csv", customers), ("orders.csv", orders), ("refunds.csv", refunds)]:
    with (data_dir / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

for file_name, body in kb_articles.items():
    (kb_dir / file_name).write_text(body.rstrip() + "\n", encoding="utf-8")

print(
    f"Seeded {len(customers) - 1} customers, {len(orders) - 1} orders, {len(refunds) - 1} refunds. "
    f"Wrote {len(kb_articles)} KB articles to data/kb/."
)
