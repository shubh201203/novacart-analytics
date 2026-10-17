-- =============================================================================
-- NovaCart SQL Analysis Suite — 10: Profitability Analysis
-- Business Objectives: Category/Product profit margins, cost structure,
-- and Pareto 80/20 cumulative profit contribution analysis using window functions.
-- =============================================================================

-- 1. Detailed Category & Subcategory Profitability Breakdown
SELECT 
    p.category,
    p.subcategory,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.product_cost ELSE 0 END), 2) AS realized_product_cost,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.shipping_cost ELSE 0 END), 2) AS realized_shipping_cost,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 0), 4) AS profit_margin
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category, p.subcategory
ORDER BY realized_profit DESC;


-- 2. Pareto 80/20 Product Profit Contribution Analysis
-- Business Question: Which top products contribute to 80% of NovaCart's total realized profit?
WITH product_profits AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) AS realized_profit,
        SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) AS realized_net_revenue
    FROM fact_sales f
    JOIN dim_product p ON f.product_key = p.product_key
    GROUP BY p.product_id, p.product_name, p.category
),
pareto_calc AS (
    SELECT 
        product_id,
        product_name,
        category,
        ROUND(realized_profit, 2) AS realized_profit,
        ROUND(realized_net_revenue, 2) AS realized_net_revenue,
        
        -- Cumulative profit sum running total
        SUM(realized_profit) OVER(ORDER BY realized_profit DESC) AS cumulative_profit,
        
        -- Total profit across all products
        SUM(realized_profit) OVER() AS total_catalog_profit,
        
        -- Cumulative percentage contribution
        ROUND(
            SUM(realized_profit) OVER(ORDER BY realized_profit DESC) * 100.0 / 
            SUM(realized_profit) OVER(), 2
        ) AS cumulative_profit_pct
    FROM product_profits
)
SELECT 
    product_id,
    product_name,
    category,
    realized_profit,
    realized_net_revenue,
    cumulative_profit,
    cumulative_profit_pct,
    CASE 
        WHEN cumulative_profit_pct <= 80.0 THEN 'Core 80% Profit Driver'
        ELSE 'Tail 20% Profit Contributor'
    END AS pareto_classification
FROM pareto_calc
ORDER BY realized_profit DESC;
