# NovaCart Platform Architecture & Dimensional Data Model

This document outlines the system architecture, star schema data warehouse design, dimensional relationships, grain definitions, and Power BI compatibility rules for NovaCart.

---

## 1. End-to-End System Architecture

```text
                                  ┌──────────────────────────┐
                                  │   Raw Data Layer         │
                                  │   (data/raw/ CSVs)       │
                                  └─────────────┬────────────┘
                                                │
                                                ▼
                                  ┌──────────────────────────┐
                                  │  Python Cleaning & ETL   │
                                  │ (src/data_processing/)   │
                                  └─────────────┬────────────┘
                                                │
                                ┌───────────────┴───────────────┐
                                ▼                               ▼
                   ┌──────────────────────────┐   ┌──────────────────────────┐
                   │   Cleaned Analytical     │   │   Quarantine Isolation   │
                   │   (data/processed/ CSVs) │   │   (data/processed/       │
                   └────────────┬─────────────┘   │    quarantine/)          │
                                │                 └──────────────────────────┘
                                ▼
                   ┌──────────────────────────┐
                   │ PostgreSQL / DuckDB DW   │
                   │ (Star Schema Data Mart)  │
                   └────────────┬─────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
    ┌──────────────────────────┐  ┌──────────────────────────┐
    │    SQL Analytics & CTEs  │  │   Power BI & Dashboard   │
    │    (sql/ 01-08 scripts)  │  │   (Interactive React)    │
    └──────────────────────────┘  └──────────────────────────┘
```

---

## 2. Dimensional Star Schema Design

```text
                            ┌───────────────────┐
                            │   dim_customer    │
                            ├───────────────────┤
                            │ PK customer_key   │
                            │    customer_id    │
                            │    customer_name  │
                            │    segment, city  │
                            └─────────┬─────────┘
                                      │
                                      │ 1:N
 ┌───────────────────┐                ▼                ┌───────────────────┐
 │    dim_product    │          ┌───────────┐          │     dim_date      │
 ├───────────────────┤   1:N    │           │   N:1    ├───────────────────┤
 │ PK product_key    ├─────────►│fact_sales │◄─────────┤ PK date_key       │
 │    product_id     │          │           │          │    full_date      │
 │    category, brand│          └─────┬─────┘          │    year, month    │
 └───────────────────┘                │                └───────────────────┘
                                      │ N:1
                                      ▼
                            ┌───────────────────┐
                            │   dim_location    │
                            ├───────────────────┤
                            │ PK location_key   │
                            │    city, state    │
                            │    region         │
                            └───────────────────┘
```

---

## 3. Table Grain & Schema Specifications

### Primary Fact Table: `fact_sales`
* **GRAIN**: **One row per product line within a customer order.**
* **Primary Key**: `sales_key` (Surrogate Integer)
* **Natural / Business Key**: `order_id` + `product_id`
* **Foreign Keys**: `date_key`, `customer_key`, `product_key`, `location_key`, `payment_key`.
* **Measures**: `quantity`, `gross_sales`, `discount_amount`, `net_revenue`, `product_cost`, `shipping_cost`, `profit`, `profit_margin`.
* **Dimensional Flags**: `is_completed`, `is_cancelled`, `is_returned`.

### Secondary Fact Table: `fact_returns`
* **GRAIN**: **One row per returned item line.**
* **Primary Key**: `return_key`
* **Foreign Keys**: `return_date_key`, `customer_key`, `product_key`.

### Secondary Fact Table: `fact_payments`
* **GRAIN**: **One row per payment transaction.**
* **Primary Key**: `payment_trans_key`
* **Foreign Keys**: `payment_date_key`, `payment_key`.

---

## 4. Power BI Model Compatibility
* **Star Schema Topography**: Single-direction (1:N) relationships radiating from dimension tables to fact tables.
* **No Ambiguous Paths**: Clean separation of sales, returns, and payment facts sharing unified dimension tables (`dim_customer`, `dim_product`, `dim_date`).
