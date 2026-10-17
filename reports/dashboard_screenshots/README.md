# NovaCart Analytics — Power BI Dashboard Screenshot Archive

This directory serves as the official, version-controlled image repository for the **NovaCart 6-Page Power BI Business Intelligence Dashboard Suite**.

All screenshots stored here are genuine exports from the live Power BI Desktop report, built on top of the local PostgreSQL 18 Star Schema data warehouse (`novacart_analytics`).

---

## Filename-to-Dashboard-Page Mapping

| Filename | Power BI Report Page | Core Purpose & Analytical Focus | Dimensions / Format | Verification Status |
| :--- | :--- | :--- | :---: | :---: |
| [`01_executive_overview.png`](./01_executive_overview.png) | **Page 1: Executive Overview** | High-level C-Suite KPI summary (Post-Return Revenue, Realized Profit & Margin, Active Customers, AOV, Return Rate, Regional Revenue, Category Profit, Trend, Order Status). | 1024 × 571 (PNG) | Verified Genuine |
| [`02_sales_profitability.png`](./02_sales_profitability.png) | **Page 2: Sales & Profitability** | Revenue composition (Gross Sales, Discounts, Placed Revenue), Monthly Realized Revenue vs Profit combo chart, Order Status breakdown, Monthly Discount depth impact. | 1024 × 573 (PNG) | Verified Genuine |
| [`03_customer_intelligence.png`](./03_customer_intelligence.png) | **Page 3: Customer Intelligence** | Customer value and loyalty, Repeat vs One-Time Customers split (82.12% vs 17.88%), Revenue Per Active Customer, Purchase frequency, Top 10 Customers ranking. | 1024 × 573 (PNG) | Verified Genuine |
| [`04_product_analytics.png`](./04_product_analytics.png) | **Page 4: Product Analytics** | Category-level margins, SKU-level profitability, Discount % vs Profit Margin scatter plot, Cross-tabulated Category Profitability Matrix. | 1024 × 574 (PNG) | Verified Genuine |
| [`05_regional_operations.png`](./05_regional_operations.png) | **Page 5: Regional Operations** | Geographic performance across 6 macro-regions and 18 Indian States, Regional fulfillment order status mix, Cross-tabulated Regional Revenue by Category Matrix. | 1024 × 573 (PNG) | Verified Genuine |
| [`06_customer_retention_rfm.png`](./06_customer_retention_rfm.png) | **Page 6: Customer Retention & RFM** | Monthly Customer Cohort Retention Heatmap Matrix (powered by `public.vw_cohort_retention`), Customer Distribution by Segment, Granular Customer Lifetime Value Table. | 1024 × 572 (PNG) | Verified Genuine |

---

## Capture Metadata

- **Date Captured:** October 17, 2026
- **Source Environment:** Microsoft Power BI Desktop connected to local PostgreSQL 18 (`novacart_analytics` on `localhost:5432`)
- **Authoring Engine:** Power BI native visuals with custom dark/light theme, custom DAX measure library, and PostgreSQL Star Schema
- **Resolution Standard:** Standard high-definition presentation exports (1024 width, 16:9 widescreen ratio)
- **Pending Manual Captures:** **None (0)**. All 6 genuine pages are captured, validated, and archived.

---

## Instructions for Updating Screenshots

Whenever modifications are made to the Power BI report (`powerbi/NovaCart_Analytics.pbix`), update this repository using the following procedure:

1. Open `powerbi/NovaCart_Analytics.pbix` in Power BI Desktop.
2. In Power BI Desktop, ensure all top slicers (Year, Month, Region, Category) are set to **"All"** (cleared state) to preserve canonical baseline metrics.
3. For each of the 6 pages:
   - Navigate to the page.
   - Capture a full-canvas screenshot (using Snipping Tool or `File -> Export -> Export to PDF / PNG` without cropping visual headers, cards, or slicers).
   - Save the image to this folder matching the exact filename listed in the mapping table above.
4. Verify file integrity using Python:
   ```bash
   python -c "
   import os; from PIL import Image
   for f in sorted(os.listdir('reports/dashboard_screenshots')):
       if f.endswith('.png'):
           p = os.path.join('reports/dashboard_screenshots', f)
           with Image.open(p) as img:
               print(f'{f}: {img.size}, {img.format}, {os.path.getsize(p)} bytes')
   "
   ```
5. Commit the updated image files to Git.
