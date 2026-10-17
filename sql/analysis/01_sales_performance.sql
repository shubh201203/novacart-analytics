-- =============================================================================
-- NovaCart SQL Analysis Suite — 01: Sales Performance
-- Business Objectives: Overall sales performance, order counts, status breakdowns,
-- AOV, and monthly revenue/profit trends adhering to Phase 3.1 metric semantics.
-- =============================================================================

-- 1. Global High-Level Sales KPI Summary
-- Demonstrates: Conditional aggregation, DISTINCT order counts vs order line counts,
-- and explicit labeling of Total Placed vs Realized Net Revenue.
SELECT 
    COUNT(*) AS total_order_lines,
    COUNT(DISTINCT order_id) AS total_distinct_orders,
    SUM(quantity) AS total_units_sold,
    COUNT(DISTINCT customer_key) AS total_active_customers,
    
    -- Financial Totals (Placed Demand)
    ROUND(SUM(gross_sales), 2) AS total_placed_gross_sales,
    ROUND(SUM(discount_amount), 2) AS total_placed_discount_amount,
    ROUND(SUM(net_revenue), 2) AS total_placed_net_revenue,
    ROUND(SUM(profit), 2) AS total_placed_profit,
    
    -- Realized Totals (Completed & Shipped Orders Only)
    ROUND(SUM(CASE WHEN is_completed THEN net_revenue ELSE 0 END), 2) AS realized_net_revenue,
    ROUND(SUM(CASE WHEN is_completed THEN profit ELSE 0 END), 2) AS realized_profit,
    
    -- AOV & Customer Metrics
    ROUND(SUM(net_revenue) / COUNT(DISTINCT order_id), 2) AS avg_order_value_placed,
    ROUND(SUM(CASE WHEN is_completed THEN net_revenue ELSE 0 END) / NULLIF(COUNT(DISTINCT CASE WHEN is_completed THEN order_id END), 0), 2) AS avg_order_value_realized,
    ROUND(CAST(SUM(quantity) AS DECIMAL) / COUNT(DISTINCT order_id), 2) AS avg_items_per_order,
    ROUND(SUM(net_revenue) / COUNT(DISTINCT customer_key), 2) AS revenue_per_customer,
    ROUND(SUM(profit) / COUNT(DISTINCT customer_key), 2) AS profit_per_customer
FROM fact_sales;


-- 2. Revenue & Order Distribution by Order Status
-- Business Question: How is order volume and revenue split across lifecycle states?
SELECT 
    order_status,
    COUNT(DISTINCT order_id) AS distinct_orders,
    COUNT(*) AS order_lines,
    SUM(quantity) AS units_sold,
    ROUND(SUM(net_revenue), 2) AS total_placed_net_revenue,
    ROUND(SUM(profit), 2) AS total_placed_profit,
    ROUND(SUM(net_revenue) * 100.0 / SUM(SUM(net_revenue)) OVER(), 2) AS revenue_percentage_share
FROM fact_sales
GROUP BY order_status
ORDER BY total_placed_net_revenue DESC;


-- 3. Monthly Sales & Profit Performance Trend
-- Business Question: What is the month-by-month trajectory of placed vs realized revenue?
SELECT 
    d.year,
    d.month_num,
    d.month_name,
    COUNT(DISTINCT f.order_id) AS distinct_orders,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.net_revenue), 2) AS total_placed_net_revenue,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue,
    ROUND(SUM(f.profit), 2) AS total_placed_profit,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.net_revenue), 0), 4) AS profit_margin
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month_num, d.month_name
ORDER BY d.year, d.month_num;
