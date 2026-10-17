# NovaCart Data Generation & Analytics Assumptions

This document outlines the core business logic, statistical modeling rules, regional configurations, and intentional data-quality flaws embedded within the NovaCart E-Commerce platform dataset.

---

## 1. Geographical & Market Scope
* **Market**: India E-Commerce Retail.
* **Regions**: South, West, North, East, Central, Northeast across 18 representative Indian States and Tier-1/Tier-2 cities.
* **Currency**: Indian Rupee (₹ / INR).

---

## 2. Customer Generation Logic
* **Customer Base**: ~5,000 unique registered customer entities spanning 2022-01-01 to 2025-09-30 signup dates.
* **Customer Segments**: Consumer (72%), Corporate (18%), Small Business (10%).
* **Purchasing Concentration**: Modeled using a Pareto distribution ($a=1.5$), where top 15% power customers generate ~45% of total order volume and revenue (80/20 rule).

---

## 3. Product Catalog & Pricing Architecture
* **Catalog Size**: 180 SKUs across 6 major categories:
  * Electronics (Smartphones, Laptops, Audio & Wearables, Cameras)
  * Apparel (Ethnic Wear, Men's Casuals, Women's Western, Footwear)
  * Home & Kitchen (Mixer Grinders, Kitchenware, Home Furnishings, Water Purifiers)
  * Beauty & Personal Care (Skincare, Haircare, Ayurvedic Care, Grooming)
  * Books & Media (Indian Fiction, Exam Prep, Business & Finance)
  * Sports & Outdoors (Cricket Gear, Gym Equipment, Yoga Mats, Badminton)
* **Cost & List Price Rules**:
  * List Price ($P_{list}$) set realistically according to subcategory market rates in INR.
  * Cost Price ($P_{cost}$) derived from category profit margins:
    * Electronics: 18%–32% profit margin.
    * Apparel: 50%–70% profit margin.
    * Home & Kitchen: 38%–58% profit margin.
    * Beauty & Personal Care: 55%–75% profit margin.
    * Books & Media: 35%–50% profit margin.
    * Sports & Outdoors: 40%–60% profit margin.

---

## 4. Seasonality & Order Volume
* **Timeframe**: Jan 1, 2023 to Dec 31, 2025 (3 full calendar years).
* **Festive & Sales Spikes**:
  * **Diwali / Navratri Great Indian Sale (October–November)**: 2.1x–2.5x volume multiplier.
  * **Independence Day Freedom Sale (August)**: 1.5x volume multiplier.
  * **Year-End / Christmas Sale (December)**: 1.4x volume multiplier.
  * **Summer Surge (May–June)**: 1.15x volume multiplier.
  * **Post-Festive Dip (January–February)**: 0.8x volume multiplier.
* **Year-Over-Year Growth**: 2023 base (1.0x), 2024 (1.25x), 2025 (1.52x).

---

## 5. Payment Behavior
* **Payment Methods**:
  * **UPI (GPay / PhonePe / Paytm)**: 52% (Dominant payment rail in India).
  * **Cash on Delivery (COD)**: 22% (Significant for tier-2/3 cities).
  * **Credit Card**: 12%.
  * **Debit Card**: 8%.
  * **Net Banking**: 4%.
  * **Digital Wallet**: 2%.

---

## 6. Discount & Promotional Strategy
* **Discount Brackets**: 0% (42%), 5% (20%), 10% (16%), 15% (10%), 20% (6%), 25% (3%), 30% (2%), 40% (1%).
* **Festive Discounting**: Higher probability of 15%–30% discounts during Oct–Nov festival sales.

---

## 7. Returns Logic
* **Overall Return Rate**: Target ~5.0%–5.5% of total ordered quantity.
* **Category Variations**: Apparel and Footwear experience higher return rates (~8%–10%) due to sizing issues; Books & Beauty experience lower return rates (<3%).
* **Return Reasons**: Defective Product (28%), Wrong Size/Color (32%), Item Not as Described (18%), Changed Mind (14%), Late Delivery (8%).

---

## 8. Intentional Raw Data-Quality Flaws (For Phase 2 Cleaning Demo)
* **Duplicates**: ~0.3% duplicate customer rows and ~0.4% duplicate order-line rows.
* **Missing Attributes**: ~0.5% missing customer names/cities, ~0.2% missing customer_id or payment_method in orders, ~0.3% missing payment_status.
* **Casing Inconsistencies**: Mixed casing in categories (`electronics`, `ELECTRONICS`, `Electronics`) and state representations (`KA`, `Karnataka`, `ka`).
* **Invalid Field Values**: ~0.05% non-positive quantities (-1, 0) and ~0.05% malformed dates (`2024-02-30`).
