# NovaCart Platform Architecture & Dimensional Data Model

This document outlines the complete system architecture, star schema data warehouse design, dimensional relationships, grain definitions, and Power BI & React application integration for NovaCart.

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
                   │ PostgreSQL 18 DW (Local) │
                   │ (Star Schema Data Mart)  │
                   └────────────┬─────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
   ┌──────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────┐
   │    SQL Analytics & CTEs  │ │  Power BI Desktop Suite  │ │ Neon Cloud PostgreSQL DW │
   │    (sql/analysis/ 01-12) │ │  (6 Pages, 30+ Measures) │ │ (novacart_analytics)     │
   └──────────────────────────┘ └──────────────────────────┘ └────────────┬─────────────┘
                                                                          │
                                                             ┌────────────▼─────────────┐
                                                             │  FastAPI Backend (Render)│
                                                             │  (Parameterized SQL API) │
                                                             └────────────┬─────────────┘
                                                                          │
                                                             ┌────────────▼─────────────┐
                                                             │ React 18 SPA (Vercel)    │
                                                             │ (Live Web BI Dashboard)  │
                                                             └──────────────────────────┘
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
* **GRAIN**: **One row per product line item within a customer order.**
* **Primary Key**: `sales_key` (Surrogate Integer)
* **Natural / Business Key**: `order_id` + `product_id`
* **Foreign Keys**: `date_key`, `customer_key`, `product_key`, `location_key`, `payment_key`.
* **Measures**: `quantity`, `gross_sales`, `discount_amount`, `net_revenue`, `product_cost`, `shipping_cost`, `profit`, `profit_margin`.
* **Dimensional Flags**: `is_completed`, `is_cancelled`, `is_returned`.
* **Verified Row Count**: 104,852 rows.

### Secondary Fact Table: `fact_returns`
* **GRAIN**: **One row per returned item line.**
* **Primary Key**: `return_key`
* **Foreign Keys**: `return_date_key`, `customer_key`, `product_key`.
* **Verified Row Count**: 5,792 rows.

### Secondary Fact Table: `fact_payments`
* **GRAIN**: **One row per payment transaction attempt.**
* **Primary Key**: `payment_trans_key`
* **Foreign Keys**: `payment_date_key`, `payment_key`.
* **Verified Row Count**: 62,952 rows.

---

## 4. Power BI Model Compatibility
* **Star Schema Topography**: Single-direction (1:N) relationships radiating from dimension tables to fact tables.
* **No Ambiguous Paths**: Clean separation of sales, returns, and payment facts sharing unified dimension tables (`dim_customer`, `dim_product`, `dim_date`).
* **Date Table Marking**: `dim_date` is marked as the official Date Table on `full_date` enabling standard Time Intelligence functions.

---

## 5. Web BI Application Stack (React + FastAPI + Neon)
* **Neon Managed PostgreSQL**: Houses the cloud star schema warehouse with SSL connection pooling on port 5432.
* **FastAPI Backend (Render)**: Exposes clean REST endpoints (`/api/overview`, `/api/sales`, `/api/customers`, `/api/products`, `/api/regional`, `/api/retention`) utilizing parameterized SQL to guarantee sub-50ms latency with strict CORS origins.
* **React 18 Dashboard (Vercel)**: Deployed to edge CDN with Vite, Tailwind CSS v4, and Recharts, offering dynamic multi-slicer filtering and client-side SPA routing (`vercel.json`).
