-- =============================================================================
-- NovaCart SQL Analysis Suite — 08: Return Analysis
-- Business Objectives: Identifies product quality issues, high-return categories,
-- regional return rates, and return reason distributions using safe non-multiplying CTE joins.
-- =============================================================================

-- 1. High-Level Return KPI Summary
WITH sales_totals AS (
    SELECT 
        SUM(quantity) AS total_ordered_units,
        SUM(net_revenue) AS total_placed_revenue
    FROM fact_sales
),
returns_totals AS (
    SELECT 
        SUM(quantity_returned) AS total_returned_units
    FROM fact_returns
),
returned_revenue_calc AS (
    SELECT 
        SUM(r.quantity_returned * (s.net_revenue / s.quantity)) AS total_returned_revenue
    FROM fact_returns r
    JOIN fact_sales s ON r.order_id = s.order_id AND r.product_key = s.product_key
)
SELECT 
    st.total_ordered_units,
    rt.total_returned_units,
    ROUND(rt.total_returned_units * 100.0 / st.total_ordered_units, 2) AS overall_return_rate_pct,
    ROUND(st.total_placed_revenue, 2) AS total_placed_revenue,
    ROUND(rr.total_returned_revenue, 2) AS total_returned_revenue,
    ROUND(rr.total_returned_revenue * 100.0 / st.total_placed_revenue, 2) AS returned_revenue_pct
FROM sales_totals st, returns_totals rt, returned_revenue_calc rr;


-- 2. Return Rate & Volume by Category
WITH category_sales AS (
    SELECT 
        p.category,
        SUM(f.quantity) AS ordered_units,
        SUM(f.net_revenue) AS category_net_revenue
    FROM fact_sales f
    JOIN dim_product p ON f.product_key = p.product_key
    GROUP BY p.category
),
category_returns AS (
    SELECT 
        p.category,
        SUM(r.quantity_returned) AS returned_units
    FROM fact_returns r
    JOIN dim_product p ON r.product_key = p.product_key
    GROUP BY p.category
)
SELECT 
    cs.category,
    cs.ordered_units,
    COALESCE(cr.returned_units, 0) AS returned_units,
    ROUND(COALESCE(cr.returned_units, 0) * 100.0 / cs.ordered_units, 2) AS return_rate_pct,
    ROUND(cs.category_net_revenue, 2) AS category_net_revenue
FROM category_sales cs
LEFT JOIN category_returns cr ON cs.category = cr.category
ORDER BY return_rate_pct DESC;


-- 3. Return Reason Breakdown
SELECT 
    return_reason,
    COUNT(return_key) AS return_events_count,
    SUM(quantity_returned) AS total_returned_units,
    ROUND(SUM(quantity_returned) * 100.0 / SUM(SUM(quantity_returned)) OVER(), 2) AS percentage_share
FROM fact_returns
GROUP BY return_reason
ORDER BY total_returned_units DESC;
