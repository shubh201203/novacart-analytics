# NovaCart Analytics — Implemented Power BI Dashboard Specification

## Document purpose

This document describes the **six Power BI report pages implemented in NovaCart Analytics**. It replaces the earlier aspirational visual plan with the current dashboard structure, based on the completed Power BI build.

NovaCart uses a **synthetic India-focused e-commerce dataset**. Figures and findings in this project are analytical results from that synthetic dataset and should not be presented as real company performance.

## Project context

- **Data source:** Synthetic India-focused e-commerce orders, customers, products, returns, and payment events.
- **Warehouse:** PostgreSQL database `novacart_analytics`.
- **Model:** Five dimensions (`dim_customer`, `dim_product`, `dim_location`, `dim_payment`, `dim_date`) and three facts (`fact_sales`, `fact_returns`, `fact_payments`).
- **Power BI source:** PostgreSQL-imported model, plus the PostgreSQL view `public.vw_cohort_retention` used for the cohort retention matrix.
- **Report pages:** Executive Overview; Sales & Profitability; Customer Intelligence; Product Analytics; Regional Operations; Customer Retention & RFM.

## Formatting and design standards

- **Primary accent:** Deep Navy Blue (`#0F2C59`).
- **Secondary accent:** Steel Teal (`#1A5D1A`).
- **Highlight/alert:** Crimson (`#D80032`).
- **Neutral background:** Soft Light Grey (`#F8F9FA`).
- **Card fill/border:** White (`#FFFFFF`) with a light-grey border (`#E0E0E0`).
- **Currency:** Indian Rupee; use a consistent display scale across pages (for example, ₹847.62M or ₹84.76 Cr).
- **Percentages:** Apply percentage formatting to percentage-valued measures only. The SQL view `public.vw_cohort_retention` stores `retention_rate` on a 0–100 scale, so the Power BI measure divides by 100 before percentage formatting.
- **Slicers:** Year, Month, Region, and Product Category are used on the implemented pages. Confirm that copied slicers have the intended interactions on each page.
- **Measure consistency:** Use the same canonical measure definitions across pages and reconcile cards with cleared slicers.

## Canonical reference metrics

The following figures are project reconciliation benchmarks under the documented metric definitions and with report filters cleared:

| Metric | Reference value |
|---|---:|
| Placed Net Revenue | ₹971,486,941.80 |
| Realized Revenue (Completed + Shipped) | ₹847,624,781.93 |
| Returned Revenue | ₹50,871,926.16 |
| Post-Return Revenue | ₹796,752,855.77 |
| Realized Profit | ₹262,159,342.82 |
| Realized Margin | 30.93% |
| Ordered Quantity | 156,395 |
| Returned Quantity | 8,712 |
| Return Rate | 5.57% |
| Total Customers | 5,000 |
| Active Customers | 3,970 |
| Repeat Customers | 3,260 |
| One-Time Customers | 710 |
| Repeat-Customer Share | 82.12% |
| Average Order Value | ₹15,452.38 |
| Realized Orders | 54,854 |

**Metric caution:** Realized Revenue includes Completed and Shipped orders. Post-Return Revenue subtracts Returned Revenue from Realized Revenue. Do not label these measures interchangeably. Fact tables have different grains; do not join `fact_sales` and `fact_payments` row by row for financial aggregation because that can multiply values.

---

## Page 1 — Executive Overview

### Purpose
Provide a high-level view of realized business performance, profitability, customers, and returns.

### KPI cards implemented
- Post-Return Revenue
- Realized Profit
- Realized Margin
- Active Customers
- Average Order Value (AOV)
- Return Rate

### Visuals implemented
- **Revenue by Region:** Compares realized revenue across regions.
- **Profit by Product Category:** Compares realized profit by category.
- **Realized Revenue Trend:** Shows realized revenue over time.
- **Order Status Breakdown:** Summarizes the distribution of order statuses.

### Slicers
- Year
- Month
- Region
- Product Category

### QA notes
- With all filters cleared, reconcile the KPI cards to the canonical metrics above.
- Confirm that year, month, region, and category selections affect the expected visuals.
- Check that the revenue trend is chronologically sorted.

---

## Page 2 — Sales & Profitability

### Purpose
Explore revenue and profit trends, order-status differences, discount impact, and product-level profitability.

### KPI cards implemented
- Gross Sales
- Discount Amount
- Total Placed Revenue
- Realized Profit
- Realized Margin

### Visuals implemented
- **Monthly Realized Revenue vs Profit:** Combo chart comparing monthly realized revenue and realized profit.
- **Placed Revenue by Order Status:** Shows placed revenue across order statuses.
- **Realized Profit by Category:** Compares realized profit by product category.
- **Monthly Discount Impact:** Displays discount amount and discount percentage over time.
- **Top 10 Products by Realized Profit:** Ranks products by realized profit.

### Slicers
- Year
- Month
- Region
- Product Category

### QA notes
- Validate the monthly axis sort order and the secondary axis on the discount-impact chart.
- Confirm that the Top 10 ranking responds appropriately to filters.
- Distinguish placed revenue from realized revenue.

---

## Page 3 — Customer Intelligence

### Purpose
Understand active, repeat, and one-time customers, customer value, and purchase frequency.

### KPI cards implemented
- Active Customers
- Repeat Customers
- One-Time Customers
- Revenue per Active Customer

### Visuals implemented
- **Repeat vs One-Time Customers:** Donut chart using the disconnected `Customer Type` helper table and `Customer Type Count` measure.
- **Realized Revenue by Region:** Compares realized revenue by region.
- **Top 10 Customers by Realized Revenue:** Ranks customers by realized revenue.
- **Customer Purchase Frequency — Top 10:** Shows the top customers by purchase-frequency measure.

### Slicers
- Year
- Month
- Region
- Product Category

### QA notes
- Confirm repeat plus one-time customers equals the intended active-customer population for the selected filter context.
- Check that customer-level revenue and order counts are filtered by customer.
- Validate any unusually high customer order-frequency values against the underlying data before citing them in project claims.

---

## Page 4 — Product Analytics

### Purpose
Compare category and product performance, margins, discounts, and product-level profitability.

### KPI cards implemented
- Realized Revenue
- Realized Profit
- Realized Margin
- Discount Percentage

### Visuals implemented
- **Profit by Category:** Compares realized profit across product categories.
- **Revenue by Category:** Compares realized revenue across categories.
- **Top 10 Products by Realized Profit:** Ranks products by realized profit.
- **Discount Percentage vs Profit Margin:** Scatter plot for product-level comparison.
- **Product Performance Matrix:** Tabular/matrix comparison of product performance measures.

### Slicers
- Year
- Month
- Region
- Product Category

### QA notes
- Confirm the scatter plot uses the intended discount and margin measures on the axes.
- Check the matrix column widths and horizontal scrolling so important measures are discoverable.
- Describe scatter relationships as associations; do not imply that discounts cause margin changes without further analysis.

---

## Page 5 — Regional Operations

### Purpose
Compare regional sales, profitability, order statuses, category mix, and leading locations.

### KPI cards implemented
- Realized Revenue
- Realized Profit
- Realized Orders
- Return Rate

### Visuals implemented
- **Revenue by Region**
- **Profit by Region**
- **Order Status Mix by Region**
- **Regional Category Matrix**
- **Top Locations by Realized Revenue**

### Slicers
- Year
- Month
- Region
- Product Category

### QA notes
- Realized Orders should count distinct orders with Completed or Shipped status, not sales-line rows.
- Check that regional and location totals reconcile with the relevant filter context.
- Verify that status breakdowns use the correct counting grain.

---

## Page 6 — Customer Retention & RFM

### Purpose
Review customer-type composition, customer segmentation, customer value, and month-by-month repeat-purchase retention.

### KPI cards planned/implemented on the page
- Active Customers
- Repeat Customers
- Repeat Customer Share
- One-Time Customers

Confirm the displayed cards and measures in the current `.pbix` before treating every item above as final.

### Visuals implemented/in progress
- **Customer Type Split:** Donut chart distinguishing repeat and one-time customers.
- **Customer Segment Distribution:** Customer counts by the available customer segment field. If the field contains Consumer, Corporate, and Small Business, title the visual “Customer Distribution by Customer Segment,” not “RFM Segment.”
- **Monthly Customer Cohort Retention:** Matrix heatmap using `public.vw_cohort_retention`.
- **Customer Value Table:** Customer-level realized revenue, realized profit, realized orders, and customer segment, sorted by realized revenue as appropriate.

### Cohort-retention data definition
The PostgreSQL view `public.vw_cohort_retention` is calculated from `fact_sales` joined to `dim_date`. A customer's cohort month is their first month with a `Completed` or `Shipped` purchase. Retention in a later month means that the customer had another `Completed` or `Shipped` purchase in that month. This is **repeat-purchase activity**, not app-login or website-session retention.

The view includes:
- `cohort_month`
- `months_since_first_purchase`
- `cohort_customers`
- `retained_customers`
- `retention_rate` (0–100 scale)

The Power BI measure should divide the SQL value by 100 before applying Percentage formatting, for example:

```DAX
Cohort Retention % =
DIVIDE(
    AVERAGE('public vw_cohort_retention'[retention_rate]),
    100
)
```

Use the actual table name shown in the Power BI Data pane if it differs. Month 0 should show 100% for each cohort with a recorded cohort size.

### QA notes
- Do not describe Consumer/Corporate/Small Business as RFM classifications.
- Verify that the customer segment field and customer-count measure use the appropriate customer population.
- Avoid misleading grand totals that average cohort retention percentages across different cohort sizes.
- Confirm customer-level order counts and revenue are correctly filtered by customer.
- Keep the cohort view independent unless relationships and filter behavior are deliberately designed and tested.

---

## Cross-page QA checklist

Before publishing the report:

- [ ] Clear slicers and reconcile repeated KPIs across pages.
- [ ] Verify the four slicers and visual interactions on each page.
- [ ] Confirm that date axes and month labels sort chronologically.
- [ ] Confirm distinct-order measures count orders rather than order lines.
- [ ] Verify customer-level measures respond to customer filter context.
- [ ] Check matrix widths, axis labels, tooltips, and conditional formatting.
- [ ] Confirm cohort Month 0 is 100% and the metric is described as repeat-purchase retention.
- [ ] Save and reopen the `.pbix` to ensure the report loads successfully.
- [ ] Capture a clean screenshot of each page for the README and portfolio.
- [ ] Keep credentials, `.env`, and other secrets out of version control.
- [ ] Label the dataset and resulting findings as synthetic.

## Repository documentation to keep in sync

- `powerbi/dashboard_specifications.md` — this implemented dashboard specification.
- `powerbi/dax_measures.md` — keep measure names and definitions aligned with the `.pbix`.
- `powerbi/power_query_m.md` — keep connector and type-conversion documentation aligned with the current model.
- SQL source for `public.vw_cohort_retention` — save the view definition in the repository so the cohort visual can be recreated.
- `reports/dashboard_screenshots/` — screenshots of all six report pages.
