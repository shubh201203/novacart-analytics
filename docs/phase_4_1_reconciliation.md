# NovaCart Phase 4.1 Data Warehouse & SQL Reconciliation Audit

This document presents the definitive audit, root-cause investigation, status breakdown matrix, and canonical KPI benchmarks reconciling Phase 3.1 and Phase 4 SQL analytical results.

---

## 1. Executive Reconciliation Summary

| Metric Name | Phase 3.1 Preliminary Note | Phase 4 Empirical DW Value | Discrepancy | Root Cause & Resolution |
| :--- | ---: | ---: | ---: | :--- |
| **Total Placed Net Revenue** | ₹971,486,941.80 | **₹971,486,941.80** | ₹0.00 | **100% Match**. Canonical Total Placed Demand across all 104,852 order lines. |
| **Realized Net Revenue** | ₹844,484,772.33 | **₹847,624,781.93** | +₹3,140,009.60 | Phase 3.1 preliminary note used a pre-recovery customer filter. The empirical DW table `fact_sales` contains exactly ₹847,624,781.93 for `is_completed = TRUE` (`Completed` + `Shipped`). |
| **Post-Return Settled Revenue**| ₹790,562,319.45 | **₹796,752,855.77** | +₹6,190,536.32 | Calculated as Realized Net Revenue (₹847,624,781.93) minus Returned Revenue (₹50,871,926.16). |
| **Total Placed Profit** | ₹300,804,487.91 | **₹300,804,487.91** | ₹0.00 | **100% Match**. Canonical Total Placed Profit across all 104,852 order lines. |
| **Realized Profit** | ₹261,489,612.40 | **₹262,159,342.82** | +₹669,730.42 | Traced to exact recovered order lines in `Completed` & `Shipped` status. |
| **Ordered Quantity** | 156,395 units | **156,395 units** | 0 units | **100% Match**. Total units across all 104,852 order lines. |
| **Returned Quantity** | 8,719 units | **8,712 units** | -7 units | Phase 1 raw data contained 8,719 returned units. Phase 2 data cleaning quarantined 6 invalid/orphan return records (7 units) into `returns_quarantine.csv`. `fact_returns` contains exactly 8,712 returned units. |

---

## 2. Order Status Breakdown Matrix

The table below details the exact breakdown of `fact_sales` by `order_status` in the data warehouse:

| Order Status | `is_completed` | Order Lines | Distinct Orders | Units Sold | Placed Net Revenue (₹) | Placed Profit (₹) | Profit Margin |
| :--- | :---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Completed** | `TRUE` | 79,042 | 47,388 | 117,723 | ₹731,845,964.25 | ₹226,516,465.54 | 30.95% |
| **Shipped** | `TRUE` | 12,307 | 7,466 | 18,477 | ₹115,778,817.68 | ₹35,642,877.28 | 30.79% |
| **Processing** | `FALSE` | 4,196 | 2,535 | 6,207 | ₹38,054,519.59 | ₹11,836,038.17 | 31.10% |
| **Cancelled** | `FALSE` | 4,233 | 2,525 | 6,360 | ₹40,080,068.13 | ₹12,407,982.33 | 30.96% |
| **Returned** | `FALSE` | 5,074 | 3,078 | 7,628 | ₹45,727,572.15 | ₹14,401,124.59 | 31.49% |
| **TOTAL (Placed Demand)** | — | **104,852** | **62,992** | **156,395** | **₹971,486,941.80** | **₹300,804,487.91** | **30.96%** |
| **REALIZED (Completed + Shipped)** | `TRUE` | **91,349** | **54,854** | **136,200** | **₹847,624,781.93** | **₹262,159,342.82** | **30.93%** |

---

## 3. Returned Quantity & Revenue Audit

### **Returned Quantity Lineage**:
* `returns_raw.csv`: 6,000 return event rows (8,719 units).
* `returns_quarantine.csv`: 6 isolated invalid/orphan return rows (7 units).
* `fact_returns` (DW): **5,792 return event rows** (**8,712 returned units**).

### **Returned Revenue Calculation**:
Joining `fact_returns` to `fact_sales` on `order_id` and `product_key`:
$$\text{Returned Revenue} = \sum \left( \text{fact\_returns.quantity\_returned} \times \frac{\text{fact\_sales.net\_revenue}}{\text{fact\_sales.quantity}} \right) = \text{₹50,871,926.16}$$

### **Post-Return Settled Revenue**:
$$\text{Net Settled Revenue} = \text{Realized Net Revenue (₹847,624,781.93)} - \text{Returned Revenue (₹50,871,926.16)} = \text{₹796,752,855.77}$$

---

## 4. RFM & Customer Base Reconciliation

* **Total Customers in `dim_customer`**: **5,000 customers**.
* **Active Customers with Completed Purchases**: **3,970 customers**.
* **Inactive / Pending Customers**: **1,030 customers** (Registered users whose orders were either cancelled, processing, or pending).
* **RFM Scoring Scope**: RFM segmentation strictly scores the **3,970 active completed customers** to ensure monetary metrics reflect true realized lifetime spend.

---

## 5. Strategic Business Opportunity Qualification

The strategic profit expansion estimate has been formalized under the required scenario modeling guidelines:

* **Title**: **"Illustrative profit opportunity under modeled strategic assumptions"**
* **Assumptions**:
  1. **Electronics Discount Cap**: Capping Electronics promotional discounts at 15% recovers ₹18.2M in profit margin.
  2. **High-Margin Spend Reallocation**: Reallocating acquisition ad spend toward Beauty & Personal Care (60%+ margin) yields ₹7.1M in incremental margin.
  3. **Total Modeled Opportunity**: **₹25.3M incremental annual profit expansion**.

---

## 6. FINAL CANONICAL APPROVED KPI BENCHMARKS

The following values represent the official canonical KPIs for all future phases (Power BI, React, and ML):

* **Total Placed Net Revenue**: **₹971,486,941.80**
* **Realized Net Revenue**: **₹847,624,781.93**
* **Post-Return Revenue (Net Settled)**: **₹796,752,855.77**
* **Total Placed Profit**: **₹300,804,487.91**
* **Realized Profit**: **₹262,159,342.82**
* **Ordered Quantity**: **156,395 units**
* **Returned Quantity**: **8,712 units**
