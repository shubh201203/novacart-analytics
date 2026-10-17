"""
NovaCart Backend Parameterized Queries
Encapsulates SQL analytics and dynamic filtering across dimensions and facts.
Adheres strictly to the established canonical metric definitions.
"""

from typing import Optional, Dict, Any, List, Tuple
from decimal import Decimal

def to_float(val: Any) -> float:
    if isinstance(val, (Decimal, int)):
        return float(val)
    return val if val is not None else 0.0

def build_filter_clause(
    year: Optional[int] = None,
    month: Optional[int] = None,
    region: Optional[str] = None,
    category: Optional[str] = None
) -> Tuple[str, List[Any]]:
    """Constructs WHERE conditions and parameters for dimensions joined to fact_sales."""
    conditions = []
    params = []
    
    if year is not None:
        conditions.append("d.year = %s")
        params.append(year)
    if month is not None:
        conditions.append("d.month_num = %s")
        params.append(month)
    if region and region != "All":
        conditions.append("l.region = %s")
        params.append(region)
    if category and category != "All":
        conditions.append("p.category = %s")
        params.append(category)
        
    clause = " AND ".join(conditions)
    if clause:
        clause = "AND " + clause
    return clause, params

def get_filter_options(conn) -> Dict[str, List[Any]]:
    """Returns available filter dropdown choices."""
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT year FROM dim_date WHERE year BETWEEN 2022 AND 2026 ORDER BY year;")
    years = [r["year"] for r in cur.fetchall()]
    
    cur.execute("SELECT DISTINCT region FROM dim_location WHERE region IS NOT NULL ORDER BY region;")
    regions = [r["region"] for r in cur.fetchall()]
    
    cur.execute("SELECT DISTINCT category FROM dim_product WHERE category IS NOT NULL ORDER BY category;")
    categories = [r["category"] for r in cur.fetchall()]
    
    months = [
        {"num": 1, "name": "January"}, {"num": 2, "name": "February"}, {"num": 3, "name": "March"},
        {"num": 4, "name": "April"}, {"num": 5, "name": "May"}, {"num": 6, "name": "June"},
        {"num": 7, "name": "July"}, {"num": 8, "name": "August"}, {"num": 9, "name": "September"},
        {"num": 10, "name": "October"}, {"num": 11, "name": "November"}, {"num": 12, "name": "December"}
    ]
    cur.close()
    return {
        "years": years,
        "months": months,
        "regions": regions,
        "categories": categories
    }

def get_overview_data(conn, year=None, month=None, region=None, category=None) -> Dict[str, Any]:
    """Overview Page 1: Executive C-Suite KPIs, Region Bars, Monthly Trend, Order Status Donut."""
    filter_sql, params = build_filter_clause(year, month, region, category)
    cur = conn.cursor()
    
    # 1. Main Fact Sales Aggregations
    sql_kpi = f"""
        SELECT 
            ROUND(SUM(f.net_revenue), 2) AS placed_net_revenue,
            ROUND(SUM(f.profit), 2) AS placed_profit,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
            SUM(f.quantity) AS ordered_quantity,
            COUNT(DISTINCT f.order_id) AS distinct_orders_placed,
            COUNT(DISTINCT CASE WHEN f.is_completed THEN f.order_id END) AS realized_orders,
            COUNT(DISTINCT CASE WHEN f.is_completed THEN f.customer_key END) AS active_customers
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql};
    """
    cur.execute(sql_kpi, params)
    kpi_res = cur.fetchone()
    
    # 2. Returned Revenue & Quantity (Using CTE on fact_sales to avoid duplication)
    sql_ret = f"""
        WITH filtered_sales AS (
            SELECT f.order_id, f.product_key, f.net_revenue, f.quantity
            FROM fact_sales f
            JOIN dim_date d ON f.date_key = d.date_key
            JOIN dim_location l ON f.location_key = l.location_key
            JOIN dim_product p ON f.product_key = p.product_key
            WHERE 1=1 {filter_sql}
        )
        SELECT 
            ROUND(SUM(r.quantity_returned * (s.net_revenue / s.quantity)), 2) AS returned_revenue,
            SUM(r.quantity_returned) AS returned_quantity
        FROM fact_returns r
        JOIN filtered_sales s ON r.order_id = s.order_id AND r.product_key = s.product_key;
    """
    cur.execute(sql_ret, params)
    ret_res = cur.fetchone()
    
    realized_rev = to_float(kpi_res["realized_net_revenue"])
    realized_prof = to_float(kpi_res["realized_profit"])
    returned_rev = to_float(ret_res["returned_revenue"])
    post_return_rev = round(realized_rev - returned_rev, 2)
    
    realized_margin = round((realized_prof / realized_rev * 100), 2) if realized_rev > 0 else 0.0
    ordered_qty = to_float(kpi_res["ordered_quantity"])
    returned_qty = to_float(ret_res["returned_quantity"])
    return_rate = round((returned_qty / ordered_qty * 100), 2) if ordered_qty > 0 else 0.0
    
    realized_orders = kpi_res["realized_orders"] or 0
    aov = round(realized_rev / realized_orders, 2) if realized_orders > 0 else 0.0
    
    # 3. Revenue by Region
    sql_region = f"""
        SELECT 
            l.region,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_revenue
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql}
        GROUP BY l.region
        ORDER BY realized_revenue DESC;
    """
    cur.execute(sql_region, params)
    region_data = [{ "region": r["region"], "realized_revenue": to_float(r["realized_revenue"]) } for r in cur.fetchall()]
    
    # 4. Profit by Product Category
    sql_cat = f"""
        SELECT 
            p.category,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql}
        GROUP BY p.category
        ORDER BY realized_profit DESC;
    """
    cur.execute(sql_cat, params)
    category_data = [{ "category": r["category"], "realized_profit": to_float(r["realized_profit"]) } for r in cur.fetchall()]
    
    # 5. Order Status Breakdown
    sql_status = f"""
        SELECT 
            f.order_status,
            COUNT(DISTINCT f.order_id) AS distinct_orders,
            ROUND(SUM(f.net_revenue), 2) AS net_revenue
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql}
        GROUP BY f.order_status
        ORDER BY net_revenue DESC;
    """
    cur.execute(sql_status, params)
    status_data = [{ "order_status": r["order_status"], "distinct_orders": r["distinct_orders"], "net_revenue": to_float(r["net_revenue"]) } for r in cur.fetchall()]
    
    # 6. Realized Revenue Monthly Trend
    sql_trend = f"""
        SELECT 
            d.year,
            d.month_num,
            d.month_name,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_revenue,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql}
        GROUP BY d.year, d.month_num, d.month_name
        ORDER BY d.year, d.month_num;
    """
    cur.execute(sql_trend, params)
    trend_data = [{
        "period": f"{r['month_name'][:3]} {r['year']}",
        "year": r["year"],
        "month_num": r["month_num"],
        "realized_revenue": to_float(r["realized_revenue"]),
        "realized_profit": to_float(r["realized_profit"])
    } for r in cur.fetchall()]
    
    cur.close()
    return {
        "kpis": {
            "post_return_revenue": post_return_rev,
            "realized_profit": realized_prof,
            "realized_margin": realized_margin,
            "active_customers": kpi_res["active_customers"] or 0,
            "average_order_value": aov,
            "return_rate": return_rate,
            "placed_net_revenue": to_float(kpi_res["placed_net_revenue"]),
            "realized_net_revenue": realized_rev,
            "returned_revenue": returned_rev,
            "ordered_quantity": ordered_qty,
            "returned_quantity": returned_qty,
            "realized_orders": realized_orders
        },
        "revenue_by_region": region_data,
        "profit_by_category": category_data,
        "order_status_breakdown": status_data,
        "revenue_trend": trend_data
    }

def get_sales_data(conn, year=None, month=None, region=None, category=None) -> Dict[str, Any]:
    """Sales & Profitability Page 2."""
    filter_sql, params = build_filter_clause(year, month, region, category)
    cur = conn.cursor()
    
    sql_kpi = f"""
        SELECT 
            ROUND(SUM(f.gross_sales), 2) AS gross_sales,
            ROUND(SUM(f.discount_amount), 2) AS discount_amount,
            ROUND(SUM(f.net_revenue), 2) AS total_placed_net_revenue,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_net_revenue
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql};
    """
    cur.execute(sql_kpi, params)
    kpis = cur.fetchone()
    realized_rev = to_float(kpis["realized_net_revenue"])
    realized_prof = to_float(kpis["realized_profit"])
    realized_margin = round((realized_prof / realized_rev * 100), 2) if realized_rev > 0 else 0.0
    
    # Monthly Realized Revenue vs Profit
    sql_monthly = f"""
        SELECT 
            d.year,
            d.month_num,
            d.month_name,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_revenue,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
            ROUND(SUM(f.discount_amount), 2) AS discount_amount,
            ROUND(SUM(f.discount_amount) * 100.0 / NULLIF(SUM(f.gross_sales), 0), 2) AS discount_pct
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql}
        GROUP BY d.year, d.month_num, d.month_name
        ORDER BY d.year, d.month_num;
    """
    cur.execute(sql_monthly, params)
    monthly_data = [{
        "period": f"{r['month_name'][:3]} {r['year']}",
        "realized_revenue": to_float(r["realized_revenue"]),
        "realized_profit": to_float(r["realized_profit"]),
        "discount_amount": to_float(r["discount_amount"]),
        "discount_pct": to_float(r["discount_pct"])
    } for r in cur.fetchall()]
    
    # Placed Revenue by Order Status
    sql_status = f"""
        SELECT 
            f.order_status,
            ROUND(SUM(f.net_revenue), 2) AS placed_net_revenue,
            COUNT(DISTINCT f.order_id) AS distinct_orders
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql}
        GROUP BY f.order_status
        ORDER BY placed_net_revenue DESC;
    """
    cur.execute(sql_status, params)
    status_data = [{ "order_status": r["order_status"], "placed_net_revenue": to_float(r["placed_net_revenue"]), "distinct_orders": r["distinct_orders"] } for r in cur.fetchall()]
    
    # Top 10 Products by Realized Profit
    sql_top_prod = f"""
        SELECT 
            p.product_name,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_revenue
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql}
        GROUP BY p.product_name
        ORDER BY realized_profit DESC
        LIMIT 10;
    """
    cur.execute(sql_top_prod, params)
    top_products = [{ "product_name": r["product_name"], "realized_profit": to_float(r["realized_profit"]), "realized_revenue": to_float(r["realized_revenue"]) } for r in cur.fetchall()]
    
    cur.close()
    return {
        "kpis": {
            "gross_sales": to_float(kpis["gross_sales"]),
            "discount_amount": to_float(kpis["discount_amount"]),
            "total_placed_revenue": to_float(kpis["total_placed_net_revenue"]),
            "realized_profit": realized_prof,
            "realized_margin": realized_margin
        },
        "monthly_performance": monthly_data,
        "revenue_by_status": status_data,
        "top_products": top_products
    }

def get_customers_data(conn, year=None, month=None, region=None, category=None) -> Dict[str, Any]:
    """Customer Intelligence Page 3."""
    filter_sql, params = build_filter_clause(year, month, region, category)
    cur = conn.cursor()
    
    # Customer counts & Repeat split
    sql_cust = f"""
        WITH customer_order_counts AS (
            SELECT 
                f.customer_key,
                COUNT(DISTINCT f.order_id) AS realized_orders,
                SUM(f.net_revenue) AS customer_revenue
            FROM fact_sales f
            JOIN dim_date d ON f.date_key = d.date_key
            JOIN dim_location l ON f.location_key = l.location_key
            JOIN dim_product p ON f.product_key = p.product_key
            WHERE f.is_completed = TRUE {filter_sql}
            GROUP BY f.customer_key
        )
        SELECT 
            COUNT(*) AS active_customers,
            COUNT(CASE WHEN realized_orders > 1 THEN 1 END) AS repeat_customers,
            COUNT(CASE WHEN realized_orders = 1 THEN 1 END) AS onetime_customers,
            ROUND(SUM(customer_revenue), 2) AS total_customer_revenue
        FROM customer_order_counts;
    """
    cur.execute(sql_cust, params)
    cust_res = cur.fetchone()
    
    active_c = cust_res["active_customers"] or 0
    repeat_c = cust_res["repeat_customers"] or 0
    onetime_c = cust_res["onetime_customers"] or 0
    total_rev = to_float(cust_res["total_customer_revenue"])
    repeat_share = round((repeat_c / active_c * 100), 2) if active_c > 0 else 0.0
    rev_per_active = round(total_rev / active_c, 2) if active_c > 0 else 0.0
    
    # Top 10 Customers by Realized Revenue (Monetary)
    sql_top_rev = f"""
        SELECT 
            c.customer_name,
            c.customer_id,
            c.customer_segment,
            COUNT(DISTINCT f.order_id) AS realized_orders,
            ROUND(SUM(f.net_revenue), 2) AS realized_revenue,
            ROUND(SUM(f.profit), 2) AS realized_profit
        FROM fact_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.is_completed = TRUE {filter_sql}
        GROUP BY c.customer_name, c.customer_id, c.customer_segment
        ORDER BY realized_revenue DESC
        LIMIT 10;
    """
    cur.execute(sql_top_rev, params)
    top_revenue_customers = [{
        "customer_name": r["customer_name"],
        "customer_id": r["customer_id"],
        "customer_segment": r["customer_segment"],
        "realized_orders": r["realized_orders"],
        "realized_revenue": to_float(r["realized_revenue"]),
        "realized_profit": to_float(r["realized_profit"])
    } for r in cur.fetchall()]

    # Top 10 Customers by Realized Distinct Orders (Purchase Frequency)
    sql_top_freq = f"""
        SELECT 
            c.customer_name,
            c.customer_id,
            c.customer_segment,
            COUNT(DISTINCT f.order_id) AS realized_orders,
            ROUND(SUM(f.net_revenue), 2) AS realized_revenue,
            ROUND(SUM(f.profit), 2) AS realized_profit
        FROM fact_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.is_completed = TRUE {filter_sql}
        GROUP BY c.customer_name, c.customer_id, c.customer_segment
        ORDER BY realized_orders DESC, realized_revenue DESC
        LIMIT 10;
    """
    cur.execute(sql_top_freq, params)
    top_frequency_customers = [{
        "customer_name": r["customer_name"],
        "customer_id": r["customer_id"],
        "customer_segment": r["customer_segment"],
        "realized_orders": r["realized_orders"],
        "realized_revenue": to_float(r["realized_revenue"]),
        "realized_profit": to_float(r["realized_profit"])
    } for r in cur.fetchall()]
    
    # Realized Revenue by Region
    sql_region = f"""
        SELECT 
            l.region,
            ROUND(SUM(f.net_revenue), 2) AS realized_revenue
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.is_completed = TRUE {filter_sql}
        GROUP BY l.region
        ORDER BY realized_revenue DESC;
    """
    cur.execute(sql_region, params)
    region_data = [{ "region": r["region"], "realized_revenue": to_float(r["realized_revenue"]) } for r in cur.fetchall()]
    
    cur.close()
    return {
        "kpis": {
            "active_customers": active_c,
            "repeat_customers": repeat_c,
            "onetime_customers": onetime_c,
            "repeat_customer_share": repeat_share,
            "revenue_per_active_customer": rev_per_active
        },
        "top_customers": top_revenue_customers,
        "top_customers_by_frequency": top_frequency_customers,
        "revenue_by_region": region_data
    }


def get_products_data(conn, year=None, month=None, region=None, category=None) -> Dict[str, Any]:
    """Product Analytics Page 4."""
    filter_sql, params = build_filter_clause(year, month, region, category)
    cur = conn.cursor()
    
    sql_kpis = f"""
        SELECT 
            ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_revenue,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
            ROUND(SUM(f.discount_amount) * 100.0 / NULLIF(SUM(f.gross_sales), 0), 2) AS discount_pct
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql};
    """
    cur.execute(sql_kpis, params)
    kpis = cur.fetchone()
    realized_rev = to_float(kpis["realized_revenue"])
    realized_prof = to_float(kpis["realized_profit"])
    realized_margin = round((realized_prof / realized_rev * 100), 2) if realized_rev > 0 else 0.0
    discount_pct = to_float(kpis["discount_pct"])
    
    # Category Matrix
    sql_cat = f"""
        SELECT 
            p.category,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_revenue,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END) * 100.0 / NULLIF(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 0), 2) AS realized_margin,
            ROUND(SUM(f.discount_amount) * 100.0 / NULLIF(SUM(f.gross_sales), 0), 2) AS discount_pct,
            SUM(f.quantity) AS units_sold
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql}
        GROUP BY p.category
        ORDER BY realized_revenue DESC;
    """
    cur.execute(sql_cat, params)
    category_data = [{
        "category": r["category"],
        "realized_revenue": to_float(r["realized_revenue"]),
        "realized_profit": to_float(r["realized_profit"]),
        "realized_margin": to_float(r["realized_margin"]),
        "discount_pct": to_float(r["discount_pct"]),
        "units_sold": r["units_sold"]
    } for r in cur.fetchall()]
    
    # Top 10 Products by Realized Profit
    sql_top_prod = f"""
        SELECT 
            p.product_name,
            p.category,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_revenue
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql}
        GROUP BY p.product_name, p.category
        ORDER BY realized_profit DESC
        LIMIT 10;
    """
    cur.execute(sql_top_prod, params)
    top_products = [{
        "product_name": r["product_name"],
        "category": r["category"],
        "realized_profit": to_float(r["realized_profit"]),
        "realized_revenue": to_float(r["realized_revenue"])
    } for r in cur.fetchall()]
    
    cur.close()
    return {
        "kpis": {
            "realized_revenue": realized_rev,
            "realized_profit": realized_prof,
            "realized_margin": realized_margin,
            "discount_pct": discount_pct
        },
        "category_performance": category_data,
        "top_products": top_products
    }

def get_regional_data(conn, year=None, month=None, region=None, category=None) -> Dict[str, Any]:
    """Regional Operations Page 5."""
    filter_sql, params = build_filter_clause(year, month, region, category)
    cur = conn.cursor()
    
    # KPIs
    sql_kpi = f"""
        SELECT 
            ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_revenue,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
            COUNT(DISTINCT CASE WHEN f.is_completed THEN f.order_id END) AS realized_orders,
            SUM(f.quantity) AS ordered_quantity
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql};
    """
    cur.execute(sql_kpi, params)
    kpis = cur.fetchone()
    
    sql_ret = f"""
        WITH filtered_sales AS (
            SELECT f.order_id, f.product_key
            FROM fact_sales f
            JOIN dim_date d ON f.date_key = d.date_key
            JOIN dim_location l ON f.location_key = l.location_key
            JOIN dim_product p ON f.product_key = p.product_key
            WHERE 1=1 {filter_sql}
        )
        SELECT SUM(r.quantity_returned) AS returned_quantity
        FROM fact_returns r
        JOIN filtered_sales s ON r.order_id = s.order_id AND r.product_key = s.product_key;
    """
    cur.execute(sql_ret, params)
    ret_res = cur.fetchone()
    
    ordered_qty = to_float(kpis["ordered_quantity"])
    returned_qty = to_float(ret_res["returned_quantity"])
    return_rate = round((returned_qty / ordered_qty * 100), 2) if ordered_qty > 0 else 0.0
    
    # Regional Realized Revenue & Profit
    sql_region = f"""
        SELECT 
            l.region,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_revenue,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.profit ELSE 0 END), 2) AS realized_profit,
            COUNT(DISTINCT CASE WHEN f.is_completed THEN f.order_id END) AS realized_orders
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql}
        GROUP BY l.region
        ORDER BY realized_revenue DESC;
    """
    cur.execute(sql_region, params)
    region_summary = [{
        "region": r["region"],
        "realized_revenue": to_float(r["realized_revenue"]),
        "realized_profit": to_float(r["realized_profit"]),
        "realized_orders": r["realized_orders"]
    } for r in cur.fetchall()]
    
    # Top States by Realized Revenue
    sql_state = f"""
        SELECT 
            l.state,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_revenue
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql}
        GROUP BY l.state
        ORDER BY realized_revenue DESC
        LIMIT 10;
    """
    cur.execute(sql_state, params)
    state_data = [{ "state": r["state"], "realized_revenue": to_float(r["realized_revenue"]) } for r in cur.fetchall()]
    
    # Regional Category Cross-Tab Matrix
    sql_matrix = f"""
        SELECT 
            l.region,
            p.category,
            ROUND(SUM(CASE WHEN f.is_completed THEN f.net_revenue ELSE 0 END), 2) AS realized_revenue
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE 1=1 {filter_sql}
        GROUP BY l.region, p.category
        ORDER BY l.region, p.category;
    """
    cur.execute(sql_matrix, params)
    matrix_rows = cur.fetchall()
    
    # Pivot into region -> category map
    matrix_dict: Dict[str, Dict[str, float]] = {}
    for row in matrix_rows:
        reg = row["region"]
        cat = row["category"]
        if reg not in matrix_dict:
            matrix_dict[reg] = {}
        matrix_dict[reg][cat] = to_float(row["realized_revenue"])
        
    regional_matrix = []
    for reg, cats in matrix_dict.items():
        total_reg = sum(cats.values())
        entry = { "region": reg, "total": round(total_reg, 2), **cats }
        regional_matrix.append(entry)
        
    cur.close()
    return {
        "kpis": {
            "realized_revenue": to_float(kpis["realized_revenue"]),
            "realized_profit": to_float(kpis["realized_profit"]),
            "realized_orders": kpis["realized_orders"] or 0,
            "return_rate": return_rate
        },
        "regional_summary": region_summary,
        "top_states": state_data,
        "regional_matrix": regional_matrix
    }

def get_retention_data(conn, year=None, month=None, region=None, category=None) -> Dict[str, Any]:
    """Customer Retention & RFM Page 6."""
    filter_sql, params = build_filter_clause(year, month, region, category)
    cur = conn.cursor()
    
    # KPIs
    sql_cust = f"""
        WITH customer_order_counts AS (
            SELECT 
                f.customer_key,
                COUNT(DISTINCT f.order_id) AS realized_orders,
                SUM(f.net_revenue) AS customer_revenue
            FROM fact_sales f
            JOIN dim_date d ON f.date_key = d.date_key
            JOIN dim_location l ON f.location_key = l.location_key
            JOIN dim_product p ON f.product_key = p.product_key
            WHERE f.is_completed = TRUE {filter_sql}
            GROUP BY f.customer_key
        )
        SELECT 
            COUNT(*) AS active_customers,
            COUNT(CASE WHEN realized_orders > 1 THEN 1 END) AS repeat_customers,
            COUNT(CASE WHEN realized_orders = 1 THEN 1 END) AS onetime_customers
        FROM customer_order_counts;
    """
    cur.execute(sql_cust, params)
    c_res = cur.fetchone()
    active_c = c_res["active_customers"] or 0
    repeat_c = c_res["repeat_customers"] or 0
    onetime_c = c_res["onetime_customers"] or 0
    repeat_share = round((repeat_c / active_c * 100), 2) if active_c > 0 else 0.0
    
    # Customer Segment Distribution
    sql_seg = f"""
        SELECT 
            c.customer_segment,
            COUNT(DISTINCT c.customer_key) AS customer_count,
            ROUND(SUM(f.net_revenue), 2) AS realized_revenue
        FROM fact_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.is_completed = TRUE {filter_sql}
        GROUP BY c.customer_segment
        ORDER BY realized_revenue DESC;
    """
    cur.execute(sql_seg, params)
    segment_data = [{
        "customer_segment": r["customer_segment"],
        "customer_count": r["customer_count"],
        "realized_revenue": to_float(r["realized_revenue"])
    } for r in cur.fetchall()]
    
    # Customer Value Table (Top 10)
    sql_val_table = f"""
        SELECT 
            c.customer_id,
            c.customer_segment,
            ROUND(SUM(f.net_revenue), 2) AS realized_revenue,
            ROUND(SUM(f.profit), 2) AS realized_profit,
            COUNT(DISTINCT f.order_id) AS realized_orders
        FROM fact_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_location l ON f.location_key = l.location_key
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.is_completed = TRUE {filter_sql}
        GROUP BY c.customer_id, c.customer_segment
        ORDER BY realized_revenue DESC
        LIMIT 10;
    """
    cur.execute(sql_val_table, params)
    customer_value_table = [{
        "customer_id": r["customer_id"],
        "customer_segment": r["customer_segment"],
        "realized_revenue": to_float(r["realized_revenue"]),
        "realized_profit": to_float(r["realized_profit"]),
        "realized_orders": r["realized_orders"]
    } for r in cur.fetchall()]
    
    # Cohort Retention Matrix from public.vw_cohort_retention (Filter independent or year filtered)
    cur.execute("""
        SELECT 
            cohort_month,
            months_since_first_purchase,
            cohort_customers,
            retained_customers,
            retention_rate
        FROM vw_cohort_retention
        WHERE cohort_month >= '2023-01-01'
        ORDER BY cohort_month, months_since_first_purchase;
    """)
    cohort_rows = cur.fetchall()
    cohort_matrix = [{
        "cohort_month": r["cohort_month"].strftime("%Y-%m") if hasattr(r["cohort_month"], "strftime") else str(r["cohort_month"])[:7],
        "month_offset": r["months_since_first_purchase"],
        "cohort_customers": r["cohort_customers"],
        "retained_customers": r["retained_customers"],
        "retention_rate": to_float(r["retention_rate"])
    } for r in cohort_rows]
    
    cur.close()
    return {
        "kpis": {
            "active_customers": active_c,
            "repeat_customers": repeat_c,
            "onetime_customers": onetime_c,
            "repeat_customer_share": repeat_share
        },
        "segment_distribution": segment_data,
        "customer_value_table": customer_value_table,
        "cohort_matrix": cohort_matrix
    }
