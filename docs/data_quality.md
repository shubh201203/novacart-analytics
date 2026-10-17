# NovaCart Data Quality & Cleaning Architecture

This document defines the data quality standards, missing `customer_id` policy, quarantine mechanics, audit log framework, and validation rules for the NovaCart Analytics Platform.

---

## 1. Data Terminology & Grain Definition

> [!IMPORTANT]
> **Grain of `orders_raw.csv` / `orders_processed.csv`**: One row per product line item within a customer order (order-line grain).

### Distinct Metric Definitions:
* **Order Line Count**: `COUNT(*)` — total rows in the orders table.
* **Distinct Order Count**: `COUNT(DISTINCT order_id)` — total unique customer purchasing transactions.
* **Items Purchased**: `SUM(quantity)` — total physical units ordered.
* **Order Lines per Customer**: `COUNT(*) / COUNT(DISTINCT customer_id)`
* **Distinct Orders per Customer**: `COUNT(DISTINCT order_id) / COUNT(DISTINCT customer_id)`

---

## 2. Missing `customer_id` Policy & Quarantine Workflow

### **Background**:
Raw order data contains ~211 order-line records where `customer_id` is `NaN` / null due to raw telemetry dropouts.

### **Policy Rules**:
1. **Deterministic Recovery**:
   * If an order line has a missing `customer_id`, check if other order lines sharing the same `order_id` possess a valid `customer_id`.
   * If a matching valid `customer_id` is found, populate the missing field deterministically.
2. **Quarantine Isolation**:
   * If an order line has a missing `customer_id` and **no other line item in that `order_id` contains a valid customer_id**, the record **CANNOT** be included in customer-level, RFM, or user-segmentation analysis.
   * Rather than silently deleting the record (`dropna()`), the unrecoverable order lines are extracted into a dedicated quarantine file:
     `data/processed/quarantine/orders_quarantine.csv`
3. **Business Impact Reporting**:
   * Quarantined revenue and order lines are tracked and reported separately in data quality summaries.
   * This ensures global financial totals remain reconcilable without corrupting customer-level RFM metrics.

---

## 3. Data Cleaning Pipeline Architecture

```text
data/raw/
   ├── customers_raw.csv
   ├── products_raw.csv
   ├── orders_raw.csv
   ├── returns_raw.csv
   └── payments_raw.csv
          │
          ▼
   src/data_processing/
   ├── clean_customers.py     --> Standardization, deduplication, age bounds, city fill
   ├── clean_products.py      --> Category casing normalization, price/margin checks
   ├── clean_orders.py        --> Date parsing, quantity checks, customer recovery/quarantine
   ├── clean_returns.py       --> Order FK validation, return date/quantity bounds
   ├── clean_payments.py      --> Payment status imputation, order FK checks
   ├── feature_engineering.py --> Financial metrics (gross_sales, net_revenue, profit, profit_margin)
   └── validate_data.py       --> Post-cleaning schema, referential integrity & formula checks
          │
          ├─────────────────────────┐
          ▼                         ▼
data/processed/           data/processed/quarantine/
   ├── customers_processed.csv    ├── orders_quarantine.csv
   ├── products_processed.csv     └── returns_quarantine.csv
   ├── orders_processed.csv
   ├── returns_processed.csv
   └── payments_processed.csv
          │
          ▼
reports/
   ├── data_quality_report.md
   ├── data_quality_summary.csv
   └── data_quality_audit_log.csv
```

---

## 4. Audit Trail Framework

Every cleaning operation logs an entry in `reports/data_quality_audit_log.csv` with fields:
`table_name`, `field_name`, `issue_type`, `action_taken`, `records_affected`, `notes`.

This provides complete auditability and interview-ready documentation of all data transformations.
