# NovaCart Analytics — React + TypeScript BI Dashboard & FastAPI Backend

This directory contains the production-grade **Web Business Intelligence Dashboard** for NovaCart, paired with a high-performance **FastAPI backend** connected directly to the local PostgreSQL 18 data warehouse (`novacart_analytics`).

---

## Architecture Overview

```text
 ┌────────────────────────────────────────────────────────┐
 │           React 18 + TypeScript Frontend               │
 │        (Vite + Tailwind CSS v4 + Recharts)             │
 │   • Global multi-slicer bar (Year, Month, Region, Cat) │
 │   • 6 Dedicated Tab Pages mirroring Power BI suite     │
 │   • Real-time Rupee (₹) & Compact Metric Formatting    │
 └───────────────────────────▲────────────────────────────┘
                             │ HTTP REST JSON (/api)
 ┌───────────────────────────▼────────────────────────────┐
 │                  FastAPI Backend                       │
 │      • Reads credentials server-side from .env         │
 │      • Parameterized SQL queries against PostgreSQL 18 │
 │      • Zero mock data; 100% dynamic calculations       │
 └───────────────────────────▲────────────────────────────┘
                             │ SQL Queries (No data duplicated)
 ┌───────────────────────────▼────────────────────────────┐
 │            PostgreSQL 18 Data Warehouse                │
 │         (novacart_analytics: 8 star schema tables)     │
 └────────────────────────────────────────────────────────┘
```

---

## 6 Interactive Dashboard Pages

1. **Executive Overview (`/api/overview`)**:
   - 6 Core C-Suite KPIs (Post-Return Revenue, Realized Profit & Margin, Active Customers, AOV, Return Rate).
   - Regional Revenue horizontal bar chart.
   - Category Profit horizontal bar chart.
   - Order Status breakdown donut chart.
   - Multi-year Realized Revenue monthly trendline (2022–2026).
2. **Sales & Profitability (`/api/sales`)**:
   - Gross Sales, Discount Amount, Placed Revenue, Realized Profit, and Realized Margin.
   - Monthly Realized Revenue vs. Profit combo bar chart.
   - Placed Revenue by Order Status breakdown.
   - Monthly Promotional Discount Depth trendline.
   - Top 10 Products by Realized Profit.
3. **Customer Intelligence (`/api/customers`)**:
   - Active Customers, Repeat Customers, One-Time Customers, Repeat Customer Share (82.12%), and Revenue Per Active Customer.
   - Customer Purchase Frequency ranking.
   - Repeat vs. One-Time Customer donut split.
   - Top 10 Customers by Realized Revenue.
   - Realized Revenue by Region.
4. **Product Analytics (`/api/products`)**:
   - Catalog Realized Revenue, Profit, Margin, and Discount %.
   - Realized Profit by Category.
   - Realized Revenue by Category.
   - Discount % vs. Profit Margin scatter plot.
   - Category Profitability cross-tabulated matrix table.
   - Top 10 Products by Realized Profit.
5. **Regional Operations (`/api/regional`)**:
   - Realized Revenue, Realized Profit, Realized Orders (54,854), and Return Rate (5.57%).
   - Regional Revenue & Profit distribution across 6 macro-regions.
   - Top 10 States by Realized Revenue.
   - Full Regional Revenue by Category cross-tabulated matrix table.
6. **Customer Retention & RFM (`/api/retention`)**:
   - Active Customers, Repeat Customers, One-Time Customers, Repeat Customer Share.
   - Realized Revenue and Account distribution by customer demographic segment (Consumer, Corporate, Small Business).
   - Top Customer Value & Purchase Behavior table.
   - **Monthly Customer Cohort Retention Heatmap Matrix**: Powered directly by `public.vw_cohort_retention` tracking repeat purchase retention rates across subsequent months ($M_0$ to $M_{18}$).

---

## Local Development & Execution Instructions

### 1. Prerequisites
- PostgreSQL 18 running locally on port `5432` with database `novacart_analytics`.
- Project root `.env` configured with your PostgreSQL credentials:
  ```env
  POSTGRES_HOST=localhost
  POSTGRES_PORT=5432
  POSTGRES_DB=novacart_analytics
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=your_password
  ```
- Python 3.10+ and Node.js v18+.

---

### 2. Start the FastAPI Backend

From the repository root:

```bash
# Start FastAPI with Uvicorn (Hot-Reload Enabled)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

- API Docs (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
- API Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

### 3. Start the React Frontend

Open a new terminal window in `dashboard/`:

```bash
cd dashboard

# Install dependencies (if not already installed)
npm install

# Start Vite Development Server
npm run dev
```

- Web Dashboard URL: [http://localhost:5173](http://localhost:5173)

---

### 4. Run Automated Backend & Frontend Tests

```bash
# Run FastAPI integration test suite
python -m pytest tests/test_backend_api.py

# Run complete repository test suite (27 tests)
python -m pytest tests/

# Run frontend production build
cd dashboard && npm run build
```
