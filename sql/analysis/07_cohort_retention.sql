-- =============================================================================
-- NovaCart SQL Analysis Suite — 07: Cohort Retention Analysis
-- Business Objectives: Tracks customer acquisition cohorts over time, measuring
-- active repeat customers and retention rate % across subsequent months.
-- =============================================================================

-- 1. Identify Customer Acquisition Cohort Month (First Realized Purchase Date)
WITH customer_cohort AS (
    SELECT 
        f.customer_key,
        MIN(d.full_date) AS first_order_date,
        STRFTIME(DATE_TRUNC('month', MIN(d.full_date)), '%Y-%m') AS cohort_month
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    WHERE f.is_completed = TRUE
    GROUP BY f.customer_key
),

-- 2. Map All Subsequent Customer Activity Months
customer_activity AS (
    SELECT 
        c.customer_key,
        c.cohort_month,
        STRFTIME(DATE_TRUNC('month', d.full_date), '%Y-%m') AS activity_month,
        
        -- Calculate Month Offset (Cohort Index: 0, 1, 2, 3...)
        (DATEDIFF('month', 
            CAST(c.cohort_month || '-01' AS DATE), 
            CAST(STRFTIME(DATE_TRUNC('month', d.full_date), '%Y-%m') || '-01' AS DATE)
        )) AS month_number,
        
        SUM(f.net_revenue) AS monthly_net_revenue
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    JOIN customer_cohort c ON f.customer_key = c.customer_key
    WHERE f.is_completed = TRUE
    GROUP BY c.customer_key, c.cohort_month, STRFTIME(DATE_TRUNC('month', d.full_date), '%Y-%m'), d.full_date
),

-- 3. Aggregate Active Customers Per Cohort & Month Index
cohort_size AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_key) AS total_cohort_size
    FROM customer_cohort
    GROUP BY cohort_month
),

cohort_matrix AS (
    SELECT 
        a.cohort_month,
        s.total_cohort_size,
        a.month_number,
        COUNT(DISTINCT a.customer_key) AS active_retained_customers,
        ROUND(SUM(a.monthly_net_revenue), 2) AS cohort_revenue
    FROM customer_activity a
    JOIN cohort_size s ON a.cohort_month = s.cohort_month
    GROUP BY a.cohort_month, s.total_cohort_size, a.month_number
)

-- 4. Cohort Retention Output Matrix
SELECT 
    cohort_month,
    total_cohort_size,
    month_number AS cohort_index_month,
    active_retained_customers,
    ROUND(active_retained_customers * 100.0 / total_cohort_size, 2) AS retention_rate_pct,
    cohort_revenue
FROM cohort_matrix
WHERE cohort_month >= '2023-01' AND month_number <= 12
ORDER BY cohort_month, cohort_index_month;
