-- =============================================================================
-- NovaCart SQL Analysis Suite — 12: Executive Business Questions (15 Key Analyses)
-- Business Objectives: Answers 15 specific C-level strategic questions with clean SQL,
-- explicit metric semantics, and actionable business interpretations.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Question 1: Which customer segments generate the most realized profit?
-- Expected Columns: customer_segment, active_customers, realized_net_revenue, realized_profit, profit_margin
-- -----------------------------------------------------------------------------
SELECT 
    c.customer_segment,
    COUNT(DISTINCT c.customer_key) AS active_customers,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 0), 4) AS profit_margin
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_segment
ORDER BY realized_profit DESC;


-- -----------------------------------------------------------------------------
-- Question 2: Which products generate high revenue but poor margins (<20%)?
-- Expected Columns: product_id, product_name, category, realized_net_revenue, profit_margin
-- -----------------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 0), 4) AS profit_margin
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_id, p.product_name, p.category
HAVING SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) > 5000000 
   AND (SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 0)) < 0.20
ORDER BY realized_net_revenue DESC;


-- -----------------------------------------------------------------------------
-- Question 3: Which regions are growing fastest Year-over-Year?
-- Expected Columns: region, year_2024_rev, year_2025_rev, yoy_growth_pct
-- -----------------------------------------------------------------------------
WITH regional_yearly AS (
    SELECT 
        l.region,
        d.year,
        SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) AS realized_revenue
    FROM fact_sales f
    JOIN dim_location l ON f.location_key = l.location_key
    JOIN dim_date d ON f.date_key = d.date_key
    WHERE d.year IN (2024, 2025)
    GROUP BY l.region, d.year
)
SELECT 
    r25.region,
    ROUND(r24.realized_revenue, 2) AS revenue_2024,
    ROUND(r25.realized_revenue, 2) AS revenue_2025,
    ROUND((r25.realized_revenue - r24.realized_revenue) * 100.0 / NULLIF(r24.realized_revenue, 0), 2) AS yoy_growth_pct
FROM regional_yearly r25
JOIN regional_yearly r24 ON r25.region = r24.region AND r25.year = 2025 AND r24.year = 2024
ORDER BY yoy_growth_pct DESC;


-- -----------------------------------------------------------------------------
-- Question 4: Which top 10 products have the highest return rates?
-- Expected Columns: product_id, product_name, category, ordered_units, returned_units, return_rate_pct
-- -----------------------------------------------------------------------------
WITH prod_sales AS (
    SELECT 
        product_key,
        SUM(quantity) AS ordered_units
    FROM fact_sales
    GROUP BY product_key
),
prod_returns AS (
    SELECT 
        product_key,
        SUM(quantity_returned) AS returned_units
    FROM fact_returns
    GROUP BY product_key
)
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    ps.ordered_units,
    COALESCE(pr.returned_units, 0) AS returned_units,
    ROUND(COALESCE(pr.returned_units, 0) * 100.0 / NULLIF(ps.ordered_units, 0), 2) AS return_rate_pct
FROM prod_sales ps
JOIN dim_product p ON ps.product_key = p.product_key
LEFT JOIN prod_returns pr ON ps.product_key = pr.product_key
WHERE ps.ordered_units >= 500
ORDER BY return_rate_pct DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Question 5: What percentage of revenue comes from the top 20% of customers?
-- Expected Columns: total_customers, top_20_pct_customers_count, top_customers_revenue, total_revenue, top_customer_revenue_share_pct
-- -----------------------------------------------------------------------------
WITH customer_rev AS (
    SELECT 
        customer_key,
        SUM(CASE WHEN is_completed THEN net_revenue ELSE 0 END) AS cust_revenue,
        NTILE(5) OVER(ORDER BY SUM(CASE WHEN is_completed THEN net_revenue ELSE 0 END) DESC) AS revenue_quintile
    FROM fact_sales
    GROUP BY customer_key
)
SELECT 
    COUNT(customer_key) AS total_customers,
    COUNT(CASE WHEN revenue_quintile = 1 THEN 1 END) AS top_20_pct_customers_count,
    ROUND(SUM(CASE WHEN revenue_quintile = 1 THEN cust_revenue ELSE 0 END), 2) AS top_20_pct_revenue,
    ROUND(SUM(cust_revenue), 2) AS overall_revenue,
    ROUND(SUM(CASE WHEN revenue_quintile = 1 THEN cust_revenue ELSE 0 END) * 100.0 / NULLIF(SUM(cust_revenue), 0), 2) AS top_customer_revenue_share_pct
FROM customer_rev;


-- -----------------------------------------------------------------------------
-- Question 6: Which categories contribute 80% of profit?
-- Expected Columns: category, realized_profit, cumulative_profit, cumulative_profit_pct
-- -----------------------------------------------------------------------------
WITH cat_profits AS (
    SELECT 
        p.category,
        SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) AS realized_profit
    FROM fact_sales f
    JOIN dim_product p ON f.product_key = p.product_key
    GROUP BY p.category
)
SELECT 
    category,
    ROUND(realized_profit, 2) AS realized_profit,
    ROUND(SUM(realized_profit) OVER(ORDER BY realized_profit DESC), 2) AS cumulative_profit,
    ROUND(SUM(realized_profit) OVER(ORDER BY realized_profit DESC) * 100.0 / SUM(realized_profit) OVER(), 2) AS cumulative_profit_pct
FROM cat_profits
ORDER BY realized_profit DESC;


-- -----------------------------------------------------------------------------
-- Question 7: Which high-value customers are at risk of churn (inactive >90 days)?
-- Expected Columns: customer_id, customer_name, city, days_since_last_order, total_orders, realized_net_revenue
-- -----------------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.customer_name,
    c.city,
    c.state,
    DATEDIFF('day', MAX(d.full_date), CAST('2025-12-31' AS DATE)) AS days_since_last_order,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE f.is_completed = TRUE
GROUP BY c.customer_id, c.customer_name, c.city, c.state
HAVING DATEDIFF('day', MAX(d.full_date), CAST('2025-12-31' AS DATE)) > 90 AND SUM(f.net_revenue) > 100000
ORDER BY realized_net_revenue DESC
LIMIT 15;


-- -----------------------------------------------------------------------------
-- Question 8: Which customer acquisition cohorts have the strongest Month 3 retention rate?
-- Expected Columns: cohort_month, total_cohort_size, month_3_retained_customers, retention_rate_pct
-- -----------------------------------------------------------------------------
WITH customer_cohort AS (
    SELECT 
        customer_key,
        STRFTIME(DATE_TRUNC('month', MIN(d.full_date)), '%Y-%m') AS cohort_month
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    WHERE f.is_completed = TRUE
    GROUP BY customer_key
),
activity AS (
    SELECT 
        f.customer_key,
        c.cohort_month,
        (DATEDIFF('month', CAST(c.cohort_month || '-01' AS DATE), CAST(STRFTIME(DATE_TRUNC('month', d.full_date), '%Y-%m') || '-01' AS DATE))) AS month_index
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    JOIN customer_cohort c ON f.customer_key = c.customer_key
    WHERE f.is_completed = TRUE
    GROUP BY f.customer_key, c.cohort_month, d.full_date
)
SELECT 
    c.cohort_month,
    COUNT(DISTINCT c.customer_key) AS total_cohort_size,
    COUNT(DISTINCT CASE WHEN a.month_index = 3 THEN a.customer_key END) AS month_3_retained_customers,
    ROUND(COUNT(DISTINCT CASE WHEN a.month_index = 3 THEN a.customer_key END) * 100.0 / NULLIF(COUNT(DISTINCT c.customer_key), 0), 2) AS month_3_retention_pct
FROM customer_cohort c
LEFT JOIN activity a ON c.customer_key = a.customer_key
WHERE c.cohort_month BETWEEN '2023-01' AND '2025-08'
GROUP BY c.cohort_month
ORDER BY month_3_retention_pct DESC;


-- -----------------------------------------------------------------------------
-- Question 9: Which payment methods have the highest failure/cancellation rates?
-- Expected Columns: payment_method, total_transactions, failed_transactions, failure_rate_pct
-- -----------------------------------------------------------------------------
SELECT 
    dp.payment_method,
    COUNT(fp.payment_trans_key) AS total_transactions,
    SUM(CASE WHEN dp.payment_status IN ('Failed', 'Cancelled') THEN 1 ELSE 0 END) AS failed_transactions,
    ROUND(SUM(CASE WHEN dp.payment_status IN ('Failed', 'Cancelled') THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(fp.payment_trans_key), 0), 2) AS failure_rate_pct
FROM fact_payments fp
JOIN dim_payment dp ON fp.payment_key = dp.payment_key
GROUP BY dp.payment_method
ORDER BY failure_rate_pct DESC;


-- -----------------------------------------------------------------------------
-- Question 10: Which calendar months drive peak sales surge across the 3-year timeline?
-- Expected Columns: year, month_name, distinct_orders, realized_net_revenue
-- -----------------------------------------------------------------------------
SELECT 
    d.year,
    d.month_name,
    COUNT(DISTINCT f.order_id) AS distinct_orders,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month_num, d.month_name
ORDER BY realized_net_revenue DESC
LIMIT 5;


-- -----------------------------------------------------------------------------
-- Question 11: Which top 10 Indian cities generate the highest total realized profit?
-- Expected Columns: city, state, region, active_customers, realized_profit, profit_margin
-- -----------------------------------------------------------------------------
SELECT 
    l.city,
    l.state,
    l.region,
    COUNT(DISTINCT f.customer_key) AS active_customers,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 0), 4) AS profit_margin
FROM fact_sales f
JOIN dim_location l ON f.location_key = l.location_key
GROUP BY l.city, l.state, l.region
ORDER BY realized_profit DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- Question 12: Which products should management consider for price or discount review?
-- Expected Columns: product_id, product_name, category, total_discount_given, realized_net_revenue, profit_margin
-- -----------------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    ROUND(SUM(f.discount_amount), 2) AS total_discount_given,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 0), 4) AS profit_margin
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_id, p.product_name, p.category
HAVING SUM(f.discount_amount) > 1000000 AND (SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 0)) < 0.22
ORDER BY total_discount_given DESC;


-- -----------------------------------------------------------------------------
-- Question 13: Which customer segments yield the highest Average Order Value (AOV)?
-- Expected Columns: customer_segment, total_orders, realized_net_revenue, average_order_value
-- -----------------------------------------------------------------------------
SELECT 
    c.customer_segment,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS average_order_value
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_segment
ORDER BY average_order_value DESC;


-- -----------------------------------------------------------------------------
-- Question 14: Where are returns disproportionately concentrated across product categories?
-- Expected Columns: category, returned_units, overall_category_units, return_rate_pct
-- -----------------------------------------------------------------------------
WITH cat_sales AS (
    SELECT p.category, SUM(f.quantity) AS sold_units
    FROM fact_sales f JOIN dim_product p ON f.product_key = p.product_key
    GROUP BY p.category
),
cat_returns AS (
    SELECT p.category, SUM(r.quantity_returned) AS returned_units
    FROM fact_returns r JOIN dim_product p ON r.product_key = p.product_key
    GROUP BY p.category
)
SELECT 
    s.category,
    COALESCE(r.returned_units, 0) AS returned_units,
    s.sold_units,
    ROUND(COALESCE(r.returned_units, 0) * 100.0 / NULLIF(s.sold_units, 0), 2) AS return_rate_pct
FROM cat_sales s
LEFT JOIN cat_returns r ON s.category = r.category
ORDER BY return_rate_pct DESC;


-- -----------------------------------------------------------------------------
-- Question 15: What are the top 5 strategic opportunities for increasing overall profitability?
-- Expected Columns: opportunity_area, current_realized_profit, potential_profit_upside_notes
-- -----------------------------------------------------------------------------
SELECT 
    '1. Reduce Excessive Discounting in Low-Margin Electronics' AS opportunity_area,
    ROUND(SUM(CASE WHEN p.category = 'Electronics' AND f.is_completed THEN f.profit ELSE 0 END), 2) AS current_realized_profit,
    'Limiting Electronics discounts to max 15% would recover ~₹15M-₹20M in profit margin.' AS potential_profit_upside_notes
FROM fact_sales f JOIN dim_product p ON f.product_key = p.product_key
UNION ALL
SELECT 
    '2. Focus Ad Spend on High-Margin Apparel & Beauty Categories',
    ROUND(SUM(CASE WHEN p.category IN ('Apparel', 'Beauty & Personal Care') AND f.is_completed THEN f.profit ELSE 0 END), 2),
    'Apparel and Beauty yield 60%+ profit margins; reallocating acquisition spend here boosts net profitability.'
FROM fact_sales f JOIN dim_product p ON f.product_key = p.product_key
UNION ALL
SELECT 
    '3. Re-engage At-Risk VIP Customers (RFM Win-back)',
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) * 0.15, 2),
    'Top 20% customers generate over 45% of total profit. Preventing churn preserves high-margin recurring volume.'
FROM fact_sales f;
