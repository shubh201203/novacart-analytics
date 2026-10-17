-- =============================================================================
-- NovaCart SQL Analysis Suite — 03: Product Analysis
-- Business Objectives: Product hierarchy performance, top/bottom SKUs, category profit margins,
-- brand contribution, and automated Product Performance Matrix classification.
-- =============================================================================

-- 1. Performance Breakdown by Product Category & Subcategory
SELECT 
    p.category,
    p.subcategory,
    COUNT(DISTINCT p.product_key) AS total_skus,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.gross_sales), 2) AS total_placed_gross_sales,
    ROUND(SUM(f.discount_amount), 2) AS total_discount_given,
    ROUND(SUM(f.net_revenue), 2) AS total_placed_net_revenue,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 0), 4) AS category_profit_margin
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category, p.subcategory
ORDER BY category, realized_net_revenue DESC;


-- 2. Top 15 Products by Realized Revenue
SELECT 
    DENSE_RANK() OVER(ORDER BY SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) DESC) AS rank_by_revenue,
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 0), 4) AS profit_margin
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_id, p.product_name, p.category, p.brand
ORDER BY realized_net_revenue DESC
LIMIT 15;


-- 3. Product Performance Matrix Classification
-- Classifies products into 4 quadrants based on median revenue and median profit margin:
--   - Star Product: High Revenue & High Profit Margin
--   - Volume Driver: High Revenue & Low Profit Margin
--   - Hidden Gem: Low Revenue & High Profit Margin
--   - Underperformer: Low Revenue & Low Profit Margin
WITH product_totals AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        SUM(f.quantity) AS units_sold,
        SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) AS realized_net_revenue,
        SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) AS realized_profit,
        SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 0) AS profit_margin
    FROM fact_sales f
    JOIN dim_product p ON f.product_key = p.product_key
    GROUP BY p.product_id, p.product_name, p.category
),
thresholds AS (
    SELECT 
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY realized_net_revenue) AS median_revenue,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY profit_margin) AS median_margin
    FROM product_totals
)
SELECT 
    pt.product_id,
    pt.product_name,
    pt.category,
    pt.units_sold,
    ROUND(pt.realized_net_revenue, 2) AS realized_net_revenue,
    ROUND(pt.realized_profit, 2) AS realized_profit,
    ROUND(pt.profit_margin, 4) AS profit_margin,
    CASE 
        WHEN pt.realized_net_revenue >= t.median_revenue AND pt.profit_margin >= t.median_margin THEN 'Star Product'
        WHEN pt.realized_net_revenue >= t.median_revenue AND pt.profit_margin < t.median_margin THEN 'Volume Driver'
        WHEN pt.realized_net_revenue < t.median_revenue AND pt.profit_margin >= t.median_margin THEN 'Hidden Gem'
        ELSE 'Underperformer'
    END AS product_matrix_category
FROM product_totals pt, thresholds t
ORDER BY realized_net_revenue DESC;
