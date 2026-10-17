-- =============================================================================
-- NovaCart SQL Analysis Suite — 05: Time Series Analysis
-- Business Objectives: MoM Growth, YoY Growth, Running Totals, and Moving Averages
-- using LAG(), LEAD(), and window frames.
-- =============================================================================

-- 1. Monthly Revenue & Profit Trajectory with MoM % Growth & 3-Month Moving Average
WITH monthly_sales AS (
    SELECT 
        d.year,
        d.month_num,
        d.month_name,
        COUNT(DISTINCT f.order_id) AS distinct_orders,
        SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) AS realized_net_revenue,
        SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) AS realized_profit
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.year, d.month_num, d.month_name
)
SELECT 
    year,
    month_num,
    month_name,
    distinct_orders,
    ROUND(realized_net_revenue, 2) AS realized_net_revenue,
    
    -- Previous Month Realized Revenue via LAG()
    ROUND(LAG(realized_net_revenue, 1) OVER(ORDER BY year, month_num), 2) AS prev_month_revenue,
    
    -- Month-over-Month Growth Percentage
    ROUND(
        (realized_net_revenue - LAG(realized_net_revenue, 1) OVER(ORDER BY year, month_num)) * 100.0 / 
        NULLIF(LAG(realized_net_revenue, 1) OVER(ORDER BY year, month_num), 0), 2
    ) AS mom_revenue_growth_pct,
    
    -- 3-Month Moving Average Revenue
    ROUND(
        AVG(realized_net_revenue) OVER(
            ORDER BY year, month_num 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 2
    ) AS moving_avg_3m_revenue,
    
    -- Cumulative Running Total Revenue
    ROUND(
        SUM(realized_net_revenue) OVER(
            ORDER BY year, month_num 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ), 2
    ) AS cumulative_running_revenue
FROM monthly_sales
ORDER BY year, month_num;


-- 2. Year-over-Year (YoY) Growth Comparison
WITH yearly_monthly_sales AS (
    SELECT 
        d.year,
        d.month_num,
        d.month_name,
        SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) AS realized_net_revenue
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.year, d.month_num, d.month_name
)
SELECT 
    curr.year,
    curr.month_num,
    curr.month_name,
    ROUND(curr.realized_net_revenue, 2) AS current_year_revenue,
    ROUND(prev.realized_net_revenue, 2) AS prior_year_revenue,
    ROUND(
        (curr.realized_net_revenue - prev.realized_net_revenue) * 100.0 / NULLIF(prev.realized_net_revenue, 0), 2
    ) AS yoy_revenue_growth_pct
FROM yearly_monthly_sales curr
LEFT JOIN yearly_monthly_sales prev 
    ON curr.month_num = prev.month_num AND curr.year = prev.year + 1
WHERE curr.year >= 2024
ORDER BY curr.year, curr.month_num;
