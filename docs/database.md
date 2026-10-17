# NovaCart Data Warehouse Setup & Administration Guide

This document describes connection parameters, DDL schema generation, data loading mechanics, indexing rationale, payment modeling semantics, return methodology, and metric reconciliation procedures.

---

## 1. Connection Configuration & Environment Variables

Database configuration is controlled via environment variables (specified in `.env` or system environment):

```ini
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=novacart_analytics
DB_USER=postgres
DB_PASSWORD=your_secure_password_here
```

### Dual Engine Fallback Support
If a local PostgreSQL instance is unavailable, the loader automatically creates an embedded DuckDB analytical database at `data/processed/novacart_analytics.duckdb`.

---

## 2. Fact Table Grains & Architectural Audit

| Fact Table | Exact Grain Definition | Primary Key | Foreign Keys | Row Count |
| :--- | :--- | :--- | :--- | ---: |
| **`fact_sales`** | **One row per product line item within an order.** | `sales_key` | `date_key`, `customer_key`, `product_key`, `location_key`, `payment_key` | 104,852 |
| **`fact_returns`** | **One row per returned product line item / return event.** | `return_key` | `return_date_key`, `customer_key`, `product_key` | 5,792 |
| **`fact_payments`** | **One row per payment transaction.** | `payment_trans_key` | `payment_date_key`, `payment_key` | 62,952 |

---

## 3. Payment Modeling Audit & Double-Counting Protection

### **Attribute vs Transaction Modeling**:
1. **`fact_sales.payment_key` $\rightarrow$ `dim_payment`**: Represents **descriptive payment attributes** (payment method and payment status associated with the order line at time of purchase). It is a dimension reference, NOT a transaction record.
2. **`fact_payments`**: Represents **actual financial payment transactions**. This is the authoritative table for auditing monetary transfers, transaction success/failure rates, and payment gateway settlement amounts.

> [!WARNING]
> **Preventing Fact-to-Fact Double Counting**:
> Do NOT join `fact_sales` directly to `fact_payments` on `order_id` in a simple `SELECT SUM(net_revenue), SUM(payment_amount)`. Because an order can contain multiple product lines in `fact_sales` and multiple retry/installment payment entries in `fact_payments`, a naive `JOIN` will create a Cartesian product and multiply revenue metrics!
> 
> **Correct Pattern**: Aggregate `fact_sales` to order level via a CTE before joining to `fact_payments`.

```sql
-- Safe Order-Level Reconciliation CTE
WITH order_sales AS (
    SELECT order_id, SUM(net_revenue) AS total_order_revenue
    FROM fact_sales
    GROUP BY order_id
),
order_payments AS (
    SELECT order_id, SUM(payment_amount) AS total_paid_amount
    FROM fact_payments
    WHERE payment_key IN (SELECT payment_key FROM dim_payment WHERE payment_status = 'Completed')
    GROUP BY order_id
)
SELECT s.order_id, s.total_order_revenue, p.total_paid_amount
FROM order_sales s
JOIN order_payments p ON s.order_id = p.order_id;
```

---

## 4. Business Metric Semantics

This section defines the exact status inclusion rules for all key performance indicators (KPIs) in SQL analytics and Power BI measures.

### Order Lifecycles & Status Categories:
* **`Completed`** / **`Shipped`** (`is_completed = TRUE`): Orders successfully processed, fulfilled, and delivered.
* **`Processing`**: Orders currently being packed or in transit.
* **`Cancelled`** (`is_cancelled = TRUE`): Orders voided prior to fulfillment. No revenue realized.
* **`Returned`** (`is_returned = TRUE`): Orders delivered but subsequently returned by the customer for refund.

---

### Status Inclusion Matrix for Analytics & Power BI:

| Metric Name | Formula / Definition | Included Statuses | Excluded Statuses | Business Context |
| :--- | :--- | :--- | :--- | :--- |
| **Total Placed Gross Sales** | $\sum (\text{quantity} \times \text{unit\_price})$ | ALL (`Completed`, `Shipped`, `Processing`, `Returned`, `Cancelled`) | None | Total demand generated at checkout before cancellations/returns. |
| **Total Placed Net Revenue** | $\sum (\text{gross\_sales} - \text{discount\_amount})$ | ALL (`Completed`, `Shipped`, `Processing`, `Returned`, `Cancelled`) | None | Benchmark dataset total: **₹971,486,941.80** across all 104,852 order lines. |
| **Realized Net Revenue** | $\sum (\text{net\_revenue}) \text{ where } \text{is\_completed} = \text{TRUE}$ | `Completed`, `Shipped` | `Cancelled`, `Returned`, `Processing` | Net settled revenue for accounting statements. |
| **Net Settled Revenue (Post-Returns)** | $\text{Realized Net Revenue} - \text{Returned Revenue}$ | `Completed`, `Shipped` (minus `fact_returns`) | `Cancelled` | Final GAAP revenue retained by NovaCart after customer refunds. |
| **Total Placed Profit** | $\sum (\text{net\_revenue} - \text{product\_cost} - \text{shipping\_cost})$ | ALL (`Completed`, `Shipped`, `Processing`, `Returned`, `Cancelled`) | None | Benchmark dataset total: **₹300,804,487.91** across all 104,852 order lines. |
| **Realized Profit** | $\sum (\text{profit}) \text{ where } \text{is\_completed} = \text{TRUE}$ | `Completed`, `Shipped` | `Cancelled`, `Returned`, `Processing` | Net operating profit earned from fulfilled sales. |
| **Ordered Quantity** | $\sum (\text{quantity})$ | ALL | None | Total units ordered: **156,395 units**. |
| **Returned Quantity** | $\sum (\text{quantity\_returned})$ | `fact_returns` table | None | Total physical units returned: **8,719 units**. |

---

## 5. Return Analysis Methodology

To evaluate product quality, customer satisfaction, and category return risks without corrupting sales facts:

1. **Return Rate Calculation**:
   $$\text{Return Rate (\%)} = \frac{\sum \text{fact\_returns.quantity\_returned}}{\sum \text{fact\_sales.quantity}} \times 100$$
2. **Returned Revenue Calculation**:
   Join `fact_returns` to `fact_sales` on `order_id` and `product_key` to retrieve line-item net revenue per unit:
   $$\text{Returned Revenue} = \sum \left( \text{fact\_returns.quantity\_returned} \times \frac{\text{fact\_sales.net\_revenue}}{\text{fact\_sales.quantity}} \right)$$
3. **Double-Counting Avoidance**:
   Do NOT join `fact_sales` to `fact_returns` using `FULL OUTER JOIN` directly in aggregated queries. Use explicit dimension joins or CTE subqueries.

---

## 6. Indexing Rationale

Analytical queries frequently filter and join on high-cardinality keys. The following indexes are created:

* `fact_sales.order_id` — Fast order lookup and CTE joining.
* `fact_sales.customer_key` — High-frequency join for RFM customer analytics.
* `fact_sales.product_key` — High-frequency join for product profitability matrix.
* `fact_sales.date_key` — Time-series aggregation, MoM, and YoY window functions.
* `fact_sales.location_key` — Regional performance breakdowns.
