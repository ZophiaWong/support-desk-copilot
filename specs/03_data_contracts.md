# Data Contracts

## customers
- customer_id: string
- email: string
- first_name: string
- last_name: string
- phone: string | nullable
- tags: string
- created_at: datetime

## orders
- order_id: string
- customer_id: string
- status: enum(created, paid, packed, shipped, delivered, canceled)
- shipping_status: enum(label_created, in_transit, delivered, exception)
- total_amount: number
- currency: string

## refunds
- refund_id: string
- order_id: string
- refund_status: enum(pending_review, approved, rejected)
- requested_at: datetime
- approved_at: datetime | nullable

## tickets
- ticket_id: string
- customer_id: string | nullable
- queue: enum(general, logistics, payments, returns)
- priority: enum(low, medium, high)
- status: enum(open, pending, escalated, closed)
- summary: string

## approval_requests
- approval_id: string
- action_type: string
- payload_json: json
- status: enum(needs_human_approval, approved, rejected)
