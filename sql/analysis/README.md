# NovaCart Advanced SQL Business Analysis Suite

This directory contains the SQL scripts powering NovaCart's business intelligence and customer/product analytics layer.

---

## SQL Analysis Script Sitemap

| Script Name | Primary Focus | Key SQL Techniques Demonstrated |
| :--- | :--- | :--- |
| [`01_sales_performance.sql`](./01_sales_performance.sql) | Global Sales KPIs, Order Status Distributions, AOV, Monthly Performance | `SUM`, `CASE WHEN`, `DISTINCT`, Conditional Aggregations, Window OVER() |
| [`02_customer_analysis.sql`](./02_customer_analysis.sql) | Top Customers, Customer Segment Profitability, Loyalty Tiers, Margin Variance | `CTEs`, `ROW_NUMBER()`, `HAVING`, Grouping, Ratio Calculations |
| [`03_product_analysis.sql`](./03_product_analysis.sql) | Category/Subcategory Margins, Top SKUs, Product Performance Matrix | `PERCENTILE_CONT()`, Nested CTEs, Threshold Quadrant Classification |
| [`04_regional_analysis.sql`](./04_regional_analysis.sql) | Regional Macro Demand, State Performance, Top City per Region | `PARTITION BY`, `ROW_NUMBER()`, Multi-table Joins |
| [`05_time_series_analysis.sql`](./05_time_series_analysis.sql) | MoM Growth %, YoY Growth %, 3-Month Moving Averages, Cumulative Running Totals | `LAG()`, `LEAD()`, `ROWS BETWEEN PRECEDING AND CURRENT ROW` |
| [`06_rfm_segmentation.sql`](./06_rfm_segmentation.sql) | Recency, Frequency, Monetary Scoring & Customer Segment Classification | `DATEDIFF()`, `NTILE(5)`, Composite Scoring, Rule Mapping |
| [`07_cohort_retention.sql`](./07_cohort_retention.sql) | Customer Acquisition Cohorts & Month-over-Month Retention Rates | `DATE_TRUNC()`, `STRFTIME()`, Cohort Index Offsets, Matrix Aggregations |
| [`08_return_analysis.sql`](./08_return_analysis.sql) | Return Rate %, Returned Revenue, Category Return Share, Return Reasons | Non-multiplying CTE joins, Safe Ratio Formulas |
| [`09_payment_analysis.sql`](./09_payment_analysis.sql) | Payment Method Share, Success/Failure Rates, Safe CTE Order Reconciliation | Authoritative `fact_payments` joins, Double-counting Prevention |
| [`10_profitability_analysis.sql`](./10_profitability_analysis.sql) | Category Cost Structure, Pareto 80/20 Profit Contribution Analysis | Cumulative SUM OVER(), Pareto Classification |
| [`11_advanced_window_analysis.sql`](./11_advanced_window_analysis.sql) | Category Product Rankings, Regional Customer Rankings, LEAD/LAG Forecasting | `DENSE_RANK()`, `LEAD()`, `LAG()`, `PERCENT_RANK()` |
| [`12_business_questions.sql`](./12_business_questions.sql) | 15 C-Level Strategic Business Questions & Executive Insights | Comprehensive Advanced SQL, UNION ALL, Subqueries |


---

## Execution Guide

All SQL scripts are executed automatically via the master Python analytics runner:

```bash
python src/analytics/run_sql_analysis.py
```

Generated result CSVs are stored under `data/analysis_results/`.
