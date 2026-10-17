# NovaCart Power BI Data Model Architecture

This document describes the Star Schema data model implementation inside Power BI, detailing table cardinality, relationships, cross-filtering directions, and fact-to-fact isolation rules.

---

## 1. Data Model Topography (Star Schema)

```text
                            ┌───────────────────┐
                            │   dim_customer    │
                            ├───────────────────┤
                            │ PK customer_key   │
                            └─────────┬─────────┘
                                      │ 1
                                      │
 ┌───────────────────┐                ▼ *              ┌───────────────────┐
 │    dim_product    │          ┌───────────┐          │     dim_date      │
 ├───────────────────┤ 1      * │           │ *      1 ├───────────────────┤
 │ PK product_key    ├─────────►│fact_sales │◄─────────┤ PK date_key       │
 └───────────────────┘          └─────┬─────┘          └───────────────────┘
                                      │ *
                                      │
                                      ▼ 1
                            ┌───────────────────┐
                            │   dim_location    │
                            ├───────────────────┤
                            │ PK location_key   │
                            └───────────────────┘
```

---

## 2. Table Relationships & Cardinality

| Primary Table (1) | Foreign Key Table (*) | Primary Key | Foreign Key | Cardinality | Cross Filter Direction | Active |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| `dim_customer` | `fact_sales` | `customer_key` | `customer_key` | **1 : \*** | Single (`dim_customer` $\rightarrow$ `fact_sales`) | **Yes** |
| `dim_product` | `fact_sales` | `product_key` | `product_key` | **1 : \*** | Single (`dim_product` $\rightarrow$ `fact_sales`) | **Yes** |
| `dim_date` | `fact_sales` | `date_key` | `date_key` | **1 : \*** | Single (`dim_date` $\rightarrow$ `fact_sales`) | **Yes** |
| `dim_location` | `fact_sales` | `location_key` | `location_key` | **1 : \*** | Single (`dim_location` $\rightarrow$ `fact_sales`) | **Yes** |
| `dim_payment` | `fact_sales` | `payment_key` | `payment_key` | **1 : \*** | Single (`dim_payment` $\rightarrow$ `fact_sales`) | **Yes** |
| `dim_customer` | `fact_returns` | `customer_key` | `customer_key` | **1 : \*** | Single (`dim_customer` $\rightarrow$ `fact_returns`) | **Yes** |
| `dim_product` | `fact_returns` | `product_key` | `product_key` | **1 : \*** | Single (`dim_product` $\rightarrow$ `fact_returns`) | **Yes** |
| `dim_date` | `fact_returns` | `date_key` | `return_date_key` | **1 : \*** | Single (`dim_date` $\rightarrow$ `fact_returns`) | **Yes** |
| `dim_date` | `fact_payments` | `date_key` | `payment_date_key` | **1 : \*** | Single (`dim_date` $\rightarrow$ `fact_payments`) | **Yes** |
| `dim_payment` | `fact_payments` | `payment_key` | `payment_key` | **1 : \*** | Single (`dim_payment` $\rightarrow$ `fact_payments`) | **Yes** |

---

## 3. Date Table Configuration
* **Date Table Name**: `dim_date`
* **Key Column**: `full_date` (DataType: `Date`)
* **Marked as Date Table**: **Yes**
* **Chronological Sorting**: `month_name` column is explicitly sorted by `month_num`; `day_name` is sorted by `day_of_week`.

---

## 4. Fact-to-Fact Relationship Isolation Policy
> [!IMPORTANT]
> `fact_sales`, `fact_returns`, and `fact_payments` are **NEVER** joined directly via bidirectional or many-to-many relationships in Power BI.
> All cross-filtering and metric comparisons occur through shared dimension tables (`dim_customer`, `dim_product`, `dim_date`) or through explicit DAX measures (`[Returned Revenue]`, `[Post-Return Revenue]`).
