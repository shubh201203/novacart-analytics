"""
NovaCart SQL Analysis Suite Master Runner
Executes sql/analysis/ 01-12 scripts against the Star Schema Data Warehouse
and exports clean result datasets to data/analysis_results/.
"""

import os
import sys
import pandas as pd
import duckdb

def run_sql_analysis():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(base_dir, "data", "processed", "novacart_analytics.duckdb")
    results_dir = os.path.join(base_dir, "data", "analysis_results")
    os.makedirs(results_dir, exist_ok=True)
    
    print("=" * 80)
    print("EXECUTING NOVACART ADVANCED SQL BUSINESS ANALYSIS SUITE")
    print("=" * 80)
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Data warehouse database not found at {db_path}! Run load_dw.py first.")
        
    conn = duckdb.connect(db_path)
    
    # 1. Execute Sales Performance (01)
    df_monthly_sales = conn.execute("""
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
    """).df()
    df_monthly_sales.to_csv(os.path.join(results_dir, "monthly_sales.csv"), index=False)
    print(f"[Exported] monthly_sales.csv ({len(df_monthly_sales)} rows)")

    # 2. Execute Customer Performance (02)
    df_customer_val = conn.execute("""
        SELECT 
            c.customer_id,
            c.customer_name,
            c.customer_segment,
            c.city,
            c.state,
            COUNT(DISTINCT f.order_id) AS total_realized_orders,
            SUM(f.quantity) AS total_units_purchased,
            ROUND(SUM(f.net_revenue), 2) AS realized_net_revenue,
            ROUND(SUM(f.profit), 2) AS realized_profit,
            ROUND(SUM(f.profit) / NULLIF(SUM(f.net_revenue), 0), 4) AS profit_margin
        FROM fact_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        WHERE f.is_completed = TRUE
        GROUP BY c.customer_id, c.customer_name, c.customer_segment, c.city, c.state
        ORDER BY realized_net_revenue DESC;
    """).df()
    df_customer_val.to_csv(os.path.join(results_dir, "customer_value.csv"), index=False)
    print(f"[Exported] customer_value.csv ({len(df_customer_val)} rows)")

    # 3. Execute Product Performance & Matrix (03)
    df_prod_matrix = conn.execute("""
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
    """).df()
    df_prod_matrix.to_csv(os.path.join(results_dir, "product_performance.csv"), index=False)
    print(f"[Exported] product_performance.csv ({len(df_prod_matrix)} rows)")

    # 4. Execute Regional Analysis (04)
    df_region = conn.execute("""
        SELECT 
            l.region,
            COUNT(DISTINCT f.customer_key) AS active_customers,
            COUNT(DISTINCT f.order_id) AS distinct_realized_orders,
            SUM(f.quantity) AS total_units_sold,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 0), 4) AS regional_profit_margin
        FROM fact_sales f
        JOIN dim_location l ON f.location_key = l.location_key
        GROUP BY l.region
        ORDER BY realized_net_revenue DESC;
    """).df()
    df_region.to_csv(os.path.join(results_dir, "regional_performance.csv"), index=False)
    print(f"[Exported] regional_performance.csv ({len(df_region)} rows)")

    # 5. Execute RFM Segmentation (06)
    df_rfm = conn.execute("""
        WITH customer_rfm_raw AS (
            SELECT 
                c.customer_id,
                DATEDIFF('day', MAX(d.full_date), CAST('2025-12-31' AS DATE)) AS recency_days,
                COUNT(DISTINCT f.order_id) AS frequency_orders,
                SUM(f.net_revenue) AS monetary_revenue,
                SUM(f.profit) AS monetary_profit
            FROM fact_sales f
            JOIN dim_customer c ON f.customer_key = c.customer_key
            JOIN dim_date d ON f.date_key = d.date_key
            WHERE f.is_completed = TRUE
            GROUP BY c.customer_id
        ),
        rfm_scores AS (
            SELECT 
                customer_id, recency_days, frequency_orders, monetary_revenue, monetary_profit,
                NTILE(5) OVER(ORDER BY recency_days DESC) AS r_score,
                NTILE(5) OVER(ORDER BY frequency_orders ASC) AS f_score,
                NTILE(5) OVER(ORDER BY monetary_revenue ASC) AS m_score
            FROM customer_rfm_raw
        ),
        rfm_segmented AS (
            SELECT 
                customer_id, recency_days, frequency_orders,
                ROUND(monetary_revenue, 2) AS monetary_revenue,
                ROUND(monetary_profit, 2) AS monetary_profit,
                r_score, f_score, m_score,
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
        SELECT 
            rfm_segment,
            COUNT(customer_id) AS customer_count,
            ROUND(COUNT(customer_id) * 100.0 / SUM(COUNT(customer_id)) OVER(), 2) AS customer_pct_share,
            ROUND(AVG(recency_days), 1) AS avg_recency_days,
            ROUND(AVG(frequency_orders), 1) AS avg_frequency_orders,
            ROUND(SUM(monetary_revenue), 2) AS segment_total_revenue,
            ROUND(SUM(monetary_profit), 2) AS segment_total_profit
        FROM rfm_segmented
        GROUP BY rfm_segment
        ORDER BY segment_total_revenue DESC;
    """).df()
    df_rfm.to_csv(os.path.join(results_dir, "rfm_segments.csv"), index=False)
    print(f"[Exported] rfm_segments.csv ({len(df_rfm)} rows)")

    # 6. Execute Cohort Retention (07)
    df_cohort = conn.execute("""
        WITH customer_cohort AS (
            SELECT 
                f.customer_key,
                STRFTIME(DATE_TRUNC('month', MIN(d.full_date)), '%Y-%m') AS cohort_month
            FROM fact_sales f
            JOIN dim_date d ON f.date_key = d.date_key
            WHERE f.is_completed = TRUE
            GROUP BY f.customer_key
        ),
        customer_activity AS (
            SELECT 
                c.customer_key,
                c.cohort_month,
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
        cohort_size AS (
            SELECT cohort_month, COUNT(DISTINCT customer_key) AS total_cohort_size
            FROM customer_cohort GROUP BY cohort_month
        )
        SELECT 
            a.cohort_month,
            s.total_cohort_size,
            a.month_number AS cohort_index_month,
            COUNT(DISTINCT a.customer_key) AS active_retained_customers,
            ROUND(COUNT(DISTINCT a.customer_key) * 100.0 / s.total_cohort_size, 2) AS retention_rate_pct,
            ROUND(SUM(a.monthly_net_revenue), 2) AS cohort_revenue
        FROM customer_activity a
        JOIN cohort_size s ON a.cohort_month = s.cohort_month
        WHERE a.cohort_month >= '2023-01' AND a.month_number <= 12
        GROUP BY a.cohort_month, s.total_cohort_size, a.month_number
        ORDER BY a.cohort_month, cohort_index_month;
    """).df()
    df_cohort.to_csv(os.path.join(results_dir, "cohort_retention.csv"), index=False)
    print(f"[Exported] cohort_retention.csv ({len(df_cohort)} rows)")

    # 7. Execute Return Analysis (08)
    df_return = conn.execute("""
        WITH category_sales AS (
            SELECT p.category, SUM(f.quantity) AS ordered_units, SUM(f.net_revenue) AS category_net_revenue
            FROM fact_sales f JOIN dim_product p ON f.product_key = p.product_key
            GROUP BY p.category
        ),
        category_returns AS (
            SELECT p.category, SUM(r.quantity_returned) AS returned_units
            FROM fact_returns r JOIN dim_product p ON r.product_key = p.product_key
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
    """).df()
    df_return.to_csv(os.path.join(results_dir, "return_analysis.csv"), index=False)
    print(f"[Exported] return_analysis.csv ({len(df_return)} rows)")

    # 8. Execute Payment Analysis (09)
    df_payment = conn.execute("""
        SELECT 
            dp.payment_method,
            COUNT(fp.payment_trans_key) AS total_transactions,
            SUM(CASE WHEN dp.payment_status = 'Completed' THEN 1 ELSE 0 END) AS successful_transactions,
            SUM(CASE WHEN dp.payment_status IN ('Failed', 'Cancelled') THEN 1 ELSE 0 END) AS failed_transactions,
            ROUND(SUM(CASE WHEN dp.payment_status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(fp.payment_trans_key), 2) AS payment_success_rate_pct,
            ROUND(SUM(fp.payment_amount), 2) AS total_transaction_value
        FROM fact_payments fp
        JOIN dim_payment dp ON fp.payment_key = dp.payment_key
        GROUP BY dp.payment_method
        ORDER BY total_transaction_value DESC;
    """).df()
    df_payment.to_csv(os.path.join(results_dir, "payment_analysis.csv"), index=False)
    print(f"[Exported] payment_analysis.csv ({len(df_payment)} rows)")

    # 9. Execute Profitability Analysis (10)
    df_profit = conn.execute("""
        SELECT 
            p.category,
            SUM(f.quantity) AS units_sold,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.product_cost ELSE 0 END), 2) AS realized_product_cost,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) / NULLIF(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 0), 4) AS profit_margin
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        GROUP BY p.category
        ORDER BY realized_profit DESC;
    """).df()
    df_profit.to_csv(os.path.join(results_dir, "profitability_analysis.csv"), index=False)
    print(f"[Exported] profitability_analysis.csv ({len(df_profit)} rows)")

    print("\n" + "=" * 80)
    print("PHASE 4 ADVANCED SQL BUSINESS ANALYSIS SUITE COMPLETED SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    run_sql_analysis()
