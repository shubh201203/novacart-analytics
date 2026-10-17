# NovaCart RFM Customer Segmentation Methodology

This document outlines the Recency, Frequency, and Monetary (RFM) customer analytics methodology implemented for NovaCart.

---

## 1. Overview & Business Objectives
RFM segmentation categorizes NovaCart's customer base using transactional behavior to optimize marketing spend, retention programs, VIP loyalty rewards, and re-engagement campaigns.

All calculations strictly utilize **Realized Transactions** (`is_completed = TRUE`), excluding cancelled orders to reflect true customer lifetime value.

---

## 2. Metric Definitions & Analysis Anchor Date

* **Analysis Reference Date**: `2025-12-31` (The fixed terminal boundary of the 3-year historical dataset).
* **Recency ($R$)**:
  $$\text{Recency (Days)} = 2025\text{-}12\text{-}31 - \text{MAX}(\text{order\_date})$$
  *Number of days elapsed between customer's latest realized purchase and analysis date.*
* **Frequency ($F$)**:
  $$\text{Frequency} = \text{COUNT}(\text{DISTINCT } \text{order\_id}) \quad \text{where } \text{is\_completed} = \text{TRUE}$$
  *Total count of distinct completed orders placed by the customer.*
* **Monetary Value ($M$)**:
  $$\text{Monetary Value (₹)} = \sum (\text{net\_revenue}) \quad \text{where } \text{is\_completed} = \text{TRUE}$$
  *Total net revenue generated from completed purchases.*

---

## 3. Quintile Scoring (`NTILE(5)`)

Each metric is scored into 5 quintiles ($1$ to $5$):

* **Recency Score ($R\_Score$)**: `NTILE(5)` over `Recency ASC` (5 = Most Recent, 1 = Least Recent).
* **Frequency Score ($F\_Score$)**: `NTILE(5)` over `Frequency ASC` (5 = Highest Order Count, 1 = Lowest Order Count).
* **Monetary Score ($M\_Score$)**: `NTILE(5)` over `Monetary ASC` (5 = Highest Spend, 1 = Lowest Spend).

Composite RFM Score = $R\_Score \times 100 + F\_Score \times 10 + M\_Score$ (e.g. `555`, `111`).

---

## 4. Segment Mapping Rules

| Segment Name | $R\_Score$ | $F\_Score$ | $M\_Score$ | Strategic Action / Recommendation |
| :--- | :---: | :---: | :---: | :--- |
| **Champions** | 4–5 | 4–5 | 4–5 | VIP concierge, early festival sales access, brand ambassador incentives. |
| **Loyal Customers** | 3–5 | 3–5 | 3–5 | Cross-sell premium brands, referral rewards, loyalty tier points. |
| **Potential Loyalists**| 3–5 | 1–3 | 1–3 | Recommend subcategory upsells, offer multi-item bundle discounts. |
| **New Customers** | 4–5 | 1 | 1–2 | Onboarding welcome series, second-purchase discount voucher. |
| **At Risk** | 1–2 | 3–5 | 3–5 | Personalized win-back discount emails, SMS alerts on price drops. |
| **Can't Lose Them** | 1–2 | 4–5 | 4–5 | Direct phone/email outreach from customer success, heavy win-back offer. |
| **Hibernating / Lost**| 1–2 | 1–2 | 1–2 | Low-cost automated email re-engagement or suppress from ad targeting. |
