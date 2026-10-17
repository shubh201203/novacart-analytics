# NovaCart End-to-End E-Commerce Sales & Customer Analytics Platform

A production-grade, portfolio-ready End-to-End E-Commerce Sales & Customer Analytics Platform built for **NovaCart**, a multi-category Indian e-commerce enterprise.

[![Executive Insights Report](https://img.shields.io/badge/Executive_Report-View_Insights-blue?style=for-the-badge)](reports/executive_insights.md)
[![Power BI Screenshots](https://img.shields.io/badge/Power_BI-6--Page_Screenshots-green?style=for-the-badge)](reports/dashboard_screenshots/README.md)
[![React Dashboard](https://img.shields.io/badge/React_Dashboard-Vite_&_FastAPI-cyan?style=for-the-badge)](dashboard/README.md)

### Executive Dashboard Preview
![NovaCart Executive Overview](reports/dashboard_screenshots/01_executive_overview.png)
*Detailed analysis and business recommendations available in the [Executive Business Insights Report](reports/executive_insights.md). Interactive web app instructions in [dashboard/README.md](dashboard/README.md).*



---

## Technical Stack & Architecture

```text
                           ┌──────────────────────────┐
                           │   Raw Data Generator     │
                           │  (India Market E-Com)    │
                           └─────────────┬────────────┘
                                         │
                                         ▼
                           ┌──────────────────────────┐
                           │  Python Cleaning & ETL   │
                           │  (Quarantine & Audit)    │
                           └─────────────┬────────────┘
                                         │
                          ┌──────────────┴──────────────┐
                          ▼                             ▼
             ┌──────────────────────────┐  ┌──────────────────────────┐
             │ PostgreSQL / DuckDB DW   │  │   Quarantine Isolation   │
             │   (Star Schema Engine)   │  │ (orders_quarantine.csv)  │
             └────────────┬─────────────┘  └──────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│   Advanced SQL Suite     │    │   Power BI & DAX Model   │
│   (sql/analysis/ 01-12)  │    │   (6-Page Executive BI)  │
└──────────────────────────┘    └──────────────────────────┘
```

---

## Canonical Approved KPI Benchmarks (Phase 4.1 & Phase 5 Reconciled)

* **Total Placed Net Revenue**: **₹971,486,941.80** (All 104,852 order lines)
* **Realized Net Revenue**: **₹847,624,781.93** (Completed & Shipped orders)
* **Post-Return Revenue (Net Settled)**: **₹796,752,855.77** (Realized Net Revenue minus Returned Revenue)
* **Total Placed Profit**: **₹300,804,487.91**
* **Realized Profit**: **₹262,159,342.82**
* **Realized Profit Margin**: **30.93%**
* **Ordered Item Quantity**: **156,395 units**
* **Returned Item Quantity**: **8,712 units**
* **Overall Return Rate**: **5.57%**
* **Active Completed Customers**: **3,970 customers** (Out of 5,000 total registered)
* **Average Order Value (AOV)**: **₹15,452.38**
* **Customer Lifetime Value (LTV)**: **₹213,507.50**

---

## Key Platform Features

1. **Synthetic India E-Commerce Data Generator**:
   * Realistic seasonality (Diwali / Navratri & Independence Freedom Sales surges).
   * Indian payment rails (UPI 52%, COD 22%, Credit/Debit 20%, Net Banking 4%, Wallets 2%).
   * 18 Indian States across 6 macro-regions (South, West, North, East, Central, Northeast).
   * Intentional raw data quality issues (~0.4% duplicates, missing values, malformed dates, age outliers) for ETL testing.
2. **Modular Python ETL & Data Quality Pipeline**:
   * Deduplication, Title Case standardization, 2-letter state code mapping, median age imputation.
   * **Missing Customer Deterministic Recovery Engine**: Recovers missing co-occurring customer IDs from order line co-occurrences. Unrecoverable records isolated in `data/processed/quarantine/orders_quarantine.csv`.
   * Complete audit trail log saved to `reports/data_quality_audit_log.csv`.
3. **PostgreSQL / DuckDB Star Schema Data Warehouse**:
   * Dimensions: `dim_customer`, `dim_product`, `dim_location`, `dim_payment`, `dim_date` (full 2022-2026 calendar).
   * Fact Tables: `fact_sales` (Grain: 1 row per product line/order), `fact_returns`, `fact_payments`.
   * 0 Orphan foreign keys, 100% mathematical revenue & profit reconciliation.
4. **Advanced SQL Analysis Suite (`sql/analysis/` 01-12)**:
   * Sales performance, customer LTV, product performance matrix, regional demand, time-series growth (MoM %, YoY %, 3M moving averages), RFM segmentation, cohort retention, return rate risk, payment success rates, and 15 C-level business questions.
5. **Power BI & DAX Business Intelligence Layer (`powerbi/`)**:
   * Star Schema model with single-direction $1:N$ relationships and Date Table marking.
   * 30+ production DAX measures (`CALCULATE`, `DIVIDE`, `SUMX`, `SAMEPERIODLASTYEAR`, `DATESINPERIOD`).
   * 6-page visual report specification (Executive Overview, Sales & Profitability, Customer Intelligence, Product Matrix Scatter Plot, Regional Demand, Customer Retention & RFM Heatmap Matrix).
   * 100% DAX metric reconciliation verified via `verify_powerbi_reconciliation.py`.

---

## Quickstart & Execution Commands

```bash
# 1. Regenerate Raw Synthetic Dataset (Default: 105,000 rows, seed=42)
python src/data_processing/generate_raw_data.py --rows 105000 --seed 42

# 2. Run Data Quality, Cleaning & Feature Engineering Pipeline
python src/data_processing/run_pipeline.py

# 3. Load Star Schema Data Warehouse (PostgreSQL / DuckDB Dual Engine)
python src/database/load_dw.py

# 4. Execute Data Warehouse Integrity & Reconciliation Checks
python src/database/validate_dw.py

# 5. Execute Advanced SQL Analytics Suite & Export Result Datasets
python src/analytics/run_sql_analysis.py

# 6. Verify Power BI DAX Measures & Reconciliation
python src/analytics/verify_powerbi_reconciliation.py

# 7. Start FastAPI Backend API (PostgreSQL 18 Direct Interface)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 8. Start React 18 + TypeScript Dashboard (Vite Dev Server)
cd dashboard
npm install
npm run dev

# 9. Build React Dashboard for Production
npm run build

# 10. Run Full Automated Test Suite (28 Tests Across ETL, DW, SQL, Power BI & API)
cd ..
python -m pytest tests/
```

---

## Test Suite Execution Results

```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\shubh\Downloads\novacart-analytics
plugins: anyio-3.7.1, asyncio-1.3.0
collected 28 items

tests\test_backend_api.py .........                                      [ 32%]
tests\test_cleaning.py ..                                                [ 39%]
tests\test_database.py .......                                           [ 64%]
tests\test_features.py .                                                 [ 67%]
tests\test_powerbi.py ...                                                [ 78%]
tests\test_sql_analysis.py ....                                          [ 92%]
tests\test_validation.py ..                                              [100%]

======================= 28 passed, 1 warning in 10.67s ========================
```
