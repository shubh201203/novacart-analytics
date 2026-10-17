-- =============================================================================
-- NovaCart SQL Analysis Suite — 11: Advanced Window Functions Demonstration
-- Business Objectives: Demonstrates RANK, DENSE_RANK, LAG, LEAD, SUM OVER,
-- AVG OVER, NTILE, FIRST_VALUE, and PERCENT_RANK with business documentation.
-- =============================================================================

-- A. Ranking: Top 3 Products Per Category by Realized Revenue using DENSE_RANK()
WITH category_product_revenue AS (
    SELECT 
        p.category,
        p.product_id,
        p.product_name,
        SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) AS realized_net_revenue,
        DENSE_RANK() OVER(
            PARTITION BY p.category 
            ORDER BY SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) DESC
        ) AS category_rank
    FROM fact_sales f
    JOIN dim_product p ON f.product_key = p.product_key
    GROUP BY p.category, p.product_id, p.product_name
)
SELECT 
    category,
    category_rank,
    product_id,
    product_name,
    ROUND(realized_net_revenue, 2) AS realized_net_revenue
FROM category_product_revenue
WHERE category_rank <= 3
ORDER BY category, category_rank;


-- B. Customer Ranking: Top 5 Customers Within Each Macro Region
WITH regional_customer_revenue AS (
    SELECT 
        l.region,
        c.customer_id,
        c.customer_name,
        c.city,
        SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) AS customer_realized_revenue,
        ROW_NUMBER() OVER(
            PARTITION BY l.region 
            ORDER BY SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) DESC
        ) AS regional_rank
    FROM fact_sales f
    JOIN dim_customer c ON f.customer_key = c.customer_key
    JOIN dim_location l ON f.location_key = l.location_key
    GROUP BY l.region, c.customer_id, c.customer_name, c.city
)
SELECT 
    region,
    regional_rank,
    customer_id,
    customer_name,
    city,
    ROUND(customer_realized_revenue, 2) AS customer_realized_revenue
FROM regional_customer_revenue
WHERE regional_rank <= 5
ORDER BY region, regional_rank;


-- C. Percent of Total Contribution: Category Share of Overall Realized Revenue
SELECT 
    p.category,
    ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS category_realized_revenue,
    ROUND(
        SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) * 100.0 / 
        SUM(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END)) OVER(), 2
    ) AS revenue_pct_share_of_total
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY category_realized_revenue DESC;


-- D. LEAD Function: Next Month Sales Comparison
WITH monthly_sales AS (
    SELECT 
        d.year,
        d.month_num,
        d.month_name,
        SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END) AS current_month_revenue
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.year, d.month_num, d.month_name
)
SELECT 
    year,
    month_num,
    month_name,
    ROUND(current_month_revenue, 2) AS current_month_revenue,
    ROUND(LEAD(current_month_revenue, 1) OVER(ORDER BY year, month_num), 2) AS next_month_revenue,
    ROUND(
        (LEAD(current_month_revenue, 1) OVER(ORDER BY year, month_num) - current_month_revenue) * 100.0 / 
        NULLIF(current_month_revenue, 0), 2
    ) AS project_next_month_growth_pct
FROM monthly_sales
ORDER BY year, month_num;
