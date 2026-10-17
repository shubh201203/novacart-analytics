# NovaCart Master Data Dictionary

This document details every table, field name, data type, description, example value, and business meaning across the raw, processed, and star schema layers.

---

## 1. Raw & Processed Tables

### `customers` (`customers_raw.csv` / `customers_processed.csv` / `dim_customer`)
* `customer_key` (INT, PK): Surrogate primary key for data warehouse dimension. (e.g., `101`)
* `customer_id` (VARCHAR, NK): Unique business identifier for customer entity. (e.g., `CUST-10042`)
* `customer_name` (VARCHAR): Full name of customer. (e.g., `Aarav Sharma`)
* `gender` (VARCHAR): Gender classification (`Male`, `Female`, `Non-binary`).
* `age` (INT): Customer age in years. Bounds: 18 to 75. (e.g., `34`)
* `signup_date` (DATE): Account creation date. Format: `YYYY-MM-DD`. (e.g., `2023-04-12`)
* `city` (VARCHAR): Primary city location. (e.g., `Bengaluru`)
* `state_code` / `state` (VARCHAR): 2-letter state code. (e.g., `KA`)
* `region` (VARCHAR): Macro geographical region (`South`, `West`, `North`, `East`, `Central`, `Northeast`).
* `customer_segment` (VARCHAR): Business segment (`Consumer`, `Corporate`, `Small Business`).

---

### `products` (`products_raw.csv` / `products_processed.csv` / `dim_product`)
* `product_key` (INT, PK): Surrogate primary key for product dimension. (e.g., `55`)
* `product_id` (VARCHAR, NK): Unique SKU identifier. (e.g., `PROD-1024`)
* `product_name` (VARCHAR): Descriptive product name. (e.g., `BoatWave Audio & Wearables A1`)
* `category` (VARCHAR): High-level category (`Electronics`, `Apparel`, `Home & Kitchen`, `Beauty & Personal Care`, `Books & Media`, `Sports & Outdoors`).
* `subcategory` (VARCHAR): Specialized subcategory. (e.g., `Smartphones`, `Ethnic Wear`)
* `brand` (VARCHAR): Manufacturer or brand name. (e.g., `BoatWave`)
* `cost_price` (NUMERIC): Internal unit cost price in INR (₹). (e.g., `1200.00`)
* `list_price` (NUMERIC): Selling list price in INR (₹). (e.g., `1999.00`)

---

### `orders` (`orders_raw.csv` / `orders_processed.csv` / `fact_sales`)
* `sales_key` (BIGINT, PK): Surrogate primary key for sales fact table.
* `order_id` (VARCHAR): Unique transaction order identifier. (e.g., `ORD-100452`)
* `date_key` (INT, FK): Integer date key in `YYYYMMDD` format. (e.g., `20241015`)
* `customer_key` (INT, FK): Reference to `dim_customer`.
* `product_key` (INT, FK): Reference to `dim_product`.
* `location_key` (INT, FK): Reference to `dim_location`.
* `payment_key` (INT, FK): Reference to `dim_payment`.
* `quantity` (INT): Units purchased in item line. (e.g., `2`)
* `gross_sales` (NUMERIC): `quantity * unit_price`. (e.g., `3998.00`)
* `discount_amount` (NUMERIC): `gross_sales * discount`. (e.g., `399.80`)
* `net_revenue` (NUMERIC): `gross_sales - discount_amount`. (e.g., `3598.20`)
* `product_cost` (NUMERIC): `quantity * cost_price`. (e.g., `2400.00`)
* `shipping_cost` (NUMERIC): Freight/shipping fee in INR (₹). (e.g., `49.00`)
* `profit` (NUMERIC): `net_revenue - product_cost - shipping_cost`. (e.g., `1149.20`)
* `profit_margin` (NUMERIC): `profit / net_revenue`. (e.g., `0.3194`)
* `order_status` (VARCHAR): Lifecycle status (`Completed`, `Shipped`, `Processing`, `Cancelled`, `Returned`).
* `is_completed` (BOOLEAN): `TRUE` if status in (`Completed`, `Shipped`).
* `is_cancelled` (BOOLEAN): `TRUE` if status == `Cancelled`.
* `is_returned` (BOOLEAN): `TRUE` if status == `Returned`.
