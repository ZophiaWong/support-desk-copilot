## ADDED Requirements

### Requirement: Customer CSV contains at least 10 rows with varied tags and identifiers
The system SHALL provide a `data/customers.csv` file with at least 10 customer rows. Rows MUST include customers with tags: `vip`, `new_user`, `at_risk`, and at least one customer with no tags. Each row MUST have a unique `customer_id` in the format `cust_XXXX`.

#### Scenario: VIP customer exists in fixture data
- **WHEN** `lookup_customer` is called with a `customer_id` that maps to a VIP customer
- **THEN** the returned customer record includes `"vip"` in the `tags` array

#### Scenario: Customer with no tags exists
- **WHEN** `lookup_customer` is called with a `customer_id` that maps to a customer with no tags
- **THEN** the returned customer record has an empty `tags` array

#### Scenario: Customer lookup by email works across all seeded customers
- **WHEN** `lookup_customer` is called with the email of any seeded customer
- **THEN** the correct customer record is returned

### Requirement: Order CSV contains at least 15 rows covering all order status edge cases
The system SHALL provide a `data/orders.csv` file with at least 15 order rows. The fixture set MUST include orders in each of the following states: `pending`, `shipped` (in_transit), `delivered` (within 30 days), `delivered` (older than 30 days), and `cancelled`. At least one order per key edge case MUST be linked to a seeded customer.

#### Scenario: In-transit order exists for address-change edge case
- **WHEN** `lookup_order` is called with an order ID that is `shipped` + `shipping_status: in_transit`
- **THEN** the returned order shows `status: shipped` and `shipping_status: in_transit`

#### Scenario: Stale delivered order exists for >30-day refund edge case
- **WHEN** `lookup_order` is called with an order ID flagged as delivered >30 days ago
- **THEN** the returned order shows `status: delivered`

#### Scenario: Cancelled order exists
- **WHEN** `lookup_order` is called with a cancelled order ID
- **THEN** the returned order shows `status: cancelled`

### Requirement: Refund CSV contains at least 8 rows covering all refund status values
The system SHALL provide a `data/refunds.csv` file with at least 8 refund rows. The fixture set MUST include refunds with statuses: `pending_review`, `approved`, `rejected`. At least one refund MUST be linked to an in-transit order (to represent a disallowed scenario) and at least one MUST be linked to a >30-day-old delivered order.

#### Scenario: Approved refund exists in fixture
- **WHEN** `lookup_order` or related tool queries refund data for an order with an approved refund
- **THEN** the refund record with `refund_status: approved` is present in `data/refunds.csv`

#### Scenario: Refund on in-transit order exists
- **WHEN** the seed data is loaded
- **THEN** at least one refund row references an order with `shipping_status: in_transit`
