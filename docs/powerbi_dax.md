# NovaCart Power BI DAX Documentation

This document provides complete documentation of all Power BI DAX measures, filter contexts, formulas, and metric reconciliations.

---

## 1. Metric Reconciliation Summary (Power BI vs Canonical Phase 4.1 Benchmarks)

| Metric Name | Power BI DAX Measure Name | Power BI Calculated Value | Phase 4.1 Benchmark | Reconciliation Status |
| :--- | :--- | ---: | ---: | :---: |
| **Total Placed Net Revenue** | `[Total Placed Revenue]` | **₹971,486,941.80** | **₹971,486,941.80** | **100% Match** (₹0.00 Diff) |
| **Realized Net Revenue** | `[Realized Revenue]` | **₹847,624,781.93** | **₹847,624,781.93** | **100% Match** (₹0.00 Diff) |
| **Post-Return Revenue** | `[Post-Return Revenue]` | **₹796,752,855.77** | **₹796,752,855.77** | **100% Match** (₹0.00 Diff) |
| **Total Placed Profit** | `[Total Placed Profit]` | **₹300,804,487.91** | **₹300,804,487.91** | **100% Match** (₹0.00 Diff) |
| **Realized Profit** | `[Realized Profit]` | **₹262,159,342.82** | **₹262,159,342.82** | **100% Match** (₹0.00 Diff) |
| **Ordered Item Quantity** | `[Ordered Units]` | **156,395 units** | **156,395 units** | **100% Match** (0 Diff) |
| **Returned Item Quantity** | `[Returned Units]` | **8,712 units** | **8,712 units** | **100% Match** (0 Diff) |

---

## 2. Major DAX Measure Definitions & Filter Context

### **Core Revenue & Profit Measures**
* `[Total Placed Revenue]`: Unfiltered sum of `fact_sales[net_revenue]`.
* `[Realized Revenue]`: Evaluated under `CALCULATE(..., fact_sales[is_completed] = TRUE())`. Filters for completed and shipped sales.
* `[Returned Revenue]`: Iterates over `fact_returns` using `SUMX` to multiply `quantity_returned` by line-item net unit price from `fact_sales`.
* `[Post-Return Revenue]`: Evaluated as `[Realized Revenue] - [Returned Revenue]`.

### **Time Intelligence Measures**
* `[Previous Month Revenue]`: Uses `DATEADD(dim_date[full_date], -1, MONTH)` to calculate prior month sales.
* `[MoM Revenue Growth %]`: Evaluates `DIVIDE([Realized Revenue] - [Previous Month Revenue], [Previous Month Revenue], 0.0)`.
* `[Previous Year Revenue]`: Uses `SAMEPERIODLASTYEAR(dim_date[full_date])`.
* `[YoY Revenue Growth %]`: Evaluates `DIVIDE([Realized Revenue] - [Previous Year Revenue], [Previous Year Revenue], 0.0)`.
* `[3M Moving Avg Revenue]`: Uses `AVERAGEX(DATESINPERIOD(... -3, MONTH), [Realized Revenue])`.
