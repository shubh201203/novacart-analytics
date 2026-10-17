-- =============================================================================
-- NovaCart SQL Analysis Suite — 09: Payment Analysis
-- Business Objectives: Payment gateway success rates, transaction volume,
-- payment method breakdown, and safe CTE order-level reconciliation.
-- =============================================================================

-- 1. Payment Method Transaction Volume & Success Rate
-- Uses authoritative fact_payments and dim_payment tables
SELECT 
    dp.payment_method,
    COUNT(fp.payment_trans_key) AS total_transactions,
    SUM(CASE WHEN dp.payment_status = 'Completed' THEN 1 ELSE 0 END) AS successful_transactions,
    SUM(CASE WHEN dp.payment_status IN ('Failed', 'Cancelled') THEN 1 ELSE 0 END) AS failed_transactions,
    SUM(CASE WHEN dp.payment_status = 'Refunded' THEN 1 ELSE 0 END) AS refunded_transactions,
    ROUND(SUM(CASE WHEN dp.payment_status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(fp.payment_trans_key), 2) AS payment_success_rate_pct,
    ROUND(SUM(fp.payment_amount), 2) AS total_transaction_value,
    ROUND(AVG(fp.payment_amount), 2) AS avg_transaction_value
FROM fact_payments fp
JOIN dim_payment dp ON fp.payment_key = dp.payment_key
GROUP BY dp.payment_method
ORDER BY total_transaction_value DESC;


-- 2. Safe CTE Order-Level Reconciliation between Sales & Payments
-- Prevents fact-to-fact double counting when joining sales to payment transactions
WITH order_sales_agg AS (
    SELECT 
        order_id,
        SUM(net_revenue) AS order_net_revenue,
        MAX(order_status) AS order_status
    FROM fact_sales
    GROUP BY order_id
),
order_payments_agg AS (
    SELECT 
        fp.order_id,
        dp.payment_method,
        dp.payment_status,
        SUM(fp.payment_amount) AS total_paid_amount
    FROM fact_payments fp
    JOIN dim_payment dp ON fp.payment_key = dp.payment_key
    GROUP BY fp.order_id, dp.payment_method, dp.payment_status
)
SELECT 
    p.payment_method,
    p.payment_status,
    COUNT(DISTINCT s.order_id) AS distinct_orders,
    ROUND(SUM(s.order_net_revenue), 2) AS total_order_revenue,
    ROUND(SUM(p.total_paid_amount), 2) AS total_settled_payment_amount,
    ROUND(SUM(p.total_paid_amount) - SUM(s.order_net_revenue), 2) AS variance
FROM order_sales_agg s
JOIN order_payments_agg p ON s.order_id = p.order_id
GROUP BY p.payment_method, p.payment_status
ORDER BY total_order_revenue DESC;
