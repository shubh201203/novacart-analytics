# NovaCart Advanced SQL Analysis Layer Documentation

This document describes the design, execution, metric semantics, and outputs of the NovaCart Advanced SQL Analytics Suite (`sql/analysis/` 01–12 scripts).

---

## 1. Executive Summary & Purpose
The SQL Analysis Layer bridges raw database tables and executive-level business intelligence. It answers strategic C-level questions regarding revenue trajectory, customer lifetime value, product margin matrices, RFM segmentation, cohort retention, regional demand, and payment gateway reliability.

---

## 2. Metric Semantics & Standards

All queries adhere strictly to Phase 3.1 & Phase 4 defined metric standards:

| Metric Name | SQL Formula / Filtering | Benchmark Value | Business Context |
| :--- | :--- | ---: | :--- |
| **Total Placed Net Revenue** | `SUM(net_revenue)` | **₹971,486,941.80** | Total gross demand generated at checkout across all 104,852 order lines. |
| **Realized Net Revenue** | `SUM(net_revenue) WHERE is_completed = TRUE` | **₹844,484,772.33** | Net settled revenue from fulfilled orders (`Completed`, `Shipped`). |
| **Post-Return Settled Revenue** | `Realized Net Revenue - Returned Revenue` | **₹790,562,319.45** | Net GAAP revenue retained after customer refunds. |
| **Total Placed Profit** | `SUM(profit)` | **₹300,804,487.91** | Total gross operating profit generated at checkout. |
| **Realized Profit** | `SUM(profit) WHERE is_completed = TRUE` | **₹261,489,612.40** | Operating profit earned from fulfilled sales. |
| **Ordered Quantity** | `SUM(quantity)` | **156,395 units** | Physical item volume ordered across all order lines. |
| **Returned Quantity** | `SUM(quantity_returned)` | **8,719 units** | Physical item volume returned via `fact_returns`. |

---

## 3. SQL Script Directory Structure (`sql/analysis/`)

```text
sql/analysis/
├── 01_sales_performance.sql      --> Global KPIs, Order Status Distributions, Monthly Trends
├── 02_customer_analysis.sql       --> Top Customers, Segment Profitability, Loyalty Tiers
├── 03_product_analysis.sql        --> Category Margins, Top SKUs, Product Matrix Classification
├── 04_regional_analysis.sql       --> Regional Demand, State Breakdowns, Top City per Region
├── 05_time_series_analysis.sql    --> MoM Growth %, YoY Growth %, Moving Averages, Running Totals
├── 06_rfm_segmentation.sql        --> Recency, Frequency, Monetary NTILE(5) Scoring & Segments
├── 07_cohort_retention.sql        --> Customer Acquisition Cohorts & Monthly Retention Rates
├── 08_return_analysis.sql         --> Return Rate %, Returned Revenue, Return Reasons
├── 09_payment_analysis.sql        --> Gateway Success Rates, Method Share, Safe Order CTEs
├── 10_profitability_analysis.sql  --> Category Cost Structure & Pareto 80/20 Profit Analysis
├── 11_advanced_window_analysis.sql--> DENSE_RANK(), LEAD(), LAG(), PERCENT_RANK() Demos
├── 12_business_questions.sql      --> 15 Strategic C-Level Business Questions
└── README.md                      --> Directory Sitemap & Execution Guide
```

---

## 4. Analytical Output CSV Datasets (`data/analysis_results/`)

Running the SQL suite produces 10 production-ready analytical datasets:

1. `monthly_sales.csv`: Month-by-month orders, placed revenue, realized revenue, profit, and margins.
2. `customer_value.csv`: Customer-level orders, units, realized revenue, profit, and margin rankings.
3. `product_performance.csv`: Product catalog metrics with automated matrix classification (`Star Product`, `Volume Driver`, `Hidden Gem`, `Underperformer`).
4. `regional_performance.csv`: Macro regional metrics across active customers, orders, revenue, and margins.
5. `rfm_segments.csv`: Customer segment breakdowns across Champions, Loyalists, At Risk, etc.
6. `cohort_retention.csv`: Cohort acquisition month retention rate % matrix over 12 months.
7. `return_analysis.csv`: Return rate % and returned revenue by product category.
8. `payment_analysis.csv`: Payment gateway transaction volume and success rates.
9. `profitability_analysis.csv`: Category cost structure and realized profit margins.
10. `business_questions_summary.csv`: Summary of C-level strategic insights.

---

## 5. Execution Commands

```bash
# 1. Execute SQL Suite and Export Analytical Datasets
python src/analytics/run_sql_analysis.py

# 2. Run Pytest Test Suite
python -m pytest tests/
```
