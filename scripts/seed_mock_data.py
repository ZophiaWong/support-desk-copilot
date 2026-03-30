from pathlib import Path
import csv

root = Path(__file__).resolve().parents[1]
data_dir = root / "data"
data_dir.mkdir(exist_ok=True)

customers = [
    ["customer_id", "email", "first_name", "last_name", "tags"],
    ["cust_1001", "alice@example.com", "Alice", "Wang", "vip"],
    ["cust_1002", "bob@example.com", "Bob", "Li", "new_user"],
]

orders = [
    ["order_id", "customer_id", "status", "shipping_status", "total_amount"],
    ["ord_2001", "cust_1001", "shipped", "in_transit", "129.00"],
    ["ord_2002", "cust_1002", "delivered", "delivered", "59.00"],
]

refunds = [
    ["refund_id", "order_id", "refund_status", "requested_at"],
    ["ref_3001", "ord_2002", "pending_review", "2026-03-01"],
]

for name, rows in [("customers.csv", customers), ("orders.csv", orders), ("refunds.csv", refunds)]:
    with (data_dir / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

print("Seeded mock data into ./data")
