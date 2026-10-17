# NovaCart Power BI DAX Measures & Metrics Suite

This document defines the complete DAX measure repository for the NovaCart Power BI Analytical Model. All measures strictly adhere to Phase 4.1 Canonical KPI Benchmarks and use optimal DAX patterns (`CALCULATE`, `DIVIDE`, `SUMX`, `VAR`/`RETURN`, Time Intelligence functions).

---

## Measure Table: `_Measures`

### 1. REVENUE MEASURES

```dax
-- Total Placed Net Revenue (Benchmark: ₹971,486,941.80)
-- Total gross demand generated at checkout across all 104,852 order lines regardless of lifecycle status.
Total Placed Revenue = 
SUM ( fact_sales[net_revenue] )
```

```dax
-- Realized Net Revenue (Benchmark: ₹847,624,781.93)
-- Net settled revenue for fulfilled orders (Completed & Shipped status).
Realized Revenue = 
CALCULATE (
    SUM ( fact_sales[net_revenue] ),
    fact_sales[is_completed] = TRUE ()
)
```

```dax
-- Returned Revenue (Benchmark: ₹50,871,926.16)
-- Monetary value of items returned by customers.
Returned Revenue = 
SUMX (
    fact_returns,
    fact_returns[quantity_returned] * RELATED ( fact_sales[net_revenue] ) / RELATED ( fact_sales[quantity] )
)
```

```dax
-- Post-Return Revenue (Net Settled) (Benchmark: ₹796,752,855.77)
-- Final GAAP revenue retained after subtracting customer refunds.
Post-Return Revenue = 
[Realized Revenue] - [Returned Revenue]
```

---

### 2. PROFIT & MARGIN MEASURES

```dax
-- Total Placed Profit (Benchmark: ₹300,804,487.91)
-- Total gross operating profit across all 104,852 order lines.
Total Placed Profit = 
SUM ( fact_sales[profit] )
```

```dax
-- Realized Profit (Benchmark: ₹262,159,342.82)
-- Net operating profit earned from fulfilled sales.
Realized Profit = 
CALCULATE (
    SUM ( fact_sales[profit] ),
    fact_sales[is_completed] = TRUE ()
)
```

```dax
-- Realized Profit Margin % (Benchmark: 30.93%)
-- Profitability percentage ratio of realized profit over realized revenue.
Realized Profit Margin % = 
DIVIDE (
    [Realized Profit],
    [Realized Revenue],
    0.0
)
```

---

### 3. ORDER & UNIT MEASURES

```dax
-- Total Order Lines (Benchmark: 104,852 lines)
Total Order Lines = 
COUNTROWS ( fact_sales )
```

```dax
-- Distinct Orders Placed (Benchmark: 62,992 orders)
Distinct Orders Placed = 
DISTINCTCOUNT ( fact_sales[order_id] )
```

```dax
-- Realized Distinct Orders (Benchmark: 54,854 orders)
Realized Distinct Orders = 
CALCULATE (
    DISTINCTCOUNT ( fact_sales[order_id] ),
    fact_sales[is_completed] = TRUE ()
)
```

```dax
-- Ordered Units (Benchmark: 156,395 units)
Ordered Units = 
SUM ( fact_sales[quantity] )
```

```dax
-- Average Items Per Order (Benchmark: 2.48 units/order)
Avg Items Per Order = 
DIVIDE (
    [Ordered Units],
    [Distinct Orders Placed],
    0.0
)
```

---

### 4. CUSTOMER ANALYTICS MEASURES

```dax
-- Total Customers (Benchmark: 5,000 customers)
Total Customers = 
COUNTROWS ( dim_customer )
```

```dax
-- Active Customers with Realized Purchases (Benchmark: 3,970 customers)
Active Customers = 
CALCULATE (
    DISTINCTCOUNT ( fact_sales[customer_key] ),
    fact_sales[is_completed] = TRUE ()
)
```

```dax
-- Repeat Customers (Customers with >1 Realized Order) (Benchmark: 3,428 customers)
Repeat Customers = 
VAR CustomerOrderCounts =
    ADDCOLUMNS (
        VALUES ( dim_customer[customer_key] ),
        "@OrderCount", CALCULATE ( DISTINCTCOUNT ( fact_sales[order_id] ), fact_sales[is_completed] = TRUE () )
    )
RETURN
    COUNTROWS ( FILTER ( CustomerOrderCounts, [@OrderCount] > 1 ) )
```

```dax
-- One-Time Customers (Customers with exactly 1 Realized Order) (Benchmark: 542 customers)
One-Time Customers = 
VAR CustomerOrderCounts =
    ADDCOLUMNS (
        VALUES ( dim_customer[customer_key] ),
        "@OrderCount", CALCULATE ( DISTINCTCOUNT ( fact_sales[order_id] ), fact_sales[is_completed] = TRUE () )
    )
RETURN
    COUNTROWS ( FILTER ( CustomerOrderCounts, [@OrderCount] = 1 ) )
```

```dax
-- Average Order Value (AOV Realized) (Benchmark: ₹15,452.38)
Average Order Value = 
DIVIDE (
    [Realized Revenue],
    [Realized Distinct Orders],
    0.0
)
```

```dax
-- Revenue Per Customer (Realized LTV) (Benchmark: ₹213,507.50)
Revenue Per Customer = 
DIVIDE (
    [Realized Revenue],
    [Active Customers],
    0.0
)
```

```dax
-- Profit Per Customer (Benchmark: ₹66,035.10)
Profit Per Customer = 
DIVIDE (
    [Realized Profit],
    [Active Customers],
    0.0
)
```

---

### 5. RETURNS MEASURES

```dax
-- Returned Units (Benchmark: 8,712 units)
Returned Units = 
SUM ( fact_returns[quantity_returned] )
```

```dax
-- Overall Return Rate % (Benchmark: 5.57%)
Overall Return Rate % = 
DIVIDE (
    [Returned Units],
    [Ordered Units],
    0.0
)
```

---

### 6. TIME INTELLIGENCE MEASURES

```dax
-- Previous Month Realized Revenue
Previous Month Revenue = 
CALCULATE (
    [Realized Revenue],
    DATEADD ( dim_date[full_date], -1, MONTH )
)
```

```dax
-- Month-over-Month (MoM) Revenue Growth %
MoM Revenue Growth % = 
VAR PrevRev = [Previous Month Revenue]
VAR CurrRev = [Realized Revenue]
RETURN
    IF (
        NOT ISBLANK ( PrevRev ) && PrevRev > 0,
        DIVIDE ( CurrRev - PrevRev, PrevRev, 0.0 ),
        BLANK ()
    )
```

```dax
-- Previous Year Realized Revenue
Previous Year Revenue = 
CALCULATE (
    [Realized Revenue],
    SAMEPERIODLASTYEAR ( dim_date[full_date] )
)
```

```dax
-- Year-over-Year (YoY) Revenue Growth %
YoY Revenue Growth % = 
VAR PrevYrRev = [Previous Year Revenue]
VAR CurrRev = [Realized Revenue]
RETURN
    IF (
        NOT ISBLANK ( PrevYrRev ) && PrevYrRev > 0,
        DIVIDE ( CurrRev - PrevYrRev, PrevYrRev, 0.0 ),
        BLANK ()
    )
```

```dax
-- Year-to-Date (YTD) Realized Revenue
YTD Realized Revenue = 
TOTALYTD ( [Realized Revenue], dim_date[full_date] )
```

```dax
-- 3-Month Moving Average Realized Revenue
3M Moving Avg Revenue = 
AVERAGEX (
    DATESINPERIOD ( dim_date[full_date], MAX ( dim_date[full_date] ), -3, MONTH ),
    [Realized Revenue]
)
```
