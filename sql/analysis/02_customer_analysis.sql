-- =============================================================================
-- NovaCart SQL Analysis Suite — 02: Customer Analysis
-- Business Objectives: Customer lifetime value, top customer rankings, customer segment
-- profitability, repeat purchase frequency, and margin variance analysis.
-- =============================================================================

-- 1. Top 20 Customers by Realized Revenue & Realized Profit
-- Demonstrates: JOIN dim_customer, WHERE is_completed = TRUE, ROW_NUMBER window function.
WITH customer_performance AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.customer_segment,
        c.city,
        c.state,
        COUNT(DISTINCT f.order_id) AS total_realized_orders,
        SUM(f.quantity) AS total_units_purchased,
        ROUND(SUM(f.net_revenue), 2) AS realized_net_revenue,
        ROUND(SUM(f.profit), 2) AS realized_profit,
        ROUND(SUM(f.profit) / NULLIF(SUM(f.net_revenue), 0), 4) AS profit_margin,
        MIN(d.full_date) AS first_purchase_date,
        MAX(d.full_date) AS latest_purchase_date
    FROM fact_sales f
    JOIN dim_customer c ON f.customer_key = c.customer_key
    JOIN dim_date d ON f.date_key = d.date_key
    WHERE f.is_completed = TRUE
    GROUP BY c.customer_id, c.customer_name, c.customer_segment, c.city, c.state
)
SELECT 
    ROW_NUMBER() OVER(ORDER BY realized_net_revenue DESC) AS revenue_rank,
    customer_id,
    customer_name,
    customer_segment,
    city,
    state,
    total_realized_orders,
    total_units_purchased,
    realized_net_revenue,
    realized_profit,
    profit_margin,
    first_purchase_date,
    latest_purchase_date
FROM customer_performance
ORDER BY realized_net_revenue DESC
LIMIT 20;


-- 2. Performance Breakdown by Customer Segment
-- Business Question: Which customer segments yield the highest revenue, profit, and AOV?
SELECT 
    c.customer_segment,
    COUNT(DISTINCT c.customer_key) AS total_customers_in_segment,
    COUNT(DISTINCT f.order_id) AS distinct_realized_orders,
    SUM(f.quantity) AS total_units_purchased,
    ROUND(SUM(f.net_revenue), 2) AS realized_net_revenue,
    ROUND(SUM(f.profit), 2) AS realized_profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.net_revenue), 0), 4) AS segment_profit_margin,
    ROUND(SUM(f.net_revenue) / COUNT(DISTINCT f.order_id), 2) AS segment_aov,
    ROUND(SUM(f.net_revenue) / COUNT(DISTINCT c.customer_key), 2) AS revenue_per_customer
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
WHERE f.is_completed = TRUE
GROUP BY c.customer_segment
ORDER BY realized_net_revenue DESC;


-- 3. Repeat vs One-Time Customer Analysis
-- Business Question: What share of customers buy repeatedly vs single order?
WITH customer_order_counts AS (
    SELECT 
        customer_key,
        COUNT(DISTINCT order_id) AS realized_order_count,
        SUM(net_revenue) AS total_revenue
    FROM fact_sales
    WHERE is_completed = TRUE
    GROUP BY customer_key
)
SELECT 
    CASE 
        WHEN realized_order_count = 1 THEN 'One-Time Buyer'
        WHEN realized_order_count BETWEEN 2 AND 4 THEN 'Repeat Buyer (2-4 Orders)'
        WHEN realized_order_count BETWEEN 5 AND 9 THEN 'Frequent Buyer (5-9 Orders)'
        ELSE 'VIP Power Buyer (10+ Orders)'
    END AS customer_loyalty_tier,
    COUNT(customer_key) AS customer_count,
    ROUND(COUNT(customer_key) * 100.0 / SUM(COUNT(customer_key)) OVER(), 2) AS customer_pct,
    ROUND(SUM(total_revenue), 2) AS group_total_revenue,
    ROUND(SUM(total_revenue) * 100.0 / SUM(SUM(total_revenue)) OVER(), 2) AS revenue_pct
FROM customer_order_counts
GROUP BY 1
ORDER BY customer_count DESC;


-- 4. High Revenue but Low Profit Customers (Margin Variance Check)
-- Business Question: Which customers drive high sales volume but generate weak margins due to discounts?
SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.net_revenue), 2) AS realized_net_revenue,
    ROUND(SUM(f.profit), 2) AS realized_profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.net_revenue), 0), 4) AS profit_margin
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
WHERE f.is_completed = TRUE
GROUP BY c.customer_id, c.customer_name, c.customer_segment
HAVING SUM(f.net_revenue) > 100000 AND (SUM(f.profit) / NULLIF(SUM(f.net_revenue), 0)) < 0.15
ORDER BY realized_net_revenue DESC;
