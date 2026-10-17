-- =============================================================================
-- NovaCart SQL Analysis Suite — 06: RFM Customer Segmentation
-- Business Objectives: Quantile scoring (NTILE 5) for Recency, Frequency, Monetary metrics
-- and rule-based customer segment classification.
-- =============================================================================

-- 1. Base Customer RFM Metrics Calculation
WITH customer_rfm_raw AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.customer_segment AS original_segment,
        c.city,
        c.state,
        
        -- Recency: Days since latest realized purchase relative to 2025-12-31
        DATEDIFF('day', MAX(d.full_date), CAST('2025-12-31' AS DATE)) AS recency_days,
        
        -- Frequency: Count of distinct completed orders
        COUNT(DISTINCT f.order_id) AS frequency_orders,
        
        -- Monetary: Total realized net revenue
        SUM(f.net_revenue) AS monetary_revenue,
        SUM(f.profit) AS monetary_profit
    FROM fact_sales f
    JOIN dim_customer c ON f.customer_key = c.customer_key
    JOIN dim_date d ON f.date_key = d.date_key
    WHERE f.is_completed = TRUE
    GROUP BY c.customer_id, c.customer_name, c.customer_segment, c.city, c.state
),

-- 2. Quintile Scoring via NTILE(5)
rfm_scores AS (
    SELECT 
        customer_id,
        customer_name,
        original_segment,
        city,
        state,
        recency_days,
        frequency_orders,
        monetary_revenue,
        monetary_profit,
        
        -- Recency Score: Lower recency_days gets higher score (5 = most recent)
        NTILE(5) OVER(ORDER BY recency_days DESC) AS r_score,
        
        -- Frequency Score: Higher orders get higher score (5 = highest freq)
        NTILE(5) OVER(ORDER BY frequency_orders ASC) AS f_score,
        
        -- Monetary Score: Higher spend gets higher score (5 = highest spend)
        NTILE(5) OVER(ORDER BY monetary_revenue ASC) AS m_score
    FROM customer_rfm_raw
),

-- 3. Segment Mapping Classification
rfm_segmented AS (
    SELECT 
        customer_id,
        customer_name,
        original_segment,
        city,
        state,
        recency_days,
        frequency_orders,
        ROUND(monetary_revenue, 2) AS monetary_revenue,
        ROUND(monetary_profit, 2) AS monetary_profit,
        r_score,
        f_score,
        m_score,
        (r_score * 100 + f_score * 10 + m_score) AS rfm_composite_score,
        CASE 
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 3 AND f_score <= 3 AND m_score <= 3 THEN 'Potential Loyalists'
            WHEN r_score >= 4 AND f_score = 1 THEN 'New Customers'
            WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'Can''t Lose Them'
            ELSE 'Hibernating / Lost'
        END AS rfm_segment
    FROM rfm_scores
)

-- 4. Segment Summary Report
SELECT 
    rfm_segment,
    COUNT(customer_id) AS customer_count,
    ROUND(COUNT(customer_id) * 100.0 / SUM(COUNT(customer_id)) OVER(), 2) AS customer_pct_share,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(frequency_orders), 1) AS avg_frequency_orders,
    ROUND(SUM(monetary_revenue), 2) AS segment_total_revenue,
    ROUND(SUM(monetary_profit), 2) AS segment_total_profit,
    ROUND(SUM(monetary_revenue) * 100.0 / SUM(SUM(monetary_revenue)) OVER(), 2) AS revenue_pct_share,
    ROUND(SUM(monetary_revenue) / NULLIF(SUM(frequency_orders), 0), 2) AS segment_aov
FROM rfm_segmented
GROUP BY rfm_segment
ORDER BY segment_total_revenue DESC;
