-- =============================================================================
-- NovaCart SQL Analysis Suite — 04: Regional Analysis
-- Business Objectives: Geographic demand mapping across Indian regions, states, and top cities.
-- =============================================================================

-- 1. Macro Regional Performance Overview
SELECT 
    l.region,
    COUNT(DISTINCT f.customer_key) AS active_customers,
    COUNT(DISTINCT f.order_id) AS distinct_realized_orders,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 0), 4) AS regional_profit_margin,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) / COUNT(DISTINCT f.order_id), 2) AS regional_aov
FROM fact_sales f
JOIN dim_location l ON f.location_key = l.location_key
GROUP BY l.region
ORDER BY realized_net_revenue DESC;


-- 2. State Level Sales & Profit Breakdown
SELECT 
    l.region,
    l.state,
    l.state_code,
    COUNT(DISTINCT f.customer_key) AS active_customers,
    COUNT(DISTINCT f.order_id) AS distinct_realized_orders,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 0), 4) AS state_profit_margin
FROM fact_sales f
JOIN dim_location l ON f.location_key = l.location_key
GROUP BY l.region, l.state, l.state_code
ORDER BY realized_net_revenue DESC;


-- 3. Top Performing City Per Region
WITH city_rankings AS (
    SELECT 
        l.region,
        l.city,
        l.state,
        COUNT(DISTINCT f.order_id) AS distinct_orders,
        SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) AS realized_net_revenue,
        SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) AS realized_profit,
        ROW_NUMBER() OVER(PARTITION BY l.region ORDER BY SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) DESC) AS city_rank_in_region
    FROM fact_sales f
    JOIN dim_location l ON f.location_key = l.location_key
    GROUP BY l.region, l.city, l.state
)
SELECT 
    region,
    city,
    state,
    distinct_orders,
    ROUND(realized_net_revenue, 2) AS realized_net_revenue,
    ROUND(realized_profit, 2) AS realized_profit
FROM city_rankings
WHERE city_rank_in_region = 1
ORDER BY realized_net_revenue DESC;
